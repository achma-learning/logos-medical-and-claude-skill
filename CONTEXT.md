# logos-officiels-maroc — AI Context File
_Last synced: 2026-10-16 @ e5e7fdf_

## 1. What This Is (Plain English)
- **In one sentence:** a Claude skill that keeps 48 cleaned-up official Moroccan logos (kingdom, Ministry of Health, CHU Marrakech, FMPM, WHO…) and hands the one you ask for back as a transparent PNG. It can also print two Marrakech Prefecture admin forms as PDFs.
- **Why it exists:** I keep needing these logos for letterheads, title pages, attestations and forms. Hunting for them online each time and cleaning off white backgrounds is a waste.
- **Who uses it:** me, plus anyone I share the skill or repo with (medical students and residents in Marrakech). Public GitHub repo, MIT licence (`LICENSE`). The logos still belong to their institutions (`README.md`, "Avertissement").
- **Vibe:** a polished personal tool. It's small, but the catalogue has to stay accurate because Claude trusts it blindly.
- **This repo is also the backup** of the skill. The logos live in **one place only: `assets/`**. There's no separate copy folder.

## 2. How To Run It
- **Setup once:** `pip install --break-system-packages reportlab arabic-reshaper python-bidi cairosvg scipy pillow` (`SKILL.md`, "Formulaires"). The forms also need the system fonts Liberation Serif and FreeSerif in `/usr/share/fonts/truetype/{liberation,freefont}/`.
  - Optional, only for adding logos: `vtracer` (vectorising), `opencv-contrib-python-headless` + the `EDSR_x4.pb` model (upscaling, `scripts/agrandir_logo.py:1-20`).
- **Get a logo:** `python3 scripts/donner_logo.py chu --lister`, then `python3 scripts/donner_logo.py <id> --sortie ./out`
- **Print a form:** `python3 scripts/formulaire_cessation_reprise.py out.pdf` / `python3 scripts/formulaire_note_stage.py out.pdf`
- **Build / deploy:** `./build.sh`. It redraws `assets/catalogue.png`, checks that everything lists the same logos, and writes `dist/logos-officiels-maroc.zip`. Upload that zip in Claude → Settings → Capabilities → Skills. For Claude Code, copy the folder to `~/.claude/skills/logos-officiels-maroc/`.
- **Required env vars:** none.

## 3. Tech Stack
- **Language + runtime:** Python 3 scripts plus Bash (`build.sh`). No Python version pinned and no `requirements.txt`.
- **Key libraries:** Pillow (all image work), cairosvg (sharp SVG→PNG when enlarging), reportlab + arabic-reshaper + python-bidi (PDF forms with Arabic), scipy/numpy (background removal), vtracer (tracing). No versions pinned anywhere.
- **What kind of project:** a Claude Agent Skill (`SKILL.md` with YAML frontmatter `name` + `description`), plus an asset library and CLI scripts.
- **External services:** none at runtime. Logo sources when adding new ones: official sites, vector.ma, seeklogo.com, Wikimedia Commons.
- **CI:** none (`.github/` absent).

## 4. Code Map (The Important Files Only)
- `SKILL.md`: **the brain.** Claude reads it, and its rules (RULE 1 hand out a logo, RULE 2 ask before putting one in a document) drive the behaviour. It also holds a catalogue table per category. Watch out: the frontmatter `description` is 976 chars, and claude.ai caps it at 1024.
- `assets/catalogue.json`: **the source of truth** for which logos exist. Each entry has `element` (organisation), `variante`, `id`, `categorie`, `description` and `fichiers[]` (with `px` for the PNG). One element can have several variants.
- `assets/logos/<categorie>/<id>.<png|svg|pdf>`: the logo files. Every entry has a PNG; SVG/PDF exist only when a vector version is available.
- `assets/couleur/`, `assets/nb/`: the 3 form logos (colour, and B&W on white). `assets/nb/` is hard-wired into the form scripts (`scripts/formulaire_cessation_reprise.py:18-20`).
- `assets/catalogue.png`: the labelled preview sheet (5 columns, 240 px tiles), drawn by `scripts/planche_catalogue.py`.
- `scripts/donner_logo.py`: **entry point.** Searches without accents across id/element/variant/category/description. Exit code 2 means several matches (Claude must ask which). It writes `<id>.png`; with `--nb` it writes `<id>-nb.png`.
- `scripts/optimiser_logo.py`, `vectoriser_logo.py`, `agrandir_logo.py`: prepare new logos (strip background + crop, trace to SVG, upscale ×4).
- `scripts/formulaire_cessation_reprise.py`, `formulaire_note_stage.py`: A4 PDF forms. `note_stage` imports helpers via `from formulaire_cessation_reprise import *`.
- `outils/verifier_catalogue.py`: repo-only check (not shipped in the skill). It exits 1 if `assets/` ≠ `catalogue.json` ≠ the `SKILL.md` / `README.md` tables, or if the "bibliothèque de N logos" count is wrong.
- `build.sh`: preview sheet + check + zip. The zip holds only `SKILL.md README.md LICENSE assets/ scripts/`.
- `to-add.md`: wishlist of missing logos, in the format `| [ ] | prio | element | variantes | remarque |`, plus a "Fait" section.

