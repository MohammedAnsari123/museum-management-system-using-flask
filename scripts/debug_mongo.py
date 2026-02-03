import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def test_connection(name, **kwargs):
    print(f"\n--- Testing: {name} ---")
    try:
        client = MongoClient(MONGO_URI, **kwargs)
        # Force a connection
        client.admin.command('ping')
        print("SUCCESS! Connected.")
        return True
    except Exception as e:
        print(f"FAILED. Error: {e}")
        return False

# 1. Standard (Current)
print("Testing current configuration...")
test_connection("Standard with certifi", tlsCAFile=certifi.where())

# 2. Without certifi (System certs)
print("\nTesting without explicit tlsCAFile...")
test_connection("System Certs")

# 3. Allow Invalid Certs (Diagnostic only)
print("\nTesting with tlsAllowInvalidCertificates=True...")
test_connection("Insecure (Invalid Certs Allowed)", tlsAllowInvalidCertificates=True)
