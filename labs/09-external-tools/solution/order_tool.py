"""Lab 09, part 1 - A tool that lives in its own service.

This is an Azure Function. It is a normal HTTP service that happens to be
easy to deploy. The agent never runs this code - your application calls it.

Run it locally with:  func start
"""

import base64
import json
from pathlib import Path

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def load_orders():
    with open(Path(__file__).parent.parent / "data/orders.json", encoding="utf-8") as f:
        return json.load(f)


@app.route(route="orders/{order_id}", methods=["GET"])
def get_order(request: func.HttpRequest) -> func.HttpResponse:
    """Return one order, but only to a caller who is allowed to see it."""

    # When this is deployed with Entra authentication switched on, the
    # platform checks the caller's token BEFORE this function runs, and
    # passes us what it found in this header. Locally there is no platform,
    # so we fake the header - which proves our logic, not our security.
    principal_header = request.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not principal_header:
        return func.HttpResponse("Who are you?", status_code=401)

    principal = json.loads(base64.b64decode(principal_header))
    roles = [claim["val"] for claim in principal["claims"]
             if claim["typ"] == "roles"]

    if "Orders.Read" not in roles:
        return func.HttpResponse("You need the Orders.Read role", status_code=403)

    wanted = request.route_params["order_id"]
    for order in load_orders():
        if order["order_id"] == wanted:
            return func.HttpResponse(json.dumps(order), mimetype="application/json")

    return func.HttpResponse("No such order", status_code=404)
