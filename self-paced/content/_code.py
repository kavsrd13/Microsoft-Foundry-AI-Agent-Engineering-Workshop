"""Pull code out of the tested solution files.

Every code block shown in an exercise comes from `labs/<lab>/solution/<file>`,
which is syntax-checked, import-checked against the real SDKs, and (for the
pure-logic parts) unit-tested. Nothing in the instructions is retyped, so the
page and the working code cannot drift apart.

The solution files are divided by `# --- Task N ---` marker comments.
"""

import re
from pathlib import Path

LABS = Path(__file__).resolve().parents[2] / "labs"

_MARKER = re.compile(r"^# --- (Task \d+|Main)[^\n]*$", re.M)


def load(lab, filename, folder="solution"):
    """The whole solution file, as text.

    `folder` defaults to the lab's solution/ directory. Pass another folder
    (for example "app") when the tested file lives elsewhere in the lab.
    """
    path = LABS / lab / folder / filename
    if not path.is_file():
        raise FileNotFoundError(f"no file at {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _split(text):
    """Break the file into ('header'|'Task 2'|...|'Main') -> body."""
    matches = list(_MARKER.finditer(text))
    if not matches:
        raise ValueError("solution file has no '# --- Task N ---' markers")

    parts = {"header": text[:matches[0].start()].rstrip() + "\n"}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        label = match.group(1)
        parts[label] = text[match.start():end].rstrip() + "\n"
    return parts


def task(lab, filename, number):
    """Just the code a learner adds in this task, without the marker line."""
    body = _split(load(lab, filename))[f"Task {number}"]
    lines = body.split("\n")[1:]          # drop the '# --- Task N ---' line
    return "\n".join(lines).strip("\n")


def header(lab, filename):
    """Imports, constants and the docstring at the top of the file."""
    return _split(load(lab, filename))["header"].strip("\n")


def upto(lab, filename, last_task, main_body):
    """The complete file as it stands once `last_task` is done.

    `main_body` is the indented body of the `if __name__ == "__main__":`
    block at that point in the lab, since it grows as tasks are added.
    """
    parts = _split(load(lab, filename))

    pieces = [parts["header"].strip("\n")]
    for number in range(2, last_task + 1):
        label = f"Task {number}"
        if label in parts:
            pieces.append(parts[label].strip("\n"))

    pieces.append('# --- Main ---------------------------------------------------\n'
                  'if __name__ == "__main__":\n' + main_body.strip("\n"))

    return "\n\n\n".join(pieces) + "\n"


def whole(lab, filename, name=None, lang="python", folder="solution"):
    """A `whole_file` block holding the finished file verbatim."""
    return {"whole_file": load(lab, filename, folder).strip("\n"),
            "name": name or filename, "lang": lang}


def block(code, lang="python"):
    return {"code": code, "lang": lang}
