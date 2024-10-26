import datetime
import hashlib
import base64


def get_hour(t=None):
    # Returns the current hour if t is None, otherwise the hour of t
    t = t or datetime.datetime.now()
    return int(t.timestamp() / 3600)


def generate_token(gate_id, valid_through_hour, secret, max_length=5):
    # Returns a token for the given gate_id and valid_through_hour
    h = hashlib.sha256(f"{gate_id}:{valid_through_hour}:{secret}".encode()).digest()
    return base64.urlsafe_b64encode(h)[:max_length].decode()


def encode_full_token(gate_id, valid_through_hour, token):
    # Returns a full token string for the given gate_id, valid_through_hour, and token
    return f"{gate_id}:{int_to_base64(valid_through_hour)}:{token}"


def decode_full_token(full_token):
    # Returns the gate_id, valid_through_hour, and token from a full token string
    gate_id, valid_through_hour, token = full_token.split(":")
    return int(gate_id), base64_to_int(valid_through_hour), token


def validate_token(full_token, secret):
    # Returns True if the full token is valid, False otherwise
    gate_id, valid_through_hour, token = decode_full_token(full_token)
    if valid_through_hour < get_hour():
        raise ValueError("Token expired")
    if token != generate_token(gate_id, valid_through_hour, secret):
        raise ValueError("Bad signature")
    return True


def int_to_base64(n):
    # Convert the integer to bytes
    int_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
    # Encode the bytes to base64
    return base64.urlsafe_b64encode(int_bytes).decode("utf-8")


def base64_to_int(s):
    # Decode the base64 string to bytes
    int_bytes = base64.urlsafe_b64decode(s)
    # Convert the bytes to an integer
    return int.from_bytes(int_bytes, byteorder="big")
