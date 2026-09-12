"""Exercise the real handler; cloud token validation is a separate live check."""
import base64
import json
from pathlib import Path
import azure.functions as func
from function_app import get_order


def request(order_id='ACME-204', roles=None):
    headers = {}
    if roles is not None:
        principal = {'role_typ':'roles', 'claims':[{'typ':'roles','val':role} for role in roles]}
        headers['X-MS-CLIENT-PRINCIPAL'] = base64.b64encode(json.dumps(principal).encode()).decode()
    return func.HttpRequest(method='GET', url='http://localhost/api/orders/' + order_id,
                           headers=headers, body=b'', route_params={'order_id':order_id})

assert get_order(request()).status_code == 401
assert get_order(request(roles=[])).status_code == 403
assert get_order(request(roles=['Other.Role'])).status_code == 403
response = get_order(request(roles=['Orders.Read']))
assert response.status_code == 200
assert json.loads(response.get_body())['status'] == 'Scheduled'
assert get_order(request('missing', ['Orders.Read'])).status_code == 404
schema = json.loads((Path(__file__).parent / 'data/openapi.json').read_text())
assert schema['paths']['/api/orders/{order_id}']['get']['security'] == [{'bearerAuth':[]}]
print('PASS: missing principal, missing/wrong role, authorised result, missing order, API auth contract.')
print('Synthetic principal tests do not validate JWTs or prove deployed Easy Auth.')
