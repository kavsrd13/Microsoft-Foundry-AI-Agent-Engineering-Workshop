from dotenv import load_dotenv
load_dotenv()

"""A Foundry agent tool hosted on Azure Functions.

The agent never calls this code over HTTP. Instead:
  1. The agent drops a JSON message on the INPUT queue.
  2. This function is triggered by that message.
  3. It writes its answer to the OUTPUT queue, echoing the CorrelationId.
  4. The agent picks the answer up and carries on the conversation.

The CorrelationId is how the agent matches an answer to the question it asked.
Leave it out and the agent waits forever.
"""

import json
import logging

import azure.functions as func

app = func.FunctionApp()

INPUT_QUEUE = "get-weather-input-queue"
OUTPUT_QUEUE = "get-weather-output-queue"


@app.function_name(name="GetWeather")
@app.queue_trigger(arg_name="msg", queue_name=INPUT_QUEUE, connection="STORAGE_CONNECTION")
@app.queue_output(arg_name="reply", queue_name=OUTPUT_QUEUE, connection="STORAGE_CONNECTION")
def get_weather(msg: func.QueueMessage, reply: func.Out[str]) -> None:
    """Answer one tool call from the agent."""
    raw = msg.get_body().decode("utf-8")
    logging.info("Message from agent: %s", raw)

    request = json.loads(raw)

    # The agent puts the tool arguments under "function_args". Older runtimes
    # put them at the top level. Look in both places so this works either way.
    arguments = request.get("function_args") or request
    location = arguments.get("location", "an unknown place")

    # This is where real business logic would go: a database lookup, an
    # internal API call, a calculation. We fake a weather report.
    weather = f"It is {len(location) + 10} degrees and sunny in {location}."

    answer = {
        "Value": weather,
        "CorrelationId": request["CorrelationId"],   # must be echoed back exactly
    }

    reply.set(json.dumps(answer))
    logging.info("Reply to agent: %s", json.dumps(answer))
