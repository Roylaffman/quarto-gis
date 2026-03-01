---
tags:
  - substack
  - writing
  - gis
  - conservation
  - california
date: 2026-02-27
status: "[[Seed 3]]"
source: "[[rana-boylii.qmd]]"
---

## Hook

There is a frog in California that will not leave the water. While most amphibians wander freely between ponds and upland habitat, *Rana boylii* — the Foothill Yellow-legged Frog — is bound to moving water with a specificity that borders on ecological inflexibility. It needs the cobbles of fast-flowing riffles, the partial sunlight that feeds its tadpoles, the unobstructed seasonal pulse of a California river rising with winter rain and dropping through the long dry summer. For tens of thousands of years, the rivers delivered. Today, nearly half of those rivers have been changed beyond the frog's tolerance — and the map of where it lives has been cut in half.

## Body

### The Sentinel

*Rana boylii* once ranged from the Willamette River in Oregon to the San Gabriel Mountains above Los Angeles — a continuous arc of Pacific Coast drainages from the Klamath to the Transverse Ranges. Biologists call it an "ecological sentinel": a species whose health reflects the vitality of the entire flowing-water ecosystem it inhabits. When the frog disappears from a watershed, it is a signal that something fundamental has changed in that river.

The map today is a fragment of what it was. An estimated 45 to 55 percent of the historical range is gone. In the Sierra Nevada, roughly two-thirds of historic populations have been lost. The frog is effectively absent from Southern California. In 2023 and 2024, the U.S. Fish & Wildlife Service made it official: four distinct populations of *Rana boylii* are now listed as Endangered or Threatened under the Endangered Species Act.

### The Habitat It Cannot Leave

The frog's requirements are precise to the point of vulnerability. It breeds in the shallow, rocky margins of riffles — coarse cobble and pebble substrate where partial sunlight drives the algae growth that its tadpoles eat during their months-long development. Eggs are laid in calm eddies in early spring, timed to the natural decline in stream flow after snowmelt. The window is narrow: a sudden dam release sends the egg mass downstream. An early drought strands the tadpoles in shrinking pools before they can metamorphose. The frog did not evolve for managed rivers, and managed rivers have not evolved for the frog.

![[images/rana-boylii/static-overview.png]]
*Rana boylii's current California range (green), management clades (dashed outlines), and 6,253 GBIF observation records. Red dot: personal sighting, Sierra Nevada foothills.*

### How California Manages a Disappearing Species

The federal ESA listing is built on two overlapping frameworks — one genetic, one ecological — that together explain how a single species gets managed differently in different parts of the same state.

**Distinct Population Segments (DPS)** are the smallest unit the ESA can protect. A population qualifies if it is discrete from other populations and significant enough that its loss would leave a major gap in the species' range or genetic diversity. For *Rana boylii*, this means the struggling populations in the southern Sierra and along the South Coast receive Endangered status — the strongest federal protection — while the comparatively healthier populations of the northern mountains remain unlisted for now. The designation is surgical by design: protect what is failing without burdening what is not.

**Management Clades** are the genetic layer underneath the legal one. California's mountain ranges have acted as barriers for thousands of years, isolating groups of frogs that gradually became distinct lineages — each adapted to the specific chemistry, hydrology, and temperature regime of its home watershed. CDFW recognizes six of these clades. They matter because conservation isn't just about numbers: you cannot take frogs from the rainy North Coast and release them into the snowmelt rivers of the southern Sierra and expect it to work. The local adaptations are real, and losing a clade is losing an evolutionary experiment that cannot be rerun.

![[images/rana-boylii/dps-range-loss.png]]
*Estimated range loss by Distinct Population Segment. South Coast and South Sierra DPS are federally Endangered.*

### Four Threats, One Pattern

The frog's decline has four causes that compound each other.

**Dams** are the most structurally decisive. Hydropower operations invert the natural flow regime — releasing cold water in summer, cutting peak flows in winter — breaking the reproductive timing that *Rana boylii* evolved over millennia. A sudden pulse of cold water in April can dislodge an entire season's egg mass. This isn't incidental: it is the direct consequence of operating a dam for power and irrigation on a river that once ran on snowmelt and gravity.

