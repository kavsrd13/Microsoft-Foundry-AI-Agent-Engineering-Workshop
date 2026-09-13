from dotenv import load_dotenv
load_dotenv()

"""Pure chunking and freshness mechanics; no cloud dependencies."""
import hashlib
import json


def split(text, strategy, size=500, overlap=80):
    if strategy == 'fixed':
        return [text[i:i + size] for i in range(0, len(text), size - overlap)]
    # PDF text blocks retain paragraph boundaries. Pack whole blocks together.
    chunks, current = [], ''
    for paragraph in text.split('\n\n'):
        if current and len(current) + len(paragraph) > size:
            chunks.append(current)
            current = ''
        current += paragraph + '\n\n'
    if current.strip():
        chunks.append(current.strip())
    return chunks


def documents(source, page, text, groups, strategy):
    return [dict(id=hashlib.sha256(f'{source}:{page}:{i}'.encode()).hexdigest(),
                 source=source, page=page, content=chunk, allowed_groups=groups)
            for i, chunk in enumerate(split(text, strategy)) if chunk.strip()]


def manifest(documents):
    return {d['id']: hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()
            for d in documents}


def changes(previous, current):
    return ([key for key, digest in current.items() if previous.get(key) != digest],
            sorted(set(previous) - set(current)))


def metrics(ranked_sources, relevant, k=3):
    # Each source counts once. Denominator k penalises returning too few results.
    ranked = list(dict.fromkeys(ranked_sources))[:k]
    hits = len(set(ranked) & set(relevant))
    reciprocal = next((1 / (i + 1) for i, s in enumerate(ranked) if s in relevant), 0)
    return dict(precision=hits / k, recall=hits / len(relevant), reciprocal_rank=reciprocal)


def group_filter(groups):
    # Called with trusted server-side groups, never an unverified browser claim.
    clauses = ["allowed_groups/any(g: g eq '" + g.replace("'", "''") + "')" for g in groups]
    return ' or '.join(clauses) if clauses else 'false'
