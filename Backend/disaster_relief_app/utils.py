from functools import wraps

# Import db in function to avoid a circular import
def get_db(bind=None):
    from disaster_relief_app import db
    if bind:
        return db.get_engine(bind=bind) 
    return db

def decode_required_token(f):
    @wraps(f)
    def decode_function(*args, **kwargs):
        #extract token
        #if valid, call original route (f)
        return f(*args, **kwargs)
    return decode_function