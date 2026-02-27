#!/usr/bin/env python3
"""
Roman Roads GIS Data Harvester
===============================
Fetches route segment and Pleiades place data from the Itiner-e digital atlas
of ancient Roman roads (https://itiner-e.org) and loads them into a PostGIS
database as line and point feature tables.

Data source: Brughmans, T., de Soto, P., Pažout, A. and Bjerregaard
Vahlstrup, P. (2024) Itiner-e: the digital atlas of ancient roads.
Licensed CC BY 4.0.

Usage:
    # 1. Fetch the nightly bulk NDJSON export (recommended for full dataset)
    python roman_roads_harvester.py --mode bulk --output ./data

    # 2. Fetch individual segments by ID
    python roman_roads_harvester.py --mode segments --ids 31702 31703 31704

    # 3. Fetch individual segments and load into PostGIS
    python roman_roads_harvester.py --mode segments --ids 31702 --load-db

    # 4. Load previously-downloaded data into PostGIS
    python roman_roads_harvester.py --mode load --input ./data

    # 5. Export local files to GeoJSON / GeoPackage / Shapefile
    python roman_roads_harvester.py --mode export --input ./data --format gpkg

Requirements:
    pip install requests geopandas sqlalchemy geoalchemy2 psycopg2-binary shapely

PostGIS connection (set env vars or use --db-url):
    export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=secret PGDATABASE=roman_roads
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("roman_roads")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://www.itiner-e.org"
SEGMENT_JSON_URL = BASE_URL + "/route-segment/{segment_id}/json"
BULK_DOWNLOAD_URL = BASE_URL + "/route-segments/download"
DEFAULT_OUTPUT_DIR = Path("./data/roman_roads")
REQUEST_DELAY = 0.5  # seconds between individual segment requests (be polite)
DEFAULT_CRS = "EPSG:4326"  # WGS 84 — native CRS of Itiner-e data

# PostGIS table names
LINES_TABLE = "roman_road_segments"
POINTS_TABLE = "roman_road_places"

# ---------------------------------------------------------------------------
# HTTP Session with retry
# ---------------------------------------------------------------------------

def _build_session() -> requests.Session:
    """Build a requests Session with automatic retries and timeout."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": "RomanRoadsHarvester/1.0 (GIS research; contact@example.com)",
        "Accept": "application/json",
    })
    return session


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RoadSegment:
    """A single Itiner-e route segment (GeoJSON LineString)."""
    segment_id: int
    name: str
    road_type: str
    segment_certainty: str
    construction_period: Optional[str]
    itinerary: Optional[str]
    author: Optional[str]
    bibliography: Optional[str]
    description: Optional[str]
    length_m: Optional[float]
    lower_date: Optional[int]
    upper_date: Optional[int]
    coordinates: list  # [[lon, lat], ...] — native GeoJSON order
    pleiades_places: list = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict) -> "RoadSegment":
        props = data.get("properties", {})
        geom = data.get("geometry", {})
        coords = geom.get("coordinates", [])

        places = []
        for p in data.get("pleiadesPlaces", []):
            pp = p.get("properties", {})
            pg = p.get("geometry", {})
            places.append(PleiadesPlace(
                pleiades_id=p.get("id"),
                name=pp.get("name"),
                place_type=pp.get("type"),
                start_year=pp.get("startYear"),
                end_year=pp.get("endYear"),
                url=pp.get("url"),
                lon=pg.get("coordinates", [None, None])[0],
                lat=pg.get("coordinates", [None, None])[1],
            ))

        return cls(
            segment_id=data.get("id") or props.get("_id"),
            name=props.get("name", "Unknown"),
            road_type=props.get("type", "Unknown"),
            segment_certainty=props.get("segmentCertainty", "Unknown"),
            construction_period=props.get("constructionPeriod"),
            itinerary=props.get("itinerary"),
            author=props.get("author"),
            bibliography=props.get("bibliography"),
            description=props.get("description"),
            length_m=props.get("lengthGeo"),
            lower_date=props.get("lowerDate"),
            upper_date=props.get("upperDate"),
            coordinates=coords,
            pleiades_places=places,
        )


