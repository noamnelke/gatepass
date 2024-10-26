#!venv/bin/python3
from config import Config
from app.reg_tokens import get_hour, encode_full_token

valid_through_hour = get_hour() + 24
token = encode_full_token(1, valid_through_hour, Config.SECRET_KEY)

if __name__ == "__main__":
    print(token)