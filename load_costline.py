# load_coastline.py
import psycopg2

def load_coastline_sql():
    """Load the Florida coastline SQL file"""
    DB_PARAMS = {
        'host': 'localhost',
        'user': 'postgres',
        'password': 'password',
        'database': 'everglades_gis'
    }
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Read the SQL file and fix NUMERIC precision
    # The export used NUMERIC(33,31) which only allows 2 digits before the decimal,
    # but values like feature_id=4128 need more room. Widen to NUMERIC.
    with open(r'C:\Users\royla\Documents\FL GIS Data\1978_FL_coastline.sql', 'r') as f:
        sql_content = f.read()

    sql_content = sql_content.replace('NUMERIC(33,31)', 'NUMERIC')
    cur.execute(sql_content)

    conn.commit()
    print("Florida coastline data loaded")
    
    # Verify
    cur.execute("""
        SELECT COUNT(*), GeometryType(wkb_geometry)
        FROM "1978_fl_coastline"
        GROUP BY GeometryType(wkb_geometry);
    """)
    
    for row in cur.fetchall():
        print(f"  • {row[0]} features of type {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    load_coastline_sql()