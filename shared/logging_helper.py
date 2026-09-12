"""Optional console output; learner scripts use print to keep the concept visible."""
import json


def banner(step: str) -> None:
    print(f"\n--- {step} ---")


def log(event: str, message: str) -> None:
    print(json.dumps({"event": event, "message": message}))
