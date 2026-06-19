# FluxTech Website — flux-tech.de

Single-page marketing site for FluxTech, hosted on GitHub Pages. It was originally
exported from Carrd; that machine-generated substrate (the `.instance-N` classes and the
`display:none` slide-switcher state machine) has since been **retired**. The site is now a
hand-authored **continuous-scroll** page maintained via a content pipeline.

<!-- fluxtech-meta:cross-repo-access BEGIN (generated — run `make sync` in fluxtech-meta) -->

## Cross-Repo Access

These repos are interconnected — packages (`co2-eos`, `fluxstyle`), the consumers
built on them, and `Physics Spec` as the shared physics source of truth (the family
`CLAUDE.md` at the repo-family root has the full map). When a task here consumes
from or feeds another repo, **reading that repo's files directly is natural and
encouraged** — work from the real source, not a remembered or copied version.
**Editing a file outside this repo is forbidden without explicit permission for that
change.** Read freely across the family; write only here.

<!-- fluxtech-meta:cross-repo-access END -->

<!-- fluxtech-meta:consuming-packages BEGIN (generated — run `make sync` in fluxtech-meta) -->

## Consuming Packages

This repo consumes shared packages; it does not vendor or re-type their contents.
Import the package's published surface — or its generated artifact, e.g. the physics
spec's `reference_operating_point.json` — rather than copying numbers, hexes, or
formulas into this repo, where they would drift from canonical. When you need a
package's value or behavior, read the package's own source as the authority. A need
that seems to require editing a package is lifted into the package, not patched here.

<!-- fluxtech-meta:consuming-packages END -->

<!-- fluxtech-meta:consuming-packages LOCAL (repo-specific; hand-authored; kept across syncs) -->
**In this repo.** `build.py` pulls the brand surface from `fluxstyle` at build
time: the brand-core `:root` tokens (`fluxstyle.brand_css()`, injected at the
`/* fluxstyle:brand-tokens */` marker in `sections/head.html`), the web-font
`<link>` (`fluxstyle.font_link_tag()`, at the `<!-- fluxstyle:font-link -->`
marker), and the three logo SVGs (`fluxstyle.logo_path()` → `assets/images/`).
Don't hand-edit any of those — change the brand in `fluxstyle` and rebuild. Only
site-layout tokens (`--maxw`, `--header-h`, `--radius`, `--shadow`, `--measure`)
stay local. Build needs fluxstyle installed: `pip install -e ../../fluxstyle`.
<!-- fluxtech-meta:consuming-packages LOCAL END -->

<!-- fluxtech-meta:fail-fast BEGIN (generated — run `make sync` in fluxtech-meta) -->

## Fail Fast

No silent defaults; no caught exceptions that substitute a fallback value. A missing
config field, an unphysical state, a failed inversion, a conservation or consistency
violation beyond tolerance — raise immediately, with context. When a real value
should exist, never paper over its absence with a default.

<!-- fluxtech-meta:fail-fast END -->

<!-- fluxtech-meta:living-documents BEGIN (generated — run `make sync` in fluxtech-meta) -->

## Living Documents — No Archaeology

