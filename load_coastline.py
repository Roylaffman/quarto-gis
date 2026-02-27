# load_coastline.py
import psycopg2

def load_coastline_sql():
    """Load the Florida coastline SQL file"""
    DB_PARAMS = {
        'host': 'localhost',
        'user': 'postgres',
        'password': 'password',  # Change this to your actual password
        'database': 'everglades_gis'
    }
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Read and execute the SQL file
    with open(r'C:\Users\royla\Documents\FL GIS Data\1978_FL_coastline.sql', 'r') as f:
        sql_content = f.read()
        cur.execute(sql_content)
    
    conn.commit()
    print("✓ Florida coastline data loaded")
    
    # Verify
    cur.execute("""
        SELECT COUNT(*), GeometryType(geom) 
        FROM florida_coastline_1978 
        GROUP BY GeometryType(geom);
    """)
    
    for row in cur.fetchall():
        print(f"  • {row[0]} features of type {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    load_coastline_sql()