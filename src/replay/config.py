import os

from dotenv import load_dotenv

load_dotenv()


APP_NAME = os.environ["APP_NAME"]
APP_ENV = os.environ["APP_ENV"]
DATABASE_URL = os.environ["DATABASE_URL"]