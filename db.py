from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
db = client.get_database()

def get_db():
    return db

def init_db():
    """
    Initialize indexes or collections if needed.
    """
    try:
        db.users.create_index("email", unique=True)
        db.admins.create_index("email", unique=True)
        db.museums.create_index("name")
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
