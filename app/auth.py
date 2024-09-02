from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser, UnauthenticatedUser
from starlette.requests import Request
from datetime import timezone

SECRET_KEY = "PRAKTIKA2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#получаем хэш пароль
def get_password_hash(password):
    return pwd_context.hash(password)

#токен
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=1000)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#извлекаем инф из токена досутпа
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

class JWTAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        # Извлекаем токен из cookies
        token = request.cookies.get("access_token")
        
        if not token:
            return AuthCredentials(), UnauthenticatedUser()

        # Проверяем токен
        try:
            payload = decode_access_token(token)
        except Exception as e:
            print(f"Ошибка декодирования токена: {e}")
            return AuthCredentials(), UnauthenticatedUser()

        if payload is None:
            return AuthCredentials(), UnauthenticatedUser()

         
        return AuthCredentials(["authenticated"]), SimpleUser(payload["sub"])
    