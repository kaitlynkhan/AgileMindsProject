from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token
from App.models import User
from App.database import db
import App.controllers.auth as auth
import App.controllers.user as userr
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
    username = get_jwt_identity()
    return jsonify(logged_in_as=username), 200

    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.json
    token = login(data['username'], data['password'])
    if not token:
       return jsonify(message='bad username or password given'), 401
    response = jsonify(access_token=token) 
    set_access_cookies(response, token)
    return response
    

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    username = get_jwt_identity()
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  user = userr.get_user_by_username(data['username'])

  if not token:
    return jsonify(message='bad username or password given'), 401
  
  response = jsonify(access_token=token) 
  user.active_token = token
  db.session.commit()
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    userid = get_jwt_identity()
    user = userr.get_user(userid)
    return jsonify(logged_in_as=user.username), 200

@auth_views.route('/api/logout', methods=['GET'])
@jwt_required()
def logout_api():
    userid = get_jwt_identity()
    user = User.query.get(userid)
    if not user:
        return {"message": "User not found"}

    if not user.active_token:
        return {"message": f"User '{user.username}' is not logged in"}

    user.active_token = None
    db.session.commit()

    response = jsonify(message=f"User '{user.username}' logged out successfully")
    unset_jwt_cookies(response)
    return response