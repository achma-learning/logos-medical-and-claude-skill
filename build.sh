#!/usr/bin/env bash
# Régénère la planche, vérifie que assets/ = catalogue = SKILL.md = README.md,
# puis empaquette la skill dans dist/logos-officiels-maroc.zip (à importer dans Claude).
set -euo pipefail
cd "$(dirname "$0")"

python3 scripts/planche_catalogue.py
python3 outils/verifier_catalogue.py

NOM=logos-officiels-maroc
rm -rf dist && mkdir -p "dist/$NOM"
# La skill = SKILL.md + assets/ + scripts/ (+ README, LICENSE). outils/, CONTEXT.md, to-add.md : hors skill.
cp -r SKILL.md README.md LICENSE assets scripts "dist/$NOM/"
find "dist/$NOM" -name __pycache__ -type d -prune -exec rm -rf {} +
(cd dist && zip -qr "$NOM.zip" "$NOM")
echo "$(pwd)/dist/$NOM.zip"
