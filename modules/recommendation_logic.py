from db import get_db
import random

def get_recommendations(user_id=None):
    db = get_db()
    
    if user_id:
        last_booking = db.bookings.find_one(
            {'user_id': user_id}, 
            sort=[('booking_date', -1)]
        )
        
        if last_booking:
            last_museum = db.museums.find_one({'_id': last_booking['museum_id']}) # This might need ObjectId coversion if stored as ObjectId
            pass

    pipeline = [{"$sample": {"size": 3}}]
    recommendations = list(db.museums.aggregate(pipeline))
    
    return recommendations

def logic_placeholder():
    pass
