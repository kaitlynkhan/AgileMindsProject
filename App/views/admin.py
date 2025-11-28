from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from flask_admin import Admin
from flask import flash, redirect, url_for, request
from App.database import db
from App.models import User, Admin as AdminModel, Staff, Schedule, Shift

class AdminView(ModelView):

    @jwt_required()
    def is_accessible(self):
        return current_user is not None

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Login to access admin")
        return redirect(url_for('index_page', next=request.url))

def setup_admin(app):
    admin = Admin(app, name='FlaskMVC', template_mode='bootstrap3')
    admin.add_view(AdminView(User, db.session))
    admin.add_view(AdminView(AdminModel, db.session, name='Admins', endpoint='admins'))
    admin.add_view(AdminView(Staff, db.session))
    admin.add_view(AdminView(Schedule, db.session))
    admin.add_view(AdminView(Shift, db.session))