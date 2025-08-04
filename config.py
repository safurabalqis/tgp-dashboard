import os
from dotenv import load_dotenv

# load .env when in development
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('AUTH_KEY', 'fallback-secret-key')
    PERMANENT_SESSION_LIFETIME = 300  # 5 minutes (in seconds)