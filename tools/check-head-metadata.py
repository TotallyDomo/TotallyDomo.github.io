#!/usr/bin/env python3
"""Build fixture content and verify the site's social metadata contract."""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser


REPO = pathlib.Path(__file__).resolve().parent.parent
BASE_URL = "https://totallydomo.github.io/"
DEFAULT_DESCRIPTION = (
    "A personal tech blog about AI skills, gamedev, and whatever I'm building."
)
VIBEMAX_DESCRIPTION = (
    "I built a low-narration response style to cut my agent's output-token bill. "
    "The measured answer: that lever barely exists. What it buys instead is reading time."
)
DEFAULT_IMAGE = BASE_URL + "img/gnome.png"
VIBEMAX_IMAGE = (
    BASE_URL
    + "img/posts/vibemax-output-style-wont-save-you-money/"
    + "session-cost-composition.png"
)


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name")
            if key:
                self.values[key] = values.get("content", "")
        elif tag == "link" and values.get("rel") == "canonical":
            self.values["canonical"] = values.get("href", "")


def parse_head(path):
    parser = HeadParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.values


def require(page, key, expected, failures):
    actual = page.get(key)
    if actual != expected:
        failures.append("%s: expected %r, got %r" % (key, expected, actual))


def main():
    scratch_root = REPO / "Temp"
    scratch_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="head-metadata-", dir=scratch_root) as temp:
        temp_path = pathlib.Path(temp)
        fixture_content = temp_path / "content"
        output = temp_path / "public"
        shutil.copytree(REPO / "content", fixture_content)

        malformed = fixture_content / "posts" / "malformed-metadata.md"
        malformed.write_text(
            "---\n"
            'title: "Malformed metadata fixture"\n'
            "date: 2026-08-17\n"
            "description: 42\n"
            "image: 42\n"
            "draft: false\n"
            "---\n\n"
            "Temporary hardening fixture.\n",
            encoding="utf-8",
            newline="\n",
        )

        env = dict(os.environ)
        env["HUGO_ENVIRONMENT"] = "production"
        result = subprocess.run(
            [
                "hugo",
                "--minify",
                "--contentDir",
                str(fixture_content),
                "--destination",
                str(output),
            ],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            sys.exit("Hugo fixture build failed:\n%s" % (result.stderr or result.stdout))

        home = parse_head(output / "index.html")
        vibemax = parse_head(
            output / "posts" / "vibemax-output-style-wont-save-you-money" / "index.html"
        )
        malformed_page = parse_head(
            output / "posts" / "malformed-metadata" / "index.html"
        )

        failures = []
        require(home, "description", DEFAULT_DESCRIPTION, failures)
        require(home, "og:title", "TotallyDomo", failures)
        require(home, "og:type", "website", failures)
        require(home, "og:url", BASE_URL, failures)
        require(home, "og:description", DEFAULT_DESCRIPTION, failures)
        require(home, "og:image", DEFAULT_IMAGE, failures)
        require(home, "twitter:card", "summary_large_image", failures)
        require(home, "canonical", BASE_URL, failures)

        vibemax_url = BASE_URL + "posts/vibemax-output-style-wont-save-you-money/"
        require(vibemax, "description", VIBEMAX_DESCRIPTION, failures)
        require(
            vibemax,
            "og:title",
            "Vibemax - Your Agent's Output Style Won't Save You Money - TotallyDomo",
            failures,
        )
        require(vibemax, "og:type", "article", failures)
        require(vibemax, "og:url", vibemax_url, failures)
        require(vibemax, "og:description", VIBEMAX_DESCRIPTION, failures)
        require(vibemax, "og:image", VIBEMAX_IMAGE, failures)
        require(vibemax, "twitter:card", "summary_large_image", failures)
        require(vibemax, "canonical", vibemax_url, failures)

        malformed_url = BASE_URL + "posts/malformed-metadata/"
        require(malformed_page, "description", "Temporary hardening fixture.", failures)
        require(malformed_page, "og:description", "Temporary hardening fixture.", failures)
        require(malformed_page, "og:image", DEFAULT_IMAGE, failures)
        require(malformed_page, "og:url", malformed_url, failures)

        if failures:
            sys.exit("Head metadata check failed:\n- " + "\n- ".join(failures))

    print("Head metadata check passed: homepage, vibemax post, malformed fallbacks")


if __name__ == "__main__":
    main()
