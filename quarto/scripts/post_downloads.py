"""Downloadable copies of posts with `downloads: true` (runs before every full render: project pre-render).

For posts/<slug>/index.qmd it writes, next to the post and its data files:
  <slug>.qmd    plain R version for RStudio ({webr} cells -> {r}, no quarto-live lines)
  <slug>.ipynb  R-kernel notebook
Commit them with the post: the buttons (_partials/downloads.lua) link to them on GitHub.
Standard library only, so it runs anywhere Quarto runs (no Jupyter needed).
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def front_matter(text):
    head, body = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S).groups()
    return head, body


def plain_qmd(head, body):
    keep = [l for l in head.splitlines() if re.match(r"(title|date|description|author):", l)]
    body = re.sub(r"^\{\{< include .*>\}\}\n", "", body, flags=re.M)
    body = body.replace("```{webr}", "```{r}")
    return "---\n" + "\n".join(keep + ["format: html"]) + "\n---\n" + body


def notebook(head, body):
    title = re.search(r'^title:\s*"?(.*?)"?\s*$', head, re.M)
    cells = [{"cell_type": "markdown", "metadata": {}, "source": f"# {title.group(1)}" if title else ""}]
    body = re.sub(r"^\{\{< include .*>\}\}\n", "", body, flags=re.M)
    for i, part in enumerate(re.split(r"^```\{(?:r|webr)\}\n(.*?)^```\s*$", body, flags=re.M | re.S)):
        if i % 2:  # code
            cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                          "source": part.rstrip("\n")})
        elif part.strip():
            cells.append({"cell_type": "markdown", "metadata": {}, "source": part.strip("\n")})
    return json.dumps({"cells": cells, "nbformat": 4, "nbformat_minor": 5, "metadata": {
        "kernelspec": {"name": "ir", "display_name": "R", "language": "R"},
        "language_info": {"name": "R"}}}, indent=1)


for qmd in sorted(ROOT.glob("posts/*/index.qmd")):
    head, body = front_matter(qmd.read_text())
    if not re.search(r"^downloads:\s*true\b", head, re.M):
        continue
    slug, folder = qmd.parent.name, qmd.parent
    (folder / f"{slug}.qmd").write_text(plain_qmd(head, body))
    (folder / f"{slug}.ipynb").write_text(notebook(head, body))
    print(f"downloads: {folder.relative_to(ROOT)}/{slug}.qmd, .ipynb")
