from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.future import select
from starlette.authentication import requires
from .models import Task, User
from .auth import verify_password, get_password_hash, create_access_token
from .database import SessionLocal

templates = Jinja2Templates(directory="app/templates")

async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

async def regis_page(request: Request):
    return templates.TemplateResponse("regis.html", {"request": request})

async def LK_page(request: Request):
    user_id = request.user.username  # получаем user_id из авторизованного пользователя
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id)
            )
            tasks = results.scalars().all()
    
    return templates.TemplateResponse("LK.html", {"request": request, "tasks": tasks})

async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

async def show_page(request: Request):
    return templates.TemplateResponse("show.html", {"request": request})

async def edit_page(request: Request):
    return templates.TemplateResponse("edit.html", {"request": request})

async def registration(request: Request):
    data = await request.json()
    
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return JSONResponse({"error": "Логин и пароль обязательны!"}, status_code=400)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User).filter(User.login == login)
            )
            existing_user = result.scalars().first()

            if existing_user:
                return JSONResponse({"error": "Пользователь с таким логином уже зарегистрирован!"}, status_code=400)

            user = User(
                login=login, password=get_password_hash(password)
            )
            session.add(user)
            await session.commit()

            return JSONResponse({"message": "Регистрация прошла успешно."})

async def auth(request):
    data = await request.json()
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User).filter(User.login == data["login"])
            )
            user = result.scalar_one_or_none()
    if user and verify_password(data["password"], user.password):
        token = create_access_token(data={"sub": user.user_id})
        return JSONResponse({"access_token": token}, status_code=200)
    return JSONResponse({"error": "Неправильные данные"}, status_code=401)

@requires("authenticated")
async def create_task(request: Request):
    form_data = await request.form()
    heading = form_data.get("heading")
    task_text = form_data.get("task_text")
    user_id = int(request.user.username)

    async with SessionLocal() as session:
        async with session.begin():
            task = Task(
                user_id=user_id,
                heading=heading,
                task_text=task_text,
            )
            session.add(task)
            await session.commit()

    # Перенаправление на страницу с текущими задачами после создания задачи
    return HTMLResponse(f'<script>window.location.href = "/LK.html";</script>', status_code=200)

@requires("authenticated")
async def get_task_by_id(request):
    task_id = int(request.path_params["task_id"])
    user_id = request.user.username
   
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()

    if task:
        return templates.TemplateResponse("show.html", {"request": request, "task": task})
    else:
        return JSONResponse({"error": "Task not found"}, status_code=404)

@requires("authenticated")
async def edit_task(request: Request):
    task_id = int(request.path_params["task_id"])
    user_id = int(request.user.username)
    
    async with SessionLocal() as session:
        async with session.begin():
            task = await session.get(Task, task_id)
            if task and task.user_id == user_id:
                task_data = {
                    "task_id": task.task_id,
                    "user_id": user_id,
                    "heading": task.heading,
                    "task_text": task.task_text,
                }
                return templates.TemplateResponse("edit.html", {"request": request, "task": task_data})
            else:
                return JSONResponse({"error": "Task not found or you don't have access"}, status_code=404)

from starlette.responses import RedirectResponse

@requires("authenticated")
async def update_task(request: Request):
    user_id = int(request.user.username)
    task_id = int(request.path_params["task_id"])

    # Парсинг данных из запроса
    form_data = await request.form()
    heading = form_data.get("heading")
    task_text = form_data.get("task_text")

    async with SessionLocal() as session:
        async with session.begin():
            task = await session.get(Task, task_id)
            
            if task and task.user_id == user_id:
                task.heading = heading
                task.task_text = task_text
                await session.commit()

                return RedirectResponse(url="/LK.html", status_code=303)
            else:
                return JSONResponse({"error": "Task not found or you don't have access"}, status_code=404)

@requires("authenticated")
async def delete_task(request):
    task_id = int(request.path_params["task_id"]) 
    user_id = request.user.username 

    async with SessionLocal() as session:
        async with session.begin():
            #точно ли задача текущего пользователя?
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()
            
            if task is None:
                return JSONResponse({"error": "Задача не найдена"}, status_code=404)

            # Удаляем задачу
            await session.delete(task)
            await session.commit()

    return JSONResponse({"message": f"Задача с айди={task_id} была удалена"})
