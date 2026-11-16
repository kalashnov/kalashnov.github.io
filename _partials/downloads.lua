-- Posts with `downloads: true` get .qmd and .ipynb buttons, both opening the post's folder on GitHub, where the
-- copies sit next to its data (written into the built site by scripts/post_downloads.py; base URL: `github-files`).
function Pandoc(doc)
  if not doc.meta.downloads or not doc.meta["github-files"] then return nil end
  local folder = pandoc.path.directory(pandoc.path.make_relative(quarto.doc.input_file, quarto.project.directory))
  local url = pandoc.utils.stringify(doc.meta["github-files"]) .. "/" .. folder
  doc.blocks:insert(1, pandoc.RawBlock("html", string.format([[
<p class="post-downloads">Download as:
  <a class="btn btn-sm btn-outline-primary" href="%s">.qmd</a>
  <a class="btn btn-sm btn-outline-primary" href="%s">.ipynb</a>
</p>]], url, url)))
  return doc
end
