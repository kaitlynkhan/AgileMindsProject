from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    
    # Represents a user in the system.
    # Attributes:
    # ID(int) : PK
    # username (string): unique for login
    # password (string): hashed password
    # role (string): Role of user (staff/admin)
    # active_token (string): optional for authentication
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    active_token = db.Column(db.String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "role"
    }

    def __init__(self, username, password, role="user") -> None:
        # Initializes user with username, password and role
        self.username = username
        self.role = role
        self.password = generate_password_hash(password)

    def check_password(self, password):
        # checks if entered password matches the stored hash 
        return check_password_hash(self.password, password)
    
    def get_json(self):
        """Return JSON representation of user."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
