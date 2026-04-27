from flask import Flask, render_template, request, redirect, url_for,flash,session,current_app as app
from backend.models import *
from backend.admin import auth_req
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io ,base64
from sqlalchemy import or_


@app.route('/professional/home', methods=['GET', 'POST'])
@auth_req
def prof_home():
    user_id = session.get('user_id')
    curr_professional = Professional.query.filter_by(user_id=user_id).first()
    if not curr_professional:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    service_requests = ServiceRequest.query.filter_by(service_id=curr_professional.service_id, is_approved=False).all()
    
    customer_det = []
    for service_request in service_requests:
        customer = Customer.query.filter_by(id=service_request.customer_id).first()
        customer_det.append(customer)
    paired = zip(service_requests, customer_det)
    
    if request.method == 'POST':
        service_request_id = request.form.get('id')
        status = request.form.get('action')
        
        if not service_request_id or not status:
            flash('Please select a request and action', 'danger')
            return render_template('professional/prof_home.html', service_requests=service_requests, paired=paired)
        service_request = ServiceRequest.query.filter_by(id=service_request_id,is_approved=False).first()
        if service_request:
            try:
                if status == 'accept':
                    service_request.status = 'accepted/close?'
                    service_request.professional_id = curr_professional.id
                    service_request.is_approved = True
                    flash('Service request accepted successfully', 'success')        
                db.session.commit()
                return redirect(url_for('prof_home'))
            except Exception as e:
                flash(f'Error updating request: {str(e)}', 'danger')
                return redirect(url_for('prof_home'))
    return render_template('professional/prof_home.html', service_requests=service_requests, paired=paired)


@app.route('/professional/profile', methods=['GET', 'POST'])
@auth_req
def prof_edit():
    user_id = session.get('user_id')
    professional = Professional.query.filter_by(user_id=user_id).first()
    if not professional:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    user=User.query.filter_by(id=user_id).first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        password=request.form.get('password')
        experience = request.form.get('experience')
        if not name or  not experience:
            flash('All fields are required', 'danger')
            return render_template('professional/prof_profile.html', professional=professional)
        professional.name = name
        professional.experience = experience
        if password:
            user.set_password(password)
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')
    return render_template('professional/prof_profile.html', professional=professional,user=user)

@app.route('/professional/search', methods=['GET', 'POST'])
@auth_req
def prof_search():
    user_id = session.get('user_id')
    professional=Professional.query.filter_by(user_id=user_id).first()
    if not professional:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        search=request.form.get('search')
        service_reqF = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional.id,
        or_(
            ServiceRequest.status.ilike(f'%{search}%'),
            ServiceRequest.date_of_request.ilike(f'%{search}%'),
            ServiceRequest.rating.ilike(f'%{search}%') )).all()
        if service_reqF:
            return render_template('professional/prof_search.html', service_req=service_reqF, search=search)
        else:
           flash('No service request found', 'success')
           return render_template('professional/prof_search.html')
    return render_template('professional/prof_search.html')

@app.route('/professional/summary', methods=['GET', 'POST'])
@auth_req
def prof_sum():
    user_id = session.get('user_id')
    professional=Professional.query.filter_by(user_id=user_id).first()
    if not professional:
        flash("Please login to access this page", "danger") 
        return redirect(url_for('home'))
    service_requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
    
    status_counts = Counter([req.status for req in service_requests])
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    
    
    fig, ax = plt.subplots()
    ax.bar(labels,values,color=['skyblue', 'salmon', 'lightgreen'])
    ax.set_xlabel('Status')
    ax.set_ylabel('Count')
    ax.set_title('Service Requests by Status')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('professional/prof_sum.html',plot_url=plot_url)

@app.route('/professional/logout', methods=['GET', 'POST'])
def prof_logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

    
    
    
