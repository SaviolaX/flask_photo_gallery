from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from decouple import config


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_HEROKU_DATABASE_URI')



#Create flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

migrate = Migrate(app, db)

############################################
# Url routes
from .photos.views import photos
from .users.views import users

app.register_blueprint(photos, url_prefix='/')
app.register_blueprint(users, url_prefix='/')
#############################################

#############################################
# models
from .users.models import User
from .photos.models import Photo, Category

#############################################
#############################################
# auth settings
login_manager = LoginManager()
# if user is not logged in, redirect => auth.login
login_manager.login_view = 'users.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#############################################

