document.addEventListener("DOMContentLoaded", function () {
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    const deleteTaskTitle = document.getElementById('delete-task-title');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

    let taskIdToDelete = null;

    // Всплытие модального окна с нужной задачей
    document.querySelectorAll('.delete-task').forEach(button => {
        button.addEventListener('click', function () {
            taskIdToDelete = this.getAttribute('data-task-id');
            const taskTitle = this.getAttribute('data-task-title');
            
            deleteTaskTitle.textContent = `"${taskTitle}"`;
            deleteModal.show();
        });
    });

    // Обработка нажатия на кнопку удаления
    confirmDeleteBtn.addEventListener('click', function () {
        fetch(`/tasks/${taskIdToDelete}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}',  // Если требуется защита от CSRF-атак
                'Content-Type': 'application/json'
            },
        })
        .then(response => {
            if (response.ok) {
                // Удаляем задачу из DOM
                document.querySelector(`[data-task-id="${taskIdToDelete}"]`).remove();

                // Закрываем модальное окно
                deleteModal.hide();
            } else {
                alert('Ошибка при удалении задачи.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });
});
