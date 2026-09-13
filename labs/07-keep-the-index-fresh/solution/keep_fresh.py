"""Lab 07 - Keep the index fresh.

Documents change. This shows how to update an index without re-processing
everything, and how to handle a scanned PDF that has no text in it.

The whole add / change / delete cycle runs in one go, so you can watch it.

Run it with:  python keep_fresh.py
"""

import hashlib
import json
import os
from pathlib import Path

import pymupdf
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchIndex,
    SimpleField,
)
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = os.environ["SEARCH_INDEX"]
MANIFEST_PATH = Path("manifest.json")
EXTRA_FILE = Path("service-hours.txt")


# --- Task 2 -----------------------------------------------------------------
def build_manifest(chunks):
    """A fingerprint of every chunk: {id -> hash of its contents}."""
    manifest = {}
    for chunk in chunks:
        as_text = json.dumps(chunk, sort_keys=True)
        manifest[chunk["id"]] = hashlib.sha256(as_text.encode()).hexdigest()
    return manifest


def find_changes(old_manifest, new_manifest):
    """Compare two fingerprints. What is new or changed? What has gone?"""
    to_upload = []
    for chunk_id, fingerprint in new_manifest.items():
        if old_manifest.get(chunk_id) != fingerprint:
            to_upload.append(chunk_id)

    to_delete = []
    for chunk_id in old_manifest:
        if chunk_id not in new_manifest:
            to_delete.append(chunk_id)

    return to_upload, to_delete


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


# --- Task 3 -----------------------------------------------------------------
def read_all_sources():
    """Read every file listed in sources.json and cut it into chunks."""
    sources = json.loads(Path("sources.json").read_text(encoding="utf-8"))
    chunks = []

    for source in sources:
        path = Path("data") / source["file"]

        if path.suffix == ".txt":
            pages = [(1, path.read_text(encoding="utf-8"))]
        else:
            with pymupdf.open(path) as pdf:
                pages = [(number + 1, page.get_text())
                         for number, page in enumerate(pdf)]

        for page_number, text in pages:
            if not text.strip():
                raise ValueError(
                    f"{path.name} has no text in it. It is probably a scan - "
                    f"see Task 6."
                )
            # One chunk per page keeps this lab focused on change detection.
            chunks.append({
                "id": f"{path.stem}-p{page_number}",
                "content": text.strip(),
                "source": path.name,
            })

    return chunks


def sync(search_client, label):
    """Upload what changed, delete what has gone, and leave the rest alone."""
    chunks = read_all_sources()

    old_manifest = load_manifest()
    new_manifest = build_manifest(chunks)
    to_upload, to_delete = find_changes(old_manifest, new_manifest)

    if to_upload:
        documents = [c for c in chunks if c["id"] in to_upload]
        search_client.upload_documents(documents)

    if to_delete:
        search_client.delete_documents([{"id": chunk_id} for chunk_id in to_delete])

    # Only record the new state once Search has accepted everything. If the
    # upload failed above, we would not get here, and the next run would
    # simply try the same work again.
    save_manifest(new_manifest)

    unchanged = len(new_manifest) - len(to_upload)
    print(f"  {label}: {len(to_upload)} uploaded, {len(to_delete)} deleted, "
          f"{unchanged} unchanged")


# --- Task 4 -----------------------------------------------------------------
def add_extra_document(closing_time):
    """Add (or change) a small text file, and list it in sources.json."""
    EXTRA_FILE.write_text(
        "SYNTHETIC TRAINING RECORD\n\n"
        f"The service desk closes at {closing_time} on Fridays.",
        encoding="utf-8",
    )

    sources_path = Path("sources.json")
    sources = json.loads(sources_path.read_text(encoding="utf-8"))

    if not any(s["file"] == EXTRA_FILE.name for s in sources):
        sources.append({"file": EXTRA_FILE.name, "allowed_groups": ["staff"]})
        sources_path.write_text(json.dumps(sources, indent=2), encoding="utf-8")


def remove_extra_document():
    sources_path = Path("sources.json")
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    sources = [s for s in sources if s["file"] != EXTRA_FILE.name]
    sources_path.write_text(json.dumps(sources, indent=2), encoding="utf-8")
    EXTRA_FILE.unlink(missing_ok=True)


