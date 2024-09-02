from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from app.views import (
    homepage, auth_page, regis_page, LK_page, edit_page, create_page, show_page,
    create_task, get_task_by_id, update_task, delete_task, edit_task
)
from app.auth import registration, auth, logout

routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    Route("/auth.html", auth_page),
    Route("/regis.html", regis_page),
    Route("/LK.html", LK_page),
    Route("/create.html", create_page),
    Route("/show.html", show_page),
    Route("/edit.html", edit_page),
    Mount("/static", StaticFiles(directory="static"), name="static"),
    Route("/registration", registration, methods=["POST"]),
    Route("/auth", auth, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/create_task", create_task, methods=["POST"]),
    Route("/tasks/{task_id:int}", get_task_by_id, methods=["GET"]),
    Route("/edit/{task_id:int}", edit_task, methods=["GET"]),
    Route("/tasks/{task_id:int}", update_task, methods=["POST"]),
    Route("/tasks/{task_id}", delete_task, methods=["DELETE"]),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(SessionMiddleware, secret_key="praktika2024")
