from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.future import select
from .models import Task, User
from .database import SessionLocal
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="app/templates")

async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

async def regis_page(request: Request):
    return templates.TemplateResponse("regis.html", {"request": request})

async def LK_page(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth.html", status_code=302)

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

async def create_task(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth.html", status_code=302)
    
    form_data = await request.form()
    heading = form_data.get("heading")
    task_text = form_data.get("task_text")

    async with SessionLocal() as session:
        async with session.begin():
            task = Task(
                user_id=user_id,
                heading=heading,
                task_text=task_text,
            )
            session.add(task)
            await session.commit()

    return RedirectResponse(url="/LK.html", status_code=303)

async def get_task_by_id(request: Request):
    task_id = int(request.path_params["task_id"])
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth.html", status_code=302)

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

async def edit_task(request: Request):
    task_id = int(request.path_params["task_id"])
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth.html", status_code=302)

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

async def update_task(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth.html", status_code=302)
    
    task_id = int(request.path_params["task_id"])

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

async def delete_task(request: Request):
    task_id = int(request.path_params["task_id"]) 
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth.html", status_code=302)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()
            
            if task is None:
                return JSONResponse({"error": "Task not found"}, status_code=404)

            await session.delete(task)
            await session.commit()

    return JSONResponse({"message": f"Задача с айди={task_id} была удалена"})
