---
layout: page
permalink: /publications/
title: Research
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->
<div class="publications">

<div class="sort-toggle" role="group" aria-label="Sort papers">
  sort by
  <button type="button" data-sort="year" aria-pressed="true">status</button>
  <button type="button" data-sort="field" aria-pressed="false">field</button>
</div>

<!-- Time view: working papers (top), published (by year), work in progress (bottom); newest first -->
<div class="by-year">
<section class="pub-section">
<h2>Working papers</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[preprint=true, wip!=true] -g none %}
</section>

<section class="pub-section">
<h2>Published</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[preprint!=true] %}
</section>

<section class="pub-section">
<h2>Work in progress</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[wip=true] -g none %}
</section>
</div>

<!-- Field view: all papers by field (order of _data/fields.yml), each field grouped by year -->
<div class="by-field">
{% for field in site.data.fields %}
<section class="pub-section">
<h2>{{ field }}</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[field={{ field }}] %}
</section>
{% endfor %}
</div>

<style>
  /* hide a section that has no entries */
  .pub-section:not(:has(li)) { display: none; }
  /* show one view at a time */
  .publications:not(.sort-field) .by-field,
  .publications.sort-field .by-year { display: none; }
  /* "sort by  time  field": plain text, same look as the paper links */
  .sort-toggle { color: var(--global-text-color-light); margin-bottom: 1.5rem; }
  .sort-toggle button {
    background: none; border: 0; padding: 0; margin-left: 0.75rem;
    color: var(--global-theme-color); cursor: pointer;
  }
  .sort-toggle button[aria-pressed="true"] {
    color: var(--global-text-color); text-decoration: underline; text-underline-offset: 0.25em;
  }
</style>

<script>
  (() => {
    const root = document.querySelector('.publications');
    const buttons = root.querySelectorAll('.sort-toggle button');
    const show = (sort) => {
      root.classList.toggle('sort-field', sort === 'field');
      buttons.forEach((b) => b.setAttribute('aria-pressed', b.dataset.sort === sort));
      try { localStorage.setItem('pubSort', sort); } catch (e) {}
    };
    buttons.forEach((b) => b.addEventListener('click', () => show(b.dataset.sort)));
    let saved = null;
    try { saved = localStorage.getItem('pubSort'); } catch (e) {}
    if (saved) show(saved);
  })();
</script>

</div>
