from flask import Flask, render_template, request, redirect, url_for,flash,session,current_app as app
from backend.models import *
from backend.admin import auth_req
from datetime import datetime
from collections import defaultdict,Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io ,base64
from sqlalchemy import or_

@app.route('/customer/home', methods=['GET', 'POST'])
@auth_req
def cust_home():
    user_id = session.get('user_id')
    
    #Rating Calculation
    service_ratings = defaultdict(list)
    requests = ServiceRequest.query.all()
    for req in requests:
        if req.rating is not None:
            service_ratings[req.service_id].append(req.rating)
            if req.package_id != "All Packages" :
                service_ratings[req.package_id].append(req.rating)            
    average_ratings = {}
    for service_id, ratings in service_ratings.items():
        average_ratings[service_id] = round(sum(ratings) / len(ratings),2)
    
    
    #Home Page
    packages=[]
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all() 
    services = Service.query.all()
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        service_id = request.form.get('service_id')
        package_id = request.form.get('package_id')
        # Displaying packages for a service
        if form_type == "form1":
            packages = Package.query.filter_by(service_id=service_id).all()
            if packages :
                return render_template('customer/c_home.html', Services=services, packages=packages, service_requests=service_requests, average_ratings=average_ratings,)
            else:
                flash('No packages available for this service', 'danger') 
        # booking a service  
        if form_type == "form2":
            price=Service.query.filter_by(id=service_id).first().base_price
            package_id="all packages"
            date_of_request = datetime.now()
            status = 'Requested'
            professional_id = Professional.query.filter_by(service_id=service_id,is_verified=True).all()
            print(professional_id)
            if not professional_id:
                flash('No professionals available for this service', 'danger')
                return redirect(url_for('cust_home'))
            service_request = ServiceRequest(customer_id=customer.id,service_id=service_id, package_id=package_id,price=price, date_of_request=date_of_request, status=status)
            db.session.add(service_request)
            db.session.commit()
            flash('Service Requested Successfully', 'success')
            return redirect(url_for('cust_home'))
        #booking a package    
        if package_id:
            price=Package.query.filter_by(service_id=service_id).first().base_price
            date_of_request = datetime.now()
            status = 'Requested'
            professional_ids = Professional.query.filter_by(service_id=service_id,is_verified=True).all()
            if professional_ids is None:
                flash('No professionals available for this service', 'danger')
                return redirect(url_for('cust_home'))
            service_request = ServiceRequest(customer_id=customer.id, service_id=service_id, package_id=package_id,price=price, date_of_request=date_of_request, status=status)
            db.session.add(service_request)
            db.session.commit()
            flash('Package Requested Successfully', 'success')    
            return redirect(url_for('cust_home'))                            
    return render_template('customer/c_home.html', Services=services, service_requests=service_requests, average_ratings=average_ratings)

# customer rating
@app.route('/customer/rate', methods=['GET', 'POST'])
@auth_req
def cust_rate():
    user_id = session.get('user_id')
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    
    service_request = None 
    professional = None 
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        rating=request.form.get('rating')
        review=request.form.get('review')
        if not booking_id:
            flash("Booking ID is missing", "danger")
            return redirect(url_for('cust_home'))
        service_request = ServiceRequest.query.filter_by(customer_id=customer.id, id=booking_id).first()
        if service_request is None:
            flash("Service Request not found", "danger")
            return redirect(url_for('cust_home'))
        professional = Professional.query.filter_by(id=service_request.professional_id).first()
        
        # Close the service request
        if rating and review:
            service_request.rating = rating
            service_request.review = review
            service_request.status = 'Closed'
            db.session.commit()
            flash('Service Request Closed Successfully', 'success')
            return redirect(url_for('cust_home'))         
    return render_template('customer/c_rate.html', service_request=service_request, professional=professional)


# customer profile
@app.route('/customer/profile', methods=['GET', 'POST'])
@auth_req
def cust_edit():
    user_id = session.get('user_id')
    user=User.query.filter_by(id=user_id).first()
    if not user:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    customer = Customer.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        password=request.form.get('password')
        if password:
            user.set_password(password)
        customer.name = request.form.get('name')
        customer.address = request.form.get('address')
        customer.pincode = request.form.get('pincode')
        try:
            db.session.commit()
            flash('Profile Updated Successfully', 'success')
            return redirect(url_for('cust_home'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')        
    return render_template('customer/cus_edit.html', customer=customer,user=user)

#customer search
@app.route('/customer/search', methods=['GET', 'POST'])
@auth_req
def cust_search():
    if request.method == 'POST':
        search=request.form.get('search')
        if search:
            services = Service.query.filter(or_(Service.id.ilike(f'%{search}%'),
                       Service.base_price.ilike(f'%{search}%'))).all()
            packages=Package.query.filter(or_(Package.id.ilike(f'%{search}%'),
                     Package.base_price.ilike(f'%{search}%'))).all()
            
            if services or packages:
                return render_template('customer/c_search.html', services=services, packages=packages, search=search)
            else:
                flash('No services found','danger') 
    return render_template('customer/c_search.html')
        
 #customer summary   
@app.route('/customer/summary')
@auth_req
def cust_sum():
    user_id = session.get('user_id')
    customer=Customer.query.filter_by(user_id=user_id).first()
    if not customer:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    status_counts = Counter([req.status for req in service_requests])
    
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=['skyblue', 'salmon', 'lightgreen'])
    ax.set_xlabel('Status')
    ax.set_ylabel('Count')
    ax.set_title('Service Requests by Status')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return render_template('customer/c_summary.html',plot_url=plot_url)

#logout
@app.route('/customer/logout')
def cust_logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

