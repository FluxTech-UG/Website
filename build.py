#!/usr/bin/env python3
"""
Build script for flux-tech.de.

Reads content.yaml, assembles section partials from sections/, processes
markdown-style formatting, and injects content to produce index.html.

It starts no browser and no process: an icon PNG is drawn by the installed
`shot`, from a page this script writes; an icon is drawn again while its page
(`<png>.html`) is newer than its PNG. While an icon PNG is owed it stops
before index.html, names the rerun and ends its stdout with the jobs block of
`fluxstyle.print_jobs` (read back by `fluxstyle.read_jobs`); a complete build
draws nothing and ends with NO_JOBS_LINE instead.

Usage:
    python3 build.py              # Build index.html (or print the owed icons' shot lines)
    python3 build.py --icons      # Print the shot lines for all nine icons (after a fluxstyle change)
    python3 build.py --html-only  # The same as a plain run (the family's callers name the flag)
    python3 build.py --check      # Dry run: validate YAML keys match template placeholders
                                  # and that no content value holds a FORBIDDEN_PHRASES entry
"""

import argparse
import os
import re
import shutil
import sys

import yaml

import fluxstyle

# Ordered list of section partials that compose the full template.
# To reorder sections or add new ones, edit this list.
SECTION_ORDER = [
    "head",
    "home",
    "problem",
    "solution",
    "prototype",
    "businessmodel",
    "physicsengineering",
    "market",
    "team",
    "status",
    "closing",
]

SECTIONS_DIR = "sections"

# Public copy that is false until the priority patent filing exists (and, in Germany,
# misleading advertising). Matched case-insensitively on whole words in every content
# value; a hit blocks the build and the dry run. Retire a phrase here once it is true.
FORBIDDEN_PHRASES = [
    "patent pending",
    "patented",
    "filed",
    "applied for",
    "with counsel",
]

# Logo SVGs are single-sourced in fluxstyle; build.py copies them into
# assets/images/ so the served files are generated, never hand-maintained.
LOGO_VARIANTS = {
    "full": "logo-fluxtech.svg",
    "icon": "logo-fluxtech-icon.svg",
    "wordmark": "logo-fluxtech-wordmark.svg",
}

# Markers in sections/head.html that build.py fills from fluxstyle before the
# content pass (so they are never seen as content placeholders).
BRAND_TOKENS_MARKER = "/* fluxstyle:brand-tokens */"
FONT_LINK_MARKER = "<!-- fluxstyle:font-link -->"


def inject_brand(template):
    """Fill the fluxstyle markers in the assembled template: the brand-core
    :root tokens (brand_css) and the web-font <link> (font_link_tag). Both come
    from fluxstyle, so the site never re-types a brand hex, gradient, or font.
    Fail loud if a marker is missing: a silently un-injected brand is the exact
    drift consuming fluxstyle is meant to prevent.
    """
    for marker in (BRAND_TOKENS_MARKER, FONT_LINK_MARKER):
        if marker not in template:
            raise ValueError(f"fluxstyle marker missing from sections/head.html: {marker}")
    template = template.replace(BRAND_TOKENS_MARKER, fluxstyle.brand_css().strip())
    template = template.replace(FONT_LINK_MARKER, fluxstyle.font_link_tag())
    return template


def sync_logo_assets():
    """Copy the canonical logo SVGs from fluxstyle into assets/images/."""
    dest_dir = os.path.join("assets", "images")
    for variant, filename in LOGO_VARIANTS.items():
        shutil.copyfile(fluxstyle.logo_path(variant), os.path.join(dest_dir, filename))
    print(f"Synced {len(LOGO_VARIANTS)} logo SVGs from fluxstyle.")


# The disc icons are drawn from fluxstyle (fluxstyle.icon_page: a white glyph on
# a disc that carries the logo's own gradient). build.py writes each icon's page
# beside its PNG (`<name>.png.html`, git-ignored) and prints the shot line that
# draws it; the PNG is made by sending that line. Site file name → fluxstyle glyph.
ICONS = {
    "icon-thermal-capture": "thermal",
    "icon-acoustic-amplification": "acoustic",
    "icon-solid-state-conversion": "conversion",
    "icon-ai-optimization": "ai",
    "icon-seamless-integration": "integration",
    "icon-heat-modulation": "heatmod",
    "icon-economic-compulsion": "economic",
    "icon-commercial-validation": "validation",
    "icon-regulation-mandates": "mandates",
}
ICON_PX = 400

# The last line of a complete build, which has no job to print.
NO_JOBS_LINE = "Nothing to draw: every icon PNG is in place, no shot line to send."


def icon_to_draw(dest):
    """True when the PNG at ``dest`` is owed: it is missing, or its page
    (``<png>.html``) has a later modification time than it. shot writes the PNG
    after reading the page, so a drawn PNG is never older than its page. The
    test reads file times only: a PNG whose time moved without a draw (a git
    checkout, a `touch`) reads as drawn; `--icons` draws all nine again."""
    if not os.path.isfile(dest):
        return True
    page = f"{dest}.html"
    return os.path.isfile(page) and os.path.getmtime(page) > os.path.getmtime(dest)


