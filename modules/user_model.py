from db import get_db
import datetime
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash

class UserModel:
    @staticmethod
    def create_user(email, password):
        db = get_db()
        hashed_password = generate_password_hash(password)
        user = {
            'email': email,
            'password': hashed_password,
            'role': 'user',
            'created_at': datetime.datetime.now()
        }
        result = db.users.insert_one(user)
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        db = get_db()
        return db.users.find_one({'email': email, 'role': 'user'})

    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        return db.users.find_one({'_id': ObjectId(user_id)})
