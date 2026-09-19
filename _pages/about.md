---
permalink: /
title: "Welcome"
author_profile: true
---

I am a physicist working on **complex networks and the energy transition**. I am a postdoctoral researcher at the Paris Interdisciplinary Energy Research Institute (LIED/PIERI), Université Paris Cité / CNRS, where I use statistical physics to study how electricity grids grow, how much material they contain, and what it costs to build and renew them worldwide.

More about [my background](/about-me/), [my research](/research/) and [my publications](/publications/).

Latest news
------
{% for item in site.data.news limit:4 %}
* **{{ item.date }}** — {{ item.text | markdownify | remove: '<p>' | remove: '</p>' | strip }}
{% endfor %}

[All news](/news/)
