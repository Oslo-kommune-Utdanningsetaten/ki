import os

class Config:
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', False)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'heioghå'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://ki:pw@localhost/ki'
    FEIDE_CLIENT_ID = os.environ.get("FEIDE_CLIENT_ID", None)
    FEIDE_CLIENT_SECRET = os.environ.get("FEIDE_CLIENT_SECRET", None)
    FEIDE_DISCOVERY_URL = (
        "https://auth.dataporten.no/.well-known/openid-configuration"
    )
    FEIDE_CALLBACK = os.environ.get("FEIDE_CALLBACK", None)
    SITENAME = os.environ.get('SITENAME') or 'AI Osloskolen'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
    OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID', None)
    OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE', None)
    OPENAI_API_TYPE = os.environ.get('OPENAI_API_TYPE', None)
    OPENAI_API_VERSION = os.environ.get('OPENAI_API_VERSION', None)
    OPENAI_API_DEPLOYMENT = os.environ.get('OPENAI_API_DEPLOYMENT', None)
