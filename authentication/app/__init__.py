#!/usr/bin/env python3

from flask import Flask
from decouple import config
import os
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SECRET_KEY'] = config("SECRET_KEY")
bcrypt = Bcrypt(app)
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# configure the SQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'

# create the extension
db = SQLAlchemy(app)
# db.init_app(app)

from app.admin.routes import *
