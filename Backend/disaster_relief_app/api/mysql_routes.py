from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import bcrypt
import datetime
import jwt
from disaster_relief_app.utils import decode_required_token, get_db

general_responses = { 200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 500: 'Internal Server Error' }

api_routes = Blueprint('api_routes', __name__)

# Secret key - THIS IS TEMPORARY - HOW DO WE STORE IN ENVIRONMENT VARIABLE IN GITLAB??
SECRET_KEY = "disaster_relief_team_3_for_the_win"

    
@api_routes.route('/requestNewAccount', methods=["POST"])
def request_new_account():
    db = get_db()
    data_payload = request.get_json()    

    try:
        requested_username = data_payload.get("username")
        requested_password = data_payload.get("password")
        requested_role = data_payload.get("role")
        email = data_payload.get("email")
        address_line1 = data_payload.get("addressline1")
        address_line2 = data_payload.get("addressline2")
        city = data_payload.get("city")
        state = data_payload.get("state")
        zip_code = data_payload.get("zipcode")
        approved_flag = 0


        #Verify valid inputs
        if not requested_username or not requested_password or not requested_role:
            return jsonify({"error": "Missing requird fields"}), 400
      
        #Check if username exists
        existing_username_query = "SELECT * FROM user WHERE username = :username"
        existing_username = db.session.execute(text(existing_username_query), ({"username": requested_username})).fetchone()
        print(existing_username)

        if existing_username:
            #Return error if username already exists
            return jsonify({"error": "Username already exists!"}), 400
      
        hashed_password = bcrypt.hashpw(requested_password.encode('utf-8'), bcrypt.gensalt())
       
        new_user_query = "INSERT INTO user (username, password, role, email, zip_code, is_approved, address_line1, address_line2, city, state) VALUES (:username, :hashed_password, :role, :email, :zip_code, :approved_flag, :address_line1, :address_line2, :city, :state)"
        db.session.execute((text(new_user_query)), ({"username": requested_username, "hashed_password": hashed_password, "role": requested_role, "email": email, "zip_code": zip_code, "approved_flag": approved_flag, "address_line1": address_line1, "address_line2": address_line2, "city": city, "state": state}))
        db.session.commit() #Save to db

        return jsonify({"message": "User request created successfully"}), 201
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    

@api_routes.route('/login', methods=["POST"])
def login():
    db = get_db()
    data_payload = request.get_json()    

    try:
        username = data_payload.get("username")
        password = data_payload.get("password")

        #Verify valid inputs
        if not username or not password:
            return jsonify({"error": "Missing requird fields"}), 400
        
        #Check if user exists
        existing_user_query = text("SELECT * FROM user WHERE is_approved = 1 AND username = :username")
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            #Return error if username already exists
            return jsonify({"error": "User does not exist"}), 401
        
        #Check for correct password
        if bcrypt.checkpw(password.encode('utf-8'), existing_user.password):
            claims = {"user_id": existing_user.user_id, "username": username, "role": existing_user.role, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)}
            token = jwt.encode(claims, SECRET_KEY, algorithm="HS256") 

            response = make_response(claims)# make_response(jsonify({"message": "Login successfull"}))
            response.set_cookie("jwt_token", token, httponly=True, secure=True)
            return response, 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except SQLAlchemyError as ex:
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:   
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    

@api_routes.route('/resetPassword', methods=["POST"])
def reset_password():
    db = get_db()
    data_payload = request.get_json()    

    try:
        username = data_payload.get("username")
        old_password = data_payload.get("old_password")
        new_password = data_payload.get("password")

        #Verify valid inputs
        if not username or not old_password or not new_password:
            return jsonify({"error": "Missing requird fields"}), 400
        
        #Check if user exists
        existing_user_query = "SELECT * FROM user WHERE is_approved = 1 AND username = :username"
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            #Return error if username already exists
            return jsonify({"error": "User does not exist"}), 401
        
        #Check for old password matches
        if bcrypt.checkpw(new_password.encode('utf-8'), existing_user.password):
            #Change password
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            update_password_query = """UPDATE user
                                SET password = :password
                                WHERE is_approved = 1 AND username = :username"""
            db.session.execute(update_password_query, {"password": hashed_new_password, "username": username})
            db.session.commit() #Save to db

            return jsonify({"message": "Password successfully updated"}), 200
        else:
            return jsonify({"message": "Invalid credentials - Unauthorized to update password"}), 401
    except SQLAlchemyError as ex:
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:  
        db.session.rollback()
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/resetForgottenPassword', methods=["POST"])
def reset_forgotten_password():
    db = get_db()
    data_payload = request.get_json()    

    try:
        username = data_payload.get("username")
        new_password = data_payload.get("new_password")

        #Verify valid inputs
        if not username or not new_password:
            return jsonify({"error": "Missing requird fields"}), 400
        
        
        #Check if user exists
        existing_user_query = text("SELECT * FROM user WHERE is_approved = 1 AND username = :username")
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            #Return error if username already exists
            return jsonify({"error": "User does not exist"}), 401
        
        
        #Change password
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_password_query = text("UPDATE user SET password = :password WHERE is_approved = 1 AND username = :username")
        db.session.execute(update_password_query, {"password": hashed_new_password, "username": username})
        db.session.commit() #Save to db

        return jsonify({"message": "Password successfully updated"}), 200
        
    except SQLAlchemyError as ex:
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:  
        db.session.rollback()
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
#End Region


