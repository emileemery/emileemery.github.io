# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal academic website (to be served at `emileemery.github.io`) built from the **Academic Pages** Jekyll template (v0.9.x, itself derived from Minimal Mistakes). It is a template instance, not the upstream theme: never open PRs back to `academicpages/academicpages.github.io` (see `AGENTS.md`). Content (about, CV, talks, teaching, publications) is derived from the CVs in `files/Emile_Emery_CV_EN.pdf` and `files/Emile_Emery_CV_FR.pdf`, copied from `../CV_en_fr/{CV_EN,CV_FR}/main.pdf` by `scripts/update_cv_pdf.sh`; `_inputs/` holds whatever source material the author drops in (never published). Personal data from the CV (phone, birth date, postal address) is deliberately not published.

## Commands

```bash
bundle install                              # Ruby deps (if it fails: rm Gemfile.lock, or `bundle config set --local path 'vendor/bundle'`)
bundle exec jekyll serve -l -H localhost    # dev server on localhost:4000 with livereload
bundle exec jekyll build --strict_front_matter   # what CI runs (JEKYLL_ENV=production); use as the "test"
docker compose up                           # alternative: containerised server on :4000 (uses _config.yml,_config_docker.yml)
npm run build:js                            # re-minify JS into assets/js/main.min.js after editing assets/js/*
bash scripts/update_cv_json.sh              # regenerate _data/cv.json from _pages/cv.md
bash scripts/update_cv_pdf.sh               # re-copy ../CV_en_fr/{CV_EN,CV_FR}/main.pdf to files/ (the sidebar links to both)
cd markdown_generator && python3 publications.py publications.csv   # -> ../_publications/*.md (must run from this dir)
python3 markdown_generator/talks.py markdown_generator/talks.tsv   # -> _talks/*.md (default output dir)
```

Changes to `_config.yml` are not picked up by a running `jekyll serve`; restart it. When a `jekyll serve` is running, do build checks with `-d` pointing outside the repo (e.g. `-d /tmp/site-check`): a production build into `_site/` overwrites the served pages with `https://emileemery.github.io` asset URLs and the local preview loses its CSS/JS.

If `bundle install` fails for lack of `ruby-dev` (no sudo), the headers can be unpacked locally: `apt download ruby3.2-dev`, extract with `dpkg-deb -x` into `~/.local/rubydev/root`, then run bundler with `RUBYOPT=-r~/.local/rubydev/patch_rbconfig.rb` (overrides `rubyhdrdir`/`rubyarchhdrdir`) and `LIBRARY_PATH=~/.local/rubydev/lib` (symlink to `libruby-3.2.so`). Bundler itself is installed with `gem install --user-install bundler` (in `~/.local/share/gem/ruby/3.2.0/bin`). There is no test suite or linter beyond the strict Jekyll build.

## Architecture

- **Site config**: `_config.yml` holds identity (`name`, `url`, `repository`), the sidebar `author:` block (avatar image in `images/`, social/academic profile links), theme choice (`site_theme`), publication categories, and front-matter `defaults` per collection. The header menu order lives in `_data/navigation.yml`.
- **Content collections** (each a folder of Markdown files with YAML front matter, output to `/:collection/:path/`): `_publications`, `_talks`, `_teaching`, `_portfolio`, plus `_posts` (blog) and `_pages` (top-level pages like `about.md` = homepage, `cv.md`, `publications.html`, `talks.html`). Listing pages in `_pages/` iterate over `site.<collection>`; each collection item's layout and flags come from `defaults` in `_config.yml` (talks use `_layouts/talk.html`, everything else `single`).
- **Publications** are grouped on `/publications/` by the front-matter `category` key, which must match a key under `publication_category` in `_config.yml` (`manuscripts`, `submitted`, `preprints`, mirroring the CV sections). Useful fields: `venue`, `date`, `paperurl`, `slidesurl`, `bibtexurl`, `citation`, `excerpt`, plus `codeurl` (added here): `_pages/data.html` lists, grouped by year, every publication whose `codeurl` is set, so a Zenodo deposit is published by filling that one field. PDFs/BibTeX go in `files/` and are served at `/files/<name>`.
- **CV** has two variants: `_pages/cv.md` (hand-written Markdown, linked in the nav) and `_pages/cv-json.md` rendered through `_includes/cv-template.html` from `_data/cv.json`. Only one should be enabled in `_data/navigation.yml`; `cv.json` is generated from `cv.md` by `scripts/`.
- **Talk map**: `talkmap.py`/`talkmap.ipynb` geocode `location:` fields of `_talks/` into `talkmap/`; the `scrape_talks.yml` workflow runs it automatically and commits the result on pushes touching `_talks/`. Shown only if `talkmap_link: true`.
- **Styling/JS**: `_sass/` (themes in `_sass/theme/`, selected via `site_theme`) compiled through `assets/css/main.scss`. JS sources `assets/js/_main.js`, `theme.js`, `plugins/` are excluded from the build; only the minified `assets/js/main.min.js` is served, so it must be rebuilt with npm after JS edits.
- **Sidebar CV links**: `author.cv_en`/`author.cv_fr` in `_config.yml` drive two download links at the top of the sidebar list, added to `_includes/author-profile.html` (one of the few deliberate theme edits, together with the removed theme toggle in `_includes/masthead.html`).
- **Layout customisation hooks**: `_includes/head/custom.html` and `_includes/footer/custom.html` are the intended places for extra `<head>` scripts (e.g. MathJax) or footer content.

## CI notes

`.github/workflows/jekyll-build.yml` is triggered by `workflow_run` of the "Cleanup bad PR" workflow on branch `main`, but this repo's branch is `master`, so it effectively never runs here; GitHub Pages' own build is what deploys the site. `bad-pr.yml` is upstream-template spam handling and irrelevant for this personal site.

## Règles pour ce site

- Site en anglais.
- Ne pas modifier les fichiers du thème (_layouts, _includes, _sass) sauf demande explicite.
- Vérifier que le site compile (bundle exec jekyll build) avant chaque commit.
- Un commit par étape, avec un message clair.
