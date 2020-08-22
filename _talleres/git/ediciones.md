---
layout: taller
title: Ediciones anteriores
tallerid: git
permalink: /talleres/git/ediciones
weight: 4
---

{% for parteTaller in site.talleres %}
    {% if parteTaller.layout == "edicion" and parteTaller.tallerid == page.tallerid %}
* [{{ parteTaller.title }}]({{ site.baseurl }}/talleres/git/ediciones/{{ parteTaller.name }}.html)
    {% endif %}
{% endfor %}
