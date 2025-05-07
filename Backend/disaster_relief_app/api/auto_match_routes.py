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
        

        #Verify valid inputs
        if not match_type_name or not request_id:
            return jsonify({"error": "Missing requird fields"}), 400
        
        #Get request
        lookup_request_query = """
            SELECT request.request_id, request.user_id AS recipient_id, request.quantity, user.zip_code, IFNULL(current_matches.total_matched,0) AS total_matched
            FROM dr_events.request 
            JOIN dr_admin.user ON request.user_id = user.user_id
            LEFT OUTER JOIN
            (
                select `match`.request_id, SUM(`match`.match_quantity) AS total_matched
                from dr_events.`match`
                WHERE `match`.canceled_flag = 0
                GROUP BY `match`.request_id
            ) current_matches ON request.request_id = current_matches.request_id 
            WHERE request.request_id = :request_id AND IFNULL(current_matches.total_matched,0) < request.quantity
        """
        #"SELECT request_id, request.user_id AS recipient_id, request.quantity, user.zip_code FROM dr_events.request JOIN dr_admin.user ON request.user_id = user.user_id WHERE request_id = :request_id"
        existing_request = db.session.execute(text(lookup_request_query), ({"request_id": request_id})).fetchone()
        print(existing_request)

        if not existing_request:
            #Return error if username already exists
            return jsonify({"error": "Request either does not exist or does not need another match"}), 400
        
        qty_needed = existing_request.quantity

        pledge_options_sp = text("CALL dr_events.get_auto_match_options(:request_id)")
        result = db.session.execute(pledge_options_sp, ({"request_id": request_id}))
        options = []
        try:
            pledge_option_rows = result.fetchall()

            if pledge_option_rows:            
                columns = result.keys()

                options = [dict(zip(columns, row)) for row in pledge_option_rows]
        except Exception as ex:   
            return []
        
        if(options == []):
            return jsonify({"error": "No pledges to match"}), 400
        
        print("options")
        print(options)
        
        matched = 0
        if(match_type_name == 'nearest'):
            matched = find_nearest(existing_request.request_id, options, qty_needed, existing_request.zip_code);    
            print(matched)  
        if(match_type_name == 'quickest'):
            matched = find_quickest(request_id, options, qty_needed)        
            print(matched)  
        if(match_type_name == 'fulfillment'):
            matched = find_most_fulfilled(request_id, options, qty_needed)
            print(matched)  

        return jsonify({"message": f"{matched} match(es) found"}), 200

    except SQLAlchemyError as ex:
        db.session.rollback()
        # Handle database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:        
        # Handle other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500
    
    

def find_nearest(request_id, options, qty_needed, request_zipcode):
    print("find_nearest")
    db = get_db()
    filtered_values = [option["donor_zipcode"] for option in options if option["donor_zipcode"] != None]
    comma_separated = ','.join(filtered_values)
    print(comma_separated)
    print(request_zipcode)

    try:
        #Call Zipcodebase api
        get_distance_api = f"https://app.zipcodebase.com/api/v1/distance?apikey={zipCodeBaseApiKey}&code={request_zipcode}&compare={comma_separated}&country=us&unit=%27miles%27"
        response = requests.get(get_distance_api)
        response.raise_for_status()
        data = response.json()
        print(data)

        distances = data["results"]
        print(distances)

        for option in options:
            option["distance"] = distances.get(option["donor_zipcode"], float('inf'))

        options.sort(key=lambda o: o["distance"])

        print(options)

        total_matched = 0
        matches_count = 0

        for option in options:
            print("inside")
            print(option)
            if total_matched >= qty_needed:
                break
            available_qty = option["pledged_items_left"]
            qty_left = min(available_qty, qty_needed - total_matched)
            if qty_left > 0:
                create_match_sp = "CALL dr_events.create_match(:param_pledge_id, :param_request_id, :param_match_quantity, :param_match_status, :param_match_type)"
                db.session.execute((text(create_match_sp)), ({"param_pledge_id": option["pledge_id"], "param_request_id": request_id, "param_match_quantity": qty_left, "param_match_status": 'matched', "param_match_type": 2}))
                db.session.commit() #Save to db

                total_matched += qty_left
                matches_count += 1


        return matches_count
    except Exception as ex:
        print(ex)
        return 0
    

def find_most_fulfilled(request_id, options, qty_needed):
    db = get_db()
    total_matched = 0
    matches_count = 0

    try:
        for option in options:
            print(option)
            if total_matched >= qty_needed:
                break
            available_qty = option["pledged_items_left"]
            qty_left = min(available_qty, qty_needed - total_matched)
            if qty_left > 0:
                create_match_sp = "CALL dr_events.create_match(:param_pledge_id, :param_request_id, :param_match_quantity, :param_match_status, :param_match_type)"
                db.session.execute((text(create_match_sp)), ({"param_pledge_id": option["pledge_id"], "param_request_id": request_id, "param_match_quantity": qty_left, "param_match_status": 'matched', "param_match_type": 4}))
                db.session.commit() #Save to db

                total_matched += qty_left
                matches_count += 1

        return matches_count
    except Exception as ex:
        print(ex)
        return 0

def find_quickest(request_id, options, qty_needed):
    options.sort(key=lambda o: (o["days_to_ship"] or float('inf'), o["pledged_items_left"]))
    db = get_db()
    total_matched = 0
    matches_count = 0

    try:
        for option in options:
            if total_matched >= qty_needed:
                break
            available_qty = option["pledged_items_left"]
            qty_left = min(available_qty, qty_needed - total_matched)
            if qty_left > 0:
                create_match_sp = "CALL dr_events.create_match(:param_pledge_id, :param_request_id, :param_match_quantity, :param_match_status, :param_match_type)"
                db.session.execute((text(create_match_sp)), ({"param_pledge_id": option["pledge_id"], "param_request_id": request_id, "param_match_quantity": qty_left, "param_match_status": 'matched', "param_match_type": 4}))
                db.session.commit() #Save to db

                total_matched += qty_left
                matches_count += 1

        return matches_count
    except Exception as ex:
        print(ex)
        return 0