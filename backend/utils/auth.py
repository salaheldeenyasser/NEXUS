import jwt
import time

SECRET_KEY = "replace_this_with_a_real_secret_key"

def create_token(user_name: str, expires_in: int = 3600):
    payload = {
        "sub": user_name,
        "exp": int(time.time()) + expires_in
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
