"""Build the CV from cv/cv.yml + data/papers.yml with RenderCV.

Writes cv/kalashnov_cv.pdf (PDF) and cv/_rendercv/cv.md (the web CV, included by cv.qmd).
Sections in cv.yml whose value is a paper status (published | working | wip) are filled from papers.yml,
so the CV and the Research page always agree.

    pip install "rendercv[full]==2.8"
    python scripts/cv_publications.py [path/to/papers.yml]
"""
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML  # ships with rendercv

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cv" / "_rendercv"  # leading underscore: Quarto does not render it as a page
yaml = YAML()


def entry(p):
    names = [a["name"] for a in p.get("coauthors") or []]
    authors = ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else "".join(names)
    summary = ", ".join(filter(None, [p.get("venue") and f"*{p['venue']}*", authors and f"with {authors}"]))
    e = {"name": f"[{p['title']}]({p['url']})" if p.get("url") else p["title"]}
    if summary:
        e["summary"] = summary
    if p.get("year") and p["status"] != "wip":
        e["date"] = int(p["year"])
    return e


def main():
    papers = yaml.load(Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "data" / "papers.yml")) or []
    papers = sorted(papers, key=lambda p: str(p.get("year") or ""), reverse=True)
    cv = yaml.load(ROOT / "cv" / "cv.yml")
    sections = cv["cv"]["sections"]
    for title, value in list(sections.items()):
        if isinstance(value, str):  # a status placeholder
            entries = [entry(p) for p in papers if p.get("status") == value]
            if entries:
                sections[title] = entries
            else:
                del sections[title]
    OUT.mkdir(exist_ok=True)
    yaml.dump(cv, OUT / "cv.yaml")
    # Paths are relative to the input file; custom Markdown templates live in cv/_rendercv/markdown/.
    subprocess.run(
        [sys.executable, "-m", "rendercv", "render", str(OUT / "cv.yaml"),
         "--pdf-path", "../kalashnov_cv.pdf", "--markdown-path", "cv.md", "--typst-path", "cv.typ",
         "--dont-generate-html", "--dont-generate-png"],
        check=True,
    )


if __name__ == "__main__":
    main()
