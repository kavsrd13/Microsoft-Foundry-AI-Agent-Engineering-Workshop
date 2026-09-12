import json
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
from call_tool import get_order_status

client = OpenAI(base_url=os.environ['AZURE_OPENAI_BASE_URL'],
    api_key=get_bearer_token_provider(DefaultAzureCredential(), 'https://cognitiveservices.azure.com/.default'))
tool = {'type':'function', 'name':'get_order_status',
        'description':'Get the status of the synthetic classroom order ACME-204.',
        'parameters':{'type':'object', 'properties':{}, 'required':[], 'additionalProperties':False}, 'strict':True}
response = client.responses.create(model=os.environ['MODEL_DEPLOYMENT_NAME'],
    input='What is the status of ACME-204?', tools=[tool],
    tool_choice={'type':'function', 'name':'get_order_status'}, parallel_tool_calls=False)
call = next(item for item in response.output if item.type == 'function_call')
assert call.name == 'get_order_status'  # Dispatch only the function we expose.
result = get_order_status()
answer = client.responses.create(model=os.environ['MODEL_DEPLOYMENT_NAME'],
    previous_response_id=response.id,
    input=[{'type':'function_call_output','call_id':call.call_id,'output':json.dumps(result)}])
print(answer.output_text)
