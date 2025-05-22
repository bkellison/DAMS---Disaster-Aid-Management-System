from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from disaster_relief_app.utils import get_db
import datetime

shipping_routes = Blueprint('shipping_routes', __name__)

@shipping_routes.route('/updateShippingStatus', methods=['POST'])
def update_shipping_status():
    db = get_db()
    data_payload = request.get_json()
    
    try:
        match_id = data_payload.get('match_id')
        shipping_status = data_payload.get('shipping_status')
        tracking_number = data_payload.get('tracking_number')
        shipping_date = data_payload.get('shipping_date')
        shipping_address = data_payload.get('shipping_address')
        user_id = data_payload.get('user_id')
        
        if not match_id or not shipping_status or not user_id:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Get user role
        user_query = text("SELECT role FROM dr_admin.user WHERE user_id = :user_id")
        user_result = db.session.execute(user_query, {'user_id': user_id}).fetchone()
        
        if not user_result:
            return jsonify({'error': 'User not found'}), 404
            
        user_role = user_result.role
        
        # Donors can only change status from pending to shipped
        if user_role == 'Donor' and shipping_status == 'delivered':
            return jsonify({'error': 'Donors can only mark items as shipped'}), 403
            
        # Only admins or recipients can change status to delivered
        # FIXED: Changed OR to AND - now only denies access if user is NEITHER admin NOR recipient
        if shipping_status == 'delivered' and (user_role != 'Admin' and user_role != 'Recipient'):
            return jsonify({'error': 'Only admins or recipients can mark items as delivered'}), 403
        
        # Convert shipping_date string to datetime if provided
        if shipping_date:
            shipping_date = datetime.datetime.strptime(shipping_date, '%Y-%m-%d')
        
        update_shipping_sp = """
            CALL dr_events.update_shipping_status(
                :param_match_id, 
                :param_shipping_status, 
                :param_tracking_number, 
                :param_shipping_date
            )
        """
        
        db.session.execute(text(update_shipping_sp), {
            'param_match_id': match_id,
            'param_shipping_status': shipping_status,
            'param_tracking_number': tracking_number,
            'param_shipping_date': shipping_date
        })
        
        # Update shipping address separately if provided
        if shipping_address:
            update_address_sp = """
                CALL dr_events.update_shipping_address(
                    :param_match_id,
                    :param_shipping_address
                )
            """
            db.session.execute(text(update_address_sp), {
                'param_match_id': match_id,
                'param_shipping_address': shipping_address
            })
        
        db.session.commit()
        
        return jsonify({'message': 'Shipping status updated successfully'}), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(ex)}), 500
    except Exception as ex:
        return jsonify({'error': 'Internal server error', 'message': str(ex)}), 500

@shipping_routes.route('/getShippingInfo/<int:match_id>', methods=['GET'])
def get_shipping_info(match_id):
    db = get_db()
    
    try:
        print(f"Fetching shipping info for match ID: {match_id}")
        
        query = text("""
            SELECT 
                m.match_id,
                m.shipping_status,
                m.shipping_date,
                m.tracking_number,
                m.shipping_address,
                r.message as response_details,
                r.is_locked,
                de.event_name,
                u.username as recipient_name,
                u.zip_code as recipient_zip
            FROM dr_events.match m
            JOIN dr_events.request req ON m.request_id = req.request_id
            LEFT JOIN dr_events.response r ON req.request_id = r.request_id
            JOIN dr_events.disaster_event de ON req.event_id = de.event_id
            JOIN dr_admin.user u ON req.user_id = u.user_id
            WHERE m.match_id = :match_id
        """)
        
        result = db.session.execute(query, {'match_id': match_id}).fetchone()
        
        if not result:
            print(f"No match found for ID: {match_id}")
            return jsonify({'error': 'Match not found'}), 404
        
        print(f"Found match data: {result}")
        
        shipping_info = {
            'match_id': result.match_id,
            'shipping_status': result.shipping_status,
            'shipping_date': result.shipping_date.strftime('%Y-%m-%d') if result.shipping_date else None,
            'tracking_number': result.tracking_number,
            'shipping_address': result.shipping_address,
            'response_details': result.response_details,
            'is_locked': result.is_locked,
            'event_name': result.event_name,
            'recipient_name': result.recipient_name,
            'recipient_zip': result.recipient_zip
        }
        
        print(f"Returning shipping info: {shipping_info}")
        return jsonify(shipping_info), 200
        
    except SQLAlchemyError as ex:
        print(f"Database error: {ex}")
        return jsonify({'error': 'Database error', 'message': str(ex)}), 500
    except Exception as ex:
        print(f"Internal server error: {ex}")
        return jsonify({'error': 'Internal server error', 'message': str(ex)}), 500

@shipping_routes.route('/updateResponse', methods=['POST'])
def update_response():
    db = get_db()
    data_payload = request.get_json()
    
    try:
        response_id = data_payload.get('response_id')
        quantity = data_payload.get('quantity')
        message = data_payload.get('message')
        
        if not response_id:
            return jsonify({'error': 'Missing response_id'}), 400
        
        # Check if response is locked
        check_lock_query = text("""
            SELECT is_locked FROM dr_events.response 
            WHERE response_id = :response_id
        """)
        
        result = db.session.execute(check_lock_query, {'response_id': response_id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Response not found'}), 404
        
        if result.is_locked:
            return jsonify({'error': 'Response is locked and cannot be edited'}), 403
        
        # Update response if not locked
        update_query = text("""
            UPDATE dr_events.response
            SET 
                quantity = :quantity,
                message = :message,
                updated_at = CURRENT_TIMESTAMP
            WHERE response_id = :response_id
        """)
        
        db.session.execute(update_query, {
            'response_id': response_id,
            'quantity': quantity,
            'message': message
        })
        
        db.session.commit()
        
        return jsonify({'message': 'Response updated successfully'}), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(ex)}), 500
    except Exception as ex:
        return jsonify({'error': 'Internal server error', 'message': str(ex)}), 500

@shipping_routes.route('/lockResponse/<int:response_id>', methods=['POST'])
def lock_response(response_id):
    db = get_db()
    
    try:
        lock_query = text("""
            UPDATE dr_events.response
            SET is_locked = TRUE
            WHERE response_id = :response_id
        """)
        
        db.session.execute(lock_query, {'response_id': response_id})
        db.session.commit()
        
        return jsonify({'message': 'Response locked successfully'}), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(ex)}), 500
    except Exception as ex:
        return jsonify({'error': 'Internal server error', 'message': str(ex)}), 500