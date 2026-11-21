# One page summing up the world's news of 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/chocolatos72/world-news-20-nov-2026/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/chocolatos72/world-news-20-nov-2026/reward.svg)](https://make.fun/c/news-image-20261120)

An entry for the make.fun bounty [Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120).

`main.py` (Python 3.13, standard library only, no network) draws a one-page
newspaper front page, 768x1024, summing up Friday 20 November 2026:

- 15 main stories with flat vector illustrations drawn in code (no photos,
  no faces, no text inside the pictures). The three big mains are Trump's
  White House press conference in Washington (he vows a data center tax
  on companies building abroad and defends calling Putin a friend),
  Russia's mass missile strike on Kyiv (nine killed, three bridges hit),
  and Cyclone Akvan slamming into Odisha (370,000 evacuated, no deaths).
  The 12 minis are COP31 in Antalya (draft drops the fossil text, talks
  into overtime), the UK-EU summit in Brussels (100,000 visas agreed,
  fees row stalls), Iran's tanker mine claim in Hormuz, Saudi Arabia
  intercepting missiles and drones over Jazan, the Sydney counter-terror
  raids, Taiwan's short-selling curbs, the Malaysian air force drug ring,
  the ANC's Johannesburg coalition deal, Glenn Phillips' century for
  New Zealand, the Asian stock plunge in Tokyo, Europe's cost-of-living
  protests in Paris, and Russian missiles hitting Poland.
  The layout follows the reference front page: the date itself is the
  masthead ("FRIDAY 20 NOVEMBER 2026", huge and bold) under a "THE WORLD
  IN ONE DAY" kicker, a one-line summary of the top three stories, region
  chips, the day's six big numbers as large figures with thin rules
  between them, three big mains and twelve minis in a 6x2 grid, and the
  world map with the other stories at the bottom, plus a DATE CHECK box
  and a line of stories left out as other days' news. The background is
  one flat cream; every story sits in its own bordered box, and every
  illustrated story carries a coloured label bar over a sharply bordered
  illustration. 40 stories in all.
- A world map drawn from real longitude/latitude outlines, one muted colour
  per continent, with numbered markers for the 15 main stories (region
  counts: Asia 7, Europe 8, Mideast 4, Americas 8, Africa 8, Oceania 4,
  Global 1).
- The other 25 stories as a two-column list, each item in its own bordered
  box on two lines (place, then a short headline), its number inside a
  coloured pill and its place in its continent's colour.
- A date check and the day's sources.

## Run it

```sh
python3 main.py            # writes /output/entry.png
OUTPUT=entry.png python3 main.py
```

Deterministic: two runs write byte-identical files. The image is 768x1024
PNG, well under the 1 MiB limit.

## The 40 stories

All 40 stories were checked against wire reports of 20 November 2026
(Reuters, AP, BBC, AFP, Xinhua, IMD, ESPNcricinfo and the day's wires),
and refreshed on the morning of Saturday 21 November once the news day
was complete (COP31's final text, the UK-EU summit outcome, the Trump
press conference, Cyclone Akvan's final toll). Claims that rest on a
single source are worded as claims ("Iran says...").
