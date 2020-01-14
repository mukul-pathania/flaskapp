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
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["linkingrait@gmail.com"]
    POSTS_PER_PAGE = 10
