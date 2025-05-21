from sqlalchemy import text
from flask import Blueprint, request, jsonify
from disaster_relief_app.utils import get_db
from sqlalchemy.exc import SQLAlchemyError
import requests

auto_match_routes = Blueprint('auto_match_routes', __name__)

zipCodeBaseApiKey = '6288ed60-245c-11f0-85d0-6d6c95e6fa37'

@auto_match_routes.route('/getAutoMatchType', methods=['GET'])
def get_match_type():
    db = get_db()

    try:
        get_match_type_query = "SELECT * FROM dr_events.match_type WHERE type = 'auto'"
        result = db.session.execute((text(get_match_type_query)))

        match_types = [dict(row) for row in result.mappings()]
        
        return jsonify(match_types), 200
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@auto_match_routes.route('/autoMatch', methods=['POST'])
def start_auto_match():
    db = get_db()
    
    data_payload = request.get_json()
    try:
        match_type_name = data_payload.get("match_type_name")
        request_id = data_payload.get("request_id")
        inventory_priority = data_payload.get("inventory_priority", "auto")
        
        #Verify valid inputs
        if not match_type_name or not request_id:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Get combined inventory options
        combined_options_query = text("""
            SELECT 
                r.request_id,
                r.item_id,
                i.quantity AS base_quantity,
                COALESCE(pt.total_pledged, 0) AS total_pledged,
                COALESCE(pt.available, 0) AS available_pledged,
                r.quantity AS request_quantity,
                COALESCE(m.total_matched, 0) AS total_matched,
                r.quantity - COALESCE(m.total_matched, 0) AS quantity_needed
            FROM dr_events.request r
            JOIN dr_events.item i ON r.item_id = i.item_id
            LEFT JOIN (
                SELECT 
                    item_id,
                    SUM(item_quantity) AS total_pledged,
                    SUM(item_quantity - (allocated_quantity + fulfilled_quantity)) AS available
                FROM dr_events.pledge
                WHERE canceled_flag = 0
                GROUP BY item_id
            ) pt ON i.item_id = pt.item_id
            LEFT JOIN (
                SELECT request_id, SUM(match_quantity) AS total_matched
                FROM dr_events.match
                WHERE canceled_flag = 0
                GROUP BY request_id
            ) m ON r.request_id = m.request_id
            WHERE r.request_id = :request_id
        """)
        
        combined_options = db.session.execute(combined_options_query, {"request_id": request_id}).fetchone()
        
        if not combined_options:
            return jsonify({"error": "Request not found"}), 404
        
        # Check if there's anything left to match
        quantity_needed = combined_options.quantity_needed
        if quantity_needed <= 0:
            return jsonify({"error": "Request is already fully matched"}), 400
        
        # Calculate total available
        total_available = combined_options.base_quantity + combined_options.available_pledged
        
        if total_available <= 0:
            return jsonify({"error": "No inventory or pledges available for matching"}), 400
        
        # Determine amounts to use from each source based on priority
        admin_quantity = 0
        pledge_quantity = 0
        
        if inventory_priority == "admin":
            # Use admin inventory first, then pledges
            admin_quantity = min(combined_options.base_quantity, quantity_needed)
            pledge_quantity = min(combined_options.available_pledged, quantity_needed - admin_quantity)
        elif inventory_priority == "pledges":
            # Use pledges first, then admin inventory
            pledge_quantity = min(combined_options.available_pledged, quantity_needed)
            admin_quantity = min(combined_options.base_quantity, quantity_needed - pledge_quantity)
        else:
            # Auto priority - based on match type
            if match_type_name == "nearest" or match_type_name == "quickest":
                # For geographic or time-based matching, prioritize pledges
                pledge_quantity = min(combined_options.available_pledged, quantity_needed)
                admin_quantity = min(combined_options.base_quantity, quantity_needed - pledge_quantity)
            else:
                # For fulfillment matching, prioritize admin inventory
                admin_quantity = min(combined_options.base_quantity, quantity_needed)
                pledge_quantity = min(combined_options.available_pledged, quantity_needed - admin_quantity)
        
        # Create match from admin inventory if needed
        matches_created = 0
        if admin_quantity > 0:
            admin_match_query = text("""
                INSERT INTO dr_events.match
                (request_id, match_status, match_quantity, shipping_status, is_admin_source, match_type_id)
                VALUES (:request_id, 'matched', :admin_quantity, 'pending', 1, 
                    (SELECT match_type_id FROM dr_events.match_type WHERE name = :match_type_name))
            """)
            
            db.session.execute(admin_match_query, {
                "request_id": request_id,
                "admin_quantity": admin_quantity,
                "match_type_name": match_type_name
            })
            
            # Update the item's base quantity
            update_item_query = text("""
                UPDATE dr_events.item
                SET quantity = quantity - :admin_quantity
                WHERE item_id = :item_id
            """)
            
            db.session.execute(update_item_query, {
                "item_id": combined_options.item_id,
                "admin_quantity": admin_quantity
            })
            
            matches_created += 1
        
        # Create matches from pledges if needed
        if pledge_quantity > 0:
            # Get the match type ID
            match_type_query = text("SELECT match_type_id FROM dr_events.match_type WHERE name = :match_type_name")
            match_type_result = db.session.execute(match_type_query, {"match_type_name": match_type_name}).fetchone()
            
            if not match_type_result:
                return jsonify({"error": "Invalid match type"}), 400
            
            match_type_id = match_type_result.match_type_id
            
            # Call the appropriate stored procedure based on match type
            if match_type_name == "nearest":
                # Get pledges sorted by distance
                pledges_result = find_nearest(request_id, match_type_id, pledge_quantity)
                matches_created += pledges_result
            elif match_type_name == "quickest":
                # Get pledges sorted by days_to_ship
                pledges_result = find_quickest(request_id, match_type_id, pledge_quantity)
                matches_created += pledges_result
            else:
                # Default to fulfillment matching
                pledges_result = find_most_fulfilled(request_id, match_type_id, pledge_quantity)
                matches_created += pledges_result
        
        # Update the request's status
        update_request_query = text("""
            UPDATE dr_events.request
            SET status = 'matched'
            WHERE request_id = :request_id
        """)
        
        db.session.execute(update_request_query, {"request_id": request_id})
        
        db.session.commit()
        
        return jsonify({
            "message": f"Created {matches_created} matches using {admin_quantity} admin items and {pledge_quantity} pledge items"
        }), 200

    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

