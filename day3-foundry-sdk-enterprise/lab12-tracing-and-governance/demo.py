"""Tracing: https://learn.microsoft.com/azure/foundry/observability/how-to/enable-tracing"""
import os
from pathlib import Path
from uuid import uuid4
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.core.settings import settings
from opentelemetry import trace
from dotenv import load_dotenv


def main() -> None:
    root = Path(__file__).resolve().parent
    load_dotenv()
    credential = DefaultAzureCredential()
    configure_azure_monitor(connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'], credential=credential)
    settings.tracing_implementation = 'opentelemetry'
    tracer = trace.get_tracer('acme.lab12')
    with tracer.start_as_current_span('acme-lab12-workshop-' + uuid4().hex[:6]) as span:
        span.set_attribute('workshop.synthetic_data', True)
        with AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential) as project, project.get_openai_client() as client:
            with tracer.start_as_current_span('foundry-response'):
                answer = client.responses.create(model=os.environ['MODEL_DEPLOYMENT_NAME'],
                    input='In one sentence, explain why audit trails help public-sector services.', store=False)
                print(answer.output_text)
        trace_id = format(span.get_span_context().trace_id, '032x')
        print('Trace ID:', trace_id)
        (root / 'trace-id.txt').write_text(trace_id, encoding='utf-8')
    trace.get_tracer_provider().force_flush()
    credential.close()


if __name__ == '__main__':
    main()
