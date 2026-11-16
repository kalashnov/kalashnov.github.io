-- Posts with `downloads: true` get buttons linking to the post as .qmd and .ipynb on GitHub
-- (copies written into the built site, next to its data, by scripts/post_downloads.py; base URL: `github-files`).
function Pandoc(doc)
  if not doc.meta.downloads or not doc.meta["github-files"] then return nil end
  local folder = pandoc.path.directory(pandoc.path.make_relative(quarto.doc.input_file, quarto.project.directory))
  local base = pandoc.utils.stringify(doc.meta["github-files"]) .. "/" .. folder .. "/" .. pandoc.path.filename(folder)
  doc.blocks:insert(1, pandoc.RawBlock("html", string.format([[
<p class="post-downloads">Run it yourself:
  <a class="btn btn-sm btn-outline-primary" href="%s.qmd">.qmd</a>
  <a class="btn btn-sm btn-outline-primary" href="%s.ipynb">.ipynb</a>
</p>]], base, base)))
  return doc
end
