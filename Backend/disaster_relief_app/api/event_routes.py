# disaster_relief_app/api/event_routes.py
from flask import Blueprint, request, jsonify
from disaster_relief_app.models import db, Event, EventCategory

event_routes = Blueprint('event_routes', __name__)

@event_routes.route('/admin/events', methods=['POST'])
def create_event():
    data = request.get_json()
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

    data = request.get_json()
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    try:
        # Update basic event information
        event.event_name = data['name']
        event.location = data.get('location', '')
        event.start_date = data['start_date']
        event.end_date = data['end_date']

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