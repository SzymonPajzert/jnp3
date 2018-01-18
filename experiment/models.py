from flask import json, jsonify
from sqlalchemy import Column, String, Integer, JSON, Text, PickleType

import experiment.user as user
from experiment.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String(120), primary_key=True)
    password = Column(String(120), unique=True)

    def __init__(self, id=None, password=None):
        self.id = id
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.id

    def login_model(self):
        return user.User(self.id, self.password, self.id == "admin")


class Config:
    def __init__(self, feedback, delay, size, training_size):
        self.feedback = feedback
        self.delay = delay              # delay of lights after the last correct key
                                        # if value is -1 it means that it's infinite
        self.size = size
        self.training_size = training_size

    def dict(self) -> String:
        return jsonify({
            'feedback':         self.feedback,
            'delay':            self.delay,
            'size':             self.size,
            'training_size':    self.training_size,
        })


class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    config = Column(PickleType)
    current = Column(PickleType)
    times = Column(PickleType)

    def __init__(self,  config=None):
        self.config = config
        self.current = None
        self.times = dict()

    def __repr__(self):
        return '<Experiment %r>' % self.id
