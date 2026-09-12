"""Offline checks; --live verifies deployment access. https://learn.microsoft.com/agent-framework/overview/"""
import argparse
import ast
import importlib.util
import os
from pathlib import Path
from dotenv import load_dotenv
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).parent
    checks = {}
    for source in (root / 'src').glob('*.py'):
        ast.parse(source.read_text(encoding='utf-8'))
    checks['Python source parses'] = True
    checks['Foundry provider installed'] = importlib.util.find_spec('agent_framework_foundry') is not None
    checks['Synthetic data folder'] = (root / 'data').is_dir()
    if args.live:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        load_dotenv(root / '.env')
        with DefaultAzureCredential() as credential, AIProjectClient(endpoint=os.environ['PROJECT_ENDPOINT'], credential=credential) as project:
            names = [d.name for d in project.deployments.list()]
            checks['Configured deployment accessible'] = os.environ['MODEL_DEPLOYMENT_NAME'] in names
    for label, passed in checks.items():
        print(('PASS' if passed else 'FAIL') + ' ' + label)
    print('Offline checks do not prove inference, RBAC, hosting or residency.')
    raise SystemExit(0 if all(checks.values()) else 1)
if __name__ == '__main__':
    main()
