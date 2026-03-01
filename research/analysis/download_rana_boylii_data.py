"""
Download GIS data for the Rana boylii (Foothill Yellow-legged Frog) story map.

Run once before rendering rana-boylii.qmd:
  cd research/analysis
  python download_rana_boylii_data.py

Downloads to: ../../data/rana_boylii/
  california.geojson          — CA state boundary (NAD83 → WGS84)
  rana_boylii_range.geojson   — CDFW CWHR ds589 current range
  rana_boylii_clades.geojson  — CDFW ds2865 DPS clade boundaries
  ca_ecoregions.geojson       — EPA Level III Ecoregions, CA subset (Albers → WGS84)
  rana_boylii_occurrences.csv — GBIF occurrence points in California
"""

import os
import sys
import io
import json
import tempfile
import zipfile
import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path

HEADERS = {
	"User-Agent": (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
		"AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/122.0.0.0 Safari/537.36"
	),
	"Accept": "application/json, */*",
}


def download_zip_gdb(url, gdb_name, label, timeout=120):
	"""Download a ZIP containing a FileGDB, extract it, return GeoDataFrame."""
	print(f"  Downloading {label} ...")
	resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
	resp.raise_for_status()
	data = resp.content

	if data[:5] in (b"<!DOC", b"<html"):
		raise ValueError("Got HTML response — possible redirect/auth required")

	# Extract ZIP to a persistent temp folder that lives as long as we need it
	tmp_dir = tempfile.mkdtemp()
	zip_path = os.path.join(tmp_dir, "data.zip")
	with open(zip_path, "wb") as fh:
		fh.write(data)
	with zipfile.ZipFile(zip_path, "r") as z:
		z.extractall(tmp_dir)

	gdb_path = os.path.join(tmp_dir, gdb_name)
	gdf = gpd.read_file(gdb_path)
	return gdf

# Output directory (relative to this script's location)
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / ".." / ".." / "data" / "rana_boylii"
DATA_DIR = DATA_DIR.resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

print(f"Data directory: {DATA_DIR}")
print()


def skip_if_exists(path, label):
	"""Return True if file exists and should be skipped."""
	if path.exists() and path.stat().st_size > 1000:
		print(f"  [skip] {label} already exists ({path.stat().st_size // 1024} KB)")
		return True
	return False


# ---------------------------------------------------------------------------
# 1. California State Boundary
# ---------------------------------------------------------------------------
CA_OUT = DATA_DIR / "california.geojson"
print("1. California state boundary ...")

if not skip_if_exists(CA_OUT, "california.geojson"):
	# California Open Data — Census TIGER 2023, state boundary
	ca_zip_url = (
		"https://data.ca.gov/dataset/e212e397-1277-4df3-8c22-40721b095f33"
		"/resource/3db1e426-fb51-44f5-82d5-a54d7c6e188b/download/ca_state.zip"
	)
	try:
		ca = gpd.read_file(ca_zip_url)
		ca = ca.to_crs(epsg=4326)
		ca.to_file(CA_OUT, driver="GeoJSON")
		print(f"  Saved: {CA_OUT} ({CA_OUT.stat().st_size // 1024} KB)")
	except Exception as e:
		print(f"  Primary URL failed: {e}")
		print("  Trying Natural Earth fallback ...")
		# Natural Earth 1:10m states/provinces — filter to California
		ne_url = (
			"https://naciscdn.org/naturalearth/10m/cultural"
			"/ne_10m_admin_1_states_provinces.zip"
		)
		try:
			states = gpd.read_file(ne_url)
			ca = states[states["iso_3166_2"] == "US-CA"].copy()
			ca = ca.to_crs(epsg=4326)
			ca.to_file(CA_OUT, driver="GeoJSON")
			print(f"  Saved (Natural Earth fallback): {CA_OUT}")
		except Exception as e2:
			print(f"  Fallback also failed: {e2}")
			sys.exit(1)


# ---------------------------------------------------------------------------
# 2. Rana boylii Current Range — CDFW CWHR ds589
# ---------------------------------------------------------------------------
RANGE_OUT = DATA_DIR / "rana_boylii_range.geojson"
print("\n2. Rana boylii range (CDFW CWHR ds589) ...")

if not skip_if_exists(RANGE_OUT, "rana_boylii_range.geojson"):
	zip_url = "https://filelib.wildlife.ca.gov/Public/BDB/GIS/BIOS/Public_Datasets/500_599/ds589.zip"
	try:
		rng = download_zip_gdb(zip_url, "ds589.gdb", "ds589 (range)")
		rng = rng.to_crs(epsg=4326)
		rng.to_file(RANGE_OUT, driver="GeoJSON")
		print(f"  Saved: {RANGE_OUT} ({RANGE_OUT.stat().st_size // 1024} KB, {len(rng)} features)")
		print(f"  Columns: {list(rng.columns)}")
	except Exception as e:
		print(f"  Download failed: {e}")
		print("  Manually download ds589 from:")
		print("  https://data.cnra.ca.gov/dataset/foothill-yellow-legged-frog-range-cwhr-a043-ds589")


# ---------------------------------------------------------------------------
# 3. Rana boylii Clade Boundaries — CDFW ds2865
# ---------------------------------------------------------------------------
CLADES_OUT = DATA_DIR / "rana_boylii_clades.geojson"
print("\n3. Rana boylii clade boundaries (CDFW ds2865) ...")

