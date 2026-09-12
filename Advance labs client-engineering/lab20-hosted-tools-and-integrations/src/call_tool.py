import os
import base64
import json
from pathlib import Path
from urllib.parse import urlparse
import httpx
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / '.env')

def get_order_status():
    """Read the single synthetic classroom order from the hosted service."""
    url = os.environ['ORDER_TOOL_URL']
    headers = {}
    if urlparse(url).hostname in ('localhost', '127.0.0.1'):
        # Synthetic local fixture only: this is not authentication.
        principal = {'role_typ':'roles', 'claims':[{'typ':'roles','val':'Orders.Read'}]}
        headers['X-MS-CLIENT-PRINCIPAL'] = base64.b64encode(json.dumps(principal).encode()).decode()
    else:
        assert urlparse(url).scheme == 'https'
        token = DefaultAzureCredential().get_token(os.environ['TOOL_SCOPE']).token
        headers['Authorization'] = 'Bearer ' + token
    response = httpx.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    print(get_order_status())
