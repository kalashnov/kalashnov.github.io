"""Downloadable copies of posts with `downloads: true` (project post-render: runs after every full render).

For posts/<slug>/index.qmd it writes into the built site, next to the post's data files:
  <slug>.qmd    plain R version for RStudio ({webr} cells -> {r}, no quarto-live lines)
  <slug>.ipynb  the same, rendered by Quarto to a Jupyter notebook with outputs (R kernel)
The site is deployed to the gh-pages branch, where the buttons (_partials/downloads.lua) link to them.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = pathlib.Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", ROOT / "_site"))
if not SITE.is_absolute():
    SITE = ROOT / SITE


def plain_qmd(text):
    head, body = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S).groups()
    keep = [l for l in head.splitlines() if re.match(r"(title|date|description|author):", l)]
    body = re.sub(r"^\{\{< include .*>\}\}\n", "", body, flags=re.M).replace("```{webr}", "```{r}")
    return "---\n" + "\n".join(keep) + "\n---\n" + body


def notebook(post, qmd_text, slug):
    # rendered outside the project, with the post's data files; setup cells are shown so the notebook runs
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for f in post.iterdir():
            if f.name != "index.qmd" and f.is_file():
                shutil.copy(f, tmp)  # data, and the post's renv settings (.Rprofile, renv.lock)
        if (post / "renv").is_dir():
            (tmp / "renv").symlink_to(post / "renv")  # the post's own R packages
        (tmp / f"{slug}.qmd").write_text(re.sub(r"^#\| include: false\n", "", qmd_text, flags=re.M))
        env = {k: v for k, v in os.environ.items() if not k.startswith("QUARTO_PROJECT")}
        subprocess.run(["quarto", "render", f"{slug}.qmd", "--to", "ipynb"], cwd=tmp, env=env, check=True)
        nb = json.loads((tmp / f"{slug}.ipynb").read_text())
    # Quarto labels knitr notebooks as Python; they are R
    nb["metadata"]["kernelspec"] = {"name": "ir", "display_name": "R", "language": "R"}
    nb["metadata"]["language_info"] = {"name": "R"}
    return json.dumps(nb, indent=1)


for index in sorted(ROOT.glob("posts/*/index.qmd")):
    text = index.read_text()
    if not re.search(r"^downloads:\s*true\b", text, re.M):
        continue
    slug, out = index.parent.name, SITE / "posts" / index.parent.name
    qmd = plain_qmd(text)
    (out / f"{slug}.qmd").write_text(qmd)
    (out / f"{slug}.ipynb").write_text(notebook(index.parent, qmd, slug))
    print(f"downloads: {out.relative_to(SITE)}/{slug}.qmd, .ipynb")
