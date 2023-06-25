from flask import render_template, request, flash, redirect, url_for, session
from app import app, db, bcrypt
from app.admin.models import  User
import secrets, os
from flask_paginate import Pagination, get_page_args
from app.utils.email import send_email
import random
import string
from datetime import datetime, timedelta
from flask import render_template_string
import uuid
from dotenv import dotenv_values, set_key, load_dotenv

env = dotenv_values(".env")



@app.route('/register', methods=["GET", "POST"])
def register():
    """ Register User
    """

    if request.method == 'POST':
        email = request.form.get('email')
        existing_user = User.query.filter_by(email=email).first()
        admin = User.query.filter().all()

        if existing_user:
            flash('User with the email already exists', 'error')
            return redirect(url_for('register'))

        
        # If the email does not exist, continue with the registration process
        hash_password = bcrypt.generate_password_hash(request.form.get('password'))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_name = request.form.get('user_name')
        token_time = datetime.now()
        id = str(uuid.uuid4())
        is_admin = False

        if len(admin) == 0:
            is_admin = True
    
         # Generate a random six-digit OTP code
        otp_code = ''.join(random.choices(string.digits, k=6))
        token = otp_code
        user = User(username=request.form.get('username'), password=hash_password, email=email,
                    first_name=first_name, last_name=last_name, token=token, token_time=token_time, id=id, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()

        # Email Template
        message = render_template_string(
            '''
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>Confirmation Email</title>
            </head>
            <body>
            <h2>Confirmation Email</h2>
            <p>Hello,</p>
            <p>Thank you for registering with us, Your verification code is:</p>
            <h3>{{ otp_code }}</h3>
            <p>Please enter this code to complete your verification.</p>
            <p>Best regards,<br>Your Company</p>
            </body>
            </html>
            ''',
            otp_code=otp_code
        )
    
        # Send email to user
        send_email(email, "Email Verification", message)
        session['email'] = email
        session['verify-type'] = 'email'
        return redirect(url_for('otp', id=id))
    
    return render_template('admin/register_admin.html', title="Registration page")


@app.route('/get-otp/<id>', methods=['GET'])
def getOtp(id):
    """ Generate OTP Code
    """
    # Check if is a valid user
    if 'email' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(id=id).first()

    # Generate a random six-digit OTP code
    otp_code = ''.join(random.choices(string.digits, k=6))

    # Double check if is a valid user
    if user and session.get('email') == user.email:
        user.token = otp_code
        user.token_time = datetime.now()
        db.session.commit()
    else:
        return redirect(url_for('login'))
    
    # Message Template
    message = render_template_string(
            '''
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>Confirmation Email</title>
            </head>
            <body>
            <h2>Confirmation Email</h2>
            <p>Hello,</p>
            <p>Your verification code is:</p>
            <h3>{{ otp_code }}</h3>
            <p>Please enter this code to complete your verification.</p>
            <p>Best regards,<br>Your Company</p>
            </body>
            </html>
            ''',
            otp_code=otp_code
        )

    # Send OTP code to user
    send_email(session['email'], "Email Verification", message)
    return ("ok")
    


@app.route('/otp/<id>', methods=["GET", "POST"])
def otp(id):
    """ Verify OTP code
    """

    user = User.query.filter_by(id=id).first()

    # Check if is a valid user
    if not user or 'email' not in session or session.get('email') != user.email:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_time = datetime.now()

        # Check if code is still valid
        time_difference = current_time - user.token_time

        if user and user.token != request.form.get('otp'):
            # Check if is a user and the token is valid
            flash('Invalid otp try again', 'danger')
            return redirect(url_for('otp', id=id))

    
        if time_difference > timedelta(minutes=2):
            print(time_difference > timedelta(minutes=2))
            # Check to see if code is expired
            flash('Expired otp try again', 'danger')
            return redirect(url_for('otp', id=id))
    
        # Check if code is for registeration
        if user and session.get('verify-type') == 'email':
            user.verified = True
            db.session.commit()
            return redirect(url_for('users', id=id))

        elif user and user.is_admin == True:
            return redirect(url_for('admin', id=id))
        
        elif user:
            return redirect(url_for('users', id=id))

        return redirect(url_for('login'))
     
    return render_template('/admin/otp.html', id=id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login route
    """
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        # check for normal user
        if user and bcrypt.check_password_hash(user.password, password):
            session['email'] = user.email

            # Check if user is verified
            if user.verified == False:
                session['verify-type'] = 'email'
            else:
                session['verify-type'] = 'login'
            return redirect(url_for('otp', id=user.id))

        else:
            flash('Wrong Password or email try again', 'danger')
    return render_template("admin/login.html", title="login")




@app.route('/logout', methods=['GET'])
def logout():
    """ Logout user
    """
    if session.get('email'):
        del session['email']
    return redirect(url_for('login'))



@app.route('/admin/<id>')
def admin(id):
    """ Admin panel where admin can see all users
    """
    user = User.query.filter_by(id=id).first()
    if not user or  'email' not in session or user.email != session.get('email'):
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    users = User.get_all(page=page)
    return render_template('admin/user.html', users=users, name=user.username, id=id)

@app.route('/admin/delete/<user_id>/<id>', methods=['POST'])
def delete_user(user_id, id):
    """ Where Admin can delete User
    """
    user = User.query.get(user_id)
    if user.is_admin == True:
        flash("can't delete admin user", "danger")
        return redirect(url_for('admin', id=id))
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin', id=id))

# # @app.route('/admin/edit/<user_id>', methods=['GET', 'POST'])
# # def edit_user(user_id):
# #     """ Where Admin can edit users Details
# #     """
# #     user = User.query.get(user_id)
# #     if not user:
# #         return redirect(url_for('admin'))
    
# #     if request.method == 'POST':
# #         user.email = request.form.get('email')
# #         user.first_name = request.form.get('first_name')
# #         user.last_name = request.form.get('last_name')
# #         db.session.commit()
# #         return redirect(url_for('admin'))
    
#     return render_template('admin/edit_user.html', user=user)


@app.route('/users/<id>')
def users(id):
    """ User Dashboard
    """
    user = User.query.filter_by(id=id).first()
    if not user or  'email' not in session or user.email != session.get('email'):
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html', username=user.username)
   


@app.route('/foreget-password', methods=['GET', 'POST'])
def foregetPassword():
    """ Request for forget Password
    """
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email = email).first()
        if user:
            session['email'] = user.email
            return redirect(url_for('resetPassword', id=user.id))
        flash('Email not registered', 'danger')
    return render_template('admin/forget_password.html')



@app.route('/resetpassword/<id>', methods=['GET', 'POST'])
def resetPassword(id):
    """ Reset Users password
    """
    user = User.query.filter_by(id=id).first()

    if not user or 'email' not in session or session.get('email') != user.email:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_time = datetime.now()

        # Check if code is still valid
        time_difference = current_time - user.token_time

        if user and user.token != request.form.get('otp'):
            # Check if is a user and the token is valid
            flash('Invalid otp try again', 'danger')
            return redirect(url_for('otp', id=id))

    
        if time_difference > timedelta(minutes=2):
            print(time_difference > timedelta(minutes=2))
            # Check to see if code is expired
            flash('Expired otp try again', 'danger')
            return redirect(url_for('otp', id=id))
        
        # Check if password is same
        password = request.form.get('password')
        confirm = request.form.get('confirmPassword')
        if password != confirm:
            flash('Password not match!', 'danger')
            return redirect(url_for('resetPassword', id=id))
        user.password = bcrypt.generate_password_hash(request.form.get('password'))
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('admin/reset_password.html', id=id)