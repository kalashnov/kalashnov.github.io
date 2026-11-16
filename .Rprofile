# Each post with R code has its own renv (posts/<slug>/renv.lock). Quarto starts R in this project folder,
# not in the post's, so activate the renv of the document being rendered (Quarto passes its folder).
local({
  post <- Sys.getenv("QUARTO_DOCUMENT_PATH")
  if (nzchar(post) && file.exists(file.path(post, "renv", "activate.R"))) {
    owd <- setwd(post)
    on.exit(setwd(owd))
    source(file.path("renv", "activate.R"))
  }
})
