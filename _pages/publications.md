---
layout: page
permalink: /publications/
title: Research
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->
<div class="publications">

<section class="pub-section">
<h2>Working papers</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[preprint=true] %}
</section>

<section class="pub-section">
<h2>Published</h2>
{% bibliography -f {{ site.scholar.bibliography }} -q @*[preprint!=true] %}
</section>

<!-- hide a section that has no entries -->
<style>.pub-section:not(:has(li)) { display: none; }</style>

</div>
