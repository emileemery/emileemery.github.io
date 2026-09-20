#!/bin/bash
# Refresh the CVs published on the site from the LaTeX source folder.
# The sidebar links to files/Emile_Emery_CV_EN.pdf and files/Emile_Emery_CV_FR.pdf,
# which must live in the repository for GitHub Pages to serve them, so the PDFs are
# copied rather than linked. Pass a different source folder as the first argument.

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${1:-$BASE_DIR/../CV_en_fr}"

copy_cv() {
  local source="$SOURCE_DIR/$1/main.pdf"
  local target="$BASE_DIR/files/$2"
  if [ ! -f "$source" ]; then
    echo "Error: CV not found at $source"
    exit 1
  fi
  cp "$source" "$target"
  echo "Copied $source -> $target"
}

copy_cv CV_EN Emile_Emery_CV_EN.pdf
copy_cv CV_FR Emile_Emery_CV_FR.pdf
echo "Commit the change to publish it."
