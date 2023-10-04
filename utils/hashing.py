import bcrypt


# Password Hashing Functions

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)