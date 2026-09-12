"""Render the self-paced exercise pages from the structured content modules.

Usage (from this folder):

    python build.py

Writes Instructions/Exercises/NN-slug.html for every lab plus index.html.
No network access and no Azure calls.
"""
import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Instructions" / "Exercises"
COURSE = "Microsoft Foundry AI Agent Engineering"

# --------------------------------------------------------------------------
# inline markup: `code`, **bold**, *italic*, [text](url)
# --------------------------------------------------------------------------
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def inline(text: str) -> str:
    """Escape, then apply the small inline markup subset."""
    parts, last = [], 0
    for m in _CODE.finditer(text):
        parts.append(("t", text[last:m.start()]))
        parts.append(("c", m.group(1)))
        last = m.end()
    parts.append(("t", text[last:]))

    out = []
    for kind, chunk in parts:
        if kind == "c":
            out.append(f"<code>{html.escape(chunk)}</code>")
            continue
        chunk = html.escape(chunk)
        chunk = _LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', chunk)
        chunk = _BOLD.sub(r"<strong>\1</strong>", chunk)
        chunk = _ITAL.sub(r"<em>\1</em>", chunk)
        out.append(chunk)
    return "".join(out)


def code_block(code: str, lang: str = "text") -> str:
    body = html.escape(code.strip("\n").rstrip())
    return f'<pre><code class="language-{lang}">{body}\n</code></pre>'


def admonition(kind: str, text: str) -> str:
    cls = {"tip": "", "note": "", "warn": " class=\"warn\"", "ok": " class=\"ok\""}[kind]
    label = {"tip": "Tip", "note": "Note", "warn": "Caution", "ok": "Check"}[kind]
    return f"<blockquote{cls}><p><strong>{label}</strong>: {inline(text)}</p></blockquote>"


def table(headers, rows) -> str:
    head = "".join(f"<th>{inline(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def bullets(items) -> str:
    return "<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"


# --------------------------------------------------------------------------
# a "block" is a str (paragraph) or a dict with one of the keys below
# --------------------------------------------------------------------------
def render_block(block) -> str:
    if isinstance(block, str):
        return f"<p>{inline(block)}</p>"
    if "code" in block:
        return code_block(block["code"], block.get("lang", "text"))
    if "bullets" in block:
        return bullets(block["bullets"])
    if "table" in block:
        return table(block["table"][0], block["table"][1])
    for kind in ("tip", "note", "warn", "ok"):
        if kind in block:
            return admonition(kind, block[kind])
    if "h3" in block:
        return f'<h3 id="{slugify(block["h3"])}">{inline(block["h3"])}</h3>'
    if "h4" in block:
        return f"<h4>{inline(block['h4'])}</h4>"
    if "html" in block:
        return block["html"]
    raise ValueError(f"Unknown block: {block!r}")


def render_blocks(blocks) -> str:
    return "\n".join(render_block(b) for b in blocks or [])


def render_steps(steps) -> str:
    """Each step is a list of blocks (or a bare string)."""
    out = ["<ol>"]
    for step in steps:
        if isinstance(step, str):
            step = [step]
        out.append("<li>" + render_blocks(step) + "</li>")
    out.append("</ol>")
    return "\n".join(out)


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "section"


# --------------------------------------------------------------------------
def render_knowledge_check(items) -> str:
    out = []
    for n, q in enumerate(items, 1):
        opts = bullets(q["options"])
        why = f'<p>{inline(q["why"])}</p>' if q.get("why") else ""
        out.append(
            f'<details class="kc"><summary>{n}. {inline(q["q"])}</summary>'
            f"{opts}"
            f'<div class="ans"><p><strong>Answer: {inline(q["answer"])}</strong></p>{why}</div>'
            f"</details>"
        )
    return "\n".join(out)


def render_toc(lab) -> str:
    entries = [("before-you-start", "Before you start")]
    entries += [(slugify(s["h2"]), s["h2"]) for s in lab["sections"]]
    if lab.get("knowledge_check"):
        entries.append(("knowledge-check", "Knowledge check"))
    entries.append(("summary", "Summary"))
    entries.append(("clean-up", "Clean up"))
    items = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in entries)
    return f'<aside class="toc"><h4>On this page</h4><ul>{items}</ul></aside>'


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>{title} | {course}</title>
<link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
<div class="topbar"><div class="wrap">
  <span class="course">{course}</span>
  <span><a href="../../index.html">&#8962; All exercises</a></span>