if not skip_if_exists(CLADES_OUT, "rana_boylii_clades.geojson"):
	zip_url = "https://filelib.wildlife.ca.gov/Public/BDB/GIS/BIOS/Public_Datasets/2800_2899/ds2865.zip"
	try:
		clades = download_zip_gdb(zip_url, "ds2865.gdb", "ds2865 (clades)")
		clades = clades.to_crs(epsg=4326)
		clades.to_file(CLADES_OUT, driver="GeoJSON")
		print(f"  Saved: {CLADES_OUT} ({CLADES_OUT.stat().st_size // 1024} KB, {len(clades)} features)")
		print(f"  Columns: {list(clades.columns)}")
	except Exception as e:
		print(f"  Download failed: {e}")
		print("  Manually download ds2865 from:")
		print("  https://data-cdfw.opendata.arcgis.com/datasets/CDFW::foothill-yellow-legged-frog-clade-boundaries-ds2865")


# ---------------------------------------------------------------------------
# 4. EPA Level III Ecoregions — California subset
# ---------------------------------------------------------------------------
ECO_OUT = DATA_DIR / "ca_ecoregions.geojson"
print("\n4. EPA Level III Ecoregions (CA subset) ...")

if not skip_if_exists(ECO_OUT, "ca_ecoregions.geojson"):
	# EPA ArcGIS REST service — Level III Ecoregions (confirmed public endpoint)
	eco_url = (
		"https://geodata.epa.gov/arcgis/rest/services/ORD"
		"/USEPA_Ecoregions_Level_III_and_IV/MapServer/11/query"
		"?where=STATE_NAME+%3D+%27California%27"
		"&outFields=US_L3NAME%2CUS_L3CODE%2CSTATE_NAME"
		"&outSR=4326&f=geojson"
	)
	try:
		eco_all = gpd.read_file(eco_url)
		ca_eco = eco_all.to_crs(epsg=4326)
		# Dissolve by ecoregion name to merge state boundary splits
		ca_eco = ca_eco.dissolve(by="US_L3NAME", as_index=False)
		ca_eco.to_file(ECO_OUT, driver="GeoJSON")
		print(f"  Saved: {ECO_OUT} ({ECO_OUT.stat().st_size // 1024} KB, {len(ca_eco)} ecoregions)")
		print(f"  Ecoregions: {sorted(ca_eco['US_L3NAME'].tolist())}")
	except Exception as e:
		print(f"  EPA ArcGIS REST failed: {e}")
		# Fallback: try the bulk national Albers shapefile from EPA FTP
		fallback_url = (
			"https://www.epa.gov/sites/default/files/2022-06"
			"/us_eco_l3.zip"
		)
		try:
			eco_all = gpd.read_file(fallback_url)
			# Filter California — try multiple possible field names
			state_field = next(
				(c for c in eco_all.columns if "STATE" in c.upper()), None
			)
			if state_field:
				ca_eco = eco_all[eco_all[state_field].str.contains("California", na=False)].copy()
			else:
				# Clip by CA bounding box as last resort
				ca_eco = eco_all.cx[-124.5:-114.0, 32.5:42.0].copy()
			ca_eco = ca_eco.to_crs(epsg=4326)
			name_field = next((c for c in ca_eco.columns if "L3NAME" in c.upper()), ca_eco.columns[0])
			ca_eco = ca_eco.dissolve(by=name_field, as_index=False)
			ca_eco.to_file(ECO_OUT, driver="GeoJSON")
			print(f"  Saved (fallback): {ECO_OUT} ({len(ca_eco)} ecoregions)")
		except Exception as e2:
			print(f"  Fallback also failed: {e2}")
			print("  Manually download from:")
			print("  https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-state")


# ---------------------------------------------------------------------------
# 5. GBIF Occurrence Points — Rana boylii in California
# ---------------------------------------------------------------------------
OCC_OUT = DATA_DIR / "rana_boylii_occurrences.csv"
print("\n5. GBIF occurrence points ...")

if not skip_if_exists(OCC_OUT, "rana_boylii_occurrences.csv"):
	# GBIF taxon key for Rana boylii = 2426814
	GBIF_URL = "https://api.gbif.org/v1/occurrence/search"
	PARAMS = {
		"taxonKey": "2426814",
		"country": "US",
		"stateProvince": "California",
		"hasCoordinate": "true",
		"hasGeospatialIssue": "false",
		"limit": 300,
		"offset": 0,
	}

	records = []
	page = 0
	while True:
		PARAMS["offset"] = page * 300
		try:
			resp = requests.get(GBIF_URL, params=PARAMS, timeout=30)
			resp.raise_for_status()
			data = resp.json()
		except Exception as e:
			print(f"  GBIF request failed at offset {PARAMS['offset']}: {e}")
			break

		results = data.get("results", [])
		for r in results:
			lat = r.get("decimalLatitude")
			lon = r.get("decimalLongitude")
			if lat and lon:
				records.append({
					"lat": lat,
					"lon": lon,
					"year": r.get("year", ""),
					"month": r.get("month", ""),
					"recorded_by": r.get("recordedBy", ""),
					"institution": r.get("institutionCode", ""),
					"basis": r.get("basisOfRecord", ""),
					"occurrence_id": r.get("key", ""),
				})

		print(f"  Page {page + 1}: {len(results)} records (total so far: {len(records)})")

		if data.get("endOfRecords", True) or len(results) < 300:
			break
		page += 1

	if records:
		occ_df = pd.DataFrame(records)
		occ_df.to_csv(OCC_OUT, index=False)
		print(f"  Saved: {OCC_OUT} ({len(occ_df)} occurrence points)")
	else:
		print("  No records retrieved from GBIF.")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Download complete. Files in data/rana_boylii/:")
for f in sorted(DATA_DIR.iterdir()):
	size_kb = f.stat().st_size // 1024
	print(f"  {f.name:<40} {size_kb:>6} KB")

print("\nNext step: quarto render analysis/rana-boylii.qmd")
