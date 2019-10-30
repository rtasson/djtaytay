# Helper script to create the database on the first run.

from os import getenv
from util import password_context
from models import User, Session, Base, engine

# Create schema
Base.metadata.create_all(engine)
session = Session()

# Create (or update) admin user
password_hash = password_context.hash(getenv('ADMIN_PASSWORD'))
user = User(id=1, username='admin', password_hash=password_hash)
session.merge(user)
session.commit()
