"""Cost arithmetic using user-supplied rates; not a price quotation. https://azure.microsoft.com/pricing/calculator/"""
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-per-million', type=float, required=True)
    parser.add_argument('--output-per-million', type=float, required=True)
    parser.add_argument('--requests', type=int, default=1000)
    args = parser.parse_args()
    assert min(args.input_per_million, args.output_per_million, args.requests) >= 0
    path = Path(__file__).resolve().parents[1] / 'data/model-results.json'
    for row in json.loads(path.read_text()):
        cost = (row['input_tokens']*args.input_per_million + row['output_tokens']*args.output_per_million)/1_000_000
        print(row['deployment'], 'estimated model cost:', round(cost*args.requests, 4), 'in the rate currency')
    print('Apply the correct model-specific rates separately. Cached/reasoning tokens, Search, Cosmos, tools and hosting are additional.')


if __name__ == '__main__':
    main()