def find_nearest(request_id, match_type_id, quantity_needed):
    """
    Find and match pledges based on geographical proximity
    
    Args:
        request_id: ID of the request to match
        match_type_id: ID of the match type
        quantity_needed: Maximum quantity to match from pledges
        
    Returns:
        Number of matches created
    """
    db = get_db()
    
    try:
        # Get request details and recipient zipcode
        request_query = text("""
            SELECT r.request_id, r.user_id, r.item_id, u.zip_code AS recipient_zipcode
            FROM dr_events.request r
            JOIN dr_admin.user u ON r.user_id = u.user_id
            WHERE r.request_id = :request_id
        """)
        
        request_info = db.session.execute(request_query, {"request_id": request_id}).fetchone()
        
        if not request_info:
            return 0
        
        # Get available pledges for this item
        pledges_query = text("""
            SELECT p.pledge_id, p.user_id AS donor_id, p.item_id, p.days_to_ship,
                   u.zip_code AS donor_zipcode,
                   (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) AS available_quantity
            FROM dr_events.pledge p
            JOIN dr_admin.user u ON p.user_id = u.user_id
            WHERE p.item_id = :item_id
              AND p.canceled_flag = 0
              AND (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) > 0
        """)
        
        pledges = db.session.execute(pledges_query, {"item_id": request_info.item_id}).fetchall()
        
        if not pledges:
            return 0
            
        # Get zipcodes for distance calculation
        filtered_zipcodes = [pledge.donor_zipcode for pledge in pledges if pledge.donor_zipcode]
        recipient_zipcode = request_info.recipient_zipcode
        
        if not filtered_zipcodes or not recipient_zipcode:
            # Fall back to fulfillment matching if zipcodes are missing
            return find_most_fulfilled(request_id, match_type_id, quantity_needed)
            
        # Prepare zipcodes for API call
        comma_separated = ','.join(filtered_zipcodes)
        
        # Call ZipCodeBase API for distance calculation
        try:
            get_distance_api = f"https://app.zipcodebase.com/api/v1/distance?apikey={zipCodeBaseApiKey}&code={recipient_zipcode}&compare={comma_separated}&country=us&unit=miles"
            response = requests.get(get_distance_api)
            response.raise_for_status()
            data = response.json()
            
            # Get distances from API response
            distances = data.get("results", {})
            
            # Add distance to each pledge
            sorted_pledges = []
            for pledge in pledges:
                if pledge.donor_zipcode in distances:
                    sorted_pledges.append({
                        "pledge_id": pledge.pledge_id,
                        "donor_id": pledge.donor_id,
                        "available_quantity": pledge.available_quantity,
                        "distance": distances[pledge.donor_zipcode]
                    })
            
            # Sort pledges by distance (nearest first)
            sorted_pledges.sort(key=lambda p: p["distance"])
            
        except Exception as e:
            print(f"Error fetching distances: {e}")
            # Fall back to fulfillment matching if distance API fails
            return find_most_fulfilled(request_id, match_type_id, quantity_needed)
        
        # Create matches from sorted pledges
        matches_created = 0
        total_matched = 0
        
        for pledge in sorted_pledges:
            if total_matched >= quantity_needed:
                break
                
            match_quantity = min(pledge["available_quantity"], quantity_needed - total_matched)
            
            if match_quantity <= 0:
                continue
                
            # Create the match
            create_match_sp = text("""
                CALL dr_events.create_match(
                    :pledge_id, 
                    :request_id, 
                    :match_quantity, 
                    'matched', 
                    :match_type_id
                )
            """)
            
            db.session.execute(create_match_sp, {
                "pledge_id": pledge["pledge_id"],
                "request_id": request_id,
                "match_quantity": match_quantity,
                "match_type_id": match_type_id
            })
            
            db.session.commit()
            
            total_matched += match_quantity
            matches_created += 1
            
        return matches_created
            
    except Exception as e:
        print(f"Error in find_nearest: {e}")
        db.session.rollback()
        return 0