@dataclass
class PleiadesPlace:
    """A Pleiades place (point) linked to a road segment."""
    pleiades_id: int
    name: str
    place_type: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    url: Optional[str]
    lon: Optional[float]
    lat: Optional[float]


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_segment(session: requests.Session, segment_id: int) -> Optional[RoadSegment]:
    """Fetch a single route segment by ID."""
    url = SEGMENT_JSON_URL.format(segment_id=segment_id)
    log.info("Fetching segment %d ...", segment_id)
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        seg = RoadSegment.from_json(data)
        log.info(
            "  ✓ %s — %d coords, %d places",
            seg.name, len(seg.coordinates), len(seg.pleiades_places),
        )
        return seg
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            log.warning("  Segment %d not found (404), skipping.", segment_id)
        else:
            log.error("  HTTP error fetching segment %d: %s", segment_id, e)
    except Exception as e:
        log.error("  Error fetching segment %d: %s", segment_id, e)
    return None


def fetch_segments(segment_ids: list[int], delay: float = REQUEST_DELAY) -> list[RoadSegment]:
    """Fetch multiple segments by ID with polite delay."""
    session = _build_session()
    segments = []
    for i, sid in enumerate(segment_ids):
        seg = fetch_segment(session, sid)
        if seg:
            segments.append(seg)
        if i < len(segment_ids) - 1:
            time.sleep(delay)
    log.info("Fetched %d / %d segments successfully.", len(segments), len(segment_ids))
    return segments


