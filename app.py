from flask import Flask
from backend.models import *
import os

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services_app.sqlite3'
    app.config['SECRET_KEY']='12345'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/resumes')
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app) 
    app.app_context().push()
    return app   
    

app=create_app()

from backend.admin import *
from backend.customer import *
from backend.professional import *
from backend.redirect import *


if __name__ == '__main__':
    app.run()