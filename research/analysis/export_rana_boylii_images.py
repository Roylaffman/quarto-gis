"""
Export static PNG images from rana-boylii.qmd for Substack article.

Generates:
  1. static-overview.png  — matplotlib map (CA range + clades + GBIF points)
  2. dps-range-loss.png   — Plotly horizontal bar (estimated range loss by DPS)
  3. gbif-by-decade.png   — Plotly bar (GBIF observations by decade)

Usage:
  cd research/analysis
  python export_rana_boylii_images.py
"""

import os
import shutil
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Output folder — save locally, then copy to Google Drive if available
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_export_images")
os.makedirs(OUT, exist_ok=True)

DRIVE_OUT = r"G:\My Drive\02. Obsidian\Lafferty Cloud\Substack\images\rana-boylii"
DRIVE_AVAILABLE = os.path.exists(r"G:\My Drive")


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


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "rana_boylii")
DATA = os.path.normpath(DATA)

print(f"Data directory: {DATA}")
print("Loading layers...")

california = gpd.read_file(os.path.join(DATA, "california.geojson")).to_crs(epsg=3310)
frog_range = gpd.read_file(os.path.join(DATA, "rana_boylii_range.geojson")).to_crs(epsg=3310)
clades = gpd.read_file(os.path.join(DATA, "rana_boylii_clades.geojson")).to_crs(epsg=3310)
ecoregions = gpd.read_file(os.path.join(DATA, "ca_ecoregions.geojson")).to_crs(epsg=3310)
occ_df = pd.read_csv(os.path.join(DATA, "rana_boylii_occurrences.csv"))
occ_df = occ_df.dropna(subset=["lat", "lon"])

occ_gdf = gpd.GeoDataFrame(
	occ_df,
	geometry=gpd.points_from_xy(occ_df["lon"], occ_df["lat"]),
	crs="EPSG:4326",
).to_crs(epsg=3310)

print(f"  {len(frog_range)} range feature, {len(clades)} clades, "
	  f"{len(ecoregions)} ecoregions, {len(occ_gdf):,} occurrence points")


# ---------------------------------------------------------------------------
# 1. Static Overview Map (matplotlib)
# ---------------------------------------------------------------------------
print("\nGenerating static-overview.png ...")

ECO_MPL_COLORS = {
	"Sierra Nevada": "#d4a574",
	"Coast Range": "#a8c5a0",
	"Central California Valley": "#e8d5a0",
	"Klamath Mountains/California High North Coast Range": "#8ab4a0",
	"Cascades": "#b0c8a8",
	"Central California Foothills and Coastal Mountains": "#c8b890",
	"Southern California Mountains": "#c8a888",
	"Southern California/Northern Baja Coast": "#d8c098",
	"Eastern Cascades Slopes and Foothills": "#c0b898",
	"Central Basin and Range": "#d8c8a8",
	"Northern Basin and Range": "#d0c4a4",
}

CLADE_MPL = {
	"Southwest/South Coast": "#f43f5e",
	"East/Southern Sierra": "#f97316",
	"NF Feather and Upper Feather River Watershed": "#f59e0b",
	"West/Central Coast": "#0ea5e9",
	"Northwest/North Coast": "#22c55e",
	"Northeast/Northern Sierra": "#a855f7",
}

fig, ax = plt.subplots(1, 1, figsize=(8, 12))

california.plot(ax=ax, color="#f8f9fa", edgecolor="#94a3b8", linewidth=0.8, zorder=1)

for _, row in ecoregions.iterrows():
	color = ECO_MPL_COLORS.get(row["US_L3NAME"], "#d0c8b8")
	gpd.GeoDataFrame([row], crs=3310).plot(
		ax=ax, color=color, edgecolor="#94a3b8", linewidth=0.3,
		alpha=0.5, zorder=2,
	)

frog_range.plot(
	ax=ax, color="#22c55e", alpha=0.4, edgecolor="#16a34a",
	linewidth=1.0, zorder=3,
)

for _, row in clades.iterrows():
	c = CLADE_MPL.get(row["Clade"], "#64748b")
	gpd.GeoDataFrame([row], crs=3310).plot(
		ax=ax, color="none", edgecolor=c, linewidth=1.8,
		linestyle="--", zorder=4,
	)

occ_thin = occ_gdf.iloc[::5]
occ_thin.plot(ax=ax, color="#0ea5e9", markersize=2, alpha=0.5, zorder=5)

