#!/usr/bin/env python3
"""
Build script for flux-tech.de.

Reads content.yaml, assembles section partials from sections/, processes
markdown-style formatting, and injects content to produce index.html.

Usage:
    python build.py            # Build index.html
    python build.py --check    # Dry run: validate YAML keys match template placeholders
"""

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
    "ask",
    "closing",
]

SECTIONS_DIR = "sections"

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
    Fail loud if a marker is missing — a silently un-injected brand is the exact
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
        # Single paragraph — return as-is (no span wrapper needed;
        # the template element may or may not use spans)
        return paragraphs[0]

    # Multiple paragraphs — wrap each in <span class="p">
    spans = []
    for p in paragraphs:
        p = p.strip()
        if p:
            spans.append(f'<span class="p">{p}</span>')
    return ''.join(spans)


def find_template_placeholders(template):
    """Return all {{key}} placeholders found in template."""
    return set(re.findall(r'\{\{([^}]+)\}\}', template))


def build(check_only=False):
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
        print("Build blocked — these would appear as literal {{key}} text on the site.")
        sys.exit(1)

    if not missing_in_template:
        print(f"OK: {len(yaml_keys)} YAML keys match {len(placeholders)} template placeholders.")

    if check_only:
        sys.exit(0)

    sync_logo_assets()

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


if __name__ == "__main__":
    check_only = "--check" in sys.argv
    build(check_only=check_only)
