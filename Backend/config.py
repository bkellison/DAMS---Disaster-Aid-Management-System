import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Use Railway's DATABASE_URL if available, otherwise fall back to local
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_admin')
    
    # Ensure we're using the correct database URLs
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_BINDS = {
        'dr_events': DATABASE_URL.replace('/dr_admin', '/dr_events')
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 60,
            'read_timeout': 60,
            'write_timeout': 60
        }
    }
    SECRET_KEY = os.getenv('SECRET_KEY', "adkfjYEShdfanThisisAutoGenteorafdkgjsk*&%$hgfad")