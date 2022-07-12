import datetime

from .. import db


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    category = db.relationship('Category')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    