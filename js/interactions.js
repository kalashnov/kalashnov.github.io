// Site-wide: quizzes (_partials/quiz.lua) and Umami custom events for reader interactions.
// Posts need no tracking code: interactions are recognised from the markup Quarto, quarto-live, plotly and
// Observable produce. Events (Umami adds the page URL to each):
//   quiz-<id>         {answer, correct}        a quiz option clicked
//   code-run          {cell, via}              a quarto-live cell run (button or keyboard)
//   code-reset / code-hint / code-solution / code-submit {cell}   the other quarto-live buttons
//   code-grade        {cell, correct}          an exercise graded
//   code-copy         {block}                  a code block copied
//   download          {format}                 a post download button
//   plot-hover / plot-zoom / plot-legend {plot}   plotly charts, the first time per chart and page view
//   plot-explore      {plot}                   an Observable plot pointed at, the first time per page view
//   input             {input, value}           an Observable input changed (sliders: on release)
// Elements are numbered in page order ("cell": 2 is the page's second quarto-live cell).
(() => {
  const track = (name, data) => window.umami?.track(name, data);
  window.track = track;   // for anything a post wants to log itself
  const nth = (el, selector) => [...document.querySelectorAll(selector)].indexOf(el) + 1;
  const done = new WeakMap();   // element -> event names already sent for it
  const once = (el, name, data) => {
    const sent = done.get(el) || new Set();
    if (!sent.has(name)) track(name, data), sent.add(name), done.set(el, sent);
  };

  // quizzes: highlight the choice, say whether it is right, show the explanation, log it
  document.addEventListener("click", (e) => {
    const option = e.target.closest(".quiz-option");
    if (!option) return;
    e.preventDefault();
    const quiz = option.closest(".quiz"), correct = option.dataset.correct === "true";
    for (const o of quiz.querySelectorAll(".quiz-option"))
      o.classList.remove("btn-success", "btn-outline-danger"), o.classList.add("btn-outline-primary");
    option.classList.replace("btn-outline-primary", correct ? "btn-success" : "btn-outline-danger");
    const right = quiz.querySelector('.quiz-option[data-correct="true"]');
    quiz.querySelector(".quiz-verdict").innerHTML =
      correct ? "<b>Right.</b>" : `<b>Not quite:</b> the answer is ${right ? right.dataset.label : "another one"}.`;
    quiz.querySelector(".quiz-answer")?.classList.remove("d-none");
    track(`quiz-${quiz.id || nth(quiz, ".quiz")}`, {answer: option.dataset.label, correct});
  });

  // buttons: quarto-live cells, code copying, downloads
  const CODE_BUTTONS = {"run code": "code-run", "start over": "code-reset", "show hint": "code-hint",
                        "show solution": "code-solution", "submit answer": "code-submit"};
  document.addEventListener("click", (e) => {
    const button = e.target.closest("button, a");
    if (!button) return;
    const editor = button.closest(".exercise-editor");
    const name = CODE_BUTTONS[button.textContent.trim().toLowerCase()];
    if (editor && name) track(name, {cell: nth(editor, ".exercise-editor"), ...(name === "code-run" && {via: "button"})});
    else if (button.matches(".code-copy-button")) track("code-copy", {block: nth(button, ".code-copy-button")});
    else if (button.closest(".post-downloads")) track("download", {format: button.textContent.trim()});
  });
  document.addEventListener("keydown", (e) => {   // quarto-live runs a cell on Ctrl/Cmd/Shift+Enter
    const editor = e.key === "Enter" && (e.ctrlKey || e.metaKey || e.shiftKey) && e.target.closest(".exercise-editor");
    if (editor) track("code-run", {cell: nth(editor, ".exercise-editor"), via: "keyboard"});
  });

  // Observable inputs (sliders report on release, not while dragging)
  document.addEventListener("change", (e) => {
    const form = e.target.closest(".observablehq form");
    if (!form || !e.isTrusted) return;
    const label = form.querySelector("label")?.textContent.trim() || `input ${nth(form, ".observablehq form")}`;
    track("input", {input: label.slice(0, 50), value: String(e.target.value).slice(0, 50)});
  });
  // Observable plots: the first time the reader points at one
  document.addEventListener("pointerover", (e) => {
    const plot = e.target.closest?.('svg[class^="plot"]');
    if (plot) once(plot, "plot-explore", {plot: nth(plot, 'svg[class^="plot"]')});
  });

  // plotly charts (also those re-drawn when a quarto-live cell runs): hook each new chart once
  const hookPlotly = () => {
    for (const gd of document.querySelectorAll(".js-plotly-plot")) {
      if (gd.dataset.tracked || typeof gd.on !== "function") continue;
      gd.dataset.tracked = "1";
      const data = () => ({plot: nth(gd, ".js-plotly-plot")});
      gd.on("plotly_hover", () => once(gd, "plot-hover", data()));
      gd.on("plotly_relayout", (r) => Object.keys(r).some((k) => /range|autorange/.test(k)) && once(gd, "plot-zoom", data()));
      gd.on("plotly_legendclick", () => once(gd, "plot-legend", data()));
    }
  };
  let queued = false;   // at most one scan per frame, however much the page changes
  new MutationObserver(() => queued || (queued = true, requestAnimationFrame(() => (queued = false, hookPlotly()))))
    .observe(document.documentElement, {childList: true, subtree: true});
  // quarto-live exercise grades appear as alerts in the cell's output
  new MutationObserver((records) => {
    for (const r of records) for (const n of r.addedNodes) {
      const grade = n.nodeType === 1 && (n.matches(".exercise-grade") ? n : n.querySelector?.(".exercise-grade"));
      if (!grade) continue;
      // the grade is shown below its cell: the last editor before it on the page
      const editors = [...document.querySelectorAll(".exercise-editor")];
      const cell = editors.filter((ed) => ed.compareDocumentPosition(grade) & Node.DOCUMENT_POSITION_FOLLOWING).length;
      track("code-grade", {cell, correct: grade.classList.contains("alert-success")});
    }
  }).observe(document.documentElement, {childList: true, subtree: true});
})();
