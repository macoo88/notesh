from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

import string
import random

SECRET_KEY = "1eec7df40492b7f94304fc3c7f14f9c5a37dae817b71c76980573a5962cd3fb4" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

########## ----------------------
## H A S H E R
import bcrypt

def hash_password(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#############-------------
######H A S H E R   __ END



def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

