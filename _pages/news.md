---
permalink: /news/
title: "News"
author_profile: true
---

{% for item in site.data.news %}
* **{{ item.date }}** — {{ item.text | markdownify | remove: '<p>' | remove: '</p>' | strip }}
{% endfor %}
