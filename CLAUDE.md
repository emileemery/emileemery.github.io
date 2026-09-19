# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal academic website (to be served at `emileemery.github.io`) built from the **Academic Pages** Jekyll template (v0.9.x, itself derived from Minimal Mistakes). It is a template instance, not the upstream theme: never open PRs back to `academicpages/academicpages.github.io` (see `AGENTS.md`). Content (about, CV, talks, teaching) is derived from the CVs in `_inputs/`: `main.pdf` (most recent CV, preferred when sources disagree), `cv_en.tex` (upstream: `../CV_en_fr/CV_EN/main.tex`) and `applicationB2.pdf` (CV section of an MSCA application; do not publish anything about the proposal itself). Personal data from the CV (phone, birth date, postal address) is deliberately not published.

## Commands

```bash
bundle install                              # Ruby deps (if it fails: rm Gemfile.lock, or `bundle config set --local path 'vendor/bundle'`)
bundle exec jekyll serve -l -H localhost    # dev server on localhost:4000 with livereload
bundle exec jekyll build --strict_front_matter   # what CI runs (JEKYLL_ENV=production); use as the "test"
docker compose up                           # alternative: containerised server on :4000 (uses _config.yml,_config_docker.yml)
npm run build:js                            # re-minify JS into assets/js/main.min.js after editing assets/js/*
bash scripts/update_cv_json.sh              # regenerate _data/cv.json from _pages/cv.md
cd markdown_generator && python3 publications.py publications.csv   # -> ../_publications/*.md (must run from this dir)
python3 markdown_generator/talks.py markdown_generator/talks.tsv   # -> _talks/*.md (default output dir)
```

Changes to `_config.yml` are not picked up by a running `jekyll serve`; restart it. There is no test suite or linter beyond the strict Jekyll build.

## Architecture

- **Site config**: `_config.yml` holds identity (`name`, `url`, `repository`), the sidebar `author:` block (avatar image in `images/`, social/academic profile links; `github: emileemery` assumes the GitHub username matches the repo name), theme choice (`site_theme`), publication categories, and front-matter `defaults` per collection. The header menu order lives in `_data/navigation.yml`.
- **Content collections** (each a folder of Markdown files with YAML front matter, output to `/:collection/:path/`): `_publications`, `_talks`, `_teaching`, `_portfolio`, plus `_posts` (blog) and `_pages` (top-level pages like `about.md` = homepage, `cv.md`, `publications.html`, `talks.html`). Listing pages in `_pages/` iterate over `site.<collection>`; each collection item's layout and flags come from `defaults` in `_config.yml` (talks use `_layouts/talk.html`, everything else `single`).
- **Publications** are grouped on `/publications/` by the front-matter `category` key, which must match a key under `publication_category` in `_config.yml` (`manuscripts`, `submitted`, `preprints`, mirroring the CV sections). Useful fields: `venue`, `date`, `paperurl`, `slidesurl`, `bibtexurl`, `citation`, `excerpt`. PDFs/BibTeX go in `files/` and are served at `/files/<name>`.
- **CV** has two variants: `_pages/cv.md` (hand-written Markdown, linked in the nav) and `_pages/cv-json.md` rendered through `_includes/cv-template.html` from `_data/cv.json`. Only one should be enabled in `_data/navigation.yml`; `cv.json` is generated from `cv.md` by `scripts/`.
- **Talk map**: `talkmap.py`/`talkmap.ipynb` geocode `location:` fields of `_talks/` into `talkmap/`; the `scrape_talks.yml` workflow runs it automatically and commits the result on pushes touching `_talks/`. Shown only if `talkmap_link: true`.
- **Styling/JS**: `_sass/` (themes in `_sass/theme/`, selected via `site_theme`) compiled through `assets/css/main.scss`. JS sources `assets/js/_main.js`, `theme.js`, `plugins/` are excluded from the build; only the minified `assets/js/main.min.js` is served, so it must be rebuilt with npm after JS edits.
- **Layout customisation hooks**: `_includes/head/custom.html` and `_includes/footer/custom.html` are the intended places for extra `<head>` scripts (e.g. MathJax) or footer content.

## CI notes

`.github/workflows/jekyll-build.yml` is triggered by `workflow_run` of the "Cleanup bad PR" workflow on branch `main`, but this repo's branch is `master`, so it effectively never runs here; GitHub Pages' own build is what deploys the site. `bad-pr.yml` is upstream-template spam handling and irrelevant for this personal site.

## Règles pour ce site

- Site en anglais.
- Ne pas modifier les fichiers du thème (_layouts, _includes, _sass) sauf demande explicite.
- Les publications viennent uniquement de _inputs/publications.bib, ne jamais inventer de référence.
- Tout le matériel source est dans _inputs/, qui ne doit jamais être publié.
- Vérifier que le site compile (bundle exec jekyll build) avant chaque commit.
- Un commit par étape, avec un message clair.
