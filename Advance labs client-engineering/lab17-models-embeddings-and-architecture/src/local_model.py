"""Optional on-device inference. https://learn.microsoft.com/azure/foundry-local/get-started"""
import os
from pathlib import Path
from dotenv import load_dotenv
from foundry_local_sdk import Configuration, FoundryLocalManager


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    FoundryLocalManager.initialize(Configuration(app_name='acme_lab17'))
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps()
    model = manager.catalog.get_model(os.environ['LOCAL_MODEL_ALIAS'])
    model.download()
    model.load()
    for part in model.get_chat_client().complete_streaming_chat([
        {'role': 'user', 'content': 'Explain why a local model can help with offline document drafting.'}
    ]):
        if part.choices and part.choices[0].delta.content:
            print(part.choices[0].delta.content, end='', flush=True)
    print()
    model.unload()


if __name__ == '__main__':
    main()
