---
layout: codep
title: Presentaciones de candidates a CoDep
permalink: /codep/presentaciones/
---

Cada año, quienes se postulan como candidates a representantes estudiantiles de CoDep escriben una breve presentación contando quiénes son y qué les gustaría hacer.

{% assign year_pages = site.pages | where_exp: "p", "p.year" | sort: "year" | reverse %}
<ul>
  {% for yp in year_pages %}
    <li><a href="{{ yp.url | relative_url }}">{{ yp.year }}</a></li>
  {% endfor %}
</ul>
