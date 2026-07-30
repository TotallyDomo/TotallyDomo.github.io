#!/usr/bin/env python3
"""Regenerate static/css/syntax.css from Chroma's built-in styles.

Emits the dark style unscoped (it is the default theme) followed by the light
style scoped to :root[data-theme="light"], so one stylesheet serves both.

    python tools/gen-syntax-css.py
"""

import pathlib
import re
import subprocess
import sys

DARK_STYLE = "github-dark"
LIGHT_STYLE = "github"
LIGHT_SCOPE = ':root[data-theme="light"]'

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "static" / "css" / "syntax.css"

RULE = re.compile(r"^(?:/\*.*?\*/\s*)?(.+?)\s*\{(.*)\}\s*$")


def chromastyles(style):
    result = subprocess.run(
        ["hugo", "gen", "chromastyles", "--style", style],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit("hugo gen chromastyles --style %s failed:\n%s" % (style, result.stderr))
    # Drop the generator comment line; this file writes its own header.
    return result.stdout.split("\n", 1)[1].strip()


def scope(css, prefix):
    lines = []
    for line in css.splitlines():
        match = RULE.match(line)
        if not match:
            continue
        selectors, declarations = match.group(1), match.group(2).strip()
        scoped = ", ".join(prefix + " " + s.strip() for s in selectors.split(","))
        lines.append("%s { %s }" % (scoped, declarations))
    return "\n".join(lines)


def main():
    header = (
        "/*\n"
        "  Chroma syntax colors for both themes. Generated - do not hand-edit.\n"
        "  Dark (default):  hugo gen chromastyles --style=%s\n"
        "  Light override:  hugo gen chromastyles --style=%s, scoped to %s\n"
        "  Regenerate with: python tools/gen-syntax-css.py\n"
        "*/\n\n" % (DARK_STYLE, LIGHT_STYLE, LIGHT_SCOPE)
    )
    body = "/* ---------- dark (default) ---------- */\n" + chromastyles(DARK_STYLE)
    light = "/* ---------- light ---------- */\n" + scope(chromastyles(LIGHT_STYLE), LIGHT_SCOPE)
    OUT.write_text(header + body + "\n\n" + light + "\n", encoding="utf-8", newline="\n")
    print("wrote %s" % OUT.relative_to(REPO))


if __name__ == "__main__":
    main()
