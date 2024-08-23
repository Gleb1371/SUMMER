document.getElementById('loginBtn').addEventListener('click', async (event) => {
    event.preventDefault();  

    const login = document.getElementById('login').value.trim();  
    const password = document.getElementById('password').value.trim(); 
    const loginMessage = document.getElementById('loginMessage');  

    // Функция для скрытия сообщения через 5 секунд
    function hideMessage() {
        setTimeout(() => {
            loginMessage.classList.add('d-none');
            loginMessage.textContent = ''; 
        }, 5000);
    }

    // Скрываем сообщение по умолчанию
    loginMessage.classList.add('d-none');

    if (login.length > 0 && password.length > 0) {
        try {
            const response = await fetch('/registration', {  
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ login, password }),  
            });

            const data = await response.json(); 

            if (response.ok) {
                Swal.fire({
                    title: 'Успех!',
                    text: 'Регистрация прошла успешно!',
                    icon: 'success',
                    confirmButtonText: 'ОК'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = 'index.html';
                    }
                });
            } else {  // Если есть ошибка
                loginMessage.textContent = data.error ? `Ошибка: ${data.error}` : 'Произошла ошибка при регистрации!';
                loginMessage.classList.remove('d-none');  
                hideMessage();  
            }
        } catch (error) {  
            console.error('Ошибка:', error);
            loginMessage.textContent = 'Произошла ошибка при отправке запроса!';
            loginMessage.classList.remove('d-none');
            hideMessage();
        }
    } else {
        loginMessage.textContent = 'Пожалуйста, заполните все поля!';
        loginMessage.classList.remove('d-none');
        hideMessage();
    }
});
