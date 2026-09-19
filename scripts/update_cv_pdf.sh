#!/bin/bash
# Refresh the CV published on the site from the LaTeX source folder.
# The CV tab links to files/Emile_Emery_CV.pdf, which must live in the repository
# for GitHub Pages to serve it, so the PDF is copied rather than linked.

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${1:-$BASE_DIR/../CV_en_fr/CV_EN/main.pdf}"
TARGET="$BASE_DIR/files/Emile_Emery_CV.pdf"

if [ ! -f "$SOURCE" ]; then
  echo "Error: CV not found at $SOURCE"
  exit 1
fi

cp "$SOURCE" "$TARGET"
echo "Copied $SOURCE -> $TARGET"
echo "Commit the change to publish it."