@api_routes.route('/getActiveEvents', methods=["GET"])
def get_active_events():
    db = get_db()
    try:
        query = text("SELECT * FROM dr_events.disaster_event WHERE is_active = 1")  
        events = db.session.execute(query).fetchall()

        events_list = [
            {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "location": event.location,
                "start_date": event.start_date.strftime("%Y-%m-%d") if event.start_date else None,
                "end_date": event.end_date.strftime("%Y-%m-%d") if event.end_date else None,
                "description": event.description
            }
            for event in events
        ]

        return jsonify(events_list), 200

    except SQLAlchemyError as ex:
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@api_routes.route('/getEventCategories/<int:event_id>', methods=["GET"])
def get_event_categories(event_id):
    db = get_db()
    try:
        query = text("""
            SELECT c.* FROM dr_events.category c
            JOIN dr_events.event_category ec ON c.category_id = ec.category_id
            WHERE ec.event_id = :event_id
        """)
        categories = db.session.execute(query, {"event_id": event_id}).fetchall()

        categories_list = [
            {
                "category_id": category.category_id,
                "category_name": category.category_name,
                "description": category.description
            }
            for category in categories
        ]

        return jsonify(categories_list), 200

    except SQLAlchemyError as ex:
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@api_routes.route('/createRequest', methods=["POST"])
def create_request():
    db = get_db()
    data_payload = request.get_json()

    try:
        user_id = data_payload.get("user_id")
        event_id = data_payload.get("event_id")
        category_id = data_payload.get("category_id")
        item_id = data_payload.get("item_id")  # New field for specific item
        quantity = data_payload.get("quantity")
        details = data_payload.get("details", "")
        status = data_payload.get("status", "pending")

        if not all([user_id, event_id, category_id, quantity]):
            return jsonify({"error": "Missing required fields"}), 400

        event_query = text("SELECT * FROM dr_events.disaster_event WHERE event_id = :event_id AND is_active = 1")
        event = db.session.execute(event_query, {"event_id": event_id}).fetchone()

        if not event:
            return jsonify({"error": "Event not found or not active"}), 404

        category_query = text("""
            SELECT * FROM dr_events.event_category 
            WHERE event_id = :event_id AND category_id = :category_id
        """)
        category = db.session.execute(category_query, {
            "event_id": event_id,
            "category_id": category_id
        }).fetchone()

        if not category:
            return jsonify({"error": "Category not available for this event"}), 400

        # If item_id is provided, verify it belongs to the selected category
        if item_id:
            item_query = text("""
                SELECT * FROM dr_events.item 
                WHERE item_id = :item_id AND category_id = :category_id
            """)
            item = db.session.execute(item_query, {
                "item_id": item_id,
                "category_id": category_id
            }).fetchone()

            if not item:
                return jsonify({"error": "Item not available in this category"}), 400

        insert_query = text("""
            INSERT INTO dr_events.request 
            (user_id, event_id, category_id, item_id, quantity, details, status, created_at) 
            VALUES (:user_id, :event_id, :category_id, :item_id, :quantity, :details, :status, NOW())
        """)

        db.session.execute(insert_query, {
            "user_id": user_id,
            "event_id": event_id,
            "category_id": category_id,
            "item_id": item_id,  # Can be NULL if not specified
            "quantity": quantity,
            "details": details,
            "status": status
        })

        db.session.commit()

        return jsonify({"message": "Request created successfully"}), 201

    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        db.session.rollback()
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@api_routes.route('/getCategories', methods=["GET"])
def get_categories():
    db = get_db()

    try:
        get_category_query = "SELECT * FROM dr_events.category"
        result = db.session.execute((text(get_category_query)))

        categories = [dict(row) for row in result.mappings()]
        
        return jsonify(categories), 200
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/getItems', methods=["GET"])
def get_items():
    db = get_db()

    try:
        get_item_query = "SELECT * FROM dr_events.item"
        result = db.session.execute((text(get_item_query)))

        items = [dict(row) for row in result.mappings()]
        
        return jsonify(items), 200
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    

