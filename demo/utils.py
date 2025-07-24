import jwt
import datetime
from django.conf import settings

# Magic link için JWT oluşturur
def create_magiclink_token(user_email):
    payload = {
        'email': user_email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_MAGICLINK_EXP_MINUTES),
        'iat': datetime.datetime.utcnow(),
        'type': 'magiclink'
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

# Magic link JWT'sini doğrular, email döner veya None
def verify_magiclink_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get('type') != 'magiclink':
            return None
        return payload['email']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None 