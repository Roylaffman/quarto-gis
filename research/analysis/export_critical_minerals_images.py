"""
Export static PNG images from critical-minerals.qmd for Substack article.

Generates:
  1. static-overview.png    — matplotlib map of all sites (Americas)
  2. lithium-production.png — Plotly horizontal bar (global lithium by country)
  3. ree-dominance.png      — Plotly donut chart (China's REE share)

Usage:
  cd research/analysis
  python export_critical_minerals_images.py
"""

import sys
import json
import os

sys.path.append("..")

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
from shapely.geometry import Point

# Output folder — save locally (copy to Google Drive manually when mounted)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_export_images")
os.makedirs(OUT, exist_ok=True)

# Try to also copy to Google Drive if available
DRIVE_OUT = r"G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\critical-minerals"
DRIVE_AVAILABLE = os.path.exists(r"G:\My Drive")

import shutil

def save_and_copy(local_path):
	"""Copy to Google Drive if available."""
	if DRIVE_AVAILABLE:
		os.makedirs(DRIVE_OUT, exist_ok=True)
		fname = os.path.basename(local_path)
		drive_path = os.path.join(DRIVE_OUT, fname)
		shutil.copy2(local_path, drive_path)
		print(f"  Copied to: {drive_path}")
	else:
		print(f"  (Google Drive not mounted — copy manually from {OUT})")

# Load site data
with open("CriticalMineralsSites.json", "r", encoding="utf-8") as f:
	sites_data = json.load(f)

sites_df = pd.DataFrame(sites_data)
print(f"Loaded {len(sites_df)} sites")


# --- 1. Static Overview (matplotlib) ---
print("Generating static-overview.png ...")

geometry = [Point(s["lon"], s["lat"]) for s in sites_data]
sites_gdf = gpd.GeoDataFrame(sites_df, geometry=geometry, crs="EPSG:4326")

# Use Natural Earth shapefile bundled with geodatasets or download
try:
	import geodatasets
	world = gpd.read_file(geodatasets.data.naturalearth.land["url"])
except ImportError:
	# Fallback: fetch directly from Natural Earth (small file, ~800KB)
	ne_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
	world = gpd.read_file(ne_url)

americas = world[world.geometry.apply(
	lambda g: g.centroid.x < -30 and g.centroid.x > -170
)]

fig, ax = plt.subplots(1, 1, figsize=(10, 14))

# Background land
americas.plot(ax=ax, color="#e2e8f0", edgecolor="#94a3b8", linewidth=0.5)

cat_colors = {
	"Lithium": "#22c55e",
	"Rare Earth": "#f97316",
	"Strategic Metals": "#0ea5e9",
}

for cat, color in cat_colors.items():
	subset = sites_gdf[sites_gdf["category"] == cat]
	if len(subset) > 0:
		subset.plot(
			ax=ax, color=color, markersize=80,
			label=cat, alpha=0.9, edgecolor="white", linewidth=0.8,
			zorder=5,
		)

ax.set_xlim(-130, -30)
ax.set_ylim(-60, 65)
ax.set_facecolor("#f1f5f9")
ax.set_title("Critical Mineral Sites — Americas", fontsize=14, fontweight="bold")
ax.set_axis_off()
ax.legend(loc="lower left", fontsize=10, framealpha=0.9)
plt.tight_layout()

out_path = os.path.join(OUT, "static-overview.png")
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()
print(f"  Saved: {out_path}")
save_and_copy(out_path)


# --- 2. Lithium Production Bar Chart (Plotly) ---
print("Generating lithium-production.png ...")

production_data = pd.DataFrame([
	{"country": "Australia", "production_kt": 112.5, "region": "Asia-Pacific"},
	{"country": "China", "production_kt": 78.0, "region": "Asia"},
	{"country": "Chile", "production_kt": 54.4, "region": "Americas"},
	{"country": "Zimbabwe", "production_kt": 22.0, "region": "Africa"},
	{"country": "Argentina", "production_kt": 10.0, "region": "Americas"},
	{"country": "Brazil", "production_kt": 5.0, "region": "Americas"},
	{"country": "Canada", "production_kt": 4.3, "region": "Americas"},
	{"country": "Portugal", "production_kt": 1.5, "region": "Europe"},
	{"country": "USA", "production_kt": 0.0, "region": "Americas"},
])

production_data = production_data.sort_values("production_kt", ascending=True)

color_map = {
	"Americas": "#22c55e",
	"Asia-Pacific": "#f43f5e",
	"Asia": "#f97316",
	"Africa": "#64748b",
	"Europe": "#0ea5e9",
}

fig = px.bar(
	production_data,
	x="production_kt",
	y="country",
	color="region",
	orientation="h",
	title="Global Lithium Production by Country (2024 est., kilotonnes LCE)",
	labels={"production_kt": "Production (kt)", "country": ""},
	color_discrete_map=color_map,
)
fig.update_layout(
	height=450,
	width=800,
	showlegend=True,
	legend_title_text="Region",
	xaxis_title="Lithium Production (kilotonnes LCE)",
	plot_bgcolor="white",
)

out_path = os.path.join(OUT, "lithium-production.png")
pio.write_image(fig, out_path, scale=2)
print(f"  Saved: {out_path}")
save_and_copy(out_path)


# --- 3. REE Dominance Donut Chart (Plotly) ---
print("Generating ree-dominance.png ...")

ree_data = pd.DataFrame([
	{"country": "China", "share_pct": 60.0},
	{"country": "USA (Mountain Pass)", "share_pct": 15.0},
	{"country": "Myanmar", "share_pct": 10.0},
	{"country": "Australia", "share_pct": 8.0},
	{"country": "Other", "share_pct": 7.0},
])

fig = px.pie(
	ree_data,
	values="share_pct",
	names="country",
	title="Global Rare Earth Oxide Production Share (2024 est.)",
	color="country",
	color_discrete_map={
		"China": "#f97316",
		"USA (Mountain Pass)": "#22c55e",
		"Myanmar": "#64748b",
		"Australia": "#f43f5e",
		"Other": "#cbd5e1",
	},
	hole=0.4,
)
fig.update_layout(height=450, width=600)

out_path = os.path.join(OUT, "ree-dominance.png")
pio.write_image(fig, out_path, scale=2)
print(f"  Saved: {out_path}")
save_and_copy(out_path)

print("\nDone! 3 images exported.")
print(f"Interactive map screenshot needed: open rendered HTML and capture manually.")
