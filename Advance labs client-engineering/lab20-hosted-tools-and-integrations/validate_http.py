from dotenv import load_dotenv
load_dotenv()

"""Offline HTTP integration: real Function handler behind a local test HTTP host."""
import os
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import azure.functions as func

sys.path.insert(0, str(Path(__file__).parent))
from function_app import get_order
from call_tool import get_order_status

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = func.HttpRequest(method='GET', url='http://localhost' + self.path,
            headers=dict(self.headers), body=b'', route_params={'order_id':self.path.rsplit('/', 1)[-1]})
        response = get_order(request)
        self.send_response(response.status_code)
        self.end_headers()
        self.wfile.write(response.get_body())

    def log_message(self, *args):
        pass

server = HTTPServer(('127.0.0.1', 0), Handler)
Thread(target=server.serve_forever, daemon=True).start()
os.environ['ORDER_TOOL_URL'] = f'http://127.0.0.1:{server.server_port}/api/orders/ACME-204'
assert get_order_status()['status'] == 'Scheduled'
server.shutdown()
server.server_close()
print('PASS: HTTP client -> local HTTP test host -> real Function handler. Not Azure Core Tools/Easy Auth.')
