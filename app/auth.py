from passlib.context import CryptContext
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy.future import select
from .models import User
from .database import SessionLocal
from starlette.templating import Jinja2Templates

# Конфигурация для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Инициализация шаблонов
templates = Jinja2Templates(directory="app/templates")

async def registration(request: Request):
    form = await request.form()
    login = form.get("login")
    password = form.get("password")

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.login == login))
            existing_user = result.scalars().first()

            if existing_user:
                return templates.TemplateResponse("regis.html", {"request": request, "error": "Пользователь с таким логином уже зарегистрирован!"})

            user = User(login=login, password=get_password_hash(password))
            session.add(user)
            await session.commit()

    return RedirectResponse(url="/index.html", status_code=302)

async def auth(request: Request):
    form = await request.form()
    login = form.get("login")
    password = form.get("password")

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.login == login))
            user = result.scalar_one_or_none()

    if user and verify_password(password, user.password):
        request.session["user_id"] = user.user_id  # Установка сессии после успешной авторизации
        return RedirectResponse(url="/LK.html", status_code=302)

    return templates.TemplateResponse("auth.html", {"request": request, "error": "Неверные данные"}, status_code=401)

async def logout(request: Request):
    request.session.clear()  # Очистка сессии
    return RedirectResponse(url="/index.html", status_code=302)
