"""Local structural checks; Bicep build and Azure rehearsal are separate."""
from pathlib import Path
import json
import yaml
root=Path(__file__).parent
json.loads((root/"src/infra/main.parameters.json").read_text())
azd=yaml.safe_load((root/"azure.yaml").read_text())
assert azd["services"]["web"]["host"] == "appservice"
assert (root/azd['infra']['path']/ 'main.bicep').is_file()
workflow=yaml.safe_load((root/'src/workflow.yml').read_text())
steps=workflow['jobs']['deploy']['steps']
gate=next(i for i,s in enumerate(steps) if 'gate.py' in s.get('run',''))
assert all(i>gate for i,s in enumerate(steps) if s.get('uses','').lower().startswith(('azure/webapps-deploy','azure/functions-action')))
assert 'lab23-evaluation-and-operations/src/evaluate.py' in steps[gate]['run']
for service in azd["services"].values():
    assert (root/service["project"]).is_dir()
assert "AuthLevel.FUNCTION" in (root/"src/function/function_app.py").read_text()
assert "disableLocalAuth: true" in (root/"src/infra/resources.bicep").read_text()
print("PASS: scaffold structure and service paths. No Azure deployment, Bicep compiler or tenant proof implied.")
