import json
import csv
import sys
import os
from pymongo import MongoClient

# Add parent directory to path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = 'museum_db' 

def normalize_name(name):
    if not name:
        return ""
    # Remove common prefixes/suffixes and punctuation for better matching
    clean = name.lower().strip()
    clean = clean.replace("'", "").replace(".", "").replace(",", "").replace("-", " ")
    clean = clean.replace("museum", "").strip() # Remove 'museum' word to match core name
    return clean

def reseed_museums():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'final_museums.csv')
    json_path = os.path.join(base_dir, 'museum_data.json')
    
    # 1. Load Coordinates from CSV
    coords_map = {}
    print(f"Reading CSV from {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Name')
            lat = row.get('Latitude')
            lng = row.get('Longitude')
            
            if name and lat and lng:
                try:
                    # Validate they are numbers and looks like valid lat/lng
                    f_lat = float(lat)
                    f_lng = float(lng)
                    if not (-90 <= f_lat <= 90) or not (-180 <= f_lng <= 180):
                        continue
                        
                    # Store both exact and normalized text
                    norm_name = normalize_name(name)
                    if norm_name:
                        coords_map[norm_name] = {
                            'latitude': f_lat,
                            'longitude': f_lng
                        }
                    # Also store by raw lower name for backup
                    coords_map[name.lower().strip()] = {
                        'latitude': f_lat,
                        'longitude': f_lng
                    }
                except ValueError:
                    continue

    print(f"Loaded coordinates for {len(coords_map)} CSV entries.")

    # 2. Load Museum Data from JSON
    print(f"Reading JSON from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        museums_data = json.load(f)
        
    updated_count = 0
    
    for m in museums_data:
        m_name = m.get('museum_name')
        if not m_name:
            continue
            
        # Try finding match
        # 1. Exact Name match (insensitive)
        match = coords_map.get(m_name.lower().strip())
        
        # 2. Normalized Name match
        if not match:
             match = coords_map.get(normalize_name(m_name))
             
        if match:
            m['latitude'] = match['latitude']
            m['longitude'] = match['longitude']
            updated_count += 1
        else:
            # User wants to "take only proper... latitude and longitude in this take... only that museum's which is present"
            # Assuming we only keep coords if we found them in CSV.
            # If CSV doesn't have it, set to None (removing randoms)
            m['latitude'] = None
            m['longitude'] = None
            
    print(f"Matched and updated coordinates for {updated_count} / {len(museums_data)} museums.")
    
    # 3. Write back to JSON file (USER REQUIREMENT)
    print(f"Writing updated data back to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(museums_data, f, indent=4)
        
    # 4. Re-seed Database
    print("Emptying 'museums' collection...")
    db.museums.delete_many({})
    
    if museums_data:
        print(f"Inserting {len(museums_data)} museums into MongoDB...")
        db.museums.insert_many(museums_data)
        print("Database update complete!")
    else:
        print("No data to insert.")

if __name__ == '__main__':
    reseed_museums()
