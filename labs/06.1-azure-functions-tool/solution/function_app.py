import json
import logging
import azure.functions as func

app = func.FunctionApp()

INPUT_QUEUE = "get-weather-input-queue"
OUTPUT_QUEUE = "get-weather-output-queue"


# Queue trigger receives agent tool calls from the input queue
# and returns results through the output queue binding
@app.function_name(name="GetWeather")
@app.queue_trigger(
    arg_name="msg",
    queue_name=INPUT_QUEUE,
    connection="STORAGE_CONNECTION",
)
@app.queue_output(
    arg_name="reply",
    queue_name=OUTPUT_QUEUE,
    connection="STORAGE_CONNECTION",
)
def get_weather(msg: func.QueueMessage, reply: func.Out[str]) -> None:
    raw = msg.get_body().decode("utf-8")
    logging.info("Message from agent: %s", raw)

    try:
        # Parse the incoming message from the agent
        messagepayload = json.loads(raw)

        # Extract the function arguments
        function_args = messagepayload.get("function_args") or messagepayload
        location = function_args.get("location", "Unknown location")

        # Run custom tool logic (in production, call your real internal API or database)
        weather_result = f"The weather in {location} is 22 degrees Celsius and sunny."

        # IMPORTANT: Return result with the CorrelationId from the original request
        # The agent uses this value to match the function output to the correct tool call
        response_message = {
            "Value": weather_result,
            "CorrelationId": messagepayload["CorrelationId"],
        }
        reply.set(json.dumps(response_message))
        logging.info("Reply to agent: %s", json.dumps(response_message))

    except Exception as e:
        logging.error("Error processing queue message: %s", e)
