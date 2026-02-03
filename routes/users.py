from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from db import get_db
from bson.objectid import ObjectId
import datetime
import uuid
import io
from modules.recommendation_logic import get_recommendations
from modules.user_model import UserModel
from utils.pdf_generator import generate_ticket_pdf
from utils.email_sender import send_booking_email

users_bp = Blueprint('users', __name__)

from werkzeug.security import check_password_hash

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            UserModel.create_user(email, password)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('users.login'))
        except Exception as e:
            flash('Email already registered.', 'danger')
            
    return render_template('users/register.html')

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = UserModel.find_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            session['email'] = user['email']
            return redirect(url_for('users.dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
            
    return render_template('users/login.html')

@users_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@users_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
        
    db = get_db()

    recommendations = get_recommendations(session['user_id'])
    
    recent_bookings = list(db.bookings.find({'user_id': session['user_id']}).sort('booking_date', -1))
    
    # Fetch Wishlist
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    wishlist_ids = user.get('wishlist', [])
    wishlist_museums = []
    if wishlist_ids:
        # Convert string IDs back to ObjectId if needed, but assuming they are stored as strings for simplicity in toggle
        # If stored as strings:
        wishlist_museums = list(db.museums.find({'_id': {'$in': [ObjectId(i) for i in wishlist_ids]}}))
        
    return render_template('users/dashboard.html', 
                           bookings=recent_bookings, 
                           recommendations=recommendations,
                           wishlist=wishlist_museums)

@users_bp.route('/museums')
def museums_list():
    db = get_db()

    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page

    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    location = request.args.get('location', '').strip()

    filters = {}
    if query:
        filters['$or'] = [
            {'museum_name': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}}
        ]
    if category:
        filters['museum_type'] = category
    if location:
        filters['$or'] = [
            {'city': {'$regex': location, '$options': 'i'}},
            {'state': {'$regex': location, '$options': 'i'}}
        ]
    
    museum_data = list(db.museums.find(filters).skip(skip).limit(per_page))
    total = db.museums.count_documents(filters)
    
    import math
    total_pages = math.ceil(total / per_page)

    categories = db.museums.distinct('museum_type')

    # Get user's wishlist if logged in
    wishlist_ids = []
    if 'user_id' in session:
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            wishlist_ids = user.get('wishlist', [])

    return render_template('users/museums.html', 
                           museums=museum_data, 
                           page=page, 
                           total=total, 
                           total_pages=total_pages,
                           per_page=per_page,
                           categories=categories,
                           search_query=query,
                           search_location=location,
                           search_category=category,
                           wishlist_ids=wishlist_ids)

@users_bp.route('/book/<museum_id>', methods=['POST'])
def book_museum(museum_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    db = get_db()
    date = request.form.get('date')
    tickets = int(request.form.get('tickets', 1))
    
    museum = db.museums.find_one({'_id': ObjectId(museum_id)})
    if not museum:
        return jsonify({'error': 'Museum not found'}), 404

    max_capacity = museum.get('max_daily_capacity') or 1000

    # Aggregate existing confirmed bookings
    existing_bookings = db.bookings.aggregate([
        {'$match': {'museum_id': museum_id, 'tour_date': date}},
        {'$group': {'_id': None, 'total_tickets': {'$sum': '$tickets'}}}
    ])
    result = list(existing_bookings)
    current_booked = result[0]['total_tickets'] if result else 0
    
    if current_booked + tickets > max_capacity:
        return jsonify({'error': f'Capacity exceeded. Only {max_capacity - current_booked} tickets remaining for this date.'}), 400

    # Instead of booking, save to session and redirect to payment
    session['pending_booking'] = {
        'user_id': session['user_id'],
        'email': session['email'],
        'user_name': session.get('user_name', 'Visitor'), # Ensure user_name is in session during login if possible
        'museum_id': museum_id,
        'museum_name': museum['museum_name'],
        'date': date,
        'tickets': tickets
    }
    print(f"DEBUG: Stored pending_booking in session: {session['pending_booking']}")
    
    return jsonify({'payment_required': True, 'redirect_url': url_for('users.payment')})

@users_bp.route('/payment', methods=['GET'])
def payment():
    if 'pending_booking' not in session:
        flash('No pending booking found.', 'warning')
        return redirect(url_for('users.dashboard'))
    return render_template('users/payment.html', booking=session['pending_booking'])

@users_bp.route('/payment/process', methods=['POST'])
def process_payment():
    print("DEBUG: Entering process_payment")
    if 'pending_booking' not in session:
        print("DEBUG: No pending_booking found in session!")
        return redirect(url_for('users.dashboard'))
        
    booking_data = session['pending_booking']
    db = get_db()
    
    # 1. Generate Booking ID
    booking_id = str(uuid.uuid4())[:8].upper()
    booking_data['booking_id'] = booking_id
    booking_data['booking_date'] = datetime.datetime.now()
    # Rename 'date' to 'tour_date' for DB consistency
    booking_data['tour_date'] = booking_data.pop('date') 
    
    # Capture Payment Method
    booking_data['payment_method'] = request.form.get('payment_method', 'Card')
    booking_data['payment_status'] = 'Paid' if booking_data['payment_method'] != 'Cash' else 'Pending (Pay at Venue)'
    
    print(f"DEBUG: Inserting booking into DB: {booking_data}")
    # 2. Insert into DB
    try:
        result = db.bookings.insert_one(booking_data)
        print(f"DEBUG: Inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"DEBUG: Error inserting into DB: {e}")
        flash('Error saving booking.', 'danger')
        return redirect(url_for('users.dashboard'))
    
    # 3. Generate PDF
    pdf_buffer = generate_ticket_pdf(booking_data)
    
    # 4. Send Email (Async or Sync - Sync for now)
    # Re-normalize keys for email template
    email_data = booking_data.copy()
    email_data['date'] = booking_data['tour_date'] 
    
    # We send to the logged-in user's email
    send_booking_email(booking_data['email'], email_data, pdf_buffer)
    
    # Clear session
    session.pop('pending_booking', None)
    
    # 5. Success Page or Dashboard
    flash(f'Booking Confirmed! Ticket sent to {booking_data["email"]}', 'success')
    return redirect(url_for('users.dashboard'))

@users_bp.route('/review/<museum_id>', methods=['POST'])
def add_review(museum_id):
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
        
    db = get_db()
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    museum = db.museums.find_one({'_id': ObjectId(museum_id)})
    if not museum:
        flash('Museum not found.', 'danger')
        return redirect(url_for('users.museums_list'))

    has_booked = db.bookings.find_one({
        'user_id': session['user_id'],
        'museum_id': museum_id
    })

    if not has_booked:
        flash('You can only review museums you have booked.', 'warning')
        return redirect(url_for('users.museums_list'))
    
    review = {
        'user_id': session['user_id'],
        'email': session['email'],
        'museum_id': museum_id,
        'museum_name': museum['museum_name'],
        'rating': rating,
        'comment': comment,
        'created_at': datetime.datetime.now()
    }
    
    db.reviews.insert_one(review)
    flash('Thank you for your review!', 'success')
    return redirect(url_for('users.museums_list'))

@users_bp.route('/feedback/<museum_id>', methods=['POST'])
def submit_booked_feedback(museum_id):
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
        
    db = get_db()
    message = request.form.get('message')
    
    museum = db.museums.find_one({'_id': ObjectId(museum_id)})
    if not museum:
        flash('Museum not found.', 'danger')
        return redirect(url_for('users.dashboard'))

    # Verify Booking
    has_booked = db.bookings.find_one({
        'user_id': session['user_id'],
        'museum_id': museum_id
    })

    if not has_booked:
        flash('You can only give feedback for museums you have booked.', 'warning')
        return redirect(url_for('users.dashboard'))
    
    feedback = {
        'user_id': session['user_id'],
        'email': session['email'], # Sender Email
        'museum_id': museum_id,
        'museum_name': museum['museum_name'], # Museum Name
        'message': message, # Feedback
        'created_at': datetime.datetime.now()
    }
    
    db.feedbacks.insert_one(feedback)
    flash('Feedback sent to museum administration!', 'success')
    return redirect(url_for('users.dashboard'))

@users_bp.route('/wishlist/toggle/<museum_id>', methods=['POST'])
def toggle_wishlist(museum_id):
    if 'user_id' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    
    db = get_db()
    user_id = session['user_id']
    
    # Check if exists
    user = db.users.find_one({'_id': ObjectId(user_id)})
    wishlist = user.get('wishlist', [])
    
    action = 'added'
    if museum_id in wishlist:
        db.users.update_one({'_id': ObjectId(user_id)}, {'$pull': {'wishlist': museum_id}})
        action = 'removed'
    else:
        db.users.update_one({'_id': ObjectId(user_id)}, {'$addToSet': {'wishlist': museum_id}})
        action = 'added'
        
    return jsonify({'status': 'success', 'action': action})

@users_bp.route('/map')
def map_view():
    db = get_db()
    museums = list(db.museums.find())
    
    map_data = []
    
    for m in museums:
        # Only include if coordinates exist
        lat = m.get('latitude')
        lng = m.get('longitude')
        
        if lat and lng:
            map_data.append({
                'museum_name': m.get('museum_name'),
                'museum_type': m.get('museum_type'),
                'city': m.get('city'),
                'state': m.get('state', ''),
                'latitude': lat,
                'longitude': lng
            })
    
    import json
    return render_template('users/map.html', museums_json=json.dumps(map_data))
        
    return render_template('users/feedback.html')
