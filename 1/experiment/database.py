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

    from experiment.models import Experiment
    from experiment.models import Config

    config = Config(True, 0, 10, 3)
    e = Experiment(config)
    db_session.add(e)
    db_session.commit()