def icon_jobs(force=False):
    """The fluxstyle.ShotJob of every disc icon to draw into assets/images/: with
    ``force`` (`--icons`, after a fluxstyle change) all nine, else each icon whose
    PNG is missing or older than its page (an icon is drawn again while its page
    is newer than its PNG). Writes each job's page beside its PNG and draws
    nothing; fluxstyle refuses a path holding a shell character with ValueError
    before the page is written."""
    dest_dir = os.path.join("assets", "images")
    jobs = []
    for filename, glyph in ICONS.items():
        dest = os.path.join(dest_dir, f"{filename}.png")
        if force or icon_to_draw(dest):
            jobs.append(fluxstyle.icon_page(glyph, dest, size=ICON_PX))
    print(f"Icons: {len(jobs)} to draw with shot, {len(ICONS) - len(jobs)} kept.")
    return jobs


def load_content(path="content.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_template():
    """Assemble the full template by concatenating section partials in order."""
    parts = []
    for name in SECTION_ORDER:
        path = os.path.join(SECTIONS_DIR, f"{name}.html")
        with open(path, "r") as f:
            parts.append(f.read())
    return "".join(parts)


def markdown_to_html(text):
    """Convert markdown-style inline formatting to HTML."""
    # Bold: **text** → <strong>text</strong>  (must run before italic)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text* → <em>text</em>  (single asterisks; bold already consumed)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Highlight: ==text== → <mark>text</mark>
    text = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text)
    # Links: [text](url) → <a href="url">text</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def escape_html_entities(text):
    """Escape bare & characters that aren't already part of HTML entities or tags."""
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', text)
    return text


def process_value(value):
    """Process a YAML value into HTML content for injection into the template."""
    value = str(value).strip()

    # Escape HTML entities before markdown conversion
    value = escape_html_entities(value)

    # Apply markdown conversion
    value = markdown_to_html(value)

    # Split into paragraphs on double newlines
    paragraphs = re.split(r'\n\n', value)

    if len(paragraphs) == 1:
        # Single paragraph: return as-is (no span wrapper needed;
        # the template element may or may not use spans)
        return paragraphs[0]

    # Multiple paragraphs: wrap each in <span class="p">
    spans = []
    for p in paragraphs:
        p = p.strip()
        if p:
            spans.append(f'<span class="p">{p}</span>')
    return ''.join(spans)


def forbidden_phrase_hits(content):
    """(key, phrase) for every content value holding a FORBIDDEN_PHRASES entry."""
    hits = []
    for key, value in content.items():
        text = str(value)
        for phrase in FORBIDDEN_PHRASES:
            if re.search(r"\b" + re.escape(phrase) + r"\b", text, re.IGNORECASE):
                hits.append((key, phrase))
    return hits


def find_template_placeholders(template):
    """Return all {{key}} placeholders found in template."""
    return set(re.findall(r'\{\{([^}]+)\}\}', template))


def build(check_only=False, icons=False):
    content = load_content()
    template = inject_brand(load_template())

    placeholders = find_template_placeholders(template)
    yaml_keys = set(content.keys())

    # Validate
    missing_in_template = yaml_keys - placeholders
    orphaned_in_template = placeholders - yaml_keys

    errors = False

    if missing_in_template:
        print(f"WARNING: YAML keys with no matching placeholder in template: {sorted(missing_in_template)}")
        errors = True

    if orphaned_in_template:
        print(f"ERROR: Template placeholders with no matching YAML key: {sorted(orphaned_in_template)}")
        print("Build blocked: these would appear as literal {{key}} text on the site.")
        sys.exit(1)

    forbidden = forbidden_phrase_hits(content)
    if forbidden:
        for key, phrase in forbidden:
            print(f"ERROR: {key}: contains \"{phrase}\", which is false until the patent is filed.")
        print("Build blocked: remove the phrase or retire it from FORBIDDEN_PHRASES in build.py.")
        sys.exit(1)

    if not missing_in_template:
        print(f"OK: {len(yaml_keys)} YAML keys match {len(placeholders)} template placeholders; "
              f"no forbidden phrase in the copy.")

    if check_only:
        sys.exit(0)

    sync_logo_assets()
    jobs = icon_jobs(force=icons)
    if jobs:
        print(f"Stopped before index.html: {len(jobs)} icon PNGs are to be drawn. Send each "
              "shot line below as its own command, then rerun `python3 build.py`.")
        fluxstyle.print_jobs(jobs)
        return

    # Build
    output = template
    for key, value in content.items():
        processed = process_value(value)
        placeholder = '{{' + key + '}}'
        if placeholder in output:
            output = output.replace(placeholder, processed)

    with open("index.html", "w") as f:
        f.write(output)

    print("Built index.html successfully.")
    print(NO_JOBS_LINE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build index.html for flux-tech.de.",
                                     allow_abbrev=False)
    parser.add_argument("--check", action="store_true",
                        help="dry run: validate the keys and the forbidden phrases")
    parser.add_argument("--icons", action="store_true",
                        help="print the shot lines for all nine icons, not only the owed")
    parser.add_argument("--html-only", action="store_true",
                        help="accepted for the family's callers; every run is HTML only")
    args = parser.parse_args()
    build(check_only=args.check, icons=args.icons)
