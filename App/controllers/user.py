from datetime import datetime

from App.database import db
from App.models import User, Admin, Staff

VALID_ROLES = {"user", "staff", "admin"}

def _normalize_role(role):
    """Normalize role to lowercase and strip spaces."""
    return role.lower().strip()


def create_user(username, password, role):
    role = _normalize_role(role)
    if role not in VALID_ROLES:
        print(f"⚠️ Invalid role '{role}'. Must be one of {VALID_ROLES}")
        return None

    if role == "admin":
        new_user = Admin(username=username, password=password)
    elif role == "staff":
        new_user = Staff(username=username, password=password)
    else:
        new_user = User(username=username, password=password, role="user")

    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_user(user_id):
    """Fetch a user by ID."""
    return db.session.get(User, user_id)


def get_user_by_username(username):
    """Fetch a user by username."""
    return User.query.filter_by(username=username).first()


def get_all_users():
    """Return all user objects."""
    return User.query.all()


def get_all_users_json():
    """Return all users as JSON objects."""
    users = get_all_users()
    return [user.get_json() for user in users] if users else []


def update_user(user_id, username):
    """Update a user's username."""
    user = get_user(user_id)
    if user:
        user.username = username
        db.session.commit()
        return user
    return None