## 5. Rules For Editing This Code
- **Same logos everywhere.** Any logo change has to land in all of these together: the file in `assets/logos/<categorie>/`, the entry in `catalogue.json`, the row in the `SKILL.md` table, the row in the `README.md` table, and the counts in the `SKILL.md` description / `README.md` intro. Then run `./build.sh`; it fails loudly on any mismatch.
- **Analyse the deployed skill too.** The copy installed in Claude (claude.ai Skills) can lag behind this repo. Before claiming a logo is available, compare the installed skill's `SKILL.md` / catalogue with this repo's `assets/`. Example: on 2026-10-16 the installed description still said 45 logos, while the repo has 48.
- File naming: `<id>.<format>`, where `id` = `<element>-<variante-slug>`, all lowercase and accent-free. Paths in `catalogue.json` are relative to the repo root.
- PNGs are RGBA with a transparent background, cropped to the content plus a 1 % margin (`scripts/optimiser_logo.py`).
- Scripts find files relative to their own location (`os.path.dirname(__file__)/..`). Keep that, because the skill runs from wherever Claude unpacks it.
- Arabic in reportlab: always `get_display(arabic_reshaper.reshape(text))`.
- All user-facing text (SKILL.md, script help, docs) is in French. Keep it French.
- Forms must stay faithful to the scanned originals. Only 2 typos were fixed (see `SKILL.md`). Never add a table to the internship grade form unless asked.

## 6. Fragile Bits & Landmines
- **Looks broken, isn't:** `drapeau-maroc` and `drapeau-region-marrakech-safi` are deliberately solid rectangles. `armoiries-maroc-filigrane` is deliberately very pale. `ministere-jeunesse-culture-communication` is white (dark backgrounds only, and the preview sheet draws it on dark grey). `fmpm-uca-encadre` keeps its white rounded box.
- **B&W printing:** plain greyscale makes the gold of the armoiries and the light green of the MS logo vanish (yellow ≈ white). That's why `--nb` uses gamma 1.6 and the `*-nb` MSPS variants exist.
- **`ms-entete-royaume-bleu`** carries the pre-2021 ministry name. Use it only to reproduce old documents.
- **Small PNGs (< 400 px)** are listed in `SKILL.md`. Don't print them wider than ~3 cm.
- **`.gitattributes`:** PNG/JPG/PDF/ZIP are marked `binary`, so `text=auto` can never rewrite line endings inside a PDF.
- **Skip on cleanup passes:** `assets/couleur/` isn't read by any script, but it holds the colour originals of the form logos. Keep it.
- `scripts/agrandir_logo.py` contains a hard-coded `/home/claude/...` model path. It's just a fallback location; leave it.

## 7. Current State
- **Last shipped:** 3 B&W MSPS variants (`ms-embleme-nb`, `msps-logo-vertical-nb`, `msps-logo-horizontal-nb`), bringing the catalogue to 48. Today: added them to the `SKILL.md` tables, redrew `catalogue.png` (it had only 45 tiles), and added `build.sh` (which `SKILL.md` already referenced but didn't exist), `scripts/planche_catalogue.py`, `outils/verifier_catalogue.py`, `.gitignore` and binary rules. Fixed `TO-ADD.md` → `to-add.md` and aligned its format with what `SKILL.md` describes.
- **Working on now:** keeping the repo as a shareable backup of the skill.
- **Next up:** re-upload `dist/logos-officiels-maroc.zip` to Claude so the installed skill has all 48 logos. Fill `to-add.md` with the logos that are still missing.

## 8. Update Protocol (Verbatim)
> **For the AI Assistant:** When asked to "Update CONTEXT.md":
> 1. Re-run Phase 0 — check for new or changed `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `.github/` files, merge what's new, and re-run Phase 3 so each of them still points to `CONTEXT.md`.
> 2. Re-scan the tree, manifests, and `.github/workflows/` for drift.
> 3. Read our recent conversation for new decisions, fragile bits discovered, or shifted goals.
> 4. Refresh the `_Last synced_` line with today's date and current commit SHA.
> 5. Rewrite — do not append. One clean source of truth. Preserve still-true content, revise the rest.
> 6. Keep §1 and §2 in plain English. Keep the file under ~200 lines.
