import json
import sys
import os

# Add parent directory to path to import db.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db

def seed_museums():
    db = get_db()
    collection = db.museums

    collection.delete_many({})
    print("Cleared existing museum data.")

    json_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "museum_data.json")
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not data:
            print("No data found in museum_data.json")
            return
            
        collection.insert_many(data)
        print(f"Successfully inserted {len(data)} museums into the database.")

        collection.create_index([("museum_name", "text"), ("description", "text")])
        print("Created text indexes.")
        
    except FileNotFoundError:
        print("museum_data.json not found. Run extract_data_v2.py first.")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    seed_museums()