def ask(search_client, question):
    """A quick look at what the index can currently support."""
    hits = list(search_client.search(question, top=1, select=["source", "content"]))
    if not hits:
        print(f"      -> nothing in the index answers that")
    else:
        preview = hits[0]["content"][:70].replace("\n", " ")
        print(f"      -> {hits[0]['source']}: {preview}")


def run_the_whole_cycle(search_client):
    """Add, change and remove a document, syncing after each step."""
    print("\n=== The freshness cycle ===")

    print("\n1. First sync - everything is new")
    sync(search_client, "sync")

    print("\n2. Sync again with nothing changed - this should cost nothing")
    sync(search_client, "sync")

    print("\n3. Add a new document that closes at 4 pm")
    add_extra_document("4 pm")
    sync(search_client, "sync")
    ask(search_client, "When does the service desk close on Fridays?")

    print("\n4. Change it to 6 pm - the old text must not survive")
    add_extra_document("6 pm")
    sync(search_client, "sync")
    ask(search_client, "When does the service desk close on Fridays?")

    print("\n5. Remove the document - the answer must go with it")
    remove_extra_document()
    sync(search_client, "sync")
    ask(search_client, "When does the service desk close on Fridays?")

    print("\nStep 2 is the one that matters for your bill: no changes,")
    print("no work. Step 5 is the one that matters for correctness.")


# --- Task 6 -----------------------------------------------------------------
def make_a_scanned_pdf():
    """Turn a normal PDF into an image-only one, so we have something to OCR."""
    print("\n=== Making a scanned document ===")

    original_path = Path("benefits/acme-code-of-conduct.pdf")
    scanned_path = Path("scanned-conduct.pdf")

    with pymupdf.open(original_path) as original, pymupdf.open() as scanned:
        for page in original:
            picture = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
            new_page = scanned.new_page(width=page.rect.width,
                                        height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=picture.tobytes("png"))
        scanned.save(scanned_path)

    print("created", scanned_path)

    # Prove it has no text in it.
    with pymupdf.open(scanned_path) as pdf:
        text = "".join(page.get_text() for page in pdf)
    print(f"normal text extraction finds {len(text.strip())} characters - "
          f"it is just pictures")

    return scanned_path


def read_the_scan_with_ocr(scanned_path):
    """Document Intelligence can read the pixels."""
    print("\n=== Reading it with OCR ===")

    client = DocumentIntelligenceClient(
        os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"],
        DefaultAzureCredential(),
    )

    with open(scanned_path, "rb") as file:
        result = client.begin_analyze_document("prebuilt-read", body=file).result()

    for page in result.pages:
        lines = [line.content for line in page.lines]
        print(f"  page {page.page_number}: {len(lines)} lines found")
        for line in lines[:3]:
            print("     ", line)

    print("\nReading embedded text is not OCR. OCR reads the image itself.")


# --- Task 7 -----------------------------------------------------------------
def clean_up(index_client):
    print("\n=== Cleaning up ===")
    if not INDEX_NAME.startswith("lab07-"):
        raise ValueError("SEARCH_INDEX must start with 'lab07-'")
    index_client.delete_index(INDEX_NAME)
    MANIFEST_PATH.unlink(missing_ok=True)
    Path("scanned-conduct.pdf").unlink(missing_ok=True)
    print("deleted index", INDEX_NAME, "and local files")


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    credential = DefaultAzureCredential()
    index_client = SearchIndexClient(os.environ["SEARCH_ENDPOINT"], credential)
    search_client = SearchClient(os.environ["SEARCH_ENDPOINT"], INDEX_NAME, credential)

    print("=== Creating the index ===")
    index_client.create_or_update_index(SearchIndex(
        name=INDEX_NAME,
        fields=[
            SimpleField(name="id", type="Edm.String", key=True),
            SearchableField(name="content", type="Edm.String"),
            SimpleField(name="source", type="Edm.String"),
        ],
    ))
    print("index", INDEX_NAME, "is ready")

    run_the_whole_cycle(search_client)

    scanned_path = make_a_scanned_pdf()
    read_the_scan_with_ocr(scanned_path)

    # Uncomment when you have finished the lab:
    # clean_up(index_client)

    print("\nDone.")
