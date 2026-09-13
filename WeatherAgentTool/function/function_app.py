from dotenv import load_dotenv
load_dotenv()

import azure.functions as func
import json
import logging

app = func.FunctionApp()


@app.function_name(name="GetWeather")
@app.queue_trigger(
    arg_name="msg",
    queue_name="get-weather-input-queue",
    connection="STORAGE_CONNECTION"
)
@app.queue_output(
    arg_name="outputQueue",
    queue_name="get-weather-output-queue",
    connection="STORAGE_CONNECTION"
)
def GetWeather(
    msg: func.QueueMessage,
    outputQueue: func.Out[str]
):
    try:
        payload = json.loads(
            msg.get_body().decode("utf-8")
        )

        logging.info("Received: %s", json.dumps(payload))

        function_args = payload.get("function_args", {})
        location = function_args.get("location")

        weather_result = (
            f"Weather in {location} is 30 degrees and Sunny"
        )

        response_message = {
            "Value": weather_result,
            "CorrelationId": payload["CorrelationId"]
        }

        outputQueue.set(json.dumps(response_message))

        logging.info("Sent: %s", json.dumps(response_message))

    except Exception as e:
        logging.error("Error processing message: %s", e)