from flask import Flask
from flask_cors import CORS
from config import Config
from disaster_relief_app.api.mysql_routes import api_routes
from disaster_relief_app.api.communication_routes import communication_routes
from disaster_relief_app.api.event_routes import event_routes
from disaster_relief_app.api.auto_match_routes import auto_match_routes
from disaster_relief_app.api.donation_items_routes import donation_routes
from disaster_relief_app.api.shipping_routes import shipping_routes
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text
from disaster_relief_app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    try:
        db.init_app(app)
        with app.app_context():
            current_db = db.session.execute(text("SELECT DATABASE()")).fetchone()
            print("✅ Connected to DB:", current_db)
    except Exception as e:
        print("❌ DB connection failed:", e)

    CORS(app, origins=[
        "http://localhost:3000", 
        "https://dams-disaster-aid-management-system.netlify.app"
    ], supports_credentials=True)
    
    app.register_blueprint(api_routes)
    app.register_blueprint(communication_routes)
    app.register_blueprint(event_routes, url_prefix='/api')
    app.register_blueprint(auto_match_routes, url_prefix='/api')
    app.register_blueprint(donation_routes, url_prefix='/api')
    app.register_blueprint(shipping_routes, url_prefix='/api')

    app.config['TESTING'] = True

    return app