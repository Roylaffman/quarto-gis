"""
Database connection helpers for PostGIS → GeoDataFrame workflows.

Usage:
    from db_connection import get_connection, query_to_dataframe, query_to_geodataframe

Credentials are read from a .env file in the research/ directory.
Copy .env.example to .env and fill in your values.
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import geopandas as gpd

load_dotenv()

def get_connection():
    """Return a psycopg2 connection using .env credentials."""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DBNAME"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
    )


def query_to_dataframe(query, params=None):
    """Run a SQL query and return results as a Pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df


def query_to_geodataframe(query, geom_col="geom", crs=4326, params=None):
    """Run a SQL query and return results as a GeoPandas GeoDataFrame.

    The query should return a geometry column (PostGIS native).
    gpd.read_postgis handles the WKB → Shapely conversion automatically.
    """
    conn = get_connection()
    try:
        gdf = gpd.read_postgis(query, conn, geom_col=geom_col, crs=crs, params=params)
    finally:
        conn.close()
    return gdf
