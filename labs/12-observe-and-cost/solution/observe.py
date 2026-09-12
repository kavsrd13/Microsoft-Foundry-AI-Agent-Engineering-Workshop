"""Lab 12 - See what your agent is doing, and what it costs.

When a resident complains about an answer they got on Tuesday, you need to
be able to find that request. This lab sends traces to Application Insights
and records how many tokens each call used.

Run it with:  python observe.py
"""

import os
import time

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from opentelemetry import trace

load_dotenv()

# Prices are examples. Put your real ones here.
PRICE_PER_MILLION_INPUT = 1.0
PRICE_PER_MILLION_OUTPUT = 2.0


# --- Task 2 -----------------------------------------------------------------
def set_up_tracing():
    """Point OpenTelemetry at Application Insights.

    This MUST happen before you create any spans. A span created before the
    exporter exists is simply thrown away, and you will spend twenty minutes
    wondering why your trace never arrived.
    """
    configure_azure_monitor(
        connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
        credential=DefaultAzureCredential(),
    )
    return trace.get_tracer("acme.workshop")


# --- Task 3 -----------------------------------------------------------------
def answer_with_tracing(tracer, client, question):
    """One request, wrapped in spans so we can see its shape afterwards."""
    print("\n=== Answering a question, with tracing ===")

    # The outer span covers the whole request, the way a web request would.
    with tracer.start_as_current_span("handle-enquiry") as request_span:
        request_span.set_attribute("workshop.lab", "12")
        request_span.set_attribute("workshop.synthetic_data", True)

        # A nested span just for the model call, so we can see how much of
        # the total time was the model and how much was everything else.
        with tracer.start_as_current_span("call-the-model") as model_span:
            started = time.perf_counter()

            response = client.responses.create(
                model=os.environ["MODEL_DEPLOYMENT"],
                instructions="Answer briefly in Australian English.",
                input=question,
            )

            seconds = time.perf_counter() - started

            # These attribute names are the OpenTelemetry convention for
            # generative AI. Using the standard names means the dashboards
            # and queries other people write will understand your traces.
            model_span.set_attribute("gen_ai.usage.input_tokens",
                                     response.usage.input_tokens)
            model_span.set_attribute("gen_ai.usage.output_tokens",
                                     response.usage.output_tokens)
            model_span.set_attribute("gen_ai.request.model",
                                     os.environ["MODEL_DEPLOYMENT"])

        trace_id = format(request_span.get_span_context().trace_id, "032x")

    print("Question:", question)
    print("Answer:  ", response.output_text)
    print(f"\nTook {round(seconds, 2)}s, "
          f"{response.usage.input_tokens} in / {response.usage.output_tokens} out")
    print("Trace ID:", trace_id)

    return trace_id, response.usage


# --- Task 4 -----------------------------------------------------------------
def what_did_that_cost(usage):
    """Turn the token counts into money."""
    print("\n=== What that one answer cost ===")

    input_cost = usage.input_tokens * PRICE_PER_MILLION_INPUT / 1_000_000
    output_cost = usage.output_tokens * PRICE_PER_MILLION_OUTPUT / 1_000_000
    total = input_cost + output_cost

    print(f"  input:  {usage.input_tokens} tokens = {input_cost:.6f}")
    print(f"  output: {usage.output_tokens} tokens = {output_cost:.6f}")
    print(f"  total:  {total:.6f} per answer")
    print(f"  at 10,000 answers a day: {total * 10000:.2f} per day")

    print("\n  This is model cost only. Search, storage, hosting and the")
    print("  judge calls from Lab 11 are all extra.")


# --- Task 5 -----------------------------------------------------------------
def what_a_failure_looks_like(tracer, client):
    """Break it on purpose, so you recognise the shape of a failure later."""
    print("\n=== What a failure looks like ===")

    with tracer.start_as_current_span("handle-enquiry") as span:
        span.set_attribute("workshop.deliberate_failure", True)
        try:
            client.responses.create(
                model="this-deployment-does-not-exist",
                input="This will not work.",
            )
        except Exception as error:
            # Recording the exception on the span is what makes it findable.
            span.record_exception(error)
            span.set_status(trace.StatusCode.ERROR, str(error))
            print(f"  failed as expected: {type(error).__name__}")

        trace_id = format(span.get_span_context().trace_id, "032x")

    print("  Failed trace ID:", trace_id)
    print("  Find this one in Application Insights too. Knowing what a")
    print("  failure looks like before an incident saves an hour during one.")


# --- Task 6 -----------------------------------------------------------------
def flush_and_explain(trace_id):
    """Telemetry is batched. A script that exits without flushing sends nothing."""
    print("\n=== Sending the traces ===")
    trace.get_tracer_provider().force_flush()
    print("  flushed")

    print("\nNow go and find it. In Application Insights, open Logs and run:")
    print(f"""
    union requests, dependencies, traces
    | where operation_Id == '{trace_id}'
    | project timestamp, itemType, name, duration, customDimensions
    | order by timestamp asc
    """)
    print("Ingestion takes a few minutes. Wait before deciding it failed.")
    print("\nA printed trace ID is NOT proof of anything. Finding the trace is.")


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    tracer = set_up_tracing()

    client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    ).get_openai_client()

    trace_id, usage = answer_with_tracing(
        tracer, client, "How does a resident report a missed bin collection?"
    )
    what_did_that_cost(usage)
    what_a_failure_looks_like(tracer, client)
    flush_and_explain(trace_id)

    print("\nDone.")
