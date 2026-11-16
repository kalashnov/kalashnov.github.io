-- Multiple-choice quizzes. In a post:
--
--   ::: {.quiz #ask-first answer="Buyer b" title="Quiz: whom do we ask first?"}
--   The question (any markdown, math included).
--
--   - Buyer a
--   - Buyer b
--
--   ::: {.quiz-answer}
--   The explanation, shown once the reader picks an option.
--   :::
--   :::
--
-- The first bullet list becomes the option buttons; `answer` is the text of the right one. The quiz is shown as a
-- callout; js/interactions.js handles the clicks and logs each choice as the Umami event `quiz-<id>`.
function Div(div)
  if not div.classes:includes("quiz") then return nil end
  local answer, blocks, listed = div.attributes.answer, pandoc.Blocks{}, false
  for _, block in ipairs(div.content) do
    if block.t == "BulletList" and not listed then
      listed = true
      local options = pandoc.Inlines{}
      for _, item in ipairs(block.content) do
        local label = pandoc.utils.stringify(item)
        options:insert(pandoc.Link(pandoc.utils.blocks_to_inlines(item), "#", "", pandoc.Attr("",
          {"btn", "btn-sm", "btn-outline-primary", "me-2", "quiz-option"},
          {role = "button", ["data-label"] = label, ["data-correct"] = tostring(label == answer)})))
      end
      options:insert(pandoc.Span({}, pandoc.Attr("", {"quiz-verdict", "ms-2"})))
      blocks:insert(pandoc.Div(pandoc.Plain(options), pandoc.Attr("", {"quiz-options", "my-2"})))
    elseif block.t == "Div" and block.classes:includes("quiz-answer") then
      block.classes:insert("d-none")   -- shown by js/interactions.js
      blocks:insert(block)
    else
      blocks:insert(block)
    end
  end
  local callout = quarto.Callout({type = "note", title = div.attributes.title or "Quiz", icon = false, content = blocks})
  return pandoc.Div(callout, pandoc.Attr(div.identifier, {"quiz"}))
end
