from pymongo import ASCENDING, DESCENDING, TEXT
import sys
import os

# Add parent directory to path to import db.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db

def create_indexes():
    db = get_db()
    
    print("Creating indexes...")
    
    # 1. Users: Email must be unique
    print("Index: users.email (unique)")
    db.users.create_index([("email", ASCENDING)], unique=True)
    
    # 2. Museums: Search functionality (Name, City, Description)
    print("Index: museums.text_search")
    
    # Drop any existing text index first to avoid conflicts
    try:
        indexes = db.museums.list_indexes()
        for index in indexes:
            if 'weights' in index: # Text indexes have weights
                print(f"Dropping existing text index: {index['name']}")
                db.museums.drop_index(index['name'])
    except Exception as e:
        print(f"Warning dropping index: {e}")

    db.museums.create_index([
        ("museum_name", TEXT),
        ("city", TEXT),
        ("description", TEXT)
    ], name="text_search")
    
    # 3. Bookings: Frequent lookups by user and date
    print("Index: bookings.user_id_date")
    db.bookings.create_index([
        ("user_id", ASCENDING),
        ("tour_date", DESCENDING)
    ])
    
    # 4. Reviews: Lookups by museum
    print("Index: reviews.museum_id")
    db.reviews.create_index([("museum_id", ASCENDING)])
    
    print("Indexes created successfully!")

if __name__ == "__main__":
    create_indexes()
