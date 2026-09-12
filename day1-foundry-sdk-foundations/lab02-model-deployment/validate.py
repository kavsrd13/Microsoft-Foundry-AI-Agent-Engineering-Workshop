"""Local checks by default; --live checks Azure. https://learn.microsoft.com/azure/foundry/how-to/deploy-models-openai"""
import argparse
import ast
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    for path in Path("src").glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"))
    print("PASS: OFFLINE source syntax; no Azure call made")
    if args.live:

        from dotenv import load_dotenv
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        load_dotenv()
        project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
        assert list(project.deployments.list()), "No deployed models returned"
        print("PASS: LIVE deployment access")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL: {type(error).__name__}: {error}")
        raise SystemExit(1)
