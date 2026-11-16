-- Posts with `downloads: true` get three buttons: git (the post's folder on GitHub; base URL: `github-files`),
-- .ipynb and .qmd (zips of the notebook or the plain .qmd with the data, next to the page).
-- The copies and zips are written into the built site by scripts/post_downloads.py.
function Pandoc(doc)
  if not doc.meta.downloads or not doc.meta["github-files"] then return nil end
  local folder = pandoc.path.directory(pandoc.path.make_relative(quarto.doc.input_file, quarto.project.directory))
  local slug = pandoc.path.filename(folder)
  local url = pandoc.utils.stringify(doc.meta["github-files"]) .. "/" .. folder
  doc.blocks:insert(1, pandoc.RawBlock("html", string.format([[
<p class="post-downloads">Download as:
  <a class="btn btn-sm btn-outline-primary" href="%s">git</a>
  <a class="btn btn-sm btn-outline-primary" href="%s-ipynb.zip" download>.ipynb</a>
  <a class="btn btn-sm btn-outline-primary" href="%s-qmd.zip" download>.qmd</a>
</p>]], url, slug, slug)))
  return doc
end
