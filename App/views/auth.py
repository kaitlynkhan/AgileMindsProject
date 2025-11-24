from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token
from App.models import User
from App.controllers.auth import login

from.index import index_views 

from App.controllers import (
    login,

)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
  data = request.json
  response = login_user(data['username'], data['password'])
  if not response:
    return jsonify(message='bad username or password given'), 403
  return response
    

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  response = login(data['username'], data['password'])
  if not response:
    return jsonify(message='bad username or password given'), 403
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    username = get_jwt_identity()
    return jsonify(logged_in_as=username), 200

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response