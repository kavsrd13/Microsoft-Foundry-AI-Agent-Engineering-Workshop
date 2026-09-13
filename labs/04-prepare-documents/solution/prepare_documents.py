"""Lab 04 - Prepare documents for search.

A PDF is not searchable. This turns three synthetic policy PDFs into small
labelled pieces of text that an index can hold.

Run it with:  python prepare_documents.py
"""

import json
import os
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

PDF_FOLDER = Path("benefits")


# --- Task 2 -----------------------------------------------------------------
def extract_one_pdf(client, pdf_path):
    """Send a PDF to Document Intelligence and get Markdown back.

    Returns a list of (page_number, page_text) so we never lose the page a
    sentence came from. Citations depend on that.
    """
    print(f"  reading {pdf_path.name} ...")

    with open(pdf_path, "rb") as file:
        operation = client.begin_analyze_document(
            "prebuilt-layout",             # understands headings and tables
            body=file,
            content_type="application/octet-stream",
            output_content_format="markdown",   # keeps tables as tables
        )
    result = operation.result()

    # Save the Markdown so you can open it and compare it with the PDF.
    markdown_path = Path("data") / (pdf_path.stem + ".md")
    markdown_path.write_text(result.content, encoding="utf-8")

    pages = []
    for page in result.pages:
        # Each page points at a slice of the returned Markdown.
        page_text = ""
        for span in page.spans:
            page_text += result.content[span.offset:span.offset + span.length]
        pages.append((page.page_number, page_text))

    print(f"    {len(pages)} pages, Markdown saved to {markdown_path}")
    return pages


# --- Task 3 -----------------------------------------------------------------
def chunk_fixed(text, size=800, overlap=150):
    """Cut the text into fixed-width windows that overlap a little.

    The overlap means a sentence split across a boundary still appears whole
    in one of the two pieces.
    """
    chunks = []
    step = size - overlap
    for start in range(0, len(text), step):
        piece = text[start:start + size]
        if piece.strip():
            chunks.append(piece)
    return chunks


def chunk_by_paragraph(text, size=800):
    """Keep whole paragraphs together, packing them up to roughly `size`."""
    chunks = []
    current = ""

    for paragraph in text.split("\n\n"):
        if current and len(current) + len(paragraph) > size:
            chunks.append(current.strip())
            current = ""
        current += paragraph + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def compare_the_two_strategies(pages):
    """Run both chunkers over the same page and look at the difference."""
    print("\n=== Comparing chunking strategies ===")

    page_number, page_text = pages[0]
    fixed = chunk_fixed(page_text)
    paragraphs = chunk_by_paragraph(page_text)

    print(f"page {page_number} is {len(page_text)} characters")
    print(f"  fixed-width  -> {len(fixed)} chunks")
    print(f"  by paragraph -> {len(paragraphs)} chunks")

    print("\nFirst fixed-width chunk starts:")
    print("  ", repr(fixed[0][:120]))
    print("First paragraph chunk starts:")
    print("  ", repr(paragraphs[0][:120]))
    print("\nLook at where the fixed-width one cuts. Does it land mid-sentence?")


# --- Task 4 -----------------------------------------------------------------
def who_can_see_this(pdf_name):
    """Decide the access labels for a document.

    The leave policy is HR-only. Everything else is fine for front-counter
    staff. In a real system this would come from the document's own metadata.
    """
    if "leave" in pdf_name:
        return ["hr-internal"]
    return ["citizen-service", "hr-internal"]


def build_chunk_records(client, strategy="paragraph"):
    """Turn every PDF into labelled chunk records, ready for an index."""
    print("\n=== Building chunk records ===")

    records = []

    for pdf_path in sorted(PDF_FOLDER.glob("*.pdf")):
        pages = extract_one_pdf(client, pdf_path)

        for page_number, page_text in pages:
            if strategy == "fixed":
                pieces = chunk_fixed(page_text)
            else:
                pieces = chunk_by_paragraph(page_text)

            for position, piece in enumerate(pieces):
                records.append({
                    # A stable id: same document, same page, same position
                    # always produces the same id. Lab 07 relies on this.
                    "id": f"{pdf_path.stem}-p{page_number}-{position}",
                    "content": piece,
                    "source": pdf_path.name,
                    "page": page_number,
                    "allowed_groups": who_can_see_this(pdf_path.name),
                })

    output = Path("chunks.json")
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\nwrote {len(records)} chunks to {output}")
    print("Open it. Every chunk knows its source, its page and who may read it.")
    return records


# --- Main -------------------------------------------------------------------
if __name__ == "__main__":
    client = DocumentIntelligenceClient(
        os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"],
        DefaultAzureCredential(),
    )

    print("=== Extracting PDFs ===")
    first_pdf_pages = extract_one_pdf(client, sorted(PDF_FOLDER.glob("*.pdf"))[0])

    compare_the_two_strategies(first_pdf_pages)
    build_chunk_records(client, strategy="paragraph")

    print("\nDone. Lab 05 turns these chunks into a searchable index.")
