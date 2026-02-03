from db import get_db
import datetime
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash

class AdminModel:
    @staticmethod
    def create_admin(email, password):
        db = get_db()
        hashed_password = generate_password_hash(password)
        admin = {
            'email': email,
            'password': hashed_password,
            'role': 'admin',
            'created_at': datetime.datetime.now()
        }
        result = db.admins.insert_one(admin)
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        db = get_db()
        return db.admins.find_one({'email': email})

    @staticmethod
    def find_by_id(admin_id):
        db = get_db()
        return db.admins.find_one({'_id': ObjectId(admin_id)})
