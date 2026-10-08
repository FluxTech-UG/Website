---
max_turns: 150
---

# 01-update-grant-figures

## What and Why

ZIM grant figures have been confirmed by VDI/VDE-IT (April 2026). The website's Ask section has outdated numbers in three places: content.yaml text, the static text blocks, and the JavaScript calculator in sections/ask.html. All need updating to match confirmed figures.

Changes needed:

**content.yaml:**
- `text06`: Change feasibility line from "up to €140k" to "up to €175k". Change ZIM R&D line from "Up to €252k for FluxTech" to "Up to €550k total for FluxTech across two R&D projects" and "up to €280k for a research partner" to "up to €560k total for research partners".
- `text02`: Change "from ~€400k to ~€1M" to "from ~€460k to ~€1.2M"
- `text34`: Change "From ~€400k to ~€1M" to "From ~€460k to ~€1.2M"

**sections/ask.html: JavaScript constants in the `calc()` function:**
- `FEAS_GRANT`: 140 → 175
- `FEAS_COFUND`: 60 → 75
- Change the ZIM R&D grant formula from `coFundAvail * (45 / 55)` to `coFundAvail * (50 / 50)` (i.e., just `coFundAvail`)
- Change the ZIM R&D cap from 252 to 550

## Constraints

- Do not change any HTML structure, CSS, or chart configuration; only text content and JS constants.
- Run `python build.py` after editing content.yaml.
- Run `python build.py --check` to verify no orphaned placeholders.

## Done When

- `python build.py --check` passes with no errors.
- `python build.py` succeeds.
- `grep -c "175" sections/ask.html` finds the updated FEAS_GRANT constant.
- `grep "€140k" content.yaml` returns nothing (old figure gone).
- `grep "€252k" content.yaml` returns nothing (old figure gone).
- Verify with `python -c "print(min(380 * (50/50), 550))"` → 380.0 (sanity check: €500k check yields €380k R&D grant).
- Git commit all changes with message: "Update grant figures to confirmed ZIM 2025 Richtlinie values"

---

# 02-add-fel-logo

## What and Why

FluxTech is based at Future Energy Labs (dena, Berlin) and should display that affiliation alongside the existing MotionLab Berlin logo on the home section. The FEL logo file is currently at the repo root as `FEL-Logo Transparent` (check exact filename with ls). It needs to be moved to `assets/images/` with a kebab-case name, and a new image element added next to the existing MotionLab logo in `sections/home.html`.

The MotionLab logo is `image15` (class `instance-15`) near the bottom of the home section. Add the FEL logo as a new image element immediately before or after `image15`, using the same `instance-15` class so it inherits the same sizing. Update `text37` in content.yaml to mention both: something like "MotionLab Berlin hardtech accelerator graduates. Based at Future Energy Labs (dena, Berlin)."

## Constraints

- Follow asset naming convention: `assets/images/logo-future-energy-labs.png` (or appropriate extension).
- Use `git mv` to move the file, not copy.
- Reuse the existing `instance-15` image class for consistent sizing. If FEL logo looks too large or small at that size, it may need a wrapper with max-height, but try the simple approach first.
- Run `python build.py` after editing content.yaml.
- Test locally with `python -m http.server 8000` and visually verify both logos appear.

## Done When

- `ls assets/images/logo-future-energy-labs.*` finds the moved file.
- The old file is gone from the repo root.
- `grep "future-energy-labs" sections/home.html` finds the new image reference.
- `python build.py` succeeds.
- Visual check: open http://localhost:8000 and confirm both logos display on the home section.
- Git commit all changes with message: "Add Future Energy Labs logo alongside MotionLab"
