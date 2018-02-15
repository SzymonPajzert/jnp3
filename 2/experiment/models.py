import json

from flask import jsonify
from sqlalchemy import Column, String, Integer, Text, PickleType, Boolean, ForeignKey

from experiment.database import Base, db_session


class Quiz(Base):
    __tablename__ = "Quiz"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(Text)
    description = Column(Text)
    description_short = Column(Text)
    goal = Column(Text)

    premise = Column(Text)
    not_premise = Column(Text)
    conclusion = Column(Text)
    not_conclusion = Column(Text)

    def __init__(self,
                 name,
                 description,
                 description_short,
                 goal,
                 premise,
                 not_premise,
                 conclusion,
                 not_conclusion):

        self.name = name
        self.description = description
        self.description_short = description_short
        self.goal = goal

        self.premise = premise
        self.not_premise = not_premise
        self.conclusion = conclusion
        self.not_conclusion = not_conclusion

    def json(self):
        return jsonify({
            "description": self.description,
            "description_short": self.description_short,
            "premise": self.premise,
            "not_premise": self.not_premise,
            "conclusion": self.conclusion,
            "not_conclusion": self.not_conclusion,
        })


class ExperimentConfig(Base):
    __tablename__ = "ExperimentConfig"

    id = Column(Integer, primary_key=True)
    message = Column(PickleType)
    execution = Column(PickleType)

    def __init__(self, id, message, execution):
        self.id = id
        self.message = message
        self.execution = execution

    def json(self):
        pass


class ExperimentResults:
    def __init__(self):

        self.current_stage = 1
        self.current_quiz = None
        self.quiz_order = None
        self.result_times = {}
        self.result_times[4] = {}

    def digest_data(self, data):
        """Digests the data assuming it comes for the current stage.

        :return: True if the data is parsed successfully."""

        print("digesting: {}".format(data))
        print(self.current_stage)

        if self.current_stage < 4:
            self.result_times[self.current_stage] = data

            self.current_stage += 1

        if self.current_stage == 4:
            if self.current_quiz is None:
                from random import shuffle
                self.quiz_order = [x + 3 for x in range(db_session.query(Quiz).count() - 2)]
                shuffle(self.quiz_order)

                self.quiz_order = [1,2] + self.quiz_order

                self.current_quiz = 0

            else:
                self.result_times[self.current_stage][self.current_quiz] = data

        print(self.json())

        return self

    def json(self):
        return {
            'current_stage': self.current_stage,
            'current_quiz': self.current_quiz,
            'quiz_order': self.quiz_order,
            'result_times': self.result_times
        }


class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pseudonym = Column(String)
    is_female = Column(Boolean)
    age = Column(Integer)
    results = Column(PickleType)
    config = Column(Integer, ForeignKey("ExperimentConfig.id"))

    def __init__(self, pseudonym, is_female, age):
        self.pseudonym = pseudonym
        self.is_female = is_female
        self.age = age
        self.results = ExperimentResults()
        self.config = 0

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'id': self.id,
            'stage': self.results.current_stage,
        }
