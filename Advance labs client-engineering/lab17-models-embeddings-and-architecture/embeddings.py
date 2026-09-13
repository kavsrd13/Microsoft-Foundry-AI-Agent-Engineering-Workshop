"""Inspect real embeddings. https://learn.microsoft.com/azure/ai-foundry/openai/how-to/embeddings"""
import json
import math
import os
import time
from pathlib import Path
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right)) / math.sqrt(sum(a*a for a in left) * sum(b*b for b in right))


def main() -> None:
    load_dotenv()
    texts = json.loads((ROOT / 'texts.json').read_text())
    token = get_bearer_token_provider(DefaultAzureCredential(), 'https://cognitiveservices.azure.com/.default')
    client = OpenAI(base_url=os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/') + '/openai/v1/', api_key=token)
    rows = []
    for dimensions in [256, 1536]:
        start = time.perf_counter()
        response = client.embeddings.create(model=os.environ['EMBEDDING_DEPLOYMENT'], input=texts, dimensions=dimensions)
        vectors = [item.embedding for item in response.data]
        assert all(len(v) == dimensions for v in vectors)
        ranking = sorted([(round(cosine(vectors[0], v), 4), text) for v, text in zip(vectors[1:], texts[1:])], reverse=True)
        row = {'dimensions': dimensions, 'seconds': round(time.perf_counter()-start, 3),
               'input_tokens': response.usage.total_tokens, 'raw_float32_bytes_per_vector': dimensions*4,
               'ranking': ranking}
        rows.append(row)
        print(json.dumps(row, indent=2))
    (ROOT / 'embedding-results.json').write_text(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
