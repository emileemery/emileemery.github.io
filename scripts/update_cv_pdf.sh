#!/bin/bash
# Rebuild the CVs published on the site from the LaTeX sources.
#
# The site is public and the source folder is not, so the published PDFs are
# recompiled without the postal address and the phone number of the header;
# everything else is left as written. The sidebar links to
# files/Emile_Emery_CV_EN.pdf and files/Emile_Emery_CV_FR.pdf, which have to
# live in the repository for GitHub Pages to serve them.
#
# Pass a different source folder as the first argument.

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${1:-$BASE_DIR/../CV_en_fr}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

build_cv() {
  local dir="$1" target="$2"
  local source="$SOURCE_DIR/$dir/main.tex"
  if [ ! -f "$source" ]; then
    echo "Error: CV source not found at $source"
    exit 1
  fi
  mkdir -p "$WORK/$dir"
  cp "$SOURCE_DIR/$dir"/*.tex "$WORK/$dir/"
  cp "$SOURCE_DIR"/*.cls "$WORK/$dir/" 2>/dev/null || true

  python3 - "$WORK/$dir/main.tex" <<'PY'
import re
import sys

path = sys.argv[1]
text = open(path, encoding='utf-8').read()

# only the header, above the first section, carries the contact details
cut = text.index('\\section{')
head, body = text[:cut], text[cut:]

phone = re.compile(r'\+\d[\d\s().-]{7,}')
postal = re.compile(r'^\d+\s+\S.*\b\d{5}\b')          # "<number> <street>, <code> <town>"

kept, removed = [], 0
for line in head.split('\n'):
    bare = line.strip().rstrip('\\')
    if bare and (phone.fullmatch(bare) or postal.match(bare)):
        removed += 1
        continue
    kept.append(line)
head = '\n'.join(kept)

# a line ending in \\ right before the end of a block would leave a blank line
head = re.sub(r'\\\\\s*\n(\s*\\end\{minipage\})', r'\n\1', head)

open(path, 'w', encoding='utf-8').write(head + body)
print(f'  redacted {removed} contact line(s)')
PY

  (cd "$WORK/$dir" && for _ in 1 2; do
      pdflatex -interaction=nonstopmode -halt-on-error main.tex > compile.log || {
        echo "Error: pdflatex failed, see $WORK/$dir/compile.log"; tail -20 compile.log; exit 1; }
    done)
  cp "$WORK/$dir/main.pdf" "$BASE_DIR/files/$target"
  echo "Built $BASE_DIR/files/$target from $source"
}

build_cv CV_EN Emile_Emery_CV_EN.pdf
build_cv CV_FR Emile_Emery_CV_FR.pdf
echo "Commit the change to publish it."
