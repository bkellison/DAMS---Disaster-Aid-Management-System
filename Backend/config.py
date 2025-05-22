import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_admin')
    SQLALCHEMY_BINDS = {
        'dr_events': os.getenv('DATABASE_URL', 'mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_admin').replace('/dr_admin', '/dr_events') if os.getenv('DATABASE_URL') else "mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_events"
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', "adkfjYEShdfanThisisAutoGenteorafdkgjsk*&%$hgfad")