def download_bulk_export(output_dir: Path) -> Path:
    """Download the nightly NDJSON bulk export of all route segments."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "itinere_all_segments.ndjson"

    log.info("Downloading bulk export from %s ...", BULK_DOWNLOAD_URL)
    session = _build_session()
    resp = session.get(BULK_DOWNLOAD_URL, timeout=300, stream=True)
    resp.raise_for_status()

    total = 0
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            f.write(chunk)
            total += len(chunk)
    log.info("  ✓ Downloaded %.2f MB → %s", total / 1e6, out_path)
    return out_path


def parse_ndjson(filepath: Path) -> list[RoadSegment]:
    """Parse an NDJSON file into RoadSegment objects."""
    segments = []
    errors = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                segments.append(RoadSegment.from_json(data))
            except Exception as e:
                errors += 1
                if errors <= 10:
                    log.warning("  Parse error on line %d: %s", lineno, e)
    log.info("Parsed %d segments (%d errors) from %s", len(segments), errors, filepath.name)
    return segments


# ---------------------------------------------------------------------------
# Save to local GeoJSON files
# ---------------------------------------------------------------------------

def save_geojson(segments: list[RoadSegment], output_dir: Path):
    """Save segments and places as GeoJSON files (no geopandas needed)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Lines ---
    line_features = []
    for seg in segments:
        feat = {
            "type": "Feature",
            "properties": {
                "segment_id": seg.segment_id,
                "name": seg.name,
                "road_type": seg.road_type,
                "segment_certainty": seg.segment_certainty,
                "construction_period": seg.construction_period,
                "itinerary": seg.itinerary,
                "author": seg.author,
                "bibliography": seg.bibliography,
                "description": seg.description,
                "length_m": seg.length_m,
                "lower_date": seg.lower_date,
                "upper_date": seg.upper_date,
                "source_url": f"{BASE_URL}/route-segment/{seg.segment_id}",
            },
            "geometry": {
                "type": "LineString",
                "coordinates": seg.coordinates,
            },
        }
        line_features.append(feat)

    lines_path = output_dir / "roman_road_segments.geojson"
    with open(lines_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": line_features}, f)
    log.info("Saved %d line features → %s", len(line_features), lines_path)

    # --- Points (deduplicated) ---
    seen_ids = set()
    point_features = []
    for seg in segments:
        for pl in seg.pleiades_places:
            if pl.pleiades_id in seen_ids or pl.lon is None or pl.lat is None:
                continue
            seen_ids.add(pl.pleiades_id)
            feat = {
                "type": "Feature",
                "properties": {
                    "pleiades_id": pl.pleiades_id,
                    "name": pl.name,
                    "place_type": pl.place_type,
                    "start_year": pl.start_year,
                    "end_year": pl.end_year,
                    "url": pl.url,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [pl.lon, pl.lat],
                },
            }
            point_features.append(feat)

    points_path = output_dir / "roman_road_places.geojson"
    with open(points_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": point_features}, f)
    log.info("Saved %d point features → %s", len(point_features), points_path)

    return lines_path, points_path


# ---------------------------------------------------------------------------
# Export to GeoPackage / Shapefile (requires geopandas)
# ---------------------------------------------------------------------------

def export_with_geopandas(segments: list[RoadSegment], output_dir: Path, fmt: str = "gpkg"):
    """Export to GeoPackage, Shapefile, or other OGR-supported format."""
    try:
        import geopandas as gpd
        from shapely.geometry import LineString, Point
    except ImportError:
        log.error("geopandas and shapely are required for export. "
                  "Install with: pip install geopandas shapely")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Lines GeoDataFrame ---
    line_records = []
    for seg in segments:
        if len(seg.coordinates) < 2:
            continue
        line_records.append({
            "segment_id": seg.segment_id,
            "name": seg.name,
            "road_type": seg.road_type,
            "segment_certainty": seg.segment_certainty,
            "construction_period": seg.construction_period,
            "itinerary": seg.itinerary,
            "author": seg.author,
            "bibliography": seg.bibliography,
            "description": seg.description,
            "length_m": seg.length_m,
            "lower_date": seg.lower_date,
            "upper_date": seg.upper_date,
            "source_url": f"{BASE_URL}/route-segment/{seg.segment_id}",
            "geometry": LineString(seg.coordinates),
        })
    gdf_lines = gpd.GeoDataFrame(line_records, crs=DEFAULT_CRS)

    # --- Points GeoDataFrame (deduplicated) ---
    seen_ids = set()
    point_records = []
    for seg in segments:
        for pl in seg.pleiades_places:
            if pl.pleiades_id in seen_ids or pl.lon is None or pl.lat is None:
                continue
            seen_ids.add(pl.pleiades_id)
            point_records.append({
                "pleiades_id": pl.pleiades_id,
                "name": pl.name,
                "place_type": pl.place_type,
                "start_year": pl.start_year,
                "end_year": pl.end_year,
                "url": pl.url,
                "geometry": Point(pl.lon, pl.lat),
            })
    gdf_points = gpd.GeoDataFrame(point_records, crs=DEFAULT_CRS)

    ext_map = {"gpkg": ".gpkg", "shp": ".shp", "geojson": ".geojson"}
    driver_map = {"gpkg": "GPKG", "shp": "ESRI Shapefile", "geojson": "GeoJSON"}
    ext = ext_map.get(fmt, ".gpkg")
    driver = driver_map.get(fmt, "GPKG")

    lines_out = output_dir / f"roman_road_segments{ext}"
    points_out = output_dir / f"roman_road_places{ext}"

    if fmt == "gpkg":
        # Both layers in one GeoPackage
        gdf_lines.to_file(lines_out, layer=LINES_TABLE, driver=driver)
        gdf_points.to_file(lines_out, layer=POINTS_TABLE, driver=driver)
        log.info("Exported %d lines + %d points → %s", len(gdf_lines), len(gdf_points), lines_out)
    else:
        gdf_lines.to_file(lines_out, driver=driver)
        gdf_points.to_file(points_out, driver=driver)
        log.info("Exported lines → %s", lines_out)
        log.info("Exported points → %s", points_out)

    return gdf_lines, gdf_points


# ---------------------------------------------------------------------------
# PostGIS Loader
# ---------------------------------------------------------------------------

def get_db_url(cli_url: Optional[str] = None) -> str:
    """Build a SQLAlchemy connection URL from env vars or CLI arg."""
    if cli_url:
        return cli_url
    host = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", "5432")
    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD", "")
    dbname = os.environ.get("PGDATABASE", "roman_roads")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def load_to_postgis(
    segments: list[RoadSegment],
    db_url: str,
    if_exists: str = "replace",
    schema: str = "public",
):
    """Load road segments (lines) and places (points) into PostGIS tables."""
    try:
        import geopandas as gpd
        from shapely.geometry import LineString, Point
        from sqlalchemy import create_engine, text
    except ImportError:
        log.error(
            "Required packages: geopandas, shapely, sqlalchemy, geoalchemy2, psycopg2-binary. "
            "Install with: pip install geopandas shapely sqlalchemy geoalchemy2 psycopg2-binary"
        )
        return

    engine = create_engine(db_url)

    # Ensure PostGIS extension exists
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    log.info("PostGIS extension confirmed.")

    # --- Build GeoDataFrames ---
    line_records = []
    for seg in segments:
        if len(seg.coordinates) < 2:
            continue
        line_records.append({
            "segment_id": seg.segment_id,
            "name": seg.name,
            "road_type": seg.road_type,
            "segment_certainty": seg.segment_certainty,
            "construction_period": seg.construction_period,
            "itinerary": seg.itinerary,
            "author": seg.author,
            "bibliography": seg.bibliography,
            "description": seg.description,
            "length_m": seg.length_m,
            "lower_date": seg.lower_date,
            "upper_date": seg.upper_date,
            "source_url": f"{BASE_URL}/route-segment/{seg.segment_id}",
            "geometry": LineString(seg.coordinates),
        })
    gdf_lines = gpd.GeoDataFrame(line_records, crs=DEFAULT_CRS)

    seen_ids = set()
    point_records = []
    for seg in segments:
        for pl in seg.pleiades_places:
            if pl.pleiades_id in seen_ids or pl.lon is None or pl.lat is None:
                continue
            seen_ids.add(pl.pleiades_id)
            point_records.append({
                "pleiades_id": pl.pleiades_id,
                "name": pl.name,
                "place_type": pl.place_type,
                "start_year": pl.start_year,
                "end_year": pl.end_year,
                "url": pl.url,
                "geometry": Point(pl.lon, pl.lat),
            })
    gdf_points = gpd.GeoDataFrame(point_records, crs=DEFAULT_CRS)

    # --- Write to PostGIS ---
    if not gdf_lines.empty:
        gdf_lines.to_postgis(
            LINES_TABLE, engine, schema=schema,
            if_exists=if_exists, index=False,
        )
        log.info("Loaded %d road segments → %s.%s", len(gdf_lines), schema, LINES_TABLE)

    if not gdf_points.empty:
        gdf_points.to_postgis(
            POINTS_TABLE, engine, schema=schema,
            if_exists=if_exists, index=False,
        )
        log.info("Loaded %d places → %s.%s", len(gdf_points), schema, POINTS_TABLE)

    # --- Create spatial indexes ---
    with engine.connect() as conn:
        for table in [LINES_TABLE, POINTS_TABLE]:
            idx_name = f"idx_{table}_geom"
            conn.execute(text(f"DROP INDEX IF EXISTS {schema}.{idx_name};"))
            conn.execute(text(
                f"CREATE INDEX {idx_name} ON {schema}.{table} USING GIST (geometry);"
            ))
        conn.commit()
    log.info("Spatial indexes created.")

    # --- Print verification queries ---
    log.info("--- Verify with these psql queries ---")
    log.info("  SELECT count(*), road_type, segment_certainty "
             "FROM %s GROUP BY road_type, segment_certainty;", LINES_TABLE)
    log.info("  SELECT count(*), place_type FROM %s GROUP BY place_type;", POINTS_TABLE)
    log.info("  SELECT name, ST_Length(geometry::geography) AS length_m "
             "FROM %s ORDER BY length_m DESC LIMIT 10;", LINES_TABLE)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Roman Roads GIS Data Harvester — fetch Itiner-e data and load into PostGIS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--mode", choices=["bulk", "segments", "load", "export"],
        required=True,
        help=(
            "bulk: download nightly NDJSON export; "
            "segments: fetch individual IDs; "
            "load: load local files into PostGIS; "
            "export: convert local files to gpkg/shp/geojson"
        ),
    )
    p.add_argument("--ids", type=int, nargs="+", help="Segment IDs to fetch (for --mode segments)")
    p.add_argument("--id-range", type=int, nargs=2, metavar=("START", "END"),
                   help="Inclusive range of segment IDs to fetch")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    p.add_argument("--input", type=Path, help="Input directory or NDJSON file (for load/export)")
    p.add_argument("--format", choices=["gpkg", "shp", "geojson"], default="gpkg",
                   help="Export format (default: gpkg)")
    p.add_argument("--load-db", action="store_true", help="Also load fetched data into PostGIS")
    p.add_argument("--db-url", type=str, help="SQLAlchemy PostGIS URL (overrides env vars)")
    p.add_argument("--db-if-exists", choices=["replace", "append", "fail"],
                   default="replace", help="Behavior when table exists")
    p.add_argument("--schema", default="public", help="PostGIS schema")
    p.add_argument("--delay", type=float, default=REQUEST_DELAY,
                   help="Seconds between individual API requests")
    p.add_argument("--verbose", "-v", action="store_true")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    segments: list[RoadSegment] = []

    # ----- MODE: bulk -----
    if args.mode == "bulk":
        ndjson_path = download_bulk_export(args.output)
        segments = parse_ndjson(ndjson_path)
        save_geojson(segments, args.output)

    # ----- MODE: segments -----
    elif args.mode == "segments":
        ids = list(args.ids or [])
        if args.id_range:
            ids.extend(range(args.id_range[0], args.id_range[1] + 1))
        if not ids:
            parser.error("--mode segments requires --ids or --id-range")
        segments = fetch_segments(ids, delay=args.delay)
        save_geojson(segments, args.output)

    # ----- MODE: load -----
    elif args.mode == "load":
        input_path = args.input or args.output
        ndjson_files = sorted(input_path.glob("*.ndjson")) if input_path.is_dir() else [input_path]
        for f in ndjson_files:
            segments.extend(parse_ndjson(f))
        if not segments:
            log.error("No segments found in %s", input_path)
            sys.exit(1)
        db_url = get_db_url(args.db_url)
        load_to_postgis(segments, db_url, if_exists=args.db_if_exists, schema=args.schema)
        return  # skip the --load-db check below

    # ----- MODE: export -----
    elif args.mode == "export":
        input_path = args.input or args.output
        ndjson_files = sorted(input_path.glob("*.ndjson")) if input_path.is_dir() else [input_path]
        for f in ndjson_files:
            segments.extend(parse_ndjson(f))
        if not segments:
            log.error("No segments found in %s", input_path)
            sys.exit(1)
        export_with_geopandas(segments, args.output, fmt=args.format)
        return

    # Optionally load into PostGIS after fetching
    if args.load_db and segments:
        db_url = get_db_url(args.db_url)
        load_to_postgis(segments, db_url, if_exists=args.db_if_exists, schema=args.schema)

    log.info("Done. %d total segments processed.", len(segments))


if __name__ == "__main__":
    main()
