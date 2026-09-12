"""A separate deployed service boundary. Function keys are a teaching-only option."""
import json
import azure.functions as func
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.route(route="collection", methods=["GET"])
def collection(req: func.HttpRequest):
    return func.HttpResponse(json.dumps({"area":"synthetic-central", "day":"Tuesday"}), mimetype="application/json")
