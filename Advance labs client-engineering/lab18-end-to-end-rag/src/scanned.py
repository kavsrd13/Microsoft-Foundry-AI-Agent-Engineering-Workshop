"""Make an image-only copy of the synthetic policy for the OCR exercise."""
from pathlib import Path
import pymupdf

root = Path(__file__).resolve().parents[1] / 'data'
with pymupdf.open(root / 'acme-code-of-conduct.pdf') as original, pymupdf.open() as scanned:
    for page in original:
        image = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
        target = scanned.new_page(width=page.rect.width, height=page.rect.height)
        target.insert_image(target.rect, stream=image.tobytes('png'))
    scanned.save(root / 'scanned-conduct.pdf')
print('Created scanned-conduct.pdf; add it to sources.json with allowed_groups before --ocr ingestion')
