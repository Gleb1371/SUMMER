from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random, string

def generate_random_login(length=8):
    """Генерирует случайный логин из букв и цифр."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def register_user(browser, login, password):
    """Регистрирует пользователя с заданными логином и паролем."""
    browser.get("http://127.0.0.1:8000/regis.html")

    try:
        login_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#login"))
        )
        login_input.clear()
        login_input.send_keys(login)

        password_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#password"))
        )
        password_input.clear()
        password_input.send_keys(password)

        register_button = browser.find_element(By.CSS_SELECTOR, "#loginBtn")
        register_button.click()

        success_modal = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-popup"))
        )

        confirm_button = browser.find_element(By.CSS_SELECTOR, ".swal2-confirm")
        confirm_button.click()

        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://127.0.0.1:8000/index.html")
        )

        return True

    except Exception as e:
        return False

def login(browser, login_url, username, password):
    """Выполняет вход в систему с заданными логином и паролем."""
    browser.get(login_url)
    browser.find_element(By.ID, "login").send_keys(username)
    browser.find_element(By.ID, "password").send_keys(password)
    browser.find_element(By.ID, "loginBtn").click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".zadachi"))
    )

    cookies = browser.get_cookies()
    access_token = None
    for cookie in cookies:
        if cookie['name'] == 'access_token':
            access_token = cookie['value']
            break

    if access_token:
        print("Токен успешно установлен:", access_token)
    else:
        print("Токен не был найден в cookies!")

    return access_token

def login_with_invalid_credentials(browser, login_url):
    """Проверяет неправильные учетные данные."""
    browser.get(login_url)
    browser.find_element(By.ID, "login").send_keys("Fake")
    browser.find_element(By.ID, "password").send_keys("fake")
    browser.find_element(By.ID, "loginBtn").click()

    try:
        error_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "loginMessage"))
        )

        return True
    
    except Exception as e:
        return False

def register_with_existing_login(browser, existing_login, password):
    """Попытка регистрации с уже существующим логином."""
    browser.get("http://127.0.0.1:8000/regis.html")

    try:
        login_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#login"))
        )
        login_input.clear()
        login_input.send_keys(existing_login)

        password_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#password"))
        )
        password_input.clear()
        password_input.send_keys(password)

        register_button = browser.find_element(By.CSS_SELECTOR, "#loginBtn")
        register_button.click()

        error_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "loginMessage"))
        )

        return True

    except Exception as e:
        return False

def create_task(browser, task_name, task_description):
    """Создает новую задачу."""
    browser.get("http://127.0.0.1:8000/create.html")

    heading_input = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#textInput1"))
    )
    heading_input.clear()
    heading_input.send_keys(task_name)

    description_input = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#textInput2"))
    )
    description_input.clear()
    description_input.send_keys(task_description)

    browser.find_element(By.CSS_SELECTOR, "button.btn-success").click()
    time.sleep(3)

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div.task strong"))
        )

        return True
    
    except Exception as e:
        return False

def edit_task(browser, heading, new_task_name, new_task_description):
    """Редактирует существующую задачу."""
    browser.get("http://127.0.0.1:8000/LK.html")

    try:
        task_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//a[@class='task-name']//strong[text()='{heading}']")
            )
        )
        
        edit_link = task_element.find_element(By.XPATH, "../../../..//span[contains(@class, 'edit-task')]")
        edit_link.click()
    except Exception as e:
        print(f"Задача с заголовком '{heading}' не найдена: {e}")
        return False

    try:
        heading_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#textInput1"))
        )
        heading_input.clear()
        heading_input.send_keys(new_task_name)

        description_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#textInput2"))
        )
        description_input.clear()
        description_input.send_keys(new_task_description)

        save_button = browser.find_element(By.CSS_SELECTOR, "button.btn-success")
        save_button.click()

        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://127.0.0.1:8000/LK.html")
        )

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//a[@class='task-name']//strong[text()='{new_task_name}']")
            )
        )

        return True
    
    except Exception as e:
        return False

def delete_task(browser, heading):
    """Удаляет задачу."""
    browser.get("http://127.0.0.1:8000/LK.html")

    try:
        delete_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f".delete-task[data-task-title='{heading}']"))
        )
        delete_button.click()

        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "deleteModal"))
        )

        confirm_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "confirm-delete-btn"))
        )
        confirm_button.click()

        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, f".delete-task[data-task-title='{heading}']"))
        )

        return True
    
    except Exception as e:
        return False

try:
    browser = webdriver.Chrome()
    browser.set_window_size(1200, 800)

    # Генерация уникального логина и пароля
    random_login = generate_random_login()
    random_password = generate_random_login(length=12)

    # Регистрация пользователя
    if register_user(browser, random_login, random_password):
        print("Пользователь успешно зарегистрирован")

        # Вход в систему с новым пользователем
        login_url = "http://127.0.0.1:8000/auth.html"
        login(browser, login_url, random_login, random_password)

        # Создание задачи
        if create_task(browser, "Новая задача", "Описание новой задачи"):
            print("Задача успешно создана")
        else:
            print("Задача не создана")

        # Редактирование задачи
        if edit_task(browser, heading="Новая задача", new_task_name="Обновленная задача", new_task_description="Обновленное описание"):
            print("Задача успешно отредактирована")
        else:
            print("Задача не отредактирована")

        # Удаление задачи
        if delete_task(browser, heading="Обновленная задача"):
            print("Задача успешно удалена")
        else:
            print("Задача не удалена")

        # Негативные тесты

        # Регистрация с существующим логином
        existing_login = "test_user"
        if register_with_existing_login(browser, existing_login, random_password):
            print("Ошибка регистрации с существующим логином отображается корректно")
        else:
            print("Ошибка при регистрации с существующим логином не обнаружена")

        # Авторизация с несуществующим логином
        if login_with_invalid_credentials(browser, login_url):
            print("Ошибка авторизации с несуществующими учетными данными отображается корректно")
        else:
            print("Ошибка при авторизации с несуществующими учетными данными не обнаружена")

    else:
        print("Регистрация пользователя не удалась")

finally:
    time.sleep(5)
    browser.quit()
