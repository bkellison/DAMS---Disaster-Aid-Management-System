import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_admin')
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_BINDS = {
        'dr_events': DATABASE_URL.replace('/dr_admin', '/dr_events')
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', "adkfjYEShdfanThisisAutoGenteorafdkgjsk*&%$hgfad")