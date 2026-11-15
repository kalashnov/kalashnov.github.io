---
layout: page
permalink: /publications/
title: Research
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->
<div class="publications">

<div class="sort-toggle mb-3" role="group" aria-label="Sort papers">
  Sort by:
  <button type="button" class="btn btn-sm z-depth-0" data-sort="year" aria-pressed="true">Time</button>
  <button type="button" class="btn btn-sm z-depth-0" data-sort="field" aria-pressed="false">Field</button>
</div>

<!-- Time view: working papers vs. published, each by year -->
<div class="by-year">
<section class="pub-section">
<h2>Working papers</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[preprint=true] %}
</section>

<section class="pub-section">
<h2>Published</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[preprint!=true] %}
</section>
</div>

<!-- Field view: all papers by field (Z->A puts Econometric theory first) -->
<div class="by-field">
{% bibliography -f {{ site.scholar.bibliography }} -g field -G descending %}
</div>

<style>
  /* hide a section that has no entries */
  .pub-section:not(:has(li)) { display: none; }
  /* show one view at a time */
  .publications:not(.sort-field) .by-field,
  .publications.sort-field .by-year { display: none; }
  .sort-toggle [aria-pressed="true"] { font-weight: bold; text-decoration: underline; }
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