Every file states only the current state. When an approach changes, rewrite the
affected passage with the new result and delete what it replaced — git holds the
history. This holds for instructions and framing as much as for outputs: say what
the architecture *is*, not what it replaced. Never leave negative framing ("unlike
the previous approach", "no longer …"): a retired claim left in the text plants a
competing attractor a later reader may draw from. The one exception is a prior
approach that is the model's likely default from training — a standard pattern it
would reach for unprompted; there, an explicit override is worth stating.

<!-- fluxtech-meta:living-documents END -->

<!-- fluxtech-meta:no-redundant-cd BEGIN (generated — run `make sync` in fluxtech-meta) -->

## No Redundant cd

Commands run from the repo root; you are already there. Run them directly
(`python scripts/run.py`), never `cd /path && …`. A leading `cd` into the repo you
are already in is noise and can trip the permission prompt.

<!-- fluxtech-meta:no-redundant-cd END -->

<!-- fluxtech-meta:collaboration BEGIN (generated — run `make sync` in fluxtech-meta) -->

## Collaboration Workflow

Branches and pull requests are for review by a collaborator, not a solo ritual. Working alone in a repo, commit and push to `main` directly — do not open a PR to yourself; reserve a feature branch and PR for changes that need another person's review. Pull `main` before starting so you are not on a stale base, never force-push a shared branch, and push before ending the session so work is never stranded locally.

<!-- fluxtech-meta:collaboration END -->

## Architecture

```
flux-tech.de/
├── CLAUDE.md              # You are here
├── content.yaml           # Source of truth for all site text
├── build.py               # Assembles sections → injects YAML content → writes index.html
├── sections/              # Hand-authored HTML partials
│   ├── head.html          # <head> + inline CSS (the whole stylesheet) + opening <body>,
│   │                      #   SVG defs, skip link, scroll-progress bar, sticky header nav,
│   │                      #   side dot-nav, and the opening <main> tag
│   ├── home.html          # #home  — hero (logo, tagline, pitch-video button, partners)
│   ├── problem.html       # #problem (incl. IEA chart figure)
│   ├── solution.html      # #solution
│   ├── businessmodel.html # #businessmodel (3-card grid)
│   ├── physicsengineering.html # #physicsengineering — numbered walkthrough of 6 steps
│   ├── market.html        # #market (3-card grid with icons)
│   ├── team.html          # #team (member cards)
│   ├── ask.html           # #ask — Chart.js grant-leverage widget (self-contained) + CTA
│   └── closing.html       # Closes </main>, site footer + credits, back-to-top, pitch-video
│                          #   lightbox, and ALL the page JS (scroll-spy, reveal, nav, etc.)
├── index.html             # Built output — served by GitHub Pages. NEVER edit directly
└── assets/
    └── images/            # Logo, headshots, IEA chart, partner logos, icons, diagrams
```

## Content Pipeline

`content.yaml` is the single source of truth for all visible text. To change site copy:

1. Edit `content.yaml`
2. Run `python build.py`
3. Commit and push — GitHub Pages serves the updated `index.html`

`sections/*.html` are HTML partials with text replaced by `{{key}}` placeholders. They
contain all CSS, JS, layout, and image references. `build.py` concatenates them in a defined
order (`SECTION_ORDER` list in `build.py`) to form the full template, then performs
placeholder replacement from `content.yaml`.

- To edit a section's structure or styling, edit `sections/<name>.html` (markup) and the
  inline `<style>` in `sections/head.html` (CSS).
- To edit text content, edit `content.yaml`.
- CDN script tags can be added to any section partial or to `sections/head.html`.
- Section order — which is also the on-page scroll order — is the `SECTION_ORDER` list in
  `build.py`.

`index.html` is a build artifact. Every line is generated by `build.py`. Manual edits will be
overwritten on next build.

## YAML Content Format

Content uses markdown-style inline formatting, converted to HTML by `build.py`:

| Markdown | HTML output |
|---|---|
| `**bold text**` | `<strong>bold text</strong>` |
| `*italic text*` | `<em>italic text</em>` |
| `==highlighted text==` | `<mark>highlighted text</mark>` |
| `[link text](url)` | `<a href="url">link text</a>` |
| `[link text](mailto:x)` | `<a href="mailto:x">link text</a>` |

Raw HTML (e.g., `<br />`, `<sub>`, `<sup>`) is allowed in YAML values when no markdown
equivalent exists. The build script passes these through unchanged.

Paragraphs within a single YAML value are separated by `\n\n`. The build script wraps each
paragraph in `<span class="p">...</span>`. These `.p` spans are styled by the stylesheet as
block-level paragraphs (the old Carrd hard dependency is gone, but the wrapper is retained so
multi-paragraph values get consistent spacing — including inside `.card` / `.feature-list`).

## HTML Structure & Navigation

The page is **one continuous scroll**. There is no slide-switcher, no landing menu, and no
per-section "Back" links. Each `sections/*.html` partial emits one
`<section id="…" class="section" tabindex="-1">`. Section `id`s (`home`, `problem`,
`solution`, `businessmodel`, `physicsengineering`, `market`, `team`, `ask`) double as the
in-page anchor targets used by the navigation and the `[here](#…)` cross-links in copy.

The navigation system (all CSS in `head.html`, all JS in `closing.html`):

- **Sticky top header** with the FluxTech brand + seven section links. On mobile it collapses
  to a horizontally scrollable chip row (labels stay visible — no hamburger).
- **Scroll-spy** via one `IntersectionObserver` (`rootMargin: -45% 0 -45%`). The active
  section's links in the top nav and dot-nav get both `.active` and `aria-current="true"`.
- **Scroll progress bar** — native CSS `animation-timeline: scroll()` where supported, with a
  small JS `scaleX` fallback otherwise.
- **Side dot-nav** — fixed vertical column, one labelled `<a>` dot per section, desktop only
  (hidden below 1180px). Driven by the same observer.
- **Smooth scroll + focus management** — a delegated click handler on `a[href^="#"]` scrolls
  the target into view (respecting `prefers-reduced-motion`) and moves keyboard focus to the
  target section (`tabindex="-1"` + `focus({preventScroll:true})`). `scroll-margin-top` on
  every section keeps anchored tops clear of the sticky header.
- **"Next" affordance** at the foot of each section advances to the next one in scroll order.
- **Back-to-top** button, revealed once the hero scrolls out of view.

`text*` IDs are legacy Carrd numbering (`text15`, `text26`, …); business-model/contract keys
use semantic IDs (`text-bm-customer`, `text-heatmod`, …). YAML keys match these element IDs.

## Reveal-on-scroll & motion

Motion is expressive but reduced-motion-safe. Base styles are fully visible with stable final
states; the hidden initial state for `.reveal` elements is declared **only** inside
`@media (prefers-reduced-motion: no-preference)` and scoped to `html.js`, so reduced-motion
**and** no-JS users always get a fully visible, non-animated page (no flash of hidden content).
Reveals fire once via `IntersectionObserver` (then unobserve) and animate only
`opacity`/`transform`. The `<html>` element gets a `.js` class from a tiny inline script in
`head.html` before first paint.

## Build Script Behavior

`build.py` assembles the full template by concatenating `sections/*.html` partials in
`SECTION_ORDER`, processes markdown formatting (bold → italic → highlight → links, in that
order), wraps `\n\n`-separated paragraphs in `<span class="p">` tags, and replaces
`{{element_id}}` tokens to produce `index.html`. It validates that every YAML key has a
matching placeholder (and errors on orphaned placeholders).

## Commands

```bash
python build.py              # Build index.html from sections + content
python build.py --check      # Dry run: validate YAML keys match template placeholders
```

## Conventions

- Fonts: Poppins (headings, gradient text, nav, numbers) and Source Code Pro (body).
- Brand palette and type tokens come from `fluxstyle` (`brand/tokens.css`), injected into
  `head.html`'s `<style>` at build time as the brand `:root` — never hand-typed here. The
  teal-to-green gradient, ink, highlight, and the Poppins/Source Code Pro stacks all live
  there; this repo adds only site-layout tokens and the `var(--c-*)` references that use them.
- Section headings (`.h-section`) and the hero tagline use Poppins with a `background-clip:text`
  gradient fill. Body text (`.prose`) uses Source Code Pro.
- All images live in `assets/images/` with descriptive kebab-case names. Every `<img>` carries
  explicit `width`/`height` (intrinsic pixels) so reveals and late media don't cause layout
  shift (CLS).
- **Logo** — three transparent SVGs single-sourced in `fluxstyle` and copied into
  `assets/images/` by `build.py` (`fluxstyle.logo_path()`); derived from one master lockup
  (gradient icon over wordmark):
  - `logo-fluxtech.svg` — full stacked lockup → **hero**.
  - `logo-fluxtech-icon.svg` — gradient icon only → **header** mark, **Ask** mark, **favicon**.
  - `logo-fluxtech-wordmark.svg` — "FluxTech." as outlined black (`#1a1d21`) paths, Poppins
    SemiBold, no font dependency → **header** wordmark.

  The header brand is the icon + wordmark composed side by side via the `.brand` flex row (each
  sized independently: `.brand__icon`, `.brand__word`). The wordmark is intentionally **black**,
  not the page's teal-green gradient. All three share one coordinate space (`userSpaceOnUse`
  gradient), so if the mark changes, re-crop the variants from the master with their bounding
  boxes rather than editing each by hand.
- The YouTube pitch-video embed (id `7AhBzJ9Yg6M`) lives in the lightbox JS in
  `sections/closing.html`; it is launched from the hero's "Watch the pitch" button
  (`[data-open-video]`).

## What to Preserve

- The `content.yaml` → `build.py` → `index.html` pipeline (YAML source of truth, `{{key}}`
  placeholder injection, `SECTION_ORDER`, key-validation). Keep markdown conversion and the
  `.p` paragraph wrapping working.
- The **Ask** Chart.js grant-leverage widget in `sections/ask.html` — its `<style>`, markup,
  and `<script>` are self-contained; keep them intact and the `Chart.js` CDN tag above it.
- The seven content sections + hero, all copy, the IEA chart, headshots, partner logos, icons,
  the heat-modulation diagram, and external links.
- The navigation system and reveal/motion behaviour described above. If you add a section,
  update `SECTION_ORDER`, add the matching links to the top nav **and** the dot-nav in
  `head.html`, and add it to the `SECTION_IDS` array in the `closing.html` scroll-spy JS.
- The brand identity: Poppins gradient headings, Source Code Pro body, the palette above.
