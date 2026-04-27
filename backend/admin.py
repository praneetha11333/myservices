
from flask import Flask, render_template, request, redirect, url_for,flash,session,current_app as app
from backend.models import *
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io ,base64
from functools import wraps

def auth_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to access this page", "success")
            return  redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_function


# admin home page 
@app.route('/admin/a_home', methods=['GET', 'POST'])
@auth_req
def a_home():
    if request.method == 'POST':
        action = request.form.get('action')
        id = request.form.get('id')
        description = request.form.get('description')
        base_price = request.form.get('base_price')
        
        # professional related
        if action in ['accept', 'reject']:
            professional = Professional.query.filter_by(id=id).first()
            if not professional:
                flash("Professional not found", "danger")
            else:
                user = User.query.filter_by(id=professional.user_id).first()
                if action == 'accept':
                    professional.is_verified = True
                    user.is_active = True
                    db.session.commit()
                    flash("Professional accepted successfully.", "success")
                elif action == 'reject':
                    db.session.delete(user)
                    db.session.commit()
                    flash("Professional rejected  successfully.", "success")
                    
        # service related
        elif action in ['edit', 'delete']:
            service = Service.query.filter_by(id=id).first()
            package=Package.query.filter_by(id=id).first()
            if service:
                if action == 'edit':
                    service.description = description
                    service.base_price = base_price
                    db.session.commit()
                    flash("Service edited successfully.", "success")
                elif action == 'delete':
                    professionals = Professional.query.filter_by(service_id=id).all()
                    if professionals:
                        for professional in professionals:
                            user = User.query.filter_by(id=professional.user_id).first()
                            if user:
                                db.session.delete(user)
                    db.session.delete(service)
                    db.session.commit()
                    flash("Service deleted successfully.", "success")
                    
            #package related        
            elif package:
                if action == 'edit':
                    package.description = description
                    package.base_price = base_price
                    db.session.commit()
                    flash("Package edited successfully.", "success")
                elif action == 'delete':
                    db.session.delete(package)
                    db.session.commit()
                    flash("Package deleted successfully.", "success")
        else:
            flash("Invalid action.", "danger")
        return redirect(url_for('a_home'))
    professionals = Professional.query.filter_by(is_verified=False).all()
    services = Service.query.all()
    packages = Package.query.all()
    return render_template('admin/a_home.html', professionals=professionals, services=services, packages=packages)

# admin new service related 
@app.route('/admin/newservice', methods=['GET', 'POST'])
@auth_req
def new_service():
    if request.method == 'POST':
        try:
            id = request.form['service'].lower()
            if Service.query.filter(Service.id==id).first():
                flash("Service already exists case(insenstitve)", "danger")
                return redirect(url_for('new_service'))
            description = request.form['description']
            base_price = request.form['base_price']
            service=Service(id=id, description=description, base_price=base_price)
            db.session.add(service)
            db.session.commit()
            flash("Service added successfully", "success")
            return redirect(url_for('new_service'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('new_service')) 
    return render_template('admin/newservice.html' )

# admin new package related
@app.route('/admin/newpackage', methods=['GET', 'POST'])
@auth_req
def new_package():
    if request.method == 'POST':
        try:
            service_id = request.form['service'].lower()
            id = request.form['name'].lower()
            base_price = request.form['base_price']
            description = request.form['description']
            if id == service_id:
                flash("Package name and service name cannot be same", "danger")
                return redirect(url_for('new_package'))
            unq_package=Package.query.filter_by(id=id).first()
            if unq_package:
                flash("Package already exists", "danger")
                return redirect(url_for('new_package'))   
            package = Package.query.filter_by(service_id=service_id, id=id).first()

            if package:
                flash("Package already exists", "danger")
                return redirect(url_for('new_package'))
            is_present=Service.query.filter(Service.id==service_id).first()
            if is_present :
                package=Package(service_id=service_id, id=id, base_price=base_price, description=description)
                db.session.add(package)
                db.session.commit()
                flash("Package added successfully", "success")
                return redirect(url_for('a_home'))
            else:
                flash("Service not found", "danger")
                return redirect(url_for('new_package'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('new_package')) 
    return render_template('admin/newpackage.html')

#definitons for search
def service_req_status(search):
    result=[]
    service_requests = ServiceRequest.query.all()
    for req in service_requests:
        if search.lower() in req.status.lower() or search.lower() in req.service_id or search.lower() in req.package_id or search in str(req.professional_id):
            result.append(req)
    return result
              
@app.route('/admin/search', methods=['GET', 'POST'])
@auth_req
def a_search():
    requests = ServiceRequest.query.all()
    users = User.query.filter(User.role == 2).all() 
    user_dict ={}
    for user in users:
        user_dict[user.id] = user.is_active
    for req in requests:
        professional = Professional.query.filter_by(id=req.professional_id).first()
        if professional:
            user_active = user_dict.get(professional.user_id, False)
            req.is_active = user_active 
        else:
            req.is_active = False
    # search       
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            service_requests = service_req_status(search)
            if not service_requests:
                flash("No results found", "success")
            return render_template('admin/a_search.html', service_requests=service_requests, search=search, requests=requests)
    
        professional_id = request.form.get('professional_id')
        action = request.form.get('action')
        if professional_id:
            professional = Professional.query.filter_by(id=professional_id).first()
            if not professional:
                flash("Professional not found", "danger")
                return redirect(url_for('a_search'))

            user = User.query.filter_by(id=professional.user_id).first()
            if user:
                if action == "block":
                    user.is_active = False
                    db.session.commit()
                    flash("Professional blocked successfully.", "success")
                elif action == "unblock":
                    user.is_active = True
                    db.session.commit()
                    flash("Professional unblocked successfully.", "success")
                else:
                    flash("Invalid action", "danger")
            else:
                flash("User not found", "danger")
        else:
            flash("Please enter a professional ID", "danger")
        return redirect(url_for('a_search'))
    return render_template('admin/a_search.html')

@app.route('/admin/summary')
@auth_req
def a_sum():
    service_requests = ServiceRequest.query.all()
    status_counts = Counter(req.status for req in service_requests)
    service_counts = Counter(req.service_id for req in service_requests)
    
    def generate_chart(labels, values, xlabel, ylabel, title):
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=['skyblue', 'salmon', 'lightgreen'])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        img = io.BytesIO()
        plt.savefig(img, format='png')
        plt.close(fig)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()
    
    plot_url1 = generate_chart(list(status_counts.keys()), list(status_counts.values()),'Status', 'Count', 'Service Requests by Status')
    plot_url2 = generate_chart(list(service_counts.keys()), list(service_counts.values()),'Service ID', 'Count', 'Service Requests by service')
    return render_template('admin/a_summary.html', plot_url1=plot_url1, plot_url2=plot_url2)

@app.route('/admin/logout')
def a_logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

 