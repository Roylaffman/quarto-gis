---
tags:
  - substack
  - writing
  - gis
date: 2026-02-24
status: "[[Seed 3]]"
source: "[[critical-minerals.qmd]]"
---

## Hook

The United States produces almost zero lithium. The single operating mine — a brine evaporation pond in the Nevada desert that's been running since 1966 — supplies a rounding error of global demand. Meanwhile, every electric vehicle, grid battery, and wind turbine depends on minerals that come overwhelmingly from a handful of salt flats in South America and processing plants in China. The geography of the energy transition is a map of dependency — and it's starting to change.

## Body

### The White Gold Rush

Lithium has become the most strategically important mineral of the twenty-first century. Global production hit 240,000 metric tonnes in 2024 and demand is accelerating as EV adoption scales worldwide. But the supply chain is lopsided. Australia and China together produce nearly 80% of the world's lithium. The Americas — despite sitting on enormous deposits — contribute about 30%, almost entirely from Chile's Atacama Desert.

The 2022 Inflation Reduction Act tried to change the math. Its clean vehicle tax credits require that critical minerals be sourced from the US or free-trade-agreement partners, triggering a wave of new mine permits from Nevada to Quebec. But permitting a mine and producing lithium are separated by years of construction, environmental review, and the kind of political fights that can stall a project indefinitely.

![[images/critical-minerals/lithium-production.png]]
*Global lithium production by country (2024 est.). Americas countries in green. Source: USGS Mineral Commodity Summaries.*

### The Lithium Triangle

The heart of the Americas' lithium supply sits in the high Andes where Chile, Argentina, and Bolivia meet. The Lithium Triangle — a region of ancient salt flats at 2,300 to 4,000 meters elevation — holds roughly 60% of the world's known lithium reserves.

The extraction process is deceptively simple: pump brine from underground, spread it in evaporation ponds, and let the desert sun concentrate the lithium over 12-18 months. It's cheap, but it's water-intensive — and the Atacama is the driest non-polar place on Earth. Indigenous communities and environmental groups have challenged projects across the triangle, arguing that brine pumping depletes aquifers that sustain fragile high-altitude ecosystems.

Chile dominates with the Salar de Atacama (producing a third of global supply through SQM and Albemarle), while Argentina has opened its doors to foreign investment — including Chinese firm Ganfeng Lithium at the Cauchari-Olaroz project. Bolivia sits on the largest reserves of all at the Salar de Uyuni (21 million tonnes), but state control and technical challenges have kept production minimal.

### The Domestic Push

Three sites in Nevada represent the US attempt to build a domestic lithium supply chain:

**Rhyolite Ridge** (Ioneer) — A lithium-boron deposit that received federal approval in 2024, making it the first lithium mine permitted under the Biden administration. Joint venture with Sibanye-Stillwater. Construction planned for 2026, production by 2029.

**Thacker Pass** (Lithium Americas) — The largest known lithium deposit in the US, under construction with a $650M General Motors investment. It's a clay deposit, not brine — a different extraction process that could supply lithium for 800,000 EVs annually.

**Silver Peak** (Albemarle) — America's only operating lithium mine, producing from brine ponds in Clayton Valley since 1966. Its output is a fraction of what the market needs.

Then there's **Twin Metals** in northern Minnesota — not lithium, but copper, nickel, cobalt, and platinum group metals, all classified as critical minerals. The proposed underground mine sits just miles from the Boundary Waters Canoe Area Wilderness, and its mineral leases were canceled in 2022 over environmental concerns. It's the sharpest example of the tension between mineral extraction and conservation that runs through every site on this map.

![[images/critical-minerals/static-overview.png]]
*Critical mineral sites across the Americas — 17 sites across 7 countries. Green = lithium, orange = rare earths, blue = strategic metals (copper, nickel, cobalt).*

### China's Rare Earth Lock

The story gets starker with rare earth elements. China controls roughly 60% of global rare earth *mining* and 85% of global rare earth *processing*. The permanent magnets in every EV motor and wind turbine depend on neodymium and praseodymium that, more often than not, pass through Chinese refineries.

The US has exactly one operating rare earth mine: **Mountain Pass** in California's Mojave Desert, operated by MP Materials. It produces about 15% of global rare earth oxide. But for years, even Mountain Pass shipped its concentrate to China for refining. MP Materials is now building domestic processing capacity, but closing the gap will take years and billions in capital.

![[images/critical-minerals/ree-dominance.png]]
*China's dominance in rare earth oxide production (2024 est.). Mountain Pass is the sole Western Hemisphere source. Source: USGS Mineral Commodity Summaries.*

### The Interactive Map

The full interactive version of this analysis maps all 17 critical mineral sites with clickable markers showing project details, operator information, and development status. You can explore it in the rendered Quarto document.

**IMAGE PLACEHOLDER: interactive-map.png** — SCREENSHOT NEEDED from rendered HTML at `research/_output/analysis/critical-minerals.html`

## Takeaway

The geography of critical minerals is the geography of twenty-first century power. The energy transition doesn't just require building EVs and wind farms — it requires securing the lithium, rare earths, cobalt, and copper that make them possible. Right now, that map tilts heavily toward a few salt flats in South America and processing plants in China. The US is trying to change the equation, but every new mine sits at the intersection of industrial demand, environmental protection, and the political will to choose between them.

## Call to Action

If this kind of spatial analysis interests you — mapping resources, geopolitics, and environmental tradeoffs — subscribe for more. The full interactive version with clickable maps and source data is available as a Quarto document. Drop a comment if there's a site or mineral you'd like to see added to the map.

## Notes to Self

**Tone**: Analytical but accessible, data-driven, geopolitical narrative. Similar to lithium analysis piece but with more geographic/mapping focus.

**Audience**: Energy/climate readers, EV followers, map nerds, geopolitics people, tech-curious generalists.

**Target length**: ~1,800 words, 4 images (3 charts + 1 interactive map screenshot)

**Publish date**: TBD

**Cross-post to**: geoglypha1.org

**Source Material**:
- USGS Mineral Commodity Summaries 2025 (Lithium, Rare Earths, Cobalt, Nickel, Copper)
- IEA Critical Minerals Report 2024
- Inflation Reduction Act of 2022, Sections 13401-13402
- Ioneer Ltd — Rhyolite Ridge Project (rhyoliteridge.com)
- Lithium Americas Corp — Thacker Pass (lithiumamericas.com)
- MP Materials — Mountain Pass (mpmaterials.com)
- Twin Metals Minnesota (twin-metals.com)
- Benchmark Minerals Intelligence — Global lithium production data

**Images / Media**:

| Description | File | Status |
|---|---|---|
| Lithium production bar chart | `images/critical-minerals/lithium-production.png` | Ready |
| Static overview map | `images/critical-minerals/static-overview.png` | Ready |
| REE dominance donut chart | `images/critical-minerals/ree-dominance.png` | Ready |
| Interactive Folium map | `images/critical-minerals/interactive-map.png` | SCREENSHOT NEEDED |

**Interactive HTML location**: `research/_output/analysis/critical-minerals.html` (22 MB standalone)