def find_quickest(request_id, match_type_id, quantity_needed):
    """
    Find and match pledges based on quickest shipping time
    
    Args:
        request_id: ID of the request to match
        match_type_id: ID of the match type
        quantity_needed: Maximum quantity to match from pledges
        
    Returns:
        Number of matches created
    """
    db = get_db()
    
    try:
        # Get request details
        request_query = text("""
            SELECT request_id, item_id
            FROM dr_events.request
            WHERE request_id = :request_id
        """)
        
        request_info = db.session.execute(request_query, {"request_id": request_id}).fetchone()
        
        if not request_info:
            return 0
        
        # Get available pledges sorted by days_to_ship
        pledges_query = text("""
            SELECT p.pledge_id, p.user_id AS donor_id, p.item_id, 
                   p.days_to_ship,
                   (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) AS available_quantity
            FROM dr_events.pledge p
            WHERE p.item_id = :item_id
              AND p.canceled_flag = 0
              AND (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) > 0
            ORDER BY p.days_to_ship ASC, available_quantity DESC
        """)
        
        pledges = db.session.execute(pledges_query, {"item_id": request_info.item_id}).fetchall()
        
        if not pledges:
            return 0
        
        # Create matches from sorted pledges
        matches_created = 0
        total_matched = 0
        
        for pledge in pledges:
            if total_matched >= quantity_needed:
                break
                
            match_quantity = min(pledge.available_quantity, quantity_needed - total_matched)
            
            if match_quantity <= 0:
                continue
                
            # Create the match
            create_match_sp = text("""
                CALL dr_events.create_match(
                    :pledge_id, 
                    :request_id, 
                    :match_quantity, 
                    'matched', 
                    :match_type_id
                )
            """)
            
            db.session.execute(create_match_sp, {
                "pledge_id": pledge.pledge_id,
                "request_id": request_id,
                "match_quantity": match_quantity,
                "match_type_id": match_type_id
            })
            
            db.session.commit()
            
            total_matched += match_quantity
            matches_created += 1
            
        return matches_created
            
    except Exception as e:
        print(f"Error in find_quickest: {e}")
        db.session.rollback()
        return 0


def find_most_fulfilled(request_id, match_type_id, quantity_needed):
    """
    Find and match pledges to minimize the number of different matches needed
    (prioritize pledges with largest available quantities)
    
    Args:
        request_id: ID of the request to match
        match_type_id: ID of the match type
        quantity_needed: Maximum quantity to match from pledges
        
    Returns:
        Number of matches created
    """
    db = get_db()
    
    try:
        # Get request details
        request_query = text("""
            SELECT request_id, item_id
            FROM dr_events.request
            WHERE request_id = :request_id
        """)
        
        request_info = db.session.execute(request_query, {"request_id": request_id}).fetchone()
        
        if not request_info:
            return 0
        
        # Get available pledges sorted by available quantity (largest first)
        pledges_query = text("""
            SELECT p.pledge_id, p.user_id AS donor_id, p.item_id,
                   (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) AS available_quantity
            FROM dr_events.pledge p
            WHERE p.item_id = :item_id
              AND p.canceled_flag = 0
              AND (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) > 0
            ORDER BY available_quantity DESC
        """)
        
        pledges = db.session.execute(pledges_query, {"item_id": request_info.item_id}).fetchall()
        
        if not pledges:
            return 0
        
        # Create matches from sorted pledges
        matches_created = 0
        total_matched = 0
        
        for pledge in pledges:
            if total_matched >= quantity_needed:
                break
                
            match_quantity = min(pledge.available_quantity, quantity_needed - total_matched)
            
            if match_quantity <= 0:
                continue
                
            # Create the match
            create_match_sp = text("""
                CALL dr_events.create_match(
                    :pledge_id, 
                    :request_id, 
                    :match_quantity, 
                    'matched', 
                    :match_type_id
                )
            """)
            
            db.session.execute(create_match_sp, {
                "pledge_id": pledge.pledge_id,
                "request_id": request_id,
                "match_quantity": match_quantity,
                "match_type_id": match_type_id
            })
            
            db.session.commit()
            
            total_matched += match_quantity
            matches_created += 1
            
        return matches_created
            
    except Exception as e:
        print(f"Error in find_most_fulfilled: {e}")
        db.session.rollback()
        return 0