**Invasive species** do the rest in the lowlands. The American Bullfrog — released across California for commercial frog farming in the early 20th century — thrives in the warm, still reservoirs that dams create. Centrarchid fish (bass, sunfish, bluegill), introduced for sport fishing, consume tadpoles and juveniles in reaches where *Rana boylii* once had no vertebrate predators. The reservoir is the bullfrog's habitat; it is the foothill yellow-legged frog's death trap.

**Climate change** amplifies both of these. More intense atmospheric rivers followed by earlier and longer droughts produce exactly the unpredictable flow regime — extreme floods during egg development, premature drying during tadpole development — that breaks the frog's life cycle. Snow-fed Sierra streams that once ran through August are drying weeks earlier.

**The conservation paradox** ties the whole thing together. Every dam on every river where *Rana boylii* has declined was built to serve a legitimate human need: water storage, flood control, hydropower, irrigation. The farmers downstream and the frog upstream need the same water at the same time. For most of the twentieth century, the frog had no legal standing in that negotiation. The ESA listings change the calculus — but they arrive after decades of damage, into a landscape already transformed.

![[images/rana-boylii/gbif-by-decade.png]]
*GBIF Rana boylii observations in California by decade. The post-2010 rise reflects iNaturalist growth, not population recovery.*

### The Interactive Map

The full interactive version maps the official CDFW current range, all six management clades with ESA status, a heatmap of 6,253 documented observations, and a personal sighting from the Sierra Nevada foothills — all overlaid on EPA Level III Ecoregions to show the ecological context. Toggle layers on and off to see how the frog's documented presence aligns with its managed boundaries.

**IMAGE PLACEHOLDER: interactive-map.png** — SCREENSHOT NEEDED from rendered HTML at `research/_output/analysis/rana-boylii.html`

## Takeaway

The Foothill Yellow-legged Frog is a precise instrument for measuring the health of California's rivers. Its requirements are so specific — the right cobble, the right flow, the right timing — that its absence is an exact diagnosis, not a vague alarm. Half of California's rivers have changed enough that the frog can no longer use them. The ESA listings are the legal acknowledgment of that loss. The harder question is whether the management tools now in place — flow prescriptions, bullfrog removal, habitat restoration — can recover a species whose decline was built into the infrastructure of a state that runs on managed water.

## Call to Action

If you found this useful — the maps, the conservation framework, the frog — subscribe for more spatial analysis on ecology, environmental history, and the geography of what's being lost. The full interactive version is a Quarto document with toggleable map layers and source data. Drop a comment if you've seen one of these frogs, or if there's a California watershed you'd like to see covered.

## Notes to Self

**Tone**: Narrative science writing — precise but accessible. Grounded in the biology and management frameworks, not advocacy. Similar register to the Critical Minerals piece but with more emphasis on ecological mechanism.

**Audience**: Environmental readers, California nature/outdoor community, GIS/data audience, conservation policy readers.

**Target length**: ~1,600 words, 4 images (1 static map + 2 charts + 1 interactive map screenshot)

**Publish date**: TBD

**Cross-post to**: geoglypha1.org

**Source Material**:
- CDFW CWHR ds589 (range polygon) + ds2865 (clade boundaries)
- USFWS Federal Register 88 FR 73498 (ESA listings 2023)
- GBIF taxonKey 2426814 (6,253 California occurrence records)
- EPA Level III Ecoregions ArcGIS REST service
- AmphibiaWeb — Rana boylii species account
- Welsh, Garthwaite & Lind (2016) — oviposition site choice, USDA PSW
- Hayes et al. (2016) — conservation assessment, USDA GTR PSW-248

**Images / Media**:

| Description | File | Status |
|---|---|---|
| Static range + clade overview map | `images/rana-boylii/static-overview.png` | EXPORT NEEDED |
| DPS range loss horizontal bar chart | `images/rana-boylii/dps-range-loss.png` | EXPORT NEEDED |
| GBIF observations by decade bar chart | `images/rana-boylii/gbif-by-decade.png` | EXPORT NEEDED |
| Interactive Folium map | `images/rana-boylii/interactive-map.png` | SCREENSHOT NEEDED |

**To export static images**: Run `python export_rana_boylii_images.py` from `research/analysis/` (script to be created — see export_critical_minerals_images.py as the pattern).

**Interactive HTML location**: `research/_output/analysis/rana-boylii.html`
