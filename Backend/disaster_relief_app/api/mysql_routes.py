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
        approved_flag = 1  # CHANGED: Auto-approve new users

        #Verify valid inputs
        if not requested_username or not requested_password or not requested_role:
            return jsonify({"error": "Missing required fields"}), 400
      
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

        return jsonify({"message": "User account created successfully and approved"}), 201
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
    print("Received login request with payload:", data_payload)

    try:
        username = data_payload.get("username")
        password = data_payload.get("password")

        print(f"Processing login for username: {username}")

        # Verify valid inputs
        if not username or not password:
            print("Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400
        
        # FIXED: Check if user exists with proper schema reference
        existing_user_query = text("SELECT * FROM dr_admin.user WHERE is_approved = 1 AND username = :username")
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            print(f"User not found: {username}")
            return jsonify({"error": "User does not exist"}), 401
        
        print(f"User found: {username}, checking password")
        
        # Check for correct password
        if bcrypt.checkpw(password.encode('utf-8'), existing_user.password):
            claims = {
                "user_id": existing_user.user_id, 
                "username": username, 
                "role": existing_user.role, 
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            }
            token = jwt.encode(claims, SECRET_KEY, algorithm="HS256") 

            # Properly format response as JSON
            response = make_response(jsonify(claims))
            response.set_cookie("jwt_token", token, httponly=True, secure=False, samesite="Lax")
            
            # FIXED: Update CORS headers for Railway deployment
            allowed_origins = [
                "http://localhost:3000",
                "https://dams-disaster-aid-management-system.netlify.app"
            ]
            origin = request.headers.get('Origin')
            if origin in allowed_origins:
                response.headers.add("Access-Control-Allow-Origin", origin)
                response.headers.add("Access-Control-Allow-Credentials", "true")
            
            print(f"Login successful for {username}, role: {existing_user.role}")
            print(f"Response data: {claims}")
            return response
        else:
            print(f"Invalid password for {username}")
            return jsonify({"error": "Invalid credentials"}), 401
    except SQLAlchemyError as ex:
        print(f"Database error: {ex}")
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        print(f"Internal server error: {ex}")
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

        # Verify valid inputs
        if not username or not new_password:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check if user exists - FIXED: Use get_db() properly
        existing_user_query = text("SELECT * FROM dr_admin.user WHERE is_approved = 1 AND username = :username")
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            return jsonify({"error": "User does not exist"}), 401
        
        # Change password
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_password_query = text("UPDATE dr_admin.user SET password = :password WHERE is_approved = 1 AND username = :username")
        db.session.execute(update_password_query, {"password": hashed_new_password, "username": username})
        db.session.commit()

        return jsonify({"message": "Password successfully updated"}), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        print(f"Database error in reset_forgotten_password: {ex}")
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:  
        db.session.rollback()
        print(f"General error in reset_forgotten_password: {ex}")
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
        item_id = data_payload.get("item_id")  
        quantity = data_payload.get("quantity")
        details = data_payload.get("details", "")
        status = data_payload.get("status", "pending")
        preferred_match_type_id = data_payload.get("preferred_match_type_id")  # New field

        if not all([user_id, event_id, category_id, quantity, preferred_match_type_id]):
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

        # Validate match type exists
        match_type_query = text("SELECT * FROM dr_events.match_type WHERE match_type_id = :match_type_id")
        match_type = db.session.execute(match_type_query, {"match_type_id": preferred_match_type_id}).fetchone()

        if not match_type:
            return jsonify({"error": "Invalid match type"}), 400

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
            (user_id, event_id, category_id, item_id, quantity, details, status, preferred_match_type_id, created_at) 
            VALUES (:user_id, :event_id, :category_id, :item_id, :quantity, :details, :status, :preferred_match_type_id, NOW())
        """)

        db.session.execute(insert_query, {
            "user_id": user_id,
            "event_id": event_id,
            "category_id": category_id,
            "item_id": item_id,
            "quantity": quantity,
            "details": details,
            "status": status,
            "preferred_match_type_id": preferred_match_type_id
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
    
    # Convert 'undefined' string to None
    if request_id == 'undefined' or request_id == '':
        request_id = None
    elif request_id is not None:
        try:
            request_id = int(request_id)
        except (ValueError, TypeError):
            request_id = None
    
    try:
        if not user_id:
            return jsonify({"error": "Missing required fields"}), 400
       
        get_requests_sp = "CALL dr_events.get_requests(:param_user_id, :request_id)"
        result = db.session.execute(text(get_requests_sp), {
            "param_user_id": int(user_id), 
            "request_id": request_id
        })
        
        try:
            rows = result.fetchall()

            if rows:            
                columns = result.keys()
                requests = [dict(zip(columns, row)) for row in rows]
                return jsonify(requests), 200    
            return jsonify([]), 200    
        except Exception as ex:   
            print(f"Error processing results: {ex}")
            return jsonify([]), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        print(f"Database error in get_requests: {ex}")
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        print(f"General error in get_requests: {ex}")
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

        # Debug logging
        print("Received pledge data:", data_payload)

        # Enhanced validation with specific error messages
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
            
        if not selected_category_id:
            return jsonify({"error": "Missing selected_category_id"}), 400
            
        if not selected_item_id:
            return jsonify({"error": "Missing selected_item_id"}), 400
            
        if not item_quantity:
            return jsonify({"error": "Missing item_quantity"}), 400
            
        try:
            item_quantity = int(item_quantity)
            if item_quantity < 1:
                return jsonify({"error": "Item quantity must be at least 1"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Item quantity must be a valid number"}), 400

        # Validate days_to_ship if provided
        if days_to_ship is not None:
            try:
                days_to_ship = int(days_to_ship)
                if days_to_ship < 1:
                    return jsonify({"error": "Days to ship must be at least 1"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Days to ship must be a valid number"}), 400
        
        # Confirm user has donor role
        confirm_user_role_query = "SELECT * FROM user WHERE user_id = :user_id"
        confirm_user_role = db.session.execute(text(confirm_user_role_query), {"user_id": user_id}).fetchone()

        if not confirm_user_role:
            return jsonify({"error": "User not found"}), 404

        if confirm_user_role.role not in ['Donor', 'Admin']:
            return jsonify({"error": "User does not have permission to create pledges"}), 403

        # Create the pledge
        new_pledge_query = "INSERT INTO dr_events.pledge (user_id, item_id, item_quantity, days_to_ship) VALUES (:user_id, :item_id, :item_quantity, :days_to_ship)"
        db.session.execute(text(new_pledge_query), {
            "user_id": user_id, 
            "item_id": selected_item_id, 
            "item_quantity": item_quantity, 
            "days_to_ship": days_to_ship
        })
        db.session.commit()

        return jsonify({"message": "Pledge request created successfully"}), 201
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        print("Database error:", ex)
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        db.session.rollback()
        print("General error:", ex)
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
    

    

# Matches  
@api_routes.route('/createMatch', methods=["POST"])
def create_match():
    db = get_db()
    data_payload = request.get_json()    

    try:
        print("=== CREATE MATCH START ===")
        print("Raw request data:", data_payload)
        
        # Extract data with proper error checking
        request_id = data_payload.get("requestId")
        pledge_id = data_payload.get("pledgeId")
        match_quantity = data_payload.get("matchQuantity")
        
        print(f"Extracted - request_id: {request_id}, pledge_id: {pledge_id}, match_quantity: {match_quantity}")
        
        # Validate required fields
        if not request_id:
            print("ERROR: Missing requestId")
            return jsonify({"error": "Missing requestId"}), 400
        if not pledge_id:
            print("ERROR: Missing pledgeId")
            return jsonify({"error": "Missing pledgeId"}), 400
        if not match_quantity:
            print("ERROR: Missing matchQuantity")
            return jsonify({"error": "Missing matchQuantity"}), 400

        # Convert and validate match_quantity
        try:
            match_quantity = int(match_quantity)
            if match_quantity <= 0:
                print(f"ERROR: Invalid match_quantity: {match_quantity}")
                return jsonify({"error": "Match quantity must be greater than 0"}), 400
        except (ValueError, TypeError) as e:
            print(f"ERROR: Cannot convert match_quantity to int: {match_quantity}, error: {e}")
            return jsonify({"error": "Match quantity must be a valid number"}), 400

        print(f"Validated data - request_id: {request_id}, pledge_id: {pledge_id}, match_quantity: {match_quantity}")

        # Check if request exists
        print("Checking if request exists...")
        request_check_query = text("SELECT request_id, status FROM dr_events.request WHERE request_id = :request_id")
        request_exists = db.session.execute(request_check_query, {"request_id": request_id}).fetchone()
        
        if not request_exists:
            print(f"ERROR: Request {request_id} not found")
            return jsonify({"error": "Request not found"}), 404
        
        print(f"Request found: {request_exists.request_id}, status: {request_exists.status}")

        # Check if pledge exists and has enough quantity
        print("Checking pledge availability...")
        pledge_check_query = text("""
            SELECT pledge_id, item_quantity, allocated_quantity, fulfilled_quantity,
                   (item_quantity - (allocated_quantity + fulfilled_quantity)) as available_quantity,
                   canceled_flag
            FROM dr_events.pledge 
            WHERE pledge_id = :pledge_id
        """)
        pledge_data = db.session.execute(pledge_check_query, {"pledge_id": pledge_id}).fetchone()
        
        if not pledge_data:
            print(f"ERROR: Pledge {pledge_id} not found")
            return jsonify({"error": "Pledge not found"}), 404
            
        if pledge_data.canceled_flag:
            print(f"ERROR: Pledge {pledge_id} is canceled")
            return jsonify({"error": "Pledge has been canceled"}), 400
            
        if pledge_data.available_quantity < match_quantity:
            print(f"ERROR: Insufficient pledge quantity. Available: {pledge_data.available_quantity}, Requested: {match_quantity}")
            return jsonify({
                "error": f"Insufficient pledge quantity. Available: {pledge_data.available_quantity}, Requested: {match_quantity}"
            }), 400

        print(f"Pledge valid: available_quantity={pledge_data.available_quantity}")

        # Try to call the stored procedure
        print("Calling stored procedure...")
        try:
            create_match_sp = text("""
                CALL dr_events.create_match(
                    :param_pledge_id, 
                    :param_request_id, 
                    :param_match_quantity, 
                    :param_match_status, 
                    :param_match_type_id
                )
            """)
            
            db.session.execute(create_match_sp, {
                "param_pledge_id": pledge_id,
                "param_request_id": request_id,
                "param_match_quantity": match_quantity,
                "param_match_status": "matched",
                "param_match_type_id": 1
            })
            
            print("Stored procedure executed successfully")
            db.session.commit()
            print("Transaction committed")
            
            return jsonify({"message": "Match created successfully"}), 201
            
        except Exception as sp_error:
            print(f"ERROR in stored procedure: {sp_error}")
            print("Attempting direct implementation...")
            db.session.rollback()
            
            # Fallback: Direct implementation without stored procedure
            try:
                db.session.begin()
                
                # 1. Get shipping address
                print("Getting shipping address...")
                address_query = text("""
                    SELECT concat_ws(' ',
                           address_line1,
                           address_line2,
                           CONCAT_WS(', ',			
                                city,
                                state				
                            ), zip_code) AS full_address
                    FROM dr_events.request
                        INNER JOIN dr_admin.user ON request.user_id = user.user_id
                    WHERE request_id = :request_id
                """)
                
                address_result = db.session.execute(address_query, {"request_id": request_id}).fetchone()
                shipping_address = address_result.full_address if address_result else None
                print(f"Shipping address: {shipping_address}")

                # 2. Create match record
                print("Creating match record...")
                insert_match_query = text("""
                    INSERT INTO dr_events.`match` 
                    (pledge_id, request_id, match_status, match_quantity, match_type_id, shipping_address)
                    VALUES 
                    (:pledge_id, :request_id, 'matched', :match_quantity, 1, :shipping_address)
                """)
                
                db.session.execute(insert_match_query, {
                    "pledge_id": pledge_id,
                    "request_id": request_id,
                    "match_quantity": match_quantity,
                    "shipping_address": shipping_address
                })
                print("Match record created")

                # 3. Update pledge
                print("Updating pledge...")
                update_pledge_query = text("""
                    UPDATE dr_events.pledge
                    SET allocated_quantity = allocated_quantity + :match_quantity, 
                        pledge_status = 'partially allocated'
                    WHERE pledge_id = :pledge_id
                """)
                
                db.session.execute(update_pledge_query, {
                    "pledge_id": pledge_id,
                    "match_quantity": match_quantity
                })
                print("Pledge updated")

                # 4. Update request
                print("Updating request...")
                update_request_query = text("""
                    UPDATE dr_events.request
                    SET status = 'matched'
                    WHERE request_id = :request_id
                """)
                
                db.session.execute(update_request_query, {"request_id": request_id})
                print("Request updated")

                db.session.commit()
                print("Direct implementation successful")
                
                return jsonify({"message": "Match created successfully (direct)"}), 201
                
            except Exception as direct_error:
                print(f"ERROR in direct implementation: {direct_error}")
                db.session.rollback()
                raise direct_error
        
    except SQLAlchemyError as ex:
        print(f"SQLAlchemy error: {ex}")
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        print(f"General error: {ex}")
        print(f"Error type: {type(ex)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    finally:
        print("=== CREATE MATCH END ===")
    
@api_routes.route('/createMatchDirect', methods=["POST"])
def create_match_direct():
    """Direct implementation without stored procedure for debugging"""
    db = get_db()
    data_payload = request.get_json()    

    try:
        request_id = data_payload.get("requestId")
        pledge_id = data_payload.get("pledgeId")
        match_quantity = data_payload.get("matchQuantity")

        print("Creating match directly:", data_payload)

        # Validate inputs
        if not all([request_id, pledge_id, match_quantity]):
            return jsonify({"error": "Missing required fields"}), 400

        match_quantity = int(match_quantity)
        if match_quantity <= 0:
            return jsonify({"error": "Invalid match quantity"}), 400

        # Start transaction
        db.session.begin()

        # 1. Get shipping address for the recipient
        address_query = text("""
            SELECT concat_ws(' ',
                   address_line1,
                   address_line2,
                   CONCAT_WS(', ',			
                        city,
                        state				
                    ), zip_code) AS full_address
            FROM dr_events.request
                INNER JOIN dr_admin.user ON request.user_id = user.user_id
            WHERE request_id = :request_id
        """)
        
        address_result = db.session.execute(address_query, {"request_id": request_id}).fetchone()
        shipping_address = address_result.full_address if address_result else None

        # 2. Create the match record
        insert_match_query = text("""
            INSERT INTO dr_events.`match` 
            (pledge_id, request_id, match_status, match_quantity, match_type_id, shipping_address)
            VALUES 
            (:pledge_id, :request_id, 'matched', :match_quantity, 1, :shipping_address)
        """)
        
        db.session.execute(insert_match_query, {
            "pledge_id": pledge_id,
            "request_id": request_id,
            "match_quantity": match_quantity,
            "shipping_address": shipping_address
        })

        # 3. Update pledge's allocated_quantity
        update_pledge_query = text("""
            UPDATE dr_events.pledge
            SET allocated_quantity = allocated_quantity + :match_quantity, 
                pledge_status = 'partially allocated'
            WHERE pledge_id = :pledge_id
        """)
        
        db.session.execute(update_pledge_query, {
            "pledge_id": pledge_id,
            "match_quantity": match_quantity
        })

        # 4. Update request's status
        update_request_query = text("""
            UPDATE dr_events.request
            SET status = 'matched'
            WHERE request_id = :request_id
        """)
        
        db.session.execute(update_request_query, {"request_id": request_id})

        # Commit the transaction
        db.session.commit()

        return jsonify({"message": "Match created successfully"}), 201

    except SQLAlchemyError as ex:
        db.session.rollback()
        print("Database error in create_match_direct:", ex)
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        db.session.rollback()
        print("General error in create_match_direct:", ex)
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/getMatches', methods=["GET"])
def get_matches():
    db = get_db()

    user_id = request.args.get('user_id')
    try:
        if not user_id:
            return jsonify({"error": "Missing required fields"}), 400
       
        # Instead of calling stored procedure, use direct query to ensure fresh data
        # Get user role first
        user_role_query = text("SELECT role FROM dr_admin.user WHERE user_id = :user_id")
        user_role_result = db.session.execute(user_role_query, {"user_id": user_id}).fetchone()
        
        if not user_role_result:
            return jsonify({"error": "User not found"}), 404
            
        user_role = user_role_result.role
        
        # Build query based on user role to match stored procedure logic
        if user_role == 'Donor':
            query = text("""
                SELECT 
                    m.match_id,
                    m.pledge_id,
                    de.event_id,
                    de.event_name,
                    de.location,
                    i.name AS item_name,
                    i.item_id,
                    c.category_id,
                    c.category_name,
                    m.request_id,
                    m.match_status,
                    m.match_quantity,
                    m.created_at,
                    m.shipping_status
                FROM dr_events.match m
                JOIN dr_events.request r ON m.request_id = r.request_id
                JOIN dr_events.disaster_event de ON r.event_id = de.event_id
                JOIN dr_events.category c ON r.category_id = c.category_id
                LEFT JOIN dr_events.pledge p ON m.pledge_id = p.pledge_id
                LEFT JOIN dr_events.item i ON r.item_id = i.item_id
                WHERE (p.user_id = :user_id OR m.pledge_id IS NULL)
                  AND m.canceled_flag = 0
            """)
        elif user_role == 'Recipient':
            query = text("""
                SELECT 
                    m.match_id,
                    m.pledge_id,
                    de.event_id,
                    de.event_name,
                    de.location,
                    i.name AS item_name,
                    i.item_id,
                    c.category_id,
                    c.category_name,
                    m.request_id,
                    m.match_status,
                    m.match_quantity,
                    m.created_at,
                    m.shipping_status
                FROM dr_events.match m
                JOIN dr_events.request r ON m.request_id = r.request_id
                JOIN dr_events.disaster_event de ON r.event_id = de.event_id
                JOIN dr_events.category c ON r.category_id = c.category_id
                LEFT JOIN dr_events.item i ON r.item_id = i.item_id
                WHERE r.user_id = :user_id
                  AND m.canceled_flag = 0
            """)
        else:  # Admin
            query = text("""
                SELECT 
                    m.match_id,
                    m.pledge_id,
                    de.event_id,
                    de.event_name,
                    de.location,
                    i.name AS item_name,
                    i.item_id,
                    c.category_id,
                    c.category_name,
                    m.request_id,
                    m.match_status,
                    m.match_quantity,
                    m.created_at,
                    m.shipping_status
                FROM dr_events.match m
                JOIN dr_events.request r ON m.request_id = r.request_id
                JOIN dr_events.disaster_event de ON r.event_id = de.event_id
                JOIN dr_events.category c ON r.category_id = c.category_id
                LEFT JOIN dr_events.item i ON r.item_id = i.item_id
                WHERE m.canceled_flag = 0
            """)
        
        result = db.session.execute(query, {"user_id": user_id})
        rows = result.fetchall()

        if rows:            
            columns = result.keys()
            matches = [dict(zip(columns, row)) for row in rows]
            return jsonify(matches), 200
        else:
            return jsonify([]), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/getRequestsForResponse', methods=["GET"])
def get_requests_for_response():
    db = get_db()
    try:
        query = text("""
            SELECT r.request_id, r.details, r.quantity, r.status, u.username, 
                e.event_name, e.location as event_location, c.category_name, i.name as item_name,
                r.preferred_match_type_id, mt.name as preferred_match_type_name, mt.description as preferred_match_type_description,
                CASE WHEN current_matches.request_id IS NULL THEN r.quantity
				WHEN r.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(r.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining
            FROM dr_events.request r
            JOIN user u ON r.user_id = u.user_id
            JOIN dr_events.disaster_event e ON r.event_id = e.event_id
            JOIN dr_events.category c ON r.category_id = c.category_id
            LEFT JOIN dr_events.item i ON r.item_id = i.item_id
            LEFT JOIN dr_events.match_type mt ON r.preferred_match_type_id = mt.match_type_id     
            LEFT OUTER JOIN
			(
				select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				from dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON r.request_id = current_matches.request_id        
            WHERE r.status IN ('pending', 'matched') 
            AND (
                current_matches.request_id IS NULL 
                OR r.quantity > current_matches.total_matched
            )
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
                "event_location": row.event_location,  # Added event location
                "category": row.category_name,
                "item_name": row.item_name,
                "preferred_match_type_id": row.preferred_match_type_id,
                "preferred_match_type_name": row.preferred_match_type_name,
                "preferred_match_type_description": row.preferred_match_type_description,
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
                   e.event_name, c.category_name, i.name as item_name,
                   r.category_id, r.item_id, c.category_id as category_id_check,
                   r.preferred_match_type_id, mt.name as preferred_match_type_name, 
                   mt.description as preferred_match_type_description,
                   e.location as event_location,
                   CASE WHEN current_matches.request_id IS NULL THEN r.quantity
				WHEN r.quantity - current_matches.total_matched < 0 THEN 0
				ELSE IFNULL(r.quantity, 0) - IFNULL(current_matches.total_matched, 0) END AS request_quantity_remaining
            FROM dr_events.request r
            JOIN dr_admin.user u ON r.user_id = u.user_id
            JOIN dr_events.disaster_event e ON r.event_id = e.event_id
            JOIN dr_events.category c ON r.category_id = c.category_id
            LEFT JOIN dr_events.item i ON r.item_id = i.item_id
            LEFT JOIN dr_events.match_type mt ON r.preferred_match_type_id = mt.match_type_id
            LEFT OUTER JOIN
			(
				select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
				from dr_events.`match`
				WHERE `match`.canceled_flag = 0
				GROUP BY `match`.request_id
			) current_matches ON r.request_id = current_matches.request_id 
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
            "event_location": row.event_location,
            "category": row.category_name,
            "category_id": row.category_id,  # Make sure this field is included
            "item_name": row.item_name,
            "item_id": row.item_id,  # Make sure this field is included
            "preferred_match_type_id": row.preferred_match_type_id,
            "preferred_match_type_name": row.preferred_match_type_name,
            "preferred_match_type_description": row.preferred_match_type_description,
            "request_quantity_remaining": row.request_quantity_remaining
        }

        print("Returning request data:", request_data)  # Debug logging
        return jsonify(request_data), 200

    except Exception as ex:
        print("Error in get_request_details:", ex)
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

        # Get current total matched quantity after this new response
        match_sum_query = text("""
            SELECT COALESCE(SUM(quantity), 0) AS total_responded
            FROM dr_events.response
            WHERE request_id = :request_id
        """)
        match_sum = db.session.execute(match_sum_query, {"request_id": request_id}).scalar()

        # Get original request quantity
        request_quantity_query = text("""
            SELECT quantity FROM dr_events.request WHERE request_id = :request_id
        """)
        request_quantity = db.session.execute(request_quantity_query, {"request_id": request_id}).scalar()

        # Only mark as approved if fully responded to
        if match_sum >= request_quantity:
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
    
# Add this to mysql_routes.py file

@api_routes.route('/getItemAvailability', methods=["GET"])
def get_item_availability():
    db = get_db()
    try:
        # Query that combines item definitions with available quantities from pledges
        query = text("""
            SELECT 
                i.item_id,
                i.name, 
                i.description,
                i.category_id,
                c.category_name,
                i.quantity AS base_quantity,  -- Base quantity added by admin
                COALESCE(pledge_totals.total_pledged, 0) AS total_pledged,
                COALESCE(pledge_totals.available, 0) AS available_pledged,
                COALESCE(pledge_totals.total_pledged, 0) + i.quantity AS total_combined,
                COALESCE(pledge_totals.available, 0) + i.quantity AS available_combined
            FROM dr_events.item i
            JOIN dr_events.category c ON i.category_id = c.category_id
            LEFT JOIN (
                SELECT 
                    p.item_id,
                    SUM(p.item_quantity) AS total_pledged,
                    SUM(p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) AS available
                FROM dr_events.pledge p
                WHERE p.canceled_flag = 0
                GROUP BY p.item_id
            ) pledge_totals ON i.item_id = pledge_totals.item_id
            ORDER BY c.category_name, i.name
        """)
        
        result = db.session.execute(query)
        
        items = [
            {
                "id": row.item_id,
                "name": row.name,
                "description": row.description,
                "category_id": row.category_id,
                "category_name": row.category_name,
                "base_quantity": row.base_quantity,  # Added by admin in the item table
                "total_pledged": row.total_pledged,  # Total from donor pledges
                "available_pledged": row.available_pledged,  # Available from pledges
                "total_combined": row.total_combined,  # Total combined (base + pledged)
                "available_combined": row.available_combined  # Available combined
            }
            for row in result
        ]
        
        return jsonify(items), 200
    except SQLAlchemyError as ex:
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
@api_routes.route('/getCombinedMatchOptions', methods=['GET'])
def get_combined_match_options():
    db = get_db()
    
    request_id = request.args.get('request_id')
    
    if not request_id:
        return jsonify({"error": "Missing request_id parameter"}), 400
    
    try:
        # First get the request details
        request_query = text("""
            SELECT r.request_id, r.user_id AS recipient_id, r.item_id,
                   r.quantity, r.status, item.name AS item_name,
                   u.zip_code AS recipient_zipcode,
                   COALESCE(matches.total_matched, 0) AS total_matched,
                   r.quantity - COALESCE(matches.total_matched, 0) AS quantity_needed
            FROM dr_events.request r
            JOIN dr_admin.user u ON r.user_id = u.user_id
            JOIN dr_events.item ON r.item_id = item.item_id
            LEFT JOIN (
                SELECT request_id, SUM(match_quantity) AS total_matched
                FROM dr_events.match
                WHERE canceled_flag = 0
                GROUP BY request_id
            ) matches ON r.request_id = matches.request_id
            WHERE r.request_id = :request_id
        """)
        
        request_result = db.session.execute(request_query, {"request_id": request_id}).fetchone()
        
        if not request_result:
            return jsonify({"error": "Request not found"}), 404
        
        # Then get all matching pledges
        pledges_query = text("""
            SELECT p.pledge_id, p.user_id AS donor_id, u.username AS donor_name,
                   u.zip_code AS donor_zipcode, p.item_id, i.name AS item_name,
                   i.category_id, c.category_name, p.item_quantity AS total_pledged,
                   p.fulfilled_quantity, p.allocated_quantity,
                   (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) AS available_quantity,
                   p.days_to_ship
            FROM dr_events.pledge p
            JOIN dr_admin.user u ON p.user_id = u.user_id
            JOIN dr_events.item i ON p.item_id = i.item_id
            JOIN dr_events.category c ON i.category_id = c.category_id
            WHERE p.item_id = :item_id
              AND p.canceled_flag = 0
              AND (p.item_quantity - (p.allocated_quantity + p.fulfilled_quantity)) > 0
            ORDER BY p.days_to_ship ASC, available_quantity DESC
        """)
        
        pledges_result = db.session.execute(pledges_query, {"item_id": request_result.item_id})
        
        pledges = [
            {
                "pledge_id": row.pledge_id,
                "donor_id": row.donor_id,
                "donor_name": row.donor_name,
                "donor_zipcode": row.donor_zipcode,
                "item_id": row.item_id,
                "item_name": row.item_name,
                "category_id": row.category_id,
                "category_name": row.category_name,
                "total_pledged": row.total_pledged,
                "available_quantity": row.available_quantity,
                "days_to_ship": row.days_to_ship
            }
            for row in pledges_result
        ]
        
        # Get the base quantity from the item table
        item_query = text("""
            SELECT i.item_id, i.name, i.quantity AS base_quantity
            FROM dr_events.item i
            WHERE i.item_id = :item_id
        """)
        
        item_result = db.session.execute(item_query, {"item_id": request_result.item_id}).fetchone()
        base_quantity = item_result.base_quantity if item_result else 0
        
        # Calculate total available
        total_from_pledges = sum(pledge["available_quantity"] for pledge in pledges)
        total_available = total_from_pledges + base_quantity
        
        # Prepare the available sources list (admin + pledges)
        available_sources = []
        
        # Add admin source if there's inventory
        if base_quantity > 0:
            available_sources.append({
                "source_type": "admin",
                "item_id": request_result.item_id,
                "item_name": request_result.item_name,
                "available_quantity": base_quantity
            })
        
        # Add each pledge as a source
        for pledge in pledges:
            available_sources.append({
                "source_type": "pledge",
                "pledge_id": pledge["pledge_id"],
                "donor_id": pledge["donor_id"],
                "donor_name": pledge["donor_name"],
                "days_to_ship": pledge["days_to_ship"],
                "item_id": pledge["item_id"],
                "item_name": pledge["item_name"],
                "available_quantity": pledge["available_quantity"]
            })
        
        response = {
            "request": {
                "request_id": request_result.request_id,
                "recipient_id": request_result.recipient_id,
                "item_id": request_result.item_id,
                "item_name": request_result.item_name,
                "quantity": request_result.quantity,
                "status": request_result.status,
                "recipient_zipcode": request_result.recipient_zipcode,
                "total_matched": request_result.total_matched,
                "quantity_needed": request_result.quantity_needed
            },
            "available_pledges": pledges,
            "available_sources": available_sources,
            "base_quantity": base_quantity,
            "total_from_pledges": total_from_pledges,
            "total_available": total_available
        }
        
        return jsonify(response), 200
    except SQLAlchemyError as ex:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

# Endpoint to create a match from admin inventory
@api_routes.route('/createAdminMatch', methods=['POST'])
def create_admin_match():
    db = get_db()
    data = request.get_json()
    
    try:
        request_id = data.get('requestId')
        admin_quantity = data.get('adminQuantity')
        
        if not request_id or not admin_quantity:
            return jsonify({"error": "Missing required fields"}), 400
        
        # 1. Get request and item details
        request_query = text("""
            SELECT r.request_id, r.user_id, r.item_id, i.quantity AS base_quantity
            FROM dr_events.request r
            JOIN dr_events.item i ON r.item_id = i.item_id
            WHERE r.request_id = :request_id
        """)
        
        request_result = db.session.execute(request_query, {"request_id": request_id}).fetchone()
        
        if not request_result:
            return jsonify({"error": "Request not found"}), 404
        
        # 2. Check if enough admin inventory is available
        if request_result.base_quantity < admin_quantity:
            return jsonify({"error": "Not enough admin inventory available"}), 400
        
        # 3. Get the shipping address for the recipient
        address_query = text("""
            SELECT concat_ws(' ',
                   address_line1,
                   address_line2,
                   CONCAT_WS(', ',			
                        city,
                        state				
                    ), zip_code) AS full_address
            FROM dr_admin.user 
            WHERE user_id = :user_id
        """)
        
        address_result = db.session.execute(address_query, {"user_id": request_result.user_id}).fetchone()
        shipping_address = address_result.full_address if address_result else None
        
        # 4. Create the match record - NOTE: No pledge_id for admin matches (NULL)
        match_query = text("""
            INSERT INTO dr_events.match
            (pledge_id, request_id, match_status, match_quantity, shipping_status, shipping_address, match_type_id)
            VALUES (NULL, :request_id, 'matched', :admin_quantity, 'pending', :shipping_address, 1)
        """)
        
        db.session.execute(match_query, {
            "request_id": request_id,
            "admin_quantity": admin_quantity,
            "shipping_address": shipping_address
        })
        
        # 5. Update the item's base quantity
        update_item_query = text("""
            UPDATE dr_events.item
            SET quantity = quantity - :admin_quantity
            WHERE item_id = :item_id
        """)
        
        db.session.execute(update_item_query, {
            "item_id": request_result.item_id,
            "admin_quantity": admin_quantity
        })
        
        # 6. Update the request's status
        update_request_query = text("""
            UPDATE dr_events.request
            SET status = 'matched'
            WHERE request_id = :request_id
        """)
        
        db.session.execute(update_request_query, {"request_id": request_id})
        
        db.session.commit()
        
        return jsonify({"message": "Match created successfully from admin inventory"}), 200
    except SQLAlchemyError as ex:
        db.session.rollback()
        print(f"Database error in createAdminMatch: {ex}")
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        db.session.rollback()
        print(f"General error in createAdminMatch: {ex}")
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@api_routes.route('/getMatchTypes', methods=["GET"])
def get_match_types():
    db = get_db()
    try:
        # Get all match types for selection
        query = text("SELECT match_type_id, name, description FROM dr_events.match_type WHERE type = 'auto'")
        match_types = db.session.execute(query).fetchall()

        match_types_list = [
            {
                "match_type_id": mt.match_type_id,
                "name": mt.name,
                "description": mt.description
            }
            for mt in match_types
        ]

        return jsonify(match_types_list), 200

    except SQLAlchemyError as ex:
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
# Replace the getPledges route in mysql_routes.py
@api_routes.route('/getPledges', methods=["GET"])
def get_pledges():
    db = get_db()

    user_id = request.args.get('user_id')
    try:
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
       
        # Convert user_id to int
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid user_id"}), 400
       
        print(f"Getting pledges for user_id: {user_id}")
        
        # FIXED: Use direct query instead of stored procedure to debug
        # First check if user exists
        user_check_query = text("SELECT role FROM dr_admin.user WHERE user_id = :user_id")
        user_result = db.session.execute(user_check_query, {"user_id": user_id}).fetchone()
        
        if not user_result:
            return jsonify({"error": "User not found"}), 404
            
        user_role = user_result.role
        print(f"User role: {user_role}")
        
        # Build query based on user role
        if user_role == 'Donor':
            pledges_query = text("""
                SELECT 
                    pledge.pledge_id,
                    pledge.user_id AS donor_id,
                    pledge.item_id,
                    item.name AS item_name,
                    pledge.item_quantity,
                    pledge.pledge_status,
                    pledge.fulfilled_quantity,
                    pledge.allocated_quantity,
                    pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left,
                    pledge.fulfilled_quantity AS items_locked,
                    pledge.allocated_quantity AS items_allocated,
                    pledge.canceled_flag,
                    pledge.fulfilled_flag,
                    pledge.created_at,
                    category.category_id,
                    category.category_name,
                    user.zip_code
                FROM dr_events.pledge
                JOIN dr_events.item ON pledge.item_id = item.item_id
                JOIN dr_events.category ON item.category_id = category.category_id
                JOIN dr_admin.user ON pledge.user_id = user.user_id
                WHERE pledge.user_id = :user_id AND pledge.canceled_flag = 0
            """)
        elif user_role == 'Admin':
            pledges_query = text("""
                SELECT 
                    pledge.pledge_id,
                    pledge.user_id AS donor_id,
                    pledge.item_id,
                    item.name AS item_name,
                    pledge.item_quantity,
                    pledge.pledge_status,
                    pledge.fulfilled_quantity,
                    pledge.allocated_quantity,
                    pledge.item_quantity - (pledge.allocated_quantity + pledge.fulfilled_quantity) AS items_left,
                    pledge.fulfilled_quantity AS items_locked,
                    pledge.allocated_quantity AS items_allocated,
                    pledge.canceled_flag,
                    pledge.fulfilled_flag,
                    pledge.created_at,
                    category.category_id,
                    category.category_name,
                    user.zip_code
                FROM dr_events.pledge
                JOIN dr_events.item ON pledge.item_id = item.item_id
                JOIN dr_events.category ON item.category_id = category.category_id
                JOIN dr_admin.user ON pledge.user_id = user.user_id
                WHERE pledge.canceled_flag = 0
            """)
        else:
            return jsonify({"error": "User role not authorized to view pledges"}), 403
        
        result = db.session.execute(pledges_query, {"user_id": user_id})
        rows = result.fetchall()

        if rows:            
            columns = result.keys()
            pledges = [dict(zip(columns, row)) for row in rows]
            print(f"Found {len(pledges)} pledges")
            return jsonify(pledges), 200
        else:
            print("No pledges found")
            return jsonify([]), 200
        
    except SQLAlchemyError as ex:
        db.session.rollback()
        print(f"Database error in get_pledges: {ex}")
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        print(f"General error in get_pledges: {ex}")
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    