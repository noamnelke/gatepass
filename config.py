import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is required")
    DATABASE = os.path.join(os.getcwd(), 'passkeys.db')
    RP_ID = os.environ.get('RP_ID') or 'gatepass.local'
    ORIGIN = os.environ.get('ORIGIN') or 'https://gatepass.local:5000'
    USER_ID = 'GatePass User'
