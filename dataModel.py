from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Time, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    userid = Column(String(40), nullable=False, primary_key=True)
    fingerprint_canvas_hash = Column(String(32))
    fingerprint_screen_size_x = Column(Integer)
    fingerprint_screen_size_y= Column(Integer)
    fingerprint_screen_color_depth= Column(Integer)
    fingerprint_timezone = Column(Integer)
    fingerprint_dnt_enabled = Column(Boolean)
    fingerprint_http_accept_headers = Column(String(512))
    fingerprint_webgl_hash = Column(String(32))
    fingerprint_language = Column(String(16))
    fingerprint_platform = Column(String(32))
    fingerprint_useragent = Column(String(255))
    fingerprint_user_ip = Column(String(15))

class UserPlugins(Base):
    __tablename__ = "fingerprint_browser_plugins"
    userid = Column(String(40), ForeignKey("user.userid"), primary_key=True)
    plugin_string = Column(String(255), primary_key=True)


class UserFonts(Base):
    __tablename__ = "fingerprint_system_fonts"
    userid = Column(String(40), ForeignKey("user.userid"), primary_key=True)
    font_string = Column(String(128), primary_key=True)


class Quiz(Base):
    __tablename__ = "quiz"
    quizid = Column(String(40), primary_key=True)
    userid = Column(String(40), ForeignKey("user.userid"), nullable=False)
    subreddit = Column(String(64), nullable=False)
    maturity = Column(Enum("Partial", "Complete"), nullable=False)


class InitialRound(Base):
    __tablename__ = "initial_round"
    roundid = Column(String(40), primary_key=True)
    roundno = Column(Integer, nullable=False)
    starttime = Column(DateTime(), nullable=False)
    image1id = Column(Integer, ForeignKey("image.id"), nullable=False)
    image2id = Column(Integer, ForeignKey("image.id"), nullable=False)
    quizid = Column(String(40), ForeignKey("quiz.quizid"), nullable=False)
    

class Round(Base):
    __tablename__ = "round"
    roundid = Column(String(40), primary_key=True)
    roundno = Column(Integer, nullable=False)
    quizid = Column(String(40), ForeignKey("quiz.quizid"), nullable=False)
    image1id = Column(Integer, ForeignKey("image.id"), nullable=False)
    image2id = Column(Integer, ForeignKey("image.id"), nullable=False)
    starttime = Column(DateTime(), nullable=False)
    preferredchoicetime = Column(Time(), nullable=False)
    upvotechoicetime = Column(Time(), nullable=False)
    preferredchoice = Column(Integer, ForeignKey("image.id"), nullable=False)
    upvotechoice = Column(Integer, ForeignKey("image.id"), nullable=False)
    correct = Column(Boolean, nullable=False)


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    subreddit = Column(String(64), primary_key=True)
    score = Column(Integer, nullable=False)
    title = Column(String(512))
    image = Column(String(512), nullable=False)
    date = Column(DateTime()) # what is this?


def initialize_session(engine_string):
    engine = create_engine(engine_string)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    """
    Running this script directly causes initialization
    """

    import sys
    initialize_session(sys.argv[1] if len(sys.argv) > 1 else "mysql://scho2:scho2gtk@localhost/gtk")
