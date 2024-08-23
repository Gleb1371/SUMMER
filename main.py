from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from app.views import (
    homepage, auth_page, regis_page, LK_page, edit_page, create_page, show_page,
    registration, auth, delete_task, get_task_by_id, create_task, update_task, edit_task
)
from app.auth import JWTAuthenticationBackend

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
    Route("/create_task", create_task, methods=["POST"]),
    Route("/tasks/{task_id:int}", get_task_by_id, methods=["GET"]),
    Route("/edit/{task_id:int}", edit_task, methods=["GET"]),
    Route("/tasks/{task_id:int}", endpoint=update_task, methods=["POST"]),
    Route("/tasks/{task_id}", endpoint=delete_task, methods=["DELETE"]),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend())
