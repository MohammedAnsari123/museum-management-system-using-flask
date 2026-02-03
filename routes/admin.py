from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from bson.objectid import ObjectId
from modules.admin_model import AdminModel
import uuid

admin_bp = Blueprint('admin', __name__)

def login_required_admin(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

from werkzeug.security import check_password_hash

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if AdminModel.find_by_email(email):
             flash('Admin email already registered.', 'danger')
        else:
            try:
                AdminModel.create_admin(email, password)
                flash('Admin registration successful! Please login.', 'success')
                return redirect(url_for('admin.login'))
            except Exception as e:
                flash('Email already registered as Admin.', 'danger')
            
    return render_template('admin/register.html')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = AdminModel.find_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            session['email'] = user['email']
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


def get_paginated_data(collection, query, page, per_page=10):
    total = collection.count_documents(query)
    total_pages = (total + per_page - 1) // per_page
    
    data = list(collection.find(query)
                .sort('created_at', -1)
                .skip((page - 1) * per_page)
                .limit(per_page))
    
    return data, total_pages, page

@admin_bp.route('/dashboard')
@login_required_admin
def dashboard():
    db = get_db()
    metrics = {
        'users': db.users.count_documents({}),
        'museums': db.museums.count_documents({}),
        'bookings': db.bookings.count_documents({}),
        'reviews': db.reviews.count_documents({}),
        'feedbacks': db.feedbacks.count_documents({})
    }
    
    # --- Graph Generation ---
    import matplotlib
    matplotlib.use('Agg') # Use non-interactive backend
    import matplotlib.pyplot as plt
    import io
    import base64
    from collections import Counter
    
    graphs = {}
    
    try:
        # 1. Bookings by Museum (Top 5)
        # Aggregate bookings by museum_name
        pipeline = [
            {"$group": {"_id": "$museum_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        booking_data = list(db.bookings.aggregate(pipeline))
        
        if booking_data:
            names = [item["_id"] for item in booking_data]
            counts = [item["count"] for item in booking_data]
            
            # Top 5 Museums - Horizontal Bar Chart for better label readability
            plt.figure(figsize=(7, 5))
            # Use a dark goldenrod/brown palette to match the theme
            colors = ['#8B4513', '#A0522D', '#CD853F', '#D2691E', '#DEB887']
            
            # Reverse lists to have the highest value on top
            plt.barh(names[::-1], counts[::-1], color=colors[:len(names)]) 
            plt.title('Top 5 Most Booked Museums', fontsize=12)
            plt.xlabel('Number of Bookings', fontsize=10)
            plt.tight_layout()
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            graphs['top_museums'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
        # 2. Museums by Category (Pie Chart) with simplified labels
        pipeline_types = [
            {"$group": {"_id": "$museum_type", "count": {"$sum": 1}}}
        ]
        type_data = list(db.museums.aggregate(pipeline_types))
        
        if type_data:
            # Filter out empty types
            labels = [item["_id"] for item in type_data if item["_id"]]
            sizes = [item["count"] for item in type_data if item["_id"]]
            
            # Clean up labels if they are too long, or use a legend
            plt.figure(figsize=(7, 5))
            
            # Use a warm color palette
            warm_colors = ['#8B4513', '#D2691E', '#CD853F', '#F4A460', '#DEB887', '#A52A2A']
            
            wedges, texts, autotexts = plt.pie(sizes, labels=None, autopct='%1.1f%%', 
                                             startangle=140, pctdistance=0.85, colors=warm_colors[:len(sizes)])
            
            # Add a circle at the center to make it a Donut Chart (looks more modern)
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            
            plt.legend(wedges, labels, title="Museum Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            plt.title('Museum Types Distribution', fontsize=12)
            plt.tight_layout()
            
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', dpi=100)
            buf2.seek(0)
            graphs['museum_types'] = base64.b64encode(buf2.getvalue()).decode('utf-8')
            plt.close()

    except Exception as e:
        print(f"Error generating graphs: {e}")
        # flash(f"Graph error: {e}", "warning") 

    return render_template('admin/dashboard.html', metrics=metrics, active_page='dashboard', graphs=graphs)

@admin_bp.route('/museums')
@login_required_admin
def museums():
    db = get_db()
    page = int(request.args.get('page', 1))
    q = request.args.get('q', '')
    type_filter = request.args.get('type', '')
    
    query = {}
    if q:
        query['$or'] = [
            {'museum_name': {'$regex': q, '$options': 'i'}},
            {'city': {'$regex': q, '$options': 'i'}}
        ]
    if type_filter:
        query['museum_type'] = type_filter
        
    today = {} # unused here effectively
    
    # Get distinct museum types for filter
    museum_types = db.museums.distinct('museum_type')
    
    museums_list, total_pages, current_page = get_paginated_data(db.museums, query, page)
    
    return render_template('admin/museums.html', 
                           museums=museums_list, 
                           total_pages=total_pages, 
                           current_page=current_page,
                           active_page='museums',
                           museum_types=museum_types)

@admin_bp.route('/users')
@login_required_admin
def users():
    db = get_db()
    page = int(request.args.get('page', 1))
    q = request.args.get('q', '')
    
    query = {}
    if q:
        query['email'] = {'$regex': q, '$options': 'i'}
        
    users_list, total_pages, current_page = get_paginated_data(db.users, query, page)
    
    return render_template('admin/users.html', 
                           users=users_list, 
                           total_pages=total_pages, 
                           current_page=current_page,
                           active_page='users')

@admin_bp.route('/bookings')
@login_required_admin
def bookings():
    db = get_db()
    page = int(request.args.get('page', 1))
    q = request.args.get('q', '')
    
    query = {}
    if q:
        query['$or'] = [
            {'email': {'$regex': q, '$options': 'i'}},
            {'museum_name': {'$regex': q, '$options': 'i'}}
        ]
        
    bookings_list, total_pages, current_page = get_paginated_data(db.bookings, query, page)
    
    return render_template('admin/bookings.html', 
                           bookings=bookings_list, 
                           total_pages=total_pages, 
                           current_page=current_page,
                           active_page='bookings')

@admin_bp.route('/reviews')
@login_required_admin
def reviews():
    db = get_db()
    page = int(request.args.get('page', 1))
    q = request.args.get('q', '')
    rating = request.args.get('rating', '')
    
    query = {}
    if q:
        query['comment'] = {'$regex': q, '$options': 'i'}
    if rating:
        query['rating'] = int(rating)
        
    reviews_list, total_pages, current_page = get_paginated_data(db.reviews, query, page)
    
    return render_template('admin/reviews.html', 
                           reviews=reviews_list, 
                           total_pages=total_pages, 
                           current_page=current_page,
                           active_page='reviews')

@admin_bp.route('/feedbacks')
@login_required_admin
def feedbacks():
    db = get_db()
    page = int(request.args.get('page', 1))
    q = request.args.get('q', '')
    
    query = {}
    if q:
        query['message'] = {'$regex': q, '$options': 'i'}
        
    feedbacks_list, total_pages, current_page = get_paginated_data(db.feedbacks, query, page)
    
    return render_template('admin/feedbacks.html', 
                           feedbacks=feedbacks_list, 
                           total_pages=total_pages, 
                           current_page=current_page,
                           active_page='feedbacks')

@admin_bp.route('/museum/add', methods=['GET', 'POST'])
@login_required_admin
def add_museum():
    db = get_db()
    
    # Fetch distinct categories for the dropdown
    categories = db.museums.distinct('museum_type')
    categories = [c for c in categories if c]
    
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location') # Using location as address
        city = request.form.get('city') if request.form.get('city') else location.split(',')[0].strip() # Fallback extraction
        state = request.form.get('state') if request.form.get('state') else 'Unknown'
        
        category = request.form.get('category')
        custom_category = request.form.get('custom_category')
        description = request.form.get('description')
        max_capacity = int(request.form.get('capacity', 1000))

        # Handle Custom Category
        final_category = custom_category if category == 'Other' and custom_category else category
        
        new_museum = {
            'museum_name': name,
            'location': location,
            'city': city,
            'state': state,
            'museum_type': final_category,
            'description': description, # Ensure field name matches DB schema
            'max_daily_capacity': max_capacity,
            'status': 'active',
            'created_at': datetime.datetime.now(),
            'museum_id': str(uuid.uuid4())
        }
        
        db.museums.insert_one(new_museum)
        flash('Museum added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/add_museum.html', categories=categories)

@admin_bp.route('/museum/edit/<id>', methods=['GET', 'POST'])
@login_required_admin
def edit_museum(id):
    db = get_db()
    if request.method == 'POST':
        updated_data = {
            'museum_name': request.form.get('name'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'museum_type': request.form.get('category'),
            'description': request.form.get('description'),
            'max_daily_capacity': int(request.form.get('capacity', 1000))
        }
        db.museums.update_one({'_id': ObjectId(id)}, {'$set': updated_data})
        flash('Museum updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    museum = db.museums.find_one({'_id': ObjectId(id)})
    return render_template('admin/edit_museum.html', museum=museum)

@admin_bp.route('/museum/delete/<id>')
@login_required_admin
def delete_museum(id):
    db = get_db()
    db.museums.delete_one({'_id': ObjectId(id)})
    flash('Museum deleted.', 'info')
    return redirect(url_for('admin.dashboard'))
