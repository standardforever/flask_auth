# from sqlalchemy import Column, String, Text, DateTime
from uuid import uuid4
from datetime import datetime
from app import app, db


""" Db for User
"""


class User(db.Model):
    id = db.Column(db.String(180), primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(180), unique=False, nullable=False)
    last_name = db.Column(db.String(180), unique=False, nullable=False)
    username = db.Column(db.String(180), unique=False, nullable=False)
    password = db.Column(db.String(180), unique=False, nullable=False)
    token_time = db.Column(db.DateTime, nullable=False)
    token = db.Column(db.String(10), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_admin = db.Column(db.Boolean, nullable=False)

    @classmethod
    def get_all(cls, page):
        """ Get a record by ID
        """
        user = db.session.query(cls).order_by(cls.created_at.desc()).paginate(page=page, per_page=15)
        if (user is None):
            return (None)
        return (user) 

    def __repr__(self):
        return '<User %r>' % self.username


with app.app_context():   # all database operations under with
    db.create_all()
