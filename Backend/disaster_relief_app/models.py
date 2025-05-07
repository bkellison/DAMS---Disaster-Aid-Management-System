# disaster_relief_app/models.py
from disaster_relief_app.extensions import db

# ----------------------------------------
# User Table
# ----------------------------------------
class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.LargeBinary, nullable=False)  # bcrypt-hashed
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255))
    zip_code = db.Column(db.String(20))
    is_approved = db.Column(db.Boolean, default=False)

    #created_items = db.relationship('Item', back_populates='creator')

# ----------------------------------------
# Category Table
# ----------------------------------------
class Category(db.Model):
    __bind_key__ = 'dr_events'
    __tablename__ = 'category'  # ✅ fixed

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    items = db.relationship('Item', back_populates='category')
    event_links = db.relationship('EventCategory', back_populates='category')

# ----------------------------------------
# Item Table
# ----------------------------------------
class Item(db.Model):
    __bind_key__ = 'dr_events'
    __tablename__ = 'item'

    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    # quantity = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    category = db.relationship('Category', back_populates='items')
    #creator = db.relationship('User', back_populates='created_items')

# ----------------------------------------
# Event Table
# ----------------------------------------
class Event(db.Model):
    __bind_key__ = 'dr_events'
    __tablename__ = 'disaster_event'

    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    type = db.Column(db.String(150))

    categories = db.relationship('EventCategory', back_populates='event')


# ----------------------------------------
# Event <-> Category Join Table
# ----------------------------------------
class EventCategory(db.Model):
    __bind_key__ = 'dr_events'
    __tablename__ = 'event_category'

    event_id = db.Column(db.Integer, db.ForeignKey('disaster_event.event_id'), primary_key=True)  # ✅ fixed
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)

    event = db.relationship('Event', back_populates='categories')
    category = db.relationship('Category', back_populates='event_links')
