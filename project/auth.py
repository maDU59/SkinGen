from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "status": "Incorrect"
        }), 200

    login_user(user, remember=remember)
    return jsonify({
        "status": "Success"
    }), 200

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return jsonify({
            "status": "Incorrect",
            "msg": "Email address already exists"
        }), 200
    
    if password is None or len(password) < 8:
        return jsonify({
            "status": "Incorrect",
            "msg": "Password must be at least 8 characters long"
        }), 200

    new_user = User(email=email, password=generate_password_hash(password), tokens=2)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "Success"
    }), 200

@auth.route('/password-reset-email', methods=['POST'])
def password_reset_email():
    email = request.form.get('email')
    # TO-DO: Implement password reset email sending
    return jsonify({
        "status": "Success",
        "msg": f"An email has been sent to {email} with instructions to reset your password."
    }), 200

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")