@api_routes.route('/getRequests', methods=["GET"])
def get_requests():
    db = get_db()

    user_id = request.args.get('user_id')
    request_id = request.args.get('request_id')
    try:
        if not user_id:
            return jsonify({"error": "Missing requird fields"}), 400
       
        get_requests_sp = "CALL dr_events.get_requests(:param_user_id, :request_id)"
        result = db.session.execute((text(get_requests_sp)), ({"param_user_id": user_id, "request_id": request_id}))
        try:
            rows = result.fetchall()

            if rows:            
                columns = result.keys()

                matches = [dict(zip(columns, row)) for row in rows]
            
                return jsonify(matches), 200    
            return []    
        except Exception as ex:   
            return []
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    

@api_routes.route('/createPledge', methods=["POST"])
def create_pledge():
    db = get_db()
    data_payload = request.get_json()    

    try:
        user_id = data_payload.get("user_id")
        selected_category_id = data_payload.get("selected_category_id")
        selected_item_id = data_payload.get("selected_item_id")
        item_quantity = data_payload.get("item_quantity")
        days_to_ship = data_payload.get("days_to_ship")

        #Verify valid inputs
        if not user_id or not selected_category_id or not selected_item_id or not item_quantity:
            return jsonify({"error": "Missing requird fields"}), 400
        
        #Confirm user_id has role of donor
        confirm_user_role_query = "SELECT * FROM user WHERE user_id = :user_id"
        confirm_user_role = db.session.execute(text(confirm_user_role_query), ({"user_id": user_id})).fetchone()

        if confirm_user_role.role != 'Donor':
            #Return error if username already exists
            return jsonify({"error": "User does not have permisson!"}), 400

        new_pledge_query = "INSERT INTO dr_events.pledge (user_id, item_id, item_quantity, days_to_ship) VALUES (:user_id, :item_id, :item_quantity, :days_to_ship)"
        db.session.execute((text(new_pledge_query)), ({"user_id": user_id, "item_id": selected_item_id, "item_quantity": item_quantity, "days_to_ship": days_to_ship}))
        db.session.commit() #Save to db

        return jsonify({"message": "Pledge request created successfully"}), 201
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/cancelPledge/<int:pledge_id>', methods=["POST"])
def cancel_pledge(pledge_id):
    db = get_db()
    try:
        query = text("""
            CALL dr_events.cancel_pledge(:pledge_id)
        """)
        db.session.execute(query, {"pledge_id": pledge_id})
        db.session.commit() #Save to db

        return jsonify({"message": "Pledge canceled successfully"}), 200
    
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/updatePledge', methods=["POST"])
def update_pledge():
    db = get_db()
    data_payload = request.get_json()    

    try:
        pledge_id = data_payload.get("pledge_id")
        item_quantity = data_payload.get("item_quantity")

        query = text("""
            UPDATE dr_events.pledge
            SET item_quantity = :item_quantity
            WHERE pledge.pledge_id = :pledge_id
        """)
        db.session.execute(query, {"item_quantity": item_quantity, "pledge_id": pledge_id})
        db.session.commit() #Save to db

        return jsonify({"message": "Pledge updated successfully"}), 200
    
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/getPledges', methods=["GET"])
def get_pledges():
    db = get_db()

    user_id = request.args.get('user_id')
    try:
        if not user_id:
            return jsonify({"error": "user_id"}), 400
       
        get_pledges_sp = "CALL dr_events.get_pledges(:param_user_id)"
        result = db.session.execute((text(get_pledges_sp)), ({"param_user_id": user_id}))

        try:
            rows = result.fetchall()

            if rows:            
                columns = result.keys()

                pledges = [dict(zip(columns, row)) for row in rows]
            
                return jsonify(pledges), 200   
            return []     
        except Exception as ex:   
            return []
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    

