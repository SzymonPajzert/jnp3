import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    if True:
        meta = MetaData(engine)
        meta.reflect()
        meta.drop_all()

    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import experiment.models
    Base.metadata.create_all(bind=engine)

    from experiment.models import ExperimentConfig

    config = ExperimentConfig(
        0, message={
            1: "Nie klikaj rytmicznie!",
            2: "Sprawdzimy czy nie klikasz rytmicznie",
            3: "Poklikaj dodatkowo w przyciski",
            4: "Postaraj się teraz odpowiadać poprawnie"
        }, execution={
            1: 1000,
            2: 1000,
            3: 1000,
            4: 0
        })

    with open("/home/svp/Programming/jnp3/2/experiment/quizes.json") as quizes_file:
        data = json.load(quizes_file)

        for element in data:
            quiz = experiment.models.Quiz(
                element['nazwa'],
                element['treść'],
                element['streszczenie'],
                element['polecenie'],

                element['P'],
                element['nP'],
                element['Q'],
                element['nQ'],
            )

            db_session.add(quiz)

    db_session.add(config)
    db_session.commit()