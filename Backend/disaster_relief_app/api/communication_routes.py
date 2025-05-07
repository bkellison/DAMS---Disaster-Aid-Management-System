from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import jwt
from disaster_relief_app.utils import decode_required_token, get_db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

communication_routes = Blueprint('communication_routes', __name__)
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

#Region: Shared Functions
def send_email(to_email, subject, html_body):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        return jsonify({"message": "Email sent successfully"})
    except Exception as ex:
        return jsonify({"error": "Issue sending email", "message": str(ex)})
#End Region

@communication_routes.route('/requestForgottenPasswordReset', methods=["POST"])
def request_forgotten_password_reset():
    db = get_db()
    data_payload = request.get_json()
    try:
        username = data_payload.get("username")

        #Check if user exists
        existing_user_query = "SELECT * FROM user WHERE is_approved = 1 AND username = :username"
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            #Return error if username already exists
            return jsonify({"error": "User does not exist"}), 401
        
        subject = "Reset Your Disaster Portal Password"
        html_body = f"""
            <html>
                <body>
                    <p>To reset your password for username: {username} 
                        <a href="https://www.google.com">Click here</a>
                    </p>
                </body>
            </html>
            """
        # send_email(existing_user.email, subject, body)
        send_email("vmkelly@uiowa.edu", subject, html_body)
        
        return jsonify({"data": "data"})
    except SQLAlchemyError as ex:
        # Handle any database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        # Handle any other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500

@communication_routes.route('/communicateAccountRequest', methods=["POST"])
def communicate_account_request():
    db = get_db()
    data_payload = request.get_json()
    try:
        username = data_payload.get("username")
        is_approved = data_payload.get("is_approved")

        #Check if user exists
        existing_user_query = "SELECT * FROM user WHERE is_approved = 1 AND username = :username"
        existing_user = db.session.execute(existing_user_query, {"username": username}).fetchone()

        if not existing_user:
            #Return error if username already exists
            return jsonify({"error": "User does not exist"}), 401
        
        
        if is_approved == 1:
            isApproved = "approved"
        else:
            isApproved = "not approved"
        
        subject = f"Your disaster relief portal request is {isApproved}"
        html_body = f"""
            <html>
                <body>
                    <p>Your request for {username} account is {isApproved}</p>
                    <p><a href="https://www.google.com">Click here</a> to log in or request another account</p>
                </body>
            </html>
            """
        # send_email(existing_user.email, subject, html_body)
        send_email("vmkelly@uiowa.edu", subject, html_body)
        
        return jsonify({"data": "data"})
    except SQLAlchemyError as ex:
        # Handle any database errors
        return jsonify({"error": "Database error", "message": str(ex)}), 500
    except Exception as ex:
        # Handle any other errors
        return jsonify({"error": "Internal server error", "message": str(ex)}), 500