</div></div>
<div class="container">
<main class="row">
{toc}
<article>
<h1 id="top">{h1}</h1>
{intro}
<p>This exercise takes approximately <strong>{minutes}</strong> minutes.</p>
<blockquote><p><strong>Note</strong>: Some of the technologies used in this exercise are in preview or in
active development. You may experience some unexpected behavior, warnings, or errors. All data used in this
exercise is synthetic; do not substitute real records.</p></blockquote>
{meta}
{tags}
{body}
<div class="pager">{pager}</div>
</article>
</main>
</div>
<footer class="site"><div class="wrap">
Synthetic training content for the {course} workshop. Fictional organisation: Acme Public Sector Pty Ltd.
</div></footer>
</body>
</html>
"""


def render_lab(lab, prev_lab, next_lab) -> str:
    body = []

    # --- Before you start ---
    body.append('<h2 id="before-you-start">Before you start</h2>')
    body.append(render_blocks(lab.get("before_intro", [])))
    if lab.get("objectives"):
        body.append("<h3>What you will do</h3>")
        body.append(bullets(lab["objectives"]))
    if lab.get("prereqs"):
        body.append("<h3>Prerequisites</h3>")
        body.append(bullets(lab["prereqs"]))
    body.append(render_blocks(lab.get("before_extra", [])))

    # --- Task sections ---
    for section in lab["sections"]:
        body.append(f'<h2 id="{slugify(section["h2"])}">{inline(section["h2"])}</h2>')
        body.append(render_blocks(section.get("intro", [])))
        if section.get("steps"):
            body.append(render_steps(section["steps"]))
        body.append(render_blocks(section.get("outro", [])))

    # --- Knowledge check ---
    if lab.get("knowledge_check"):
        body.append('<h2 id="knowledge-check">Knowledge check</h2>')
        body.append("<p>Answer each question, then expand it to check yourself.</p>")
        body.append(render_knowledge_check(lab["knowledge_check"]))

    # --- Summary ---
    body.append('<h2 id="summary">Summary</h2>')
    body.append(render_blocks(lab["summary"]))

    # --- Clean up ---
    body.append('<h2 id="clean-up">Clean up</h2>')
    body.append(render_blocks(lab["cleanup"]))

    # --- References ---
    if lab.get("refs"):
        body.append('<h2 id="references">Further reading</h2>')
        body.append(bullets([f"[{t}]({u})" for t, u in lab["refs"]]))

    meta_rows = [
        f'<div><strong>Lab folder</strong>: <code>{html.escape(lab["lab_path"])}</code></div>',
        f'<div><strong>Run scripts from</strong>: the lab folder (not from <code>src</code>)</div>',
    ]
    if lab.get("env_note"):
        meta_rows.append(f'<div><strong>Environment</strong>: {inline(lab["env_note"])}</div>')
    meta = f'<div class="meta">{"".join(meta_rows)}</div>'

    tags = ""
    if lab.get("module_tags"):
        chips = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in lab["module_tags"])
        track = f'<span class="tag alt">{html.escape(lab["track"])}</span>' if lab.get("track") else ""
        tags = f'<div class="tags">{track}{chips}</div>'

    pager_l = (
        f'<a href="{prev_lab["slug"]}.html">&#8592; {html.escape(prev_lab["short"])}</a>'
        if prev_lab else '<a href="../../index.html">&#8592; All exercises</a>'
    )
    pager_r = (
        f'<a href="{next_lab["slug"]}.html">{html.escape(next_lab["short"])} &#8594;</a>'
        if next_lab else '<a href="../../index.html">All exercises &#8594;</a>'
    )

    return PAGE.format(
        title=html.escape(lab["title"]),
        course=html.escape(COURSE),
        h1=inline(lab["title"]),
        toc=render_toc(lab),
        intro=render_blocks(lab["intro"]),
        minutes=lab["minutes"],
        meta=meta,
        tags=tags,
        body="\n".join(b for b in body if b.strip()),
        pager=pager_l + pager_r,
    )


INDEX = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>{course} &mdash; self-paced exercises</title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="topbar"><div class="wrap">
  <span class="course">{course}</span>
  <span>Self-paced exercises</span>
</div></div>
<div class="container">
<main class="row">
<aside class="toc"><h4>Days</h4><ul>{nav}</ul></aside>
<article>
<h1 id="top">Self-paced exercises</h1>
<p>Twenty-four hands-on exercises that build a grounded, secured, evaluated and deployed agent on
Microsoft Foundry, using synthetic data for the fictional <em>Acme Public Sector Pty&nbsp;Ltd</em>.</p>
<p>Each exercise is self-contained: it names its own prerequisites, its own Python environment and its own
clean-up. You do not have to complete them in order, though the numbering is the recommended path.</p>
<blockquote><p><strong>Note</strong>: These exercises run against Azure resources that your instructor or
administrator supplies. Running them consumes quota and incurs charges. Every dataset in this workshop is
synthetic &mdash; never substitute real citizen, staff or customer records.</p></blockquote>

<h2 id="start-here">Start here</h2>
<ol>
<li><p>Install <strong>Python 3.11</strong>, <strong>Git</strong> and the <strong>Azure CLI</strong>. Exercise 16's
hosted deployment additionally needs Python 3.13 and the Azure Developer CLI.</p></li>
<li><p>Sign in and select your subscription:</p>
<pre><code class="language-powershell">az login --tenant YOUR-TENANT-ID
az account set --subscription YOUR-SUBSCRIPTION-ID
az account show --query "{{tenant:tenantId,subscription:id}}"
</code></pre></li>
<li><p>Create a <strong>separate virtual environment for every exercise</strong>. The exercises pin different,
deliberately incompatible SDK versions &mdash; a single shared environment will break them.</p></li>
<li><p>Work through an exercise from its own folder, copying that folder's <code>.env.example</code> to
<code>.env</code> and filling in your own resource values.</p></li>
</ol>
{groups}
<h2 id="module-map">Where each capability is taught</h2>
{modmap}
</article>
</main>
</div>
<footer class="site"><div class="wrap">
Synthetic training content for the {course} workshop. Fictional organisation: Acme Public Sector Pty Ltd.
</div></footer>
</body>
</html>
"""


