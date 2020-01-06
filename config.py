import os
from dotenv import load_dotenv

load_dotenv()
class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "This-is-top-secret"
    DB_CONFIG = {"host":str(os.environ.get("DATABASE_HOST")),
                 "user":str(os.environ.get("DATABASE_USER")),
                 "password":str(os.environ.get("DATABASE_PASSWORD")),
                 "database":str(os.environ.get("DATABASE_NAME"))
            }
