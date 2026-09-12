"""Create synthetic training data. https://pymupdf.readthedocs.io/en/latest/page.html"""
import json
import random
from pathlib import Path
import pymupdf

ROOT = Path(__file__).parent / "datasets"
POLICIES = {
    "acme-leave-policy": [
        ("Annual leave", "Full-time employees receive 20 days of annual leave per year."),
        ("Personal leave", "Full-time employees receive 10 days of personal leave per year."),
        ("Leave requests", "Submit annual leave requests through the staff portal at least 14 days before leave begins."),
        ("Approval", "The employee's line manager approves annual leave requests."),
        ("Evidence", "A medical certificate is required for personal leave lasting more than two consecutive days."),
        ("Part-time leave", "Part-time leave entitlements are calculated pro rata."),
        ("Leave support", "Contact people@acme-example.com.au for leave policy questions."),
        ("Policy review", "The synthetic leave policy is reviewed every September."),
    ],
    "acme-code-of-conduct": [
        ("Respect", "Treat colleagues and citizens with courtesy and respect."),
        ("Conflicts", "Declare conflicts of interest to your line manager before making a related decision."),
        ("Gifts", "Record gifts valued above AUD 50 in the gifts register."),
        ("Privacy", "Access citizen records only when required for assigned duties."),
        ("Reporting", "Report suspected misconduct to integrity@acme-example.com.au."),
        ("Training", "Complete code of conduct training once each year."),
    ],
    "acme-travel-policy": [
        ("Approval", "Obtain manager approval before booking business travel."),
        ("Air travel", "Use economy class for domestic flights."),
        ("Accommodation", "The accommodation limit is AUD 220 per night including GST."),
        ("Meals", "The daily meal allowance is AUD 75 including GST."),
        ("Claims", "Submit travel expense claims within 30 days of returning."),
        ("Receipts", "Attach itemised receipts to all travel expense claims."),
    ],
}
QUESTIONS = [
    "How many annual leave days do full-time employees receive?", "How many personal leave days do full-time employees receive?",
    "When and where must annual leave requests be submitted?", "Who approves annual leave?",
    "When is a medical certificate required?", "How is part-time leave calculated?",
    "Who can answer leave policy questions?", "When is the leave policy reviewed?",
    "How should colleagues and citizens be treated?", "When and to whom should conflicts of interest be declared?",
    "Which gifts must be recorded?", "When may staff access citizen records?",
    "Where is suspected misconduct reported?", "How often is conduct training required?",
    "What is required before booking travel?", "Which class is used for domestic flights?",
    "What is the accommodation limit?", "What is the daily meal allowance?",
    "When must travel claims be submitted?", "What must be attached to travel claims?",
]


def main() -> None:
    random.seed(42)
    (ROOT / "benefits").mkdir(parents=True, exist_ok=True)
    (ROOT / "eval").mkdir(exist_ok=True)
    names = ["Olivia Wilson", "Noah Nguyen", "Amelia Patel", "Jack Williams", "Charlotte Brown"]
    orders = []
    for i in range(25):
        items = [{"name": "Training workbook", "quantity": random.randint(1, 4), "unit_price_aud": 25.0},
                 {"name": "Workshop seat", "quantity": 1, "unit_price_aud": 120.0}]
        orders.append({"order_id": f"ORD-{i+1:03}", "customer_name": names[i % 5],
                       "status": ["processing", "shipped", "delivered"][i % 3],
                       "order_date": f"2026-09-{i+1:02}T09:00:00+10:00",
                       "total_aud": sum(x["quantity"] * x["unit_price_aud"] for x in items),
                       "items": items, "region": ["NSW", "VIC", "QLD", "WA", "SA"][i % 5]})
    profiles = [{"user_id": f"user-{i+1:03}", "display_name": name,
                 "groups": ["citizen-service"] if i % 2 == 0 else ["citizen-service", "hr-internal"],
                 "language": "Australian English", "tone": "concise" if i % 2 == 0 else "friendly",
                 "preferred_channel": "email"} for i, name in enumerate(names)]
    (ROOT / "orders.json").write_text(json.dumps(orders, indent=2) + "\n", encoding="utf-8")
    (ROOT / "user_preferences.json").write_text(json.dumps(profiles, indent=2) + "\n", encoding="utf-8")
    chunks, qa = [], []
    for slug, sections in POLICIES.items():
        doc = pymupdf.open()
        for offset in range(0, len(sections), 4):
            page = doc.new_page(width=595, height=842)
            page.insert_text((45, 48), "ACME PUBLIC SECTOR PTY LTD", fontsize=16, color=(0.2, 0.15, 0.45))
            page.insert_text((45, 73), "SYNTHETIC TRAINING POLICY - NOT LEGAL OR EMPLOYMENT ADVICE", fontsize=8)
            page.insert_text((45, 108), slug.replace("acme-", "").replace("-", " ").title(), fontsize=20)
            y = 145
            for title, content in sections[offset:offset+4]:
                page.insert_text((45, y), title, fontsize=12)
                page.insert_textbox(pymupdf.Rect(45, y+12, 550, y+76), content, fontsize=11)
                number = len(chunks)
                chunks.append({"id": f"chunk-{number+1:02}", "content": content,
                               "source": f"{slug}.pdf", "page": offset//4+1,
                               "allowed_groups": ["hr-internal"] if slug == "acme-leave-policy" else ["citizen-service", "hr-internal"]})
                qa.append({"query": QUESTIONS[number], "ground_truth": content,
                           "context": content, "expected_source": f"{slug}.pdf"})
                y += 94
            if slug == "acme-leave-policy" and offset == 0:
                for row, cells in enumerate([("Entitlement", "Days per year"), ("Annual leave", "20"), ("Personal leave", "10")]):
                    top = 566 + row * 30
                    for col, cell in enumerate(cells):
                        x = 45 + col * 250
                        page.draw_rect(pymupdf.Rect(x, top, x+250, top+30), color=(0.5, 0.5, 0.5))
                        page.insert_text((x+8, top+20), cell, fontsize=11)
            page.insert_text((45, 800), f"Synthetic | 10 September 2026, 09:00 AEST | Page {offset//4+1}", fontsize=9)
        doc.set_metadata({"title": slug, "author": "Acme Public Sector Pty Ltd (synthetic)", "creationDate": "D:20260910090000+10'00'"})
        doc.save(ROOT / "benefits" / f"{slug}.pdf", no_new_id=True, garbage=4, deflate=True)
        doc.close()
    (ROOT / "chunks.json").write_text(json.dumps(chunks, indent=2) + "\n", encoding="utf-8")
    (ROOT / "eval" / "qa_dataset.jsonl").write_text("\n".join(json.dumps(row) for row in qa)+"\n", encoding="utf-8")
    for path in sorted(ROOT.rglob("*")):
        if path.is_file():
            print(path.relative_to(ROOT), path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
