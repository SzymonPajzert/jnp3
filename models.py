from sqlalchemy import Column, Integer, String, Boolean

from experiment.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    password = Column(String(120), unique=True)
    is_admin = Column(Boolean)

    def __init__(self, id=None, password=None):
        self.id = id
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.id