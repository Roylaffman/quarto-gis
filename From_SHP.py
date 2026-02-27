# load_coastline_shapefile.py
import geopandas as gpd
from sqlalchemy import create_engine

def load_shapefile():
    """Load shapefile directly into PostGIS"""
    
    # Database connection string
    db_connection = "postgresql://postgres:password@localhost:5432/everglades_gis"
    
    print("Reading shapefile...")
    # Read the shapefile
    gdf = gpd.read_file(r'C:\Users\royla\Documents\FL GIS Data\1978_FL_coastline.shp')
    
    print(f"✓ Loaded {len(gdf)} features")
    print(f"  Geometry type: {gdf.geom_type.unique()}")
    print(f"  CRS: {gdf.crs}")
    print(f"  Columns: {list(gdf.columns)}")
    
    # Ensure it's in WGS84 (EPSG:4326)
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        print(f"  Reprojecting from {gdf.crs.to_epsg()} to 4326...")
        gdf = gdf.to_crs(epsg=4326)
    
    # Create database engine
    engine = create_engine(db_connection)
    
    print("\nLoading into PostgreSQL...")
    # Load into PostGIS
    gdf.to_postgis(
        name='florida_coastline_1978',
        con=engine,
        if_exists='replace',
        index=True,
        index_label='id'
    )
    
    print("✓ Florida coastline loaded into PostGIS")
    
    # Verify
    import pandas as pd
    query = "SELECT COUNT(*) as count FROM florida_coastline_1978;"
    result = pd.read_sql(query, engine)
    print(f"\n✓ Verified: {result['count'][0]} features in database")
    
    engine.dispose()

if __name__ == "__main__":
    try:
        load_shapefile()
    except ImportError as e:
        print("✗ Missing required packages. Install with:")
        print("  pip install geopandas sqlalchemy psycopg2-binary")
    except Exception as e:
        print(f"✗ Error: {e}")