# Matches  
@api_routes.route('/createMatch', methods=["POST"])
def create_match():
    db = get_db()
    data_payload = request.get_json()    

    try:
        request_id = data_payload.get("requestId")
        pledge_id = data_payload.get("pledgeId")
        match_quantity = data_payload.get("matchQuantity")
        match_status = 'matched',
        match_type = 1

        #Verify valid inputs
        if not request_id or not pledge_id or not match_quantity:
            return jsonify({"error": "Missing requird fields"}), 400
       
        create_match_sp = "CALL dr_events.create_match(:param_pledge_id, :param_request_id, :param_match_quantity, :param_match_status, :match_type)"
        db.session.execute((text(create_match_sp)), ({"param_pledge_id": pledge_id, "param_request_id": request_id, "param_match_quantity": match_quantity, "param_match_status": match_status, "match_type": match_type}))
        db.session.commit() #Save to db

        return jsonify({"message": "Match request created successfully"}), 200
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
@api_routes.route('/getMatches', methods=["GET"])
def get_matches():
    db = get_db()

    user_id = request.args.get('user_id')
    try:
        if not user_id:
            return jsonify({"error": "Missing requird fields"}), 400
       
        get_matches_sp = "CALL dr_events.get_matches(:param_user_id)"
        result = db.session.execute((text(get_matches_sp)), ({"param_user_id": user_id}))

        try:
            rows = result.fetchall()

            if rows:            
                columns = result.keys()

                matches = [dict(zip(columns, row)) for row in rows]
            
                return jsonify(matches), 200  
            return jsonify([]), 200  # Return empty array instead of just []     
        except Exception as ex:   
            return jsonify([]), 200  # Return empty array instead of just []
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@api_routes.route('/getRequestsForResponse', methods=["GET"])
def get_requests_for_response():
    db = get_db()
    try:
        query = text("""
            SELECT r.request_id, r.details, r.quantity, r.status, u.username, 
                e.event_name, c.category_name, i.name as item_name
                ,CASE WHEN current_matches.request_id IS NULL THEN r.quantity
				WHEN r.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(r.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining
            FROM dr_events.request r
            JOIN user u ON r.user_id = u.user_id
            JOIN dr_events.disaster_event e ON r.event_id = e.event_id
            JOIN dr_events.category c ON r.category_id = c.category_id
            LEFT JOIN dr_events.item i ON r.item_id = i.item_id     
            LEFT OUTER JOIN
			(
				select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				from dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON r.request_id = current_matches.request_id        
            WHERE r.status = 'pending' 
        """)
        results = db.session.execute(query).fetchall()

        requests = [
            {
                "request_id": row.request_id,
                "details": row.details,
                "quantity": row.quantity,
                "status": row.status,
                "requested_by": row.username,
                "event_name": row.event_name,
                "category": row.category_name,
                "item_name": row.item_name,  # Will be None if no specific item
                "request_quantity_remaining": row.request_quantity_remaining
            }
            for row in results
        ]

        return jsonify(requests), 200

    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@api_routes.route('/getRequestDetails/<int:request_id>', methods=["GET"])
def get_request_details(request_id):
    db = get_db()
    try:
        query = text("""
            SELECT r.request_id, r.details, r.quantity, r.status, u.username, 
                   e.event_name, c.category_name, i.name as item_name
            FROM dr_events.request r
            JOIN user u ON r.user_id = u.user_id
            JOIN dr_events.disaster_event e ON r.event_id = e.event_id
            JOIN dr_events.category c ON r.category_id = c.category_id
            LEFT JOIN dr_events.item i ON r.item_id = i.item_id
            WHERE r.request_id = :request_id
        """)
        row = db.session.execute(query, {"request_id": request_id}).fetchone()

        if not row:
            return jsonify({"error": "Request not found"}), 404

        request_data = {
            "request_id": row.request_id,
            "details": row.details,
            "quantity": row.quantity,
            "status": row.status,
            "requested_by": row.username,
            "event_name": row.event_name,
            "category": row.category_name,
            "item_name": row.item_name  # Will be None if no specific item
        }

        return jsonify(request_data), 200

    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/submitResponse', methods=["POST"])
def submit_response():
    db = get_db()
    data = request.get_json()
    
    try:
        request_id = data.get("request_id")
        donor_id = data.get("donor_id")  
        quantity = data.get("quantity")
        message = data.get("message", "")

        if not request_id or not donor_id or not quantity:
            return jsonify({"error": "Missing required fields"}), 400

        # Insert the pledge/response
        insert_query = text("""
            INSERT INTO dr_events.response (request_id, donor_id, quantity, message, responded_at)
            VALUES (:request_id, :donor_id, :quantity, :message, NOW())
        """)
        db.session.execute(insert_query, {
            "request_id": request_id,
            "donor_id": donor_id,
            "quantity": quantity,
            "message": message
        })

        update_query = text("UPDATE dr_events.request SET status = 'approved' WHERE request_id = :request_id")
        db.session.execute(update_query, {"request_id": request_id})

        db.session.commit()
        return jsonify({"message": "Response submitted successfully"}), 201

    except Exception as ex:
        db.session.rollback()
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/getItemsByCategory/<int:category_id>', methods=["GET"])
def get_items_by_category(category_id):
    db = get_db()
    try:
        query = text("""
            SELECT item_id, name, description 
            FROM dr_events.item 
            WHERE category_id = :category_id
        """)
        results = db.session.execute(query, {"category_id": category_id}).fetchall()

        items = [
            {
                "item_id": row.item_id,
                "name": row.name,
                "description": row.description
            }
            for row in results
        ]

        return jsonify(items), 200

    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500