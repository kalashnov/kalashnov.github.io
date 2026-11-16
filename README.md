# kalashnov.github.io

Personal website, built with [Quarto](https://quarto.org) and deployed to GitHub Pages by
[`.github/workflows/publish.yml`](.github/workflows/publish.yml) on every push to `master`, weekly, and on demand.
The repository holds only sources: everything generated (papers, previews, CV, post outputs, downloads) is built
during the deploy and published on the `gh-pages` branch.

## What to edit

| To change | Edit |
|---|---|
| Papers (title, authors, abstract, venue, summary, picture, links, tags `selected` / `forthcoming` / `field: …`) | Zotero "My Publications" (summary = the Extra field); picked up by the next deploy |
| Co-author homepages, order of fields on the Research page | `data/coauthors.yml`, `data/fields.yml` (a new field also needs a section in `publications.qmd`) |
| About page | `index.qmd`, `images/prof_pic.jpg` |
| CV (publications are filled in from Zotero) | `cv/cv.yml` |
| Posts and tutorials | `posts/<date>-<slug>/index.qmd` |
| Menu, colours, fonts, analytics | `_quarto.yml`, `theme/`, `_partials/head.html` |

## Posts with R code

Each post with R code has its own [renv](https://rstudio.github.io/renv/) in its folder (`renv.lock`; packages used in
quarto-live `{webr}` cells are listed in its `DESCRIPTION`). `.Rprofile` activates the renv of the post being rendered.
Interactive posts use [quarto-live](https://r-wasm.github.io/quarto-live/): `format: live-html`, `{webr}` cells, and the
two includes at the top of the body (see the OHIE tutorial). `downloads: true` adds buttons: git (the post folder on GitHub) and `.ipynb`/`.qmd` zips with the data.

## Quizzes and analytics

A multiple-choice quiz in any post (rendered as a callout by `_partials/quiz.lua`):

```markdown
::: {.quiz #ask-first answer="Buyer b" title="Quiz: whom do we ask first?"}
The question.

- Buyer a
- Buyer b

::: {.quiz-answer}
The explanation, shown once the reader picks an option.
:::
:::
```

Analytics: [Umami Cloud](https://cloud.umami.is), cookieless; the website ID is in `_partials/head.html`. Besides page
views, `js/interactions.js` logs custom events without any code in the posts: each quiz's answers (`quiz-<id>`),
quarto-live code cells (runs, hints, solutions, grades), copied code, downloads, plotly and Observable plots, and
Observable inputs such as sliders. The full list is at the top of that file.

## Working locally

```sh
scripts/get_quarto_live.sh                                  # quarto-live extension (pinned)
git fetch origin gh-pages                                   # data built by the last deploy
git show FETCH_HEAD:data/papers.yml > data/papers.yml       # (or: ZOTERO_API_KEY=... python scripts/zotero_sync.py)
git archive FETCH_HEAD images/previews | tar -x
(cd posts/<post> && Rscript -e 'renv::restore()')           # once per post with R code
python scripts/cv_publications.py                           # optional: the CV (pip install "rendercv[full]==2.8")
quarto preview
```
