from flask import jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, JWTManager,
    get_jwt_identity, set_access_cookies, verify_jwt_in_request
)
from App.models import User, user
from App.database import db

def _get_user_by_username(username):
    """Fetch a user object by username."""
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()

def login(username, password):
    user = _get_user_by_username(username)
    if user and user.check_password(password):
        token = create_access_token(identity=user)
        return token
    return None


def loginCLI(username, password):
    user = _get_user_by_username(username)

    if user and user.check_password(password):

        # Return existing token if already logged in
        if user.active_token:
            return {"message": "User already logged in", "token": user.active_token}

        # Generate new token
        token = create_access_token(identity=str(user.id))
        user.active_token = token
        db.session.commit()

        return {"message": "Login successful", "token": token}

    return {"message": "Invalid username or password"}


def logout(username):
    user = _get_user_by_username(username)

    if not user:
        return {"message": "User not found"}

    if not user.active_token:
        return {"message": f"User '{username}' is not logged in"}

    user.active_token = None
    db.session.commit()

    return {"message": f"User '{username}' logged out successfully"}


def setup_jwt(app):
    jwt = JWTManager(app)

    # Always store user.id (as string) in JWT
    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        user_id = getattr(identity, "id", identity)
        return str(user_id) if user_id is not None else None

    # Automatically load user from JWT on request
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        try:
            return db.session.get(User, int(identity))
        except (TypeError, ValueError):
            return None

    return jwt

def add_auth_context(app):
    @app.context_processor
    def inject_user():
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user_id = int(identity) if identity is not None else None

            current_user = (
                db.session.get(User, user_id)
                if user_id is not None else None
            )

            is_authenticated = current_user is not None

        except Exception:
            # Invalid or missing JWT
            is_authenticated = False
            current_user = None

        return dict(
            is_authenticated=is_authenticated,
            current_user=current_user
        )
