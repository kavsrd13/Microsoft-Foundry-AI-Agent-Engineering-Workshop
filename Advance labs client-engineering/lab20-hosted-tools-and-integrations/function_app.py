from dotenv import load_dotenv
load_dotenv()

"""Cloud access is enforced by platform Entra authentication and caller allowlist."""
import json
import base64
from pathlib import Path
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
orders = json.loads((Path(__file__).parent / 'orders.json').read_text())

@app.route(route='orders/{order_id}', methods=['GET'])
def get_order(req: func.HttpRequest) -> func.HttpResponse:
    # Easy Auth validates cloud tokens and supplies this header. Core Tools does not.
    principal_header = req.headers.get('X-MS-CLIENT-PRINCIPAL')
    if not principal_header:
        return func.HttpResponse('Authentication required', status_code=401)
    principal = json.loads(base64.b64decode(principal_header))
    roles = [claim['val'] for claim in principal['claims']
             if claim['typ'] == principal.get('role_typ', 'roles')]
    if 'Orders.Read' not in roles:
        return func.HttpResponse('Orders.Read required', status_code=403)
    order = orders.get(req.route_params['order_id'])
    if order is None:
        return func.HttpResponse('Order not found', status_code=404)
    return func.HttpResponse(json.dumps(order), mimetype='application/json')