def render_index(labs, groups, module_map) -> str:
    nav = "".join(f'<li><a href="#{slugify(g)}">{html.escape(g)}</a></li>' for g, _ in groups)
    nav += '<li><a href="#module-map">Capability map</a></li>'

    chunks = []
    for group, blurb in groups:
        members = [l for l in labs if l["group"] == group]
        cards = []
        for lab in members:
            cards.append(
                f'<div class="card">'
                f'<div class="num">Exercise {html.escape(lab["num"])}</div>'
                f'<h3><a href="Instructions/Exercises/{lab["slug"]}.html">{inline(lab["short"])}</a></h3>'
                f'<p>{inline(lab["blurb"])}</p>'
                f'<div class="mins">{lab["minutes"]} minutes</div>'
                f"</div>"
            )
        chunks.append(
            f'<div class="daygroup"><h2 id="{slugify(group)}">{html.escape(group)}</h2>'
            f"<p>{inline(blurb)}</p>"
            f'<div class="cards">{"".join(cards)}</div></div>'
        )

    rows = []
    for module, where in module_map:
        rows.append([module, where])
    modmap = table(["Client capability", "Taught in"], rows)

    return INDEX.format(course=html.escape(COURSE), nav=nav,
                        groups="\n".join(chunks), modmap=modmap)


def main() -> None:
    from content import LABS, GROUPS, MODULE_MAP

    OUT.mkdir(parents=True, exist_ok=True)
    for i, lab in enumerate(LABS):
        prev_lab = LABS[i - 1] if i else None
        next_lab = LABS[i + 1] if i + 1 < len(LABS) else None
        (OUT / f"{lab['slug']}.html").write_text(
            render_lab(lab, prev_lab, next_lab), encoding="utf-8")
        print("wrote", (OUT / f"{lab['slug']}.html").relative_to(ROOT))

    (ROOT / "index.html").write_text(
        render_index(LABS, GROUPS, MODULE_MAP), encoding="utf-8")
    print("wrote index.html")
    print(f"\n{len(LABS)} exercise pages + index generated.")


if __name__ == "__main__":
    main()
