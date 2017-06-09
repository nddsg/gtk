from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    userid = Column(String(32), nullable=False, primary_key=True)


class Quiz(Base):
    __tablename__ = "quiz"
    quizid = Column(String(32), primary_key=True)
    userid = Column(String(32), ForeignKey("user.userid"))


class Round(Base):
    __tablename__ = "round"
    roundid = Column(String(32), primary_key=True)
    quizid = Column(String(32), ForeignKey("quiz.quizid"))
    image1id = Column(String(512), ForeignKey("image.id"))
    image2id = Column(String(512), ForeignKey("image.id"))
    time = Column(Time())
    outcome = Column(String(32))


class Image(Base):
    __tablename__ = "image"
    id = Column(String(32), primary_key=True)
    subreddit = Column(String(64))
    score = Column(Integer)
    title = Column(String(512))
    image = Column(String(512))
    date = Column(DateTime())


def initialize_session(engine_string):
    engine = create_engine(engine_string)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    """
    Running this script directly causes initialization
    """

    import sys
    initialize_session(sys.argv[1] if len(sys.argv) > 1 else "mysql://scho2:scho2gtk@localhost/gtk")
