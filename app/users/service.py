from app.models.user import User
from app.core.database import db

class UserService:
    @staticmethod
    def create(data):
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user
