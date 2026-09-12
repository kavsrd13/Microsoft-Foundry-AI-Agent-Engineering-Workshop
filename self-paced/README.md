# Self-paced exercises

Microsoft Learn-style HTML exercise pages for all 24 workshop labs.

**Open [`index.html`](index.html)** in a browser. Everything is static and self-contained — no CDN, no build
step and no server required. The pages work from `file://` and can equally be published to GitHub Pages or any
static host.

## Layout

```
self-paced/
  index.html                      landing page: all 24 exercises + capability map
  assets/css/style.css            self-contained stylesheet (no CDN)
  Instructions/Exercises/*.html   the 24 exercise pages
  build.py                        renderer
  content/                        exercise content as structured Python
    __init__.py                   lab order, day groupings, capability map
    day1.py  day2.py  day3.py  day4.py
    advanced1.py  advanced2.py
```

## Editing

Edit the content modules, not the HTML — the HTML is generated and will be overwritten.

```powershell
cd self-paced
python build.py
```

No dependencies beyond the standard library.

### Content format

Each exercise is a dictionary. A *step* is a list of blocks; a block is either a string (a paragraph) or a
single-key dictionary:

| Block | Renders as |
|---|---|
| `"some text"` | A paragraph, with `` `code` ``, `**bold**`, `*italic*` and `[text](url)` supported |
| `{"code": "...", "lang": "powershell"}` | A fenced code block |
| `{"bullets": [...]}` | A bulleted list |
| `{"table": ([headers], [[row], ...])}` | A table |
| `{"tip": "..."}` | A Tip callout |
| `{"note": "..."}` | A Note callout |
| `{"warn": "..."}` | A Caution callout (amber) |
| `{"ok": "..."}` | A Check callout (green), used for expected output |
| `{"h3": "..."}` / `{"h4": "..."}` | A subheading |

## Relationship to the lab folders

These pages are instructions only. The code, data, `.env.example`, validators and clean-up scripts stay in
their original lab folders — `day1-…` through `day4-…` and `Advance labs client-engineering/`. Every page
names its lab folder in the header strip, and every command it gives has been checked to point at a file that
exists.

## Conventions used in the pages

- **Expected output is stated** for each command, as a green Check callout.
- **Deliberate-break experiments** appear throughout: the fastest way to understand a control is to watch it
  fail once, on synthetic data, on purpose.
- **Environment variable names differ between exercises** (`MODEL_DEPLOYMENT` vs `MODEL_DEPLOYMENT_NAME`, and
  others). This mirrors the SDK sample each lab is based on. The pages warn at each transition; always copy
  the `.env.example` from the exercise you are running.
- **Every exercise uses its own virtual environment.** Day 4 in particular pins package versions that are
  deliberately incompatible with Days 1–3.
- **Claims are kept honest.** An offline validator passing means what its PASS line says and no more; live
  Azure behaviour, regional availability, quota, RBAC and output quality are separate checks.

See [`../LAB-ANALYSIS.md`](../LAB-ANALYSIS.md) for the review and test report behind this conversion.
