from dotenv import load_dotenv
load_dotenv()

"""Call local ResponsesHostServer without a key. https://learn.microsoft.com/azure/foundry/how-to/develop/framework-hosted-agents"""
import json
import urllib.request
def main() -> None:
    request = urllib.request.Request('http://localhost:8088/responses', data=json.dumps({'model': 'acme-lab16-assistant', 'input': 'Explain why sources matter in a service briefing.', 'stream': False}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=120) as response:
        print(json.dumps(json.load(response), indent=2))
if __name__ == '__main__':
    main()
