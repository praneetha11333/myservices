
from flask import Flask, render_template, request, redirect, url_for, flash, session
from backend.models import *
from backend.admin import *
from backend.professional import *
from flask import current_app as app
import os
from werkzeug.utils import secure_filename

#functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def check_user_existence(email):
    return User.query.filter_by(email=email).first()

def handle_error(e, redirect_route):
    flash(f"An error occurred: {str(e)}", "danger")
    return redirect(url_for(redirect_route))

def login_user(user):
    session['user_id'] = user.id
    if user.role == 0:
        return redirect(url_for('a_home'))
    elif user.role == 1:
        return redirect(url_for('cust_home'))
    elif user.role == 2:  
        return redirect(url_for('prof_home'))
    

# Redirections
@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            username = request.form['email']
            psswrd = request.form['password']
            user = check_user_existence(username)
            if not user:
                flash("User does not exist. Register to login", "danger")
                return redirect(url_for('home'))
            if not user.check_password(psswrd):
                flash("Incorrect Password", "danger")
                return redirect(url_for('home'))
            professional=Professional.query.filter_by(user_id=user.id).first()
            if user.is_active == False and professional.is_verified == False:
                flash("User pending for admin approval", "danger")
                return redirect(url_for('home'))
            if user.is_active==False and professional:
                flash("U have benn BLOCKED for  your POOR service wait for admin approval", "danger")
                return redirect(url_for('home'))   
            return login_user(user)
        except Exception as e:
            return handle_error(e, 'home')
    return render_template('login.html')


# customer signup
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['email']
            psswrd = request.form['password']
            Name = request.form['name']
            Address = request.form['address']
            Pincode = request.form['pincode']
            user = check_user_existence(username)
            if user:
                flash("User already exists", "danger")
                return redirect(url_for('home'))
            user = User(email=username,  role=1, is_active=True)
            user.set_password(psswrd)
            db.session.add(user)
            db.session.commit()
            customer = Customer(user_id=user.id, name=Name, address=Address, pincode=Pincode)
            db.session.add(customer)
            db.session.commit()
            flash("User created successfully, Login to view our services", "success")
            return redirect(url_for('home'))
        except Exception as e:
            return handle_error(e, 'signup')
    return render_template('signup.html')

# professional signup
@app.route('/psignup', methods = ['GET', 'POST'])
def psign():
    if request.method == 'POST':
        try:
            username = request.form['email']
            psswrd = request.form['password']
            Name = request.form['name']
            service = request.form['service']
            Experience = request.form['experience']
            file = request.files['document']
            user = check_user_existence(username)
            
            if user:
                flash("User already exists", "danger")
                return redirect(url_for('home'))
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Invalid file format", "danger")
                return redirect(url_for('psign')) 
             
            user = User(email=username, role=2, is_active=False)
            user.set_password(psswrd)
            db.session.add(user)
            db.session.commit()
            professional = Professional(user_id=user.id, name=Name, service_id=service, experience=Experience, document_url=filename, is_verified=False)
            db.session.add(professional)
            db.session.commit()
            flash("User created successfully, pending admin approval", "success")
            return redirect(url_for('home'))
        except Exception as e:
            return handle_error(e, 'psign')
    services = Service.query.all()
    return render_template('professional.html', services=services)
