import pytest
import asyncio
import random
import string
import re
from httpx import AsyncClient, ASGITransport
from main import app
from app.database import SessionLocal
from app.models import User  
from app.auth import get_password_hash 

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with SessionLocal() as session:
        async with session.begin():
            await session.execute("TRUNCATE TABLE tasks CASCADE")
            await session.execute("TRUNCATE TABLE users CASCADE")
        await session.commit()

base_url = "http://testserver"

def generate_random_login(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def extract_task_id(response_text):
    match = re.search(r'data-task-id="(\d+)"', response_text)
    return match.group(1) if match else None

@pytest.fixture(scope="function")
async def existing_user():
    async with SessionLocal() as session:
        # Создаем пользователя в базе данных
        login = generate_random_login()
        password = "testpass"
        hashed_password = get_password_hash(password)
        user = User(login=login, hashed_password=hashed_password)
        session.add(user)
        await session.commit()
        return login, password

@pytest.mark.asyncio
async def test_create_task(existing_user):
    login, password = existing_user
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        # Аутентификация и получение токена
        auth_response = await client.post("/auth", json={"login": login, "password": password})
        assert auth_response.status_code == 200
        token = auth_response.json()["access_token"]
        
        # Передача токена в заголовке Authorization
        headers = {"Authorization": f"Bearer {token}"}
        
        # Создание задачи
        form_data = {
            "heading": "New Task",
            "task_text": "Task description"
        }
        create_response = await client.post("/create_task", data=form_data, headers=headers)
        assert create_response.status_code == 200
        
        # Проверка отображения задачи
        lk_response = await client.get("/LK.html", headers=headers)
        assert lk_response.status_code == 200
        assert "New Task" in lk_response.text

@pytest.mark.asyncio
async def test_get_tasks(existing_user):
    login, password = existing_user
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        # Аутентификация и получение токена
        auth_response = await client.post("/auth", json={"login": login, "password": password})
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Проверка получения списка задач
        lk_response = await client.get("/LK.html", headers=headers)
        assert lk_response.status_code == 200
        assert "<div id=\"task-list\">" in lk_response.text

@pytest.mark.asyncio
async def test_edit_task(existing_user):
    login, password = existing_user
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        # Аутентификация и получение токена
        auth_response = await client.post("/auth", json={"login": login, "password": password})
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Создание задачи
        form_data = {
            "heading": "Task to edit",
            "task_text": "Initial description"
        }
        create_response = await client.post("/create_task", data=form_data, headers=headers)
        assert create_response.status_code == 200
        
        # Получение идентификатора задачи
        lk_response = await client.get("/LK.html", headers=headers)
        task_id = extract_task_id(lk_response.text)
        assert task_id is not None, "Task ID not found"
        
        # Редактирование задачи
        edit_form_data = {
            "heading": "Edited Task",
            "task_text": "Edited description"
        }
        edit_response = await client.post(f"/tasks/{task_id}", data=edit_form_data, headers=headers)
        assert edit_response.status_code == 303
        
        # Проверка изменений
        lk_response_after_edit = await client.get("/LK.html", headers=headers)
        assert "Edited Task" in lk_response_after_edit.text
        assert "Edited description" in lk_response_after_edit.text

@pytest.mark.asyncio
async def test_delete_task(existing_user):
    login, password = existing_user
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        # Аутентификация и получение токена
        auth_response = await client.post("/auth", json={"login": login, "password": password})
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Создание задачи
        form_data = {
            "heading": "Task to delete",
            "task_text": "To be deleted"
        }
        create_response = await client.post("/create_task", data=form_data, headers=headers)
        assert create_response.status_code == 200
        
        # Получение идентификатора задачи
        lk_response = await client.get("/LK.html", headers=headers)
        task_id = extract_task_id(lk_response.text)
        assert task_id is not None, "Task ID not found"
        
        # Удаление задачи
        delete_response = await client.post(f"/tasks/{task_id}/delete", headers=headers)
        assert delete_response.status_code == 200
        
        # Проверка удаления
        lk_response_after_delete = await client.get("/LK.html", headers=headers)
        assert "Task to delete" not in lk_response_after_delete.text
