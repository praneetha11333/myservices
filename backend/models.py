from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    customers= db.relationship('Customer', cascade="all, delete", backref='user',uselist=False, lazy=True)
    professionals = db.relationship('Professional', cascade="all,delete", backref='user', uselist=False,lazy=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    #relationship
    service_requests = db.relationship('ServiceRequest',backref='customer', lazy=True)

class Professional(db.Model):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String, nullable=False)
    service_id = db.Column(db.String, db.ForeignKey('services.id',ondelete="CASCADE"), nullable=False)  
    experience = db.Column(db.Integer, nullable=False)
    document_url = db.Column(db.String, nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    #relationship
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy=True)

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.String, primary_key=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    base_price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    #relationship
    packages = db.relationship('Package', cascade="all,delete", backref='service', lazy=True)
    service_requests = db.relationship('ServiceRequest', cascade="all,delete", backref='service', lazy=True)
    professionals = db.relationship('Professional',cascade="all,delete" ,backref='service', lazy=True)
   

class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.String, primary_key=True,nullable=False)
    service_id = db.Column(db.String, db.ForeignKey('services.id'), nullable=False)  
    base_price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    #relationship
    
    service_requests = db.relationship('ServiceRequest', cascade="all,delete", backref='package', lazy=True)
    

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id',ondelete="SET NULL"), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id',ondelete="SET NULL"), nullable=True)
    service_id = db.Column(db.String, db.ForeignKey('services.id'), nullable=False)
    package_id = db.Column(db.String, db.ForeignKey('packages.id'), nullable=False)
    price=db.Column(db.Integer, nullable=False)
    date_of_request = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    review = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    