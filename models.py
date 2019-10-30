from os import getenv
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Index

Base = declarative_base()
load_dotenv()

engine = create_engine(getenv('DB_CONNECTION_STRING'), echo=True)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    # The below password hash is an Argon2d hash with time component 3,
    # memory component 12 and parallelism 1.
    password_hash = Column(String)
    admin = Boolean()

    def __repr__(self):
        return "<User(id='{}', username='{}'>".format(self.id, self.username)

Index('username_index', User.username, unique=True)
