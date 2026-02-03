
import sys
import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
print(f"Testing connection to: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else 'Wait, invalid URI format for display'}")

configs = [
    {"name": "Default", "kwargs": {}},
    {"name": "Allow Invalid Certs", "kwargs": {"tlsAllowInvalidCertificates": True}},
    {"name": "Certifi CA", "kwargs": {"tlsCAFile": certifi.where()}},
    {"name": "Certifi + Allow Invalid", "kwargs": {"tlsCAFile": certifi.where(), "tlsAllowInvalidCertificates": True}},
    {"name": "TLS + Allow Invalid", "kwargs": {"tls": True, "tlsAllowInvalidCertificates": True}},
]

for config in configs:
    print(f"\nTesting config: {config['name']}")
    try:
        client = MongoClient(MONGO_URI, **config['kwargs'], serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        print("SUCCESS!")
        break
    except Exception as e:
        print(f"FAILED: {e}")
