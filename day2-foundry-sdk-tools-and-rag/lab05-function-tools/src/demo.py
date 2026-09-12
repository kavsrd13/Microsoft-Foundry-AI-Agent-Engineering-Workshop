"""Function calling. https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling"""
import json
import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from state import ROOT, STATE, state

def get_order_status(order_id: str) -> dict:
    orders = json.loads((ROOT / 'data/orders.json').read_text(encoding='utf-8'))
    return next((o for o in orders if o['order_id'] == order_id), {'error': 'Order not found'})

def search_orders_by_customer(customer_name: str) -> list:
    orders = json.loads((ROOT / 'data/orders.json').read_text(encoding='utf-8'))
    return [o for o in orders if customer_name.casefold() in o['customer_name'].casefold()]

def calculate_order_total(order_id: str) -> dict:
    order = get_order_status(order_id)
    if 'error' in order:
        return order
    total = sum(item['quantity'] * item['unit_price_aud'] for item in order['items'])
    return {'order_id': order_id, 'total_aud': round(total, 2), 'currency': 'AUD'}

def main() -> None:
    load_dotenv(ROOT / '.env')
    saved = state()
    project = AIProjectClient(os.environ['PROJECT_ENDPOINT'], DefaultAzureCredential())
    functions = {'get_order_status': get_order_status, 'search_orders_by_customer': search_orders_by_customer,
                 'calculate_order_total': calculate_order_total}
    tools = []
    for name in functions:
        argument = 'customer_name' if name == 'search_orders_by_customer' else 'order_id'
        tools.append(FunctionTool(name=name, description=name.replace('_', ' '), strict=True,
            parameters={'type': 'object', 'properties': {argument: {'type': 'string'}},
                        'required': [argument], 'additionalProperties': False}))
    if 'version' not in saved:
        agent = project.agents.create_version(agent_name=saved['name'], definition=PromptAgentDefinition(
            model=os.environ['MODEL_DEPLOYMENT'], instructions='Use tools for order facts. Amounts are AUD.', tools=tools))
        saved['version'] = agent.version
        STATE.write_text(json.dumps(saved))
    client = project.get_openai_client()
    reference = {'agent': {'type': 'agent_reference', 'name': saved['name'], 'version': saved['version']}}
    first = json.loads((ROOT / 'data/orders.json').read_text(encoding='utf-8'))[0]
    started = time.monotonic()
    response = client.responses.create(input=f"Find orders for {first['customer_name']}, and get status and total for {first['order_id']}.", extra_body=reference)
    saved.setdefault('responses', []).append(response.id)
    STATE.write_text(json.dumps(saved))
    while True:
        calls = [item for item in response.output if item.type == 'function_call']
        if not calls:
            break
        if time.monotonic() - started > 540:
            raise TimeoutError('Tool loop exceeded nine-minute classroom budget; start a new response.')
        outputs = []
        for call in calls:
            result = functions[call.name](**json.loads(call.arguments))
            print('Tool:', call.name, result)
            outputs.append({'type': 'function_call_output', 'call_id': call.call_id, 'output': json.dumps(result)})
        response = client.responses.create(input=outputs, previous_response_id=response.id, extra_body=reference)
        saved['responses'].append(response.id)
        STATE.write_text(json.dumps(saved))
    print(response.output_text)

if __name__ == '__main__':
    main()
