# disaster_relief_app/api/event_routes.py
from flask import Blueprint, request, jsonify
from disaster_relief_app.models import db, Event, EventCategory
from sqlalchemy import text
from disaster_relief_app.utils import get_db

event_routes = Blueprint('event_routes', __name__)

def check_admin_permissions(user_id):
    """Check if user has full admin permissions (not just observer)"""
    try:
        db_connection = get_db()
        
        user_query = text("SELECT role FROM dr_admin.user WHERE user_id = :user_id")
        result = db_connection.session.execute(user_query, {"user_id": user_id}).fetchone()
        
        if not result:
            return False
            
        return result.role == 'Admin'  # Only full Admin role can edit
    except Exception as e:
        print(f"Error checking admin permissions: {e}")
        return False

def get_user_from_session():
    """Get user ID from session/request - you'll need to implement this based on your auth system"""
    return request.json.get('user_id') if request.json else None

@event_routes.route('/admin/events', methods=['POST'])
def create_event():
    data = request.get_json()
    
    # Check permissions - only full Admins can create events
    user_id = get_user_from_session()
    if user_id and not check_admin_permissions(user_id):
        return jsonify({'error': 'Insufficient permissions. Only Admins can create events.'}), 403
    
    try:
        new_event = Event(
            event_name=data['name'],
            type=data['type'],
            location=data['location'],  # This will be the combined location string
            start_date=data['startDate'],
            end_date=data['endDate'],
            description=data.get('description', ''),  # Optional description
            is_active=True
        )

        # Add individual location fields if they exist
        if 'address' in data:
            new_event.address = data['address']
        if 'city' in data:
            new_event.city = data['city']
        if 'state' in data:
            new_event.state = data['state']
        if 'zipCode' in data:
            new_event.zip_code = data['zipCode']

        db.session.add(new_event)
        db.session.flush()

        category_ids = data.get('categoryIds', [])
        for cat_id in category_ids:
            if not cat_id or not str(cat_id).isdigit():
                continue
            link = EventCategory(event_id=new_event.event_id, category_id=cat_id)
            db.session.add(link)
        
        db.session.commit()
        return jsonify({'message': 'Event created', 'id': new_event.event_id}), 201
    except Exception as e:
        db.session.rollback()
        print("Event creation failed:", e)
        return jsonify({'error': 'Failed to create event'}), 500

@event_routes.route('/admin/events', methods=['GET'])
def get_events():
    try:
        from disaster_relief_app.models import Category, EventCategory

        events = Event.query.all()
        event_list = []

        for e in events:
            # Get category names via join
            categories = (
                db.session.query(Category.category_name)
                .join(EventCategory, EventCategory.category_id == Category.category_id)
                .filter(EventCategory.event_id == e.event_id)
                .all()
            )
            category_names = [c.category_name for c in categories]

            event_list.append({
                'event_id': e.event_id,
                'name': e.event_name,
                'type': e.type,
                'location': e.location,
                'address': getattr(e, 'address', ''),
                'city': getattr(e, 'city', ''),
                'state': getattr(e, 'state', ''),
                'zip_code': getattr(e, 'zip_code', ''),
                'start_date': e.start_date.strftime('%Y-%m-%d') if e.start_date else None,
                'end_date': e.end_date.strftime('%Y-%m-%d') if e.end_date else None,
                'description': e.description,
                'is_active': e.is_active,
                'categories': category_names
            })

        return jsonify(event_list), 200
    except Exception as e:
        print("Error fetching events:", e)
        return jsonify({'error': 'Failed to fetch events'}), 500

@event_routes.route('/categories', methods=['GET'])
def get_categories():
    from disaster_relief_app.models import Category

    try:
        categories = Category.query.all()
        category_list = [{
            'category_id': c.category_id,
            'category_name': c.category_name,
            'description': c.description
        } for c in categories]
        return jsonify(category_list), 200
    except Exception as e:
        print("Error fetching categories:", e)
        return jsonify({'error': 'Failed to fetch categories'}), 500
    
@event_routes.route('/admin/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    # Check permissions - only full Admins can delete events
    user_id = get_user_from_session()
    if user_id and not check_admin_permissions(user_id):
        return jsonify({'error': 'Insufficient permissions. Only Admins can delete events.'}), 403
    
    try:
        # First, delete all related event_category entries
        EventCategory.query.filter_by(event_id=event_id).delete()
        
        # Then delete the event
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
            
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error deleting event:", e)
        return jsonify({'error': 'Failed to delete event'}), 500

@event_routes.route('/admin/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    from disaster_relief_app.models import EventCategory

    # Check permissions - only full Admins can update events
    user_id = get_user_from_session()
    if user_id and not check_admin_permissions(user_id):
        return jsonify({'error': 'Insufficient permissions. Only Admins can update events.'}), 403

    data = request.get_json()
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    try:
        # Update basic event information
        event.event_name = data['name']
        event.type = data.get('type', event.type)
        event.location = data.get('location', '')
        event.start_date = data['start_date']
        event.end_date = data['end_date']
        event.description = data.get('description', event.description)

        # Update individual location fields if provided
        if 'address' in data:
            event.address = data['address']
        if 'city' in data:
            event.city = data['city']
        if 'state' in data:
            event.state = data['state']
        if 'zipCode' in data:
            event.zip_code = data['zipCode']

        # Remove existing category associations
        EventCategory.query.filter_by(event_id=event_id).delete()

        # Add new category associations
        for cat_id in data.get('categoryIds', []):
            db.session.add(EventCategory(event_id=event_id, category_id=cat_id))

        db.session.commit()
        return jsonify({'message': 'Event and categories updated'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error updating event:", e)
        return jsonify({'error': 'Failed to update event'}), 500

@event_routes.route('/admin/events/<int:event_id>/categories', methods=['GET'])
def get_event_categories(event_id):
    from disaster_relief_app.models import EventCategory, Category

    try:
        categories = (
            db.session.query(Category)
            .join(EventCategory, EventCategory.category_id == Category.category_id)
            .filter(EventCategory.event_id == event_id)
            .all()
        )

        category_list = [
            {'category_id': c.category_id, 'category_name': c.category_name}
            for c in categories
        ]
        return jsonify(category_list), 200

    except Exception as e:
        print(f"Error fetching categories for event {event_id}:", e)
        return jsonify({'error': 'Failed to fetch event categories'}), 500

# Additional utility route to check user permissions (optional)
@event_routes.route('/admin/check-permissions', methods=['GET'])
def check_permissions():
    """Check if current user has admin permissions"""
    user_id = get_user_from_session()
    if not user_id:
        return jsonify({'error': 'No user session found'}), 401
    
    has_admin_permissions = check_admin_permissions(user_id)
    
    try:
        db_connection = get_db()
        user_query = text("SELECT role FROM dr_admin.user WHERE user_id = :user_id")
        result = db_connection.session.execute(user_query, {"user_id": user_id}).fetchone()
        
        return jsonify({
            'user_id': user_id,
            'role': result.role if result else None,
            'can_edit': has_admin_permissions,
            'can_view': result.role in ['Admin', 'Admin Observer'] if result else False
        }), 200
    except Exception as e:
        print(f"Error checking permissions: {e}")
        return jsonify({'error': 'Failed to check permissions'}), 500