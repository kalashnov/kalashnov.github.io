{# Web CV header (cv.qmd): one line of contact links; the page title replaces the name. #}
::: cv-contact
[{{ cv.email }}](mailto:{{ cv.email }}){% if cv.website %} · [{{ cv.website|clean_url }}]({{ cv.website }}){% endif %}{% for n in cv.social_networks or [] %} · [{{ n.network }}]({{ n.url }}){% endfor %}{% for c in cv.custom_connections or [] %} · [{{ c.placeholder }}]({{ c.url }}){% endfor %}

:::
