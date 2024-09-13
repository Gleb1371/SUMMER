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
    browser.get("http://77.222.54.203/regis.html")

    try:
        login_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, "login"))
        )
        login_input.clear()
        login_input.send_keys(login)

        password_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(password)

        register_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        register_button.click()

        # Ожидание перехода на главную страницу после успешной регистрации
        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://77.222.54.203/index.html")
        )

        return True

    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return False

def login(browser, login_url, username, password):
    """Выполняет вход в систему с заданными логином и паролем."""
    browser.get(login_url)
    browser.find_element(By.NAME, "login").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    try:
        # Ожидание перехода на страницу личного кабинета после успешного входа
        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://77.222.54.203/LK.html")
        )
        print("Вход выполнен успешно!")

        return True

    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        return False

def login_with_invalid_credentials(browser, login_url):
    """Проверяет неправильные учетные данные."""
    browser.get(login_url)
    browser.find_element(By.NAME, "login").send_keys("FakeUser")
    browser.find_element(By.NAME, "password").send_keys("fakepassword")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    try:
        error_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))  
        )
        return True
    
    except Exception as e:
        print(f"Ошибка авторизации с неверными данными: {e}")
        return False

def register_with_existing_login(browser, existing_login, password):
    """Попытка регистрации с уже существующим логином."""
    browser.get("http://77.222.54.203/regis.html")

    try:
        login_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, "login"))
        )
        login_input.clear()
        login_input.send_keys(existing_login)

        password_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(password)

        register_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        register_button.click()

        error_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )

        return True

    except Exception as e:
        print(f"Ошибка регистрации с существующим логином: {e}")
        return False

def create_task(browser, task_name, task_description):
    """Создает новую задачу."""
    browser.get("http://77.222.54.203/create.html")

    heading_input = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "textInput1"))
    )
    heading_input.clear()
    heading_input.send_keys(task_name)

    description_input = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "textInput2"))
    )
    description_input.clear()
    description_input.send_keys(task_description)

    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    try:
        # Проверка, что задача появилась в списке задач
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div.task strong"))
        )
        return True
    
    except Exception as e:
        print(f"Ошибка создания задачи: {e}")
        return False

def edit_task(browser, task_id, new_task_name, new_task_description):
    """Редактирует существующую задачу."""
    edit_url = f"http://77.222.54.203/edit/{task_id}"
    browser.get(edit_url)

    try:
        heading_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "textInput1"))
        )
        heading_input.clear()
        heading_input.send_keys(new_task_name)

        description_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "textInput2"))
        )
        description_input.clear()
        description_input.send_keys(new_task_description)

        save_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_button.click()

        WebDriverWait(browser, 10).until(
            EC.url_to_be("http://77.222.54.203/LK.html")
        )

        # Проверка обновленного заголовка задачи на странице
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"div.task[data-task-id='{task_id}'] .task-name strong")
            )
        )

        return True
    
    except Exception as e:
        print(f"Ошибка редактирования задачи: {e}")
        return False

def delete_task(browser, task_id):
    """Удаляет задачу."""
    browser.get("http://77.222.54.203/LK.html")

    try:
        # Ожидание появления задачи в списке
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div.task[data-task-id='{task_id}']"))
        )

        # Поиск и клик по кнопке удаления
        delete_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".delete-task[data-task-id='{task_id}']"))
        )
        delete_button.click()

        # Ожидание появления модального окна
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "deleteModal"))
        )

        # Поиск и клик по кнопке подтверждения удаления
        confirm_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "confirm-delete-btn"))
        )
        confirm_button.click()

        # Ожидание исчезновения задачи из списка
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, f"div.task[data-task-id='{task_id}']"))
        )

        return True

    except Exception as e:
        print(f"Ошибка удаления задачи: {e}")
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
        login_url = "http://77.222.54.203/auth.html"
        if login(browser, login_url, random_login, random_password):
            # Создание задачи
            if create_task(browser, "Новая задача", "Описание новой задачи"):
                print("Задача успешно создана")
                
                # Получение task_id задачи для дальнейшего использования
                task_id = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.task"))
                ).get_attribute("data-task-id")

                # Редактирование задачи
                if edit_task(browser, task_id, new_task_name="Обновленная задача", new_task_description="Обновленное описание"):
                    print("Задача успешно отредактирована")
                else:
                    print("Задача не отредактирована")

                # Удаление задачи
                if delete_task(browser, task_id):
                    print("Задача успешно удалена")
                else:
                    print("Задача не удалена")
            else:
                print("Задача не создана")

        # Негативные тесты

        # Регистрация с существующим логином
        if register_with_existing_login(browser, random_login, random_password):
            print("Ошибка регистрации с существующим логином отображается корректно")
        else:
            print("Ошибка при регистрации с существующим логином не обнаружена")

        # Авторизация с несуществующим логином
        if login_with_invalid_credentials(browser, login_url):
            print("Ошибка авторизации с несуществующими учетными данными отображается корректно")
        else:
            print("Ошибка при авторизации с несуществующими учетными данными не обнаружена")

except Exception as e:
    print(f"Ошибка при выполнении тестов: {e}")

finally:
    browser.quit()

