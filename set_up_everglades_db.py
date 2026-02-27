import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'password',  # Change this
    'database': 'postgres'  # Connect to default database first
}

def create_database():
    """Create the GIS database and enable PostGIS"""
    conn = psycopg2.connect(**DB_PARAMS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Create database
    try:
        cur.execute("CREATE DATABASE everglades_gis;")
        print("✓ Database 'everglades_gis' created")
    except psycopg2.errors.DuplicateDatabase:
        print("! Database 'everglades_gis' already exists")
    
    cur.close()
    conn.close()
    
    # Connect to new database and enable PostGIS
    DB_PARAMS['database'] = 'everglades_gis'
    conn = psycopg2.connect(**DB_PARAMS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    print("✓ PostGIS extension enabled")
    
    cur.close()
    conn.close()

def create_tables():
    """Create the historical sites table with PostGIS geometry"""
    DB_PARAMS['database'] = 'everglades_gis'
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Create historical sites point table
    cur.execute("""
        DROP TABLE IF EXISTS historical_sites CASCADE;
        
        CREATE TABLE historical_sites (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            latitude DECIMAL(10, 7),
            longitude DECIMAL(10, 7),
            description TEXT,
            site_type VARCHAR(100),
            year_established INTEGER,
            significance_level VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            geom GEOMETRY(Point, 4326)
        );
        
        -- Create spatial index
        CREATE INDEX idx_historical_sites_geom ON historical_sites USING GIST(geom);
    """)
    
    print("✓ Table 'historical_sites' created with spatial index")
    
    # Create routes/paths table for lines
    cur.execute("""
        DROP TABLE IF EXISTS historical_routes CASCADE;
        
        CREATE TABLE historical_routes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            route_type VARCHAR(100),
            year_active INTEGER,
            length_km DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            geom GEOMETRY(LineString, 4326)
        );
        
        -- Create spatial index
        CREATE INDEX idx_historical_routes_geom ON historical_routes USING GIST(geom);
    """)
    
    print("✓ Table 'historical_routes' created with spatial index")
    
    conn.commit()
    cur.close()
    conn.close()

def insert_historical_sites():
    """Insert the historical sites data"""
    DB_PARAMS['database'] = 'everglades_gis'
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    sites_data = [
        # Your original 5 sites
        ('Ted Smallwood Store', 25.8134, -81.3626, 
         'Historic trading post; central hub for locals, outlaws, and early trade.',
         'Trading Post', 1906, 'High'),
        
        ('Everglades City Center', 25.8582, -81.3861,
         'Epicenter of "Operation Everglades" (1983); the town where ~80% of the male population was arrested.',
         'Town Center', 1873, 'High'),
        
        ('Watson\'s Place (Chatham Bend)', 25.6854, -81.2937,
         'Site of the Ed Watson homestead; represents the area\'s deep history of lawlessness and isolation.',
         'Homestead', 1890, 'High'),
        
        ('Chokoloskee Island', 25.8143, -81.3601,
         'The primary island community connected to the mainland; home to Totch Brown.',
         'Settlement', 1874, 'High'),
        
        ('Fakahatchee Strand State Preserve', 25.9686, -81.3060,
         'Historic logging area often used for clandestine airstrips due to its remote, linear features.',
         'Preserve', 1974, 'Medium'),
        
        # Additional historical sites to expand your dataset
        ('Smallwood\'s Dock', 25.8138, -81.3623,
         'Original dock where supplies arrived by boat; critical supply line for the island.',
         'Dock', 1906, 'Medium'),
        
        ('Chevelier Bay', 25.7921, -81.3498,
         'Historic fishing grounds and smuggling route during Prohibition era.',
         'Bay', 1920, 'Medium'),
        
        ('Lopez River', 25.7456, -81.3112,
         'Remote waterway used for rum-running and later marijuana smuggling operations.',
         'Waterway', 1920, 'Medium'),
        
        ('Turner River', 25.8901, -81.3445,
         'Historic canal and transportation route through the mangroves.',
         'Waterway', 1930, 'Low'),
        
        ('Halfway Creek', 25.7823, -81.3289,
         'Midpoint stop for traders between Everglades City and the outer islands.',
         'Creek', 1910, 'Low'),
        
        ('Indian Key Pass', 25.7634, -81.3778,
         'Historic Calusa Indian site and later smuggling route.',
         'Pass', 1500, 'High'),
        
        ('Pavilion Key', 25.6912, -81.4523,
         'Remote island used as a camp by fishermen and later as a drop point.',
         'Island', 1900, 'Low'),
        
        ('Rabbit Key', 25.7234, -81.4012,
         'Small key used for temporary camps and clandestine meetings.',
         'Island', 1920, 'Low'),
        
        ('Mormon Key', 25.6523, -81.3890,
         'Historic farming attempt site; represents failed settlement efforts.',
         'Island', 1880, 'Medium'),
        
        ('Lostmans River', 25.5912, -81.2634,
         'Extremely remote waterway; site of Ed Watson murders and ongoing lawlessness.',
         'Waterway', 1890, 'High'),
        
        ('Shark River', 25.3456, -81.1234,
         'Major waterway through the Everglades; historic Seminole route.',
         'Waterway', 1800, 'Medium'),
        
        ('Flamingo', 25.1390, -80.9281,
         'Remote outpost at the southern tip; historic fishing village.',
         'Settlement', 1893, 'Medium'),
        
        ('Cape Sable', 25.1245, -81.1012,
         'Southernmost point; historic lighthouse and remote settlement.',
         'Cape', 1838, 'High'),
        
        ('Whitewater Bay', 25.2134, -81.0456,
         'Large shallow bay; historic fishing grounds and smuggling route.',
         'Bay', 1900, 'Low'),
        
        ('Oyster Bay', 25.7812, -81.2945,
         'Historic oyster harvesting area; important food source.',
         'Bay', 1890, 'Low'),
    ]
    
    for site in sites_data:
        cur.execute("""
            INSERT INTO historical_sites 
            (name, latitude, longitude, description, site_type, year_established, significance_level, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (site[0], site[1], site[2], site[3], site[4], site[5], site[6], site[2], site[1]))
    
    conn.commit()
    print(f"✓ Inserted {len(sites_data)} historical sites")
    
    cur.close()
    conn.close()

def insert_historical_routes():
    """Insert some historical routes/paths"""
    DB_PARAMS['database'] = 'everglades_gis'
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    routes_data = [
        # Route from Everglades City to Ted Smallwood Store
        ('Barron River Route', 
         'Main water route from Everglades City to Chokoloskee via Barron River',
         'Water Route', 1900,
         [(-81.3861, 25.8582), (-81.3745, 25.8456), (-81.3626, 25.8134)]),
        
        # Route to Watson's Place
        ('Chatham River Route',
         'Water route from Chokoloskee to Watson\'s Place at Chatham Bend',
         'Water Route', 1890,
         [(-81.3601, 25.8143), (-81.3245, 25.7567), (-81.2937, 25.6854)]),
        
        # Smuggling route through Lopez River
        ('Lopez River Smuggling Route',
         'Historic rum-running and later marijuana smuggling route',
         'Smuggling Route', 1920,
         [(-81.3498, 25.7921), (-81.3289, 25.7823), (-81.3112, 25.7456)]),
        
        # Route to Cape Sable
        ('Wilderness Waterway (North Section)',
         'Historic route through the Ten Thousand Islands to Flamingo',
         'Water Route', 1900,
         [(-81.3861, 25.8582), (-81.2500, 25.5000), (-81.1500, 25.3000), (-80.9281, 25.1390)]),
    ]
    
    for route in routes_data:
        # Convert coordinate pairs to WKT LineString
        coords_wkt = ', '.join([f'{lon} {lat}' for lon, lat in route[4]])
        linestring_wkt = f'LINESTRING({coords_wkt})'
        
        cur.execute("""
            INSERT INTO historical_routes 
            (name, description, route_type, year_active, geom)
            VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326))
        """, (route[0], route[1], route[2], route[3], linestring_wkt))
    
    # Calculate route lengths
    cur.execute("""
        UPDATE historical_routes
        SET length_km = ST_Length(ST_Transform(geom, 3857)) / 1000;
    """)
    
    conn.commit()
    print(f"✓ Inserted {len(routes_data)} historical routes")
    
    cur.close()
    conn.close()

def verify_data():
    """Verify the data was inserted correctly"""
    DB_PARAMS['database'] = 'everglades_gis'
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM historical_sites;")
    site_count = cur.fetchone()[0]
    print(f"\n✓ Total historical sites: {site_count}")
    
    cur.execute("SELECT COUNT(*) FROM historical_routes;")
    route_count = cur.fetchone()[0]
    print(f"✓ Total historical routes: {route_count}")
    
    print("\n--- Sample Sites ---")
    cur.execute("""
        SELECT name, latitude, longitude, site_type 
        FROM historical_sites 
        LIMIT 5;
    """)
    for row in cur.fetchall():
        print(f"  • {row[0]} ({row[3]}): {row[1]}, {row[2]}")
    
    print("\n--- Sample Routes ---")
    cur.execute("""
        SELECT name, route_type, length_km 
        FROM historical_routes;
    """)
    for row in cur.fetchall():
        print(f"  • {row[0]} ({row[1]}): {row[2]:.2f} km")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("Setting up Everglades Historical GIS Database\n")
    print("=" * 50)
    
    create_database()
    create_tables()
    insert_historical_sites()
    insert_historical_routes()
    verify_data()
    
    print("\n" + "=" * 50)
    print("✓ Database setup complete!")
    print("\nConnection details:")
    print("  Database: everglades_gis")
    print("  Tables: historical_sites, historical_routes")

