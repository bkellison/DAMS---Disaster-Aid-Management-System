from flask import Blueprint, request, jsonify
from disaster_relief_app.models import db, Item
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

donation_routes = Blueprint('donation_routes', __name__)


@donation_routes.route('/admin/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'id': i.item_id,
        'name': i.name,
        'description': i.description,
        'category_id': i.category_id,
        'quantity': i.quantity,  # Include quantity in response
        'created_by': i.created_by,
        'created_at': i.created_at.strftime('%Y-%m-%d %H:%M:%S') if i.created_at else None
    } for i in items])

@donation_routes.route('/admin/items', methods=['POST'])
def create_item():
    data = request.get_json()
    try:
        item = Item(
            name=data['name'],
            description=data.get('description', ''),
            category_id=data.get('category_id'),
            quantity=data.get('quantity', 1),  # Default to 1 if not provided
            created_by=data.get('created_by'),
            created_at=datetime.now()
        )
        db.session.add(item)
        db.session.commit()
        
        # Return the created item with its ID
        return jsonify({
            'message': 'Item created successfully',
            'item': {
                'id': item.item_id,
                'name': item.name,
                'description': item.description,
                'category_id': item.category_id,
                'quantity': item.quantity,
                'created_by': item.created_by,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@donation_routes.route('/admin/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@donation_routes.route('/admin/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    try:
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        item.category_id = data.get('category_id', item.category_id)
        item.quantity = data.get('quantity', item.quantity)

        db.session.commit()
        
        # Return the updated item
        return jsonify({
            'message': 'Item updated successfully',
            'item': {
                'id': item.item_id,
                'name': item.name,
                'description': item.description,
                'category_id': item.category_id,
                'quantity': item.quantity,
                'created_by': item.created_by,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else None
            }
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500