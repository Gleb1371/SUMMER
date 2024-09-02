import pytest
import asyncio
import random
import string
from httpx import AsyncClient, ASGITransport
from main import app
from app.database import SessionLocal

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
    return ''.join(random.choice(letters_and_digits) for i in range(length))

@pytest.mark.asyncio
async def test_registration():
    random_login = generate_random_login()
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        response = await client.post("/registration", json={"login": random_login, "password": "testpass"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Регистрация прошла успешно."

@pytest.mark.asyncio
async def test_registration_existing_user():
    random_login = generate_random_login()
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        await client.post("/registration", json={"login": random_login, "password": "testpass"})
        response = await client.post("/registration", json={"login": random_login, "password": "testpass"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Пользователь с таким логином уже зарегистрирован!"

@pytest.mark.asyncio
async def test_auth():
    random_login = generate_random_login()
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        await client.post("/registration", json={"login": random_login, "password": "authpass"})
        response = await client.post("/auth", json={"login": random_login, "password": "authpass"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

@pytest.mark.asyncio
async def test_auth_wrong_password():
    random_login = generate_random_login()
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as client:
        await client.post("/registration", json={"login": random_login, "password": "authpass"})
        response = await client.post("/auth", json={"login": random_login, "password": "wrongpass"})
        assert response.status_code == 401
        data = response.json()
        assert "Неправильные данные" in data["error"]
