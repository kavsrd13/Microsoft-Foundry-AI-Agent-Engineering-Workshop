"""Record token and latency telemetry without prompt text. https://learn.microsoft.com/azure/foundry/observability/how-to/enable-tracing"""
import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from opentelemetry import trace


def main() -> None:
    load_dotenv()
    credential = DefaultAzureCredential()
    configure_azure_monitor(connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'], credential=credential)
    tracer = trace.get_tracer('acme.lab23')
    client = AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential).get_openai_client()
    with tracer.start_as_current_span('rag-answer') as span:
        span.set_attribute('workshop.lab', '23')
        span.set_attribute('model.deployment', os.environ['MODEL_DEPLOYMENT'])
        response = client.responses.create(model=os.environ['MODEL_DEPLOYMENT'], store=False,
            input='Give one sentence about checking evidence before answering resident enquiries.')
        span.set_attribute('gen_ai.usage.input_tokens', response.usage.input_tokens)
        span.set_attribute('gen_ai.usage.output_tokens', response.usage.output_tokens)
        print('Trace:', format(span.get_span_context().trace_id, '032x'))
        print('Tokens:', response.usage.input_tokens, response.usage.output_tokens)
    trace.get_tracer_provider().force_flush()


if __name__ == '__main__':
    main()
