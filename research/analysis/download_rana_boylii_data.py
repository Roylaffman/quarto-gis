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
import json
import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path

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
	# ArcGIS FeatureServer GeoJSON export from California Natural Resources Agency
	arcgis_url = (
		"https://services.arcgis.com/I0GHkPaHBmjXBMpO/arcgis/rest/services"
		"/CWHR_Range_Maps/FeatureServer/0/query"
		"?where=CWHR_ID+%3D+%27A043%27"
		"&outFields=CWHR_ID%2CCOMMON_NAME%2CSCI_NAME%2CSOURCE%2CDS_ID"
		"&outSR=4326&f=geojson"
	)
	try:
		rng = gpd.read_file(arcgis_url)
		rng = rng.to_crs(epsg=4326)
		rng.to_file(RANGE_OUT, driver="GeoJSON")
		print(f"  Saved: {RANGE_OUT} ({RANGE_OUT.stat().st_size // 1024} KB, {len(rng)} features)")
	except Exception as e:
		print(f"  ArcGIS endpoint failed: {e}")
		# Fallback: CNRA CKAN direct GeoJSON download
		fallback_url = (
			"https://opendata.arcgis.com/datasets"
			"/dfb1bce58d79400aa8ea747906d2b32f_0.geojson"
		)
		try:
			rng = gpd.read_file(fallback_url)
			rng = rng.to_crs(epsg=4326)
			rng.to_file(RANGE_OUT, driver="GeoJSON")
			print(f"  Saved (fallback): {RANGE_OUT} ({len(rng)} features)")
		except Exception as e2:
			print(f"  Fallback also failed: {e2}")
			# Create a placeholder so the script doesn't break the qmd
			print("  Creating placeholder — manually download ds589 from:")
			print("  https://data.cnra.ca.gov/dataset/foothill-yellow-legged-frog-range-cwhr-a043-ds589")


# ---------------------------------------------------------------------------
# 3. Rana boylii Clade Boundaries — CDFW ds2865
# ---------------------------------------------------------------------------
CLADES_OUT = DATA_DIR / "rana_boylii_clades.geojson"
print("\n3. Rana boylii clade boundaries (CDFW ds2865) ...")

if not skip_if_exists(CLADES_OUT, "rana_boylii_clades.geojson"):
	# ArcGIS Hub GeoJSON export for ds2865
	clades_url = (
		"https://opendata.arcgis.com/datasets"
		"/dfb1bce58d79400aa8ea747906d2b32f_1.geojson"
	)
	try:
		clades = gpd.read_file(clades_url)
		clades = clades.to_crs(epsg=4326)
		clades.to_file(CLADES_OUT, driver="GeoJSON")
		print(f"  Saved: {CLADES_OUT} ({CLADES_OUT.stat().st_size // 1024} KB, {len(clades)} features)")
		print(f"  Columns: {list(clades.columns)}")
	except Exception as e:
		print(f"  Primary URL failed: {e}")
		# Fallback: CDFW ArcGIS Open Data portal
		fallback = (
			"https://gis.data.ca.gov/datasets"
			"/CDFW::foothill-yellow-legged-frog-clade-boundaries-ds2865_0.geojson"
		)
		try:
			clades = gpd.read_file(fallback)
			clades = clades.to_crs(epsg=4326)
			clades.to_file(CLADES_OUT, driver="GeoJSON")
			print(f"  Saved (fallback): {CLADES_OUT} ({len(clades)} features)")
		except Exception as e2:
			print(f"  Fallback also failed: {e2}")
			print("  Manually download ds2865 from:")
			print("  https://data-cdfw.opendata.arcgis.com/datasets/CDFW::foothill-yellow-legged-frog-clade-boundaries-ds2865")


# ---------------------------------------------------------------------------
# 4. EPA Level III Ecoregions — California subset
# ---------------------------------------------------------------------------
ECO_OUT = DATA_DIR / "ca_ecoregions.geojson"
print("\n4. EPA Level III Ecoregions (CA subset) ...")

if not skip_if_exists(ECO_OUT, "ca_ecoregions.geojson"):
	# EPA S3 bucket — national Level III ecoregions with state boundaries
	eco_url = (
		"https://dmap-prod-oms-edc.s3.us-east-1.amazonaws.com"
		"/ORD/Ecoregions/us_eco_l3/us_eco_l3_state_boundaries.zip"
	)
	try:
		eco_all = gpd.read_file(eco_url)
		# Filter to California
		ca_eco = eco_all[eco_all["STATE_NAME"] == "California"].copy()
		ca_eco = ca_eco.to_crs(epsg=4326)
		# Dissolve by ecoregion to merge state boundary splits
		ca_eco = ca_eco.dissolve(by="US_L3NAME", as_index=False)
		ca_eco.to_file(ECO_OUT, driver="GeoJSON")
		print(f"  Saved: {ECO_OUT} ({ECO_OUT.stat().st_size // 1024} KB, {len(ca_eco)} ecoregions)")
		print(f"  Ecoregions: {sorted(ca_eco['US_L3NAME'].tolist())}")
	except Exception as e:
		print(f"  EPA S3 download failed: {e}")
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
