{# Web CV entry (cv.qmd): date and location on the right, then the same main column as the PDF. #}
{% set lines = entry.main_column.splitlines()|reject("equalto", "!!! summary")|map("trim")|list %}
::: cv-entry
[{{ entry.date_and_location_column.splitlines()|reverse|join(" · ") }}]{.cv-date}
{% for line in lines %}
{% if line.startswith("- ") and loop.previtem and not loop.previtem.startswith("- ") %}

{% endif %}
{{ line }}{{ "  " if not line.startswith("- ") }}
{% endfor %}
:::
