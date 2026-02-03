import json
import csv
import sys
import os
import uuid
from datetime import datetime
from pymongo import MongoClient
import certifi

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = 'museum_management_system_1'

def convert_and_import():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'final_museums.csv')
    json_path = os.path.join(base_dir, 'museum_data.json')
    
    print(f"Reading CSV from: {csv_path}")
    
    museums_list = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows
            if not row.get('Name'):
                continue
                
            # Parse Coords
            lat = None
            lng = None
            try:
                if row.get('Latitude'):
                    lat = float(row.get('Latitude'))
                if row.get('Longitude'):
                    lng = float(row.get('Longitude'))
            except ValueError:
                pass # Keep as None if invalid
                
            # Construct Entry based on Schema
            now = datetime.now().isoformat()
            
            # Basic Address Construction
            city = row.get('City', '').strip()
            state = row.get('State', '').strip()
            address = f"{city}, {state}, India"
            
            entry = {
                "museum_id": str(uuid.uuid4()),
                "museum_name": row.get('Name', '').strip(),
                "museum_type": row.get('Type', 'General').strip(),
                "established_year": row.get('Established', '').strip() or None,
                "description": row.get('Description', '').strip() or f"Explore the rich history and culture at {row.get('Name')}.",
                "address": address,
                "city": city,
                "state": state,
                "country": "India",
                "pincode": None, # CSV doesn't have pincode
                "latitude": lat,
                "longitude": lng,
                
                # Default Fields
                "opening_time": "10:00 AM",
                "closing_time": "06:00 PM",
                "weekly_off_days": ["Monday"],
                "entry_fee": 50, # Default fee
                "ticket_currency": "INR",
                "average_visit_duration_minutes": 90,
                "max_daily_capacity": 500,
                "wheelchair_accessible": True,
                "parking_available": True,
                "guided_tours_available": False,
                "audio_guide_available": False,
                
                # Contact (Empty)
                "contact_phone": None,
                "contact_email": None,
                "official_website": None,
                "google_maps_link": None,
                
                # Media
                "cover_image": None,
                "gallery_images": [],
                "video_url": None,
                
                # Stats
                "average_rating": 4.5, # Default rating for good looks
                "total_reviews": 0,
                "annual_visitors": None,
                "popularity_score": 0,
                
                # Discounts
                "student_discount": 50,
                "senior_citizen_discount": 30,
                "free_entry_days": [],
                "special_exhibition_fee": None,
                
                # System
                "status": "active",
                "created_at": now,
                "updated_at": now
            }
            
            museums_list.append(entry)
            
    print(f"Buidling {len(museums_list)} museum entries from CSV.")
    
    # 1. Write to JSON
    print(f"Writing to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(museums_list, f, indent=4)
        
    # 2. Reseed DB
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    
    print("Emptying 'museums' collection...")
    db.museums.delete_many({})
    
    if museums_list:
        print(f"Inserting {len(museums_list)} entries...")
        db.museums.insert_many(museums_list)
        print("Success! Database populated with CSV data.")
    else:
        print("Warning: No data found in CSV to import.")

if __name__ == '__main__':
    convert_and_import()
