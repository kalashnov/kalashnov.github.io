// Site-wide: quizzes (_partials/quiz.lua) and Umami custom events for reader interactions.
// Posts need no tracking code: interactions are recognised from the markup Quarto, quarto-live, plotly and
// Observable produce. Events (Umami adds the page URL to each):
//   quiz-<id>         {answer, correct, attempt}   a quiz option clicked; attempt = 1, 2, ... within this page view
//                     (kept in memory only, nothing stored in the browser: filter attempt = 1 for first answers)
//   code-run          {cell, via}              a quarto-live cell run (button or keyboard)
//   code-reset / code-hint / code-solution / code-submit {cell}   the other quarto-live buttons
//   code-grade        {cell, correct}          an exercise graded
//   code-copy         {block}                  a code block copied
//   download          {format}                 a post download button
//   plot-hover / plot-zoom / plot-legend {plot}   plotly charts, the first time per chart and page view
//   plot-explore      {plot}                   an Observable plot pointed at, the first time per page view
//   input             {input, value}           an Observable input changed (sliders: on release)
//   runtime-ready     {engine, total, page, runtime, packages, data, setup, network}   quarto-live became ready to
//                     run code: seconds since the page opened; page = before quarto-live started; then per startup
//                     stage (download of webR/Pyodide, installing the packages, data files, setup); network type
//   runtime-abandoned {engine, stage, total, network}   the reader left before it was ready
//   runtime-error     {engine, message}        startup failed
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
  const attempts = new Map();   // quiz -> answers so far in this page view
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
    attempts.set(quiz, (attempts.get(quiz) || 0) + 1);
    track(`quiz-${quiz.id || nth(quiz, ".quiz")}`, {answer: option.dataset.label, correct, attempt: attempts.get(quiz)});
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
  // quarto-live startup, timed from its own status line (#exercise-loading-status), which reads "Downloading webR",
  // "Downloading package: X", "Downloading resource: Y", ... and disappears once code can run
  const STAGES = [[/^Downloading (webR|Pyodide)/, "runtime"], [/^Downloading package/, "packages"],
                  [/^Downloading resource/, "data"], [/^(Initialise|Installing webR shims|.* environment setup)$/, "setup"]];
  const startup = {engine: null, stage: null, since: 0, start: null, times: {}, done: false};
  const secs = (ms) => Math.round(ms / 100) / 10;
  const network = () => navigator.connection?.effectiveType || "unknown";   // Chromium only
  const lap = (now) => startup.stage && (startup.times[startup.stage] = (startup.times[startup.stage] || 0) + now - startup.since);
  const finish = (name, data) => {
    if (startup.done || !startup.engine) return;
    startup.done = true;
    track(name, {engine: startup.engine, ...data});
  };
  const watchStartup = () => {
    const status = document.getElementById("exercise-loading-status");
    if (!status) return;   // no quarto-live cells on this page
    new MutationObserver(() => {
      const now = performance.now(), text = status.querySelector(".exercise-loading-details")?.textContent.trim();
      if (!text) {   // the status line is gone: ready
        lap(now);
        const times = Object.fromEntries(Object.entries(startup.times).map(([k, ms]) => [k, secs(ms)]));
        return finish("runtime-ready", {total: secs(now), page: secs(startup.start ?? now), ...times, network: network()});
      }
      startup.start ??= now;
      startup.engine ||= /Pyodide/.test(text) ? "pyodide" : /webR/.test(text) ? "webr" : null;
      const stage = (STAGES.find(([re]) => re.test(text)) || [, "error"])[1];
      if (stage === "error") return finish("runtime-error", {message: text.slice(0, 100)});
      if (stage !== startup.stage) lap(now), Object.assign(startup, {stage, since: now});
    }).observe(status, {childList: true, subtree: true, characterData: true});
    // ponytail: best effort, an event sent while the page closes can be lost
    addEventListener("pagehide", () => finish("runtime-abandoned", {stage: startup.stage, total: secs(performance.now()), network: network()}));
  };
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", watchStartup) : watchStartup();

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
