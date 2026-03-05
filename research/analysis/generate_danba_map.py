"""
generate_danba_map.py — Ryan Lafferty
Fetches OSM data for Danba County and renders an earth-tone local map.
Output: _export_images/danba-osmnx.png

Run from: research/analysis/
    python generate_danba_map.py
"""

import os
import warnings
warnings.filterwarnings("ignore")

import osmnx as ox
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Disable Overpass rate-limit pause — prevents multi-minute hangs
ox.settings.overpass_rate_limit = False
ox.settings.requests_timeout = 60

CENTER = (30.88, 101.89)
DIST = 4000

BG		= "#f5ede0"
BLD_FC	= "#c4a882"
BLD_EC	= "#7c3d12"
ST_EC	= "#a8896c"
WAT_FC	= "#7dd3fc"
WAT_EC	= "#0369a1"
GRN_FC	= "#a7c4a0"
GRN_EC	= "#4a7c59"


def fetch_layers():
	print("Fetching OSM layers for Danba County...")

	G = ox.graph_from_point(CENTER, dist=DIST, network_type="all", retain_all=True)
	_, edges = ox.graph_to_gdfs(G)
	edges = edges.to_crs(epsg=3857)
	print(f"  streets:   {len(edges)} edges")

	try:
		bldgs = ox.features_from_point(CENTER, tags={"building": True}, dist=DIST)
		bldgs = bldgs[bldgs.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].to_crs(epsg=3857)
		print(f"  buildings: {len(bldgs)}")
	except Exception as e:
		bldgs = None
		print(f"  buildings: none ({e})")

	try:
		water = ox.features_from_point(
			CENTER,
			tags={"natural": ["water", "river"], "waterway": ["river", "stream", "canal"]},
			dist=DIST,
		)
		water = water[water.geometry.geom_type.isin(
			["Polygon", "MultiPolygon", "LineString", "MultiLineString"]
		)].to_crs(epsg=3857)
		print(f"  water:     {len(water)}")
	except Exception as e:
		water = None
		print(f"  water:     none ({e})")

	try:
		green = ox.features_from_point(
			CENTER,
			tags={"landuse": ["grass", "forest", "farmland"], "natural": ["wood", "scrub"]},
			dist=DIST,
		)
		green = green[green.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].to_crs(epsg=3857)
		print(f"  green:     {len(green)}")
	except Exception as e:
		green = None
		print(f"  green:     none ({e})")

	return edges, bldgs, water, green


def render_map(edges, bldgs, water, green, out_path):
	fig, ax = plt.subplots(figsize=(9, 9), facecolor=BG)
	ax.set_facecolor(BG)
	ax.set_aspect("equal")

	if green is not None and len(green):
		green.plot(ax=ax, facecolor=GRN_FC, edgecolor=GRN_EC, linewidth=0.3, alpha=0.7)

	# Streets — str.contains safely handles list-valued highway column
	hw_col = edges["highway"].astype(str)
	for hw_type, lw in [
		("motorway", 3.5), ("trunk", 3.5), ("primary", 2.8),
		("secondary", 2.2), ("tertiary", 1.6), ("residential", 1.0),
		("service", 0.7), ("unclassified", 0.7),
	]:
		mask = hw_col.str.contains(hw_type, na=False)
		if mask.any():
			edges[mask].plot(ax=ax, color=ST_EC, linewidth=lw, alpha=0.85)
	edges.plot(ax=ax, color=ST_EC, linewidth=0.3, alpha=0.35)

	if water is not None and len(water):
		polys = water[water.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
		lines = water[water.geometry.geom_type.isin(["LineString", "MultiLineString"])]
		if len(polys):
			polys.plot(ax=ax, facecolor=WAT_FC, edgecolor=WAT_EC, linewidth=0.5, alpha=0.9)
		if len(lines):
			lines.plot(ax=ax, color=WAT_EC, linewidth=1.8, alpha=0.9)

	if bldgs is not None and len(bldgs):
		bldgs.plot(ax=ax, facecolor=BLD_FC, edgecolor=BLD_EC, linewidth=0.4, alpha=0.92)

	ax.set_title(
		"Danba County \u2014 Dadu River Valley",
		fontsize=14, fontweight="bold", color="#44403c", pad=12,
	)
	ax.set_axis_off()
	ax.text(
		0.99, 0.01, "\u00a9 OpenStreetMap contributors (ODbL)",
		transform=ax.transAxes, fontsize=7, color="#78716c", ha="right", va="bottom",
	)
	plt.tight_layout()

	os.makedirs(os.path.dirname(out_path), exist_ok=True)
	fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
	plt.close()
	size_kb = os.path.getsize(out_path) // 1024
	print(f"\nSaved: {out_path}  ({size_kb} KB)")


if __name__ == "__main__":
	out = "_export_images/danba-osmnx.png"
	edges, bldgs, water, green = fetch_layers()
	render_map(edges, bldgs, water, green, out)
