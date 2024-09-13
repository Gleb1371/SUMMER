import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.database import SessionLocal, engine
from app.models import Base, Task
from sqlalchemy.future import select
import random
import string

@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    # Создаем таблицы перед тестами
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем таблицы после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_user_registration_and_auth_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Случайные данные для регистрации и авторизации
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # 1. Регистрация нового пользователя
        response = await client.post("/registration", data={"login": username, "password": password})
        assert response.status_code == 302
        assert response.headers["location"] == "/index.html"

        # 2. Попытка зарегистрироваться с тем же логином (отрицательный тест)
        response = await client.post("/registration", data={"login": username, "password": password})
        assert response.status_code == 200
        assert "Пользователь с таким логином уже зарегистрирован!" in response.text

        # 3. Успешная авторизация с правильными данными
        response = await client.post("/auth", data={"login": username, "password": password})
        assert response.status_code == 302
        assert response.headers["location"] == "/LK.html"

        # 4. Попытка авторизации с неправильным паролем (отрицательный тест)
        response = await client.post("/auth", data={"login": username, "password": "wrongpassword"})
        assert response.status_code == 401
        assert "Неверные данные" in response.text

        # 5. Создание задачи после успешной авторизации
        response = await client.post("/create_task", data={"heading": "Test Task", "task_text": "Task details"})
        assert response.status_code == 303  # Redirect after task creation

        # Проверка, что задача создалась в базе данных
        async with SessionLocal() as session:
            result = await session.execute(select(Task).filter(Task.heading == "Test Task"))
            task = result.scalar_one_or_none()
            assert task is not None
            assert task.task_text == "Task details"

        # 6. Получение задачи
        response = await client.get(f"/tasks/{task.task_id}")
        assert response.status_code == 200
        assert "Test Task" in response.text

        # 7. Редактирование задачи
        response = await client.post(f"/tasks/{task.task_id}", data={"heading": "Edited Task", "task_text": "Edited details"})
        assert response.status_code == 303  # Redirect after task edit

        # Проверка, что задача отредактировалась в базе данных
        async with SessionLocal() as session:
            result = await session.execute(select(Task).filter(Task.task_id == task.task_id))
            edited_task = result.scalar_one_or_none()
            assert edited_task.heading == "Edited Task"
            assert edited_task.task_text == "Edited details"

        # 8. Удаление задачи
        response = await client.delete(f"/tasks/{task.task_id}")
        assert response.status_code == 200
        assert f"Задача с айди={task.task_id} была удалена" in response.json()["message"]

        # Проверка, что задача удалена из базы данных
        async with SessionLocal() as session:
            result = await session.execute(select(Task).filter(Task.task_id == task.task_id))
            deleted_task = result.scalar_one_or_none()
            assert deleted_task is None
