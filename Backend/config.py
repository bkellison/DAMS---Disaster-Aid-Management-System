import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_admin')
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:ynBdnmKRbBPXRxtDruqh@127.0.0.1:3306/dr_admin')
    SQLALCHEMY_BINDS = {
        'dr_events': "mysql+pymysql://root:anakinskywalker1!@127.0.0.1:3306/dr_events"
        #'dr_events': "mysql+pymysql://root:ynBdnmKRbBPXRxtDruqh@127.0.0.1:3306/dr_events"
        #'dr_events': "mysql+pymysql://root:Hawkeyes#12292002!@127.0.0.1:3306/dr_events"
    }
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:Hawkeyes#12292002!@127.0.0.1:3306/dr_admin')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = "adkfjYEShdfanThisisAutoGenteorafdkgjsk*&%$hgfad"