legend_handles = [
	mpatches.Patch(color="#22c55e", alpha=0.5, label="Current Range (CDFW ds589)"),
	mpatches.Patch(facecolor="none", edgecolor="#f43f5e", linestyle="--",
				   label="South Coast DPS \u2014 Endangered"),
	mpatches.Patch(facecolor="none", edgecolor="#f97316", linestyle="--",
				   label="South Sierra DPS \u2014 Endangered"),
	mpatches.Patch(facecolor="none", edgecolor="#f59e0b", linestyle="--",
				   label="North Feather DPS \u2014 Threatened"),
	mpatches.Patch(facecolor="none", edgecolor="#0ea5e9", linestyle="--",
				   label="Central Coast DPS \u2014 Threatened"),
	plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#0ea5e9",
			   markersize=5, label="GBIF Occurrences (thinned 1:5)"),
]
ax.legend(handles=legend_handles, loc="lower left", fontsize=7,
		  framealpha=0.9, title="Legend", title_fontsize=8)
ax.set_title("Rana boylii \u2014 California Range & Management Clades",
			 fontsize=12, fontweight="bold")
ax.set_axis_off()
plt.tight_layout()

out_path = os.path.join(OUT, "static-overview.png")
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()
print(f"  Saved: {out_path}")
save_and_copy(out_path)


# ---------------------------------------------------------------------------
# 2. DPS Range Loss Bar Chart (Plotly)
# ---------------------------------------------------------------------------
print("\nGenerating dps-range-loss.png ...")

dps_data = pd.DataFrame([
	{"DPS": "South Coast",           "loss": 70, "status": "Endangered"},
	{"DPS": "South Sierra",          "loss": 66, "status": "Endangered"},
	{"DPS": "Central California Coast", "loss": 50, "status": "Threatened"},
	{"DPS": "North Feather River",   "loss": 40, "status": "Threatened"},
])

fig = go.Figure(go.Bar(
	x=dps_data["loss"],
	y=dps_data["DPS"],
	orientation="h",
	marker_color=["#f43f5e", "#f97316", "#0ea5e9", "#f59e0b"],
	text=[f"{v}%" for v in dps_data["loss"]],
	textposition="outside",
))
fig.update_layout(
	title="Estimated Range Loss by Distinct Population Segment",
	xaxis_title="Estimated Range Loss (%)",
	xaxis=dict(range=[0, 90]),
	yaxis=dict(autorange="reversed"),
	height=320,
	width=700,
	plot_bgcolor="white",
	showlegend=False,
	margin=dict(l=180, r=60, t=60, b=50),
)

out_path = os.path.join(OUT, "dps-range-loss.png")
pio.write_image(fig, out_path, scale=2)
print(f"  Saved: {out_path}")
save_and_copy(out_path)


# ---------------------------------------------------------------------------
# 3. GBIF Observations by Decade (Plotly)
# ---------------------------------------------------------------------------
print("\nGenerating gbif-by-decade.png ...")

occ_clean = occ_df[occ_df["year"].notna() & (occ_df["year"] > 1900)].copy()
occ_clean["decade"] = (occ_clean["year"] // 10 * 10).astype(int)
decade_counts = (
	occ_clean.groupby("decade")
	.size()
	.reset_index(name="observations")
)

fig = px.bar(
	decade_counts,
	x="decade",
	y="observations",
	title="GBIF Rana boylii Observations in California by Decade",
	labels={"decade": "Decade", "observations": "Observation Records"},
	color_discrete_sequence=["#22c55e"],
)
fig.update_layout(
	height=350,
	width=750,
	plot_bgcolor="white",
	margin=dict(l=60, r=40, t=60, b=50),
)

out_path = os.path.join(OUT, "gbif-by-decade.png")
pio.write_image(fig, out_path, scale=2)
print(f"  Saved: {out_path}")
save_and_copy(out_path)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Done. 3 images exported to:")
print(f"  {OUT}")
for f in sorted(os.listdir(OUT)):
	if f.endswith(".png"):
		size_kb = os.path.getsize(os.path.join(OUT, f)) // 1024
		print(f"  {f:<35} {size_kb:>5} KB")
print("\nNext step: screenshot interactive map from")
print("  research/_output/analysis/rana-boylii.html")
print("  Save as: images/rana-boylii/interactive-map.png")
