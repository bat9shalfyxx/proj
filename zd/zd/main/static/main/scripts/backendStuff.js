document.addEventListener('DOMContentLoaded', function() {
    // Функция для показа уведомлений
    function showNotification(message, type = 'success') {
        const container = document.querySelector('.notifications-container');
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="close-notification">&times;</button>
        `;
        container.appendChild(notification);
        
        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Закрытие уведомлений
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close-notification')) {
            e.target.parentElement.remove();
        }
    });
    
    // AJAX отправка формы входа
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = document.getElementById('login-submit');
            const originalText = submitButton.value;
            
            // Показываем индикатор загрузки
            submitButton.value = 'Вход...';
            submitButton.disabled = true;
            
            // Убираем предыдущие ошибки
            const errorElements = document.querySelectorAll('.login-error');
            errorElements.forEach(el => el.remove());
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Успешный вход - редирект
                    showNotification('Вход выполнен успешно!', 'success');
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                } else {
                    // Ошибка входа - показываем сообщение
                    if (data.error) {
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'error login-error';
                        errorDiv.textContent = data.error;
                        loginForm.querySelector('.sign-in-form').appendChild(errorDiv);
                        showNotification(data.error, 'error');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Произошла ошибка при входе', 'error');
            })
            .finally(() => {
                submitButton.value = originalText;
                submitButton.disabled = false;
            });
        });
    }
    
    // Валидация email и телефона (ваш существующий код)
    const emailInput = document.querySelector('input[name="email"]');
    const phoneInput = document.querySelector('input[name="phone_number"]');
    
    if (emailInput && phoneInput) {
        // Создаем элементы для ошибок, если их нет
        if (!document.getElementById('live-email-error')) {
            const emailError = document.createElement('div');
            emailError.id = 'live-email-error';
            emailError.className = 'error';
            emailInput.parentNode.insertBefore(emailError, emailInput.nextSibling);
        }
        
        if (!document.getElementById('live-phone-error')) {
            const phoneError = document.createElement('div');
            phoneError.id = 'live-phone-error';
            phoneError.className = 'error';
            phoneInput.parentNode.insertBefore(phoneError, phoneInput.nextSibling);
        }
        
        const emailError = document.getElementById('live-email-error');
        const phoneError = document.getElementById('live-phone-error');
        
        emailInput.addEventListener('input', function() {
            emailError.textContent = '';
            emailInput.style.borderColor = '';
            
            clearTimeout(window.emailTimeout);
            window.emailTimeout = setTimeout(() => {
                if (emailInput.value.length > 3) {
                    checkEmailExists(emailInput.value);
                }
            }, 1000);
        });
        
        phoneInput.addEventListener('input', function() {
            phoneError.textContent = '';
            phoneInput.style.borderColor = '';
            
            clearTimeout(window.phoneTimeout);
            window.phoneTimeout = setTimeout(() => {
                if (phoneInput.value.length > 5) {
                    checkPhoneExists(phoneInput.value);
                }
            }, 1000);
        });
        
        function checkEmailExists(email) {
            fetch(`/validate-email/?email=${encodeURIComponent(email)}`)
                .then(r => r.json())
                .then(data => {
                    if (data.exists && emailInput.value === email) {
                        emailError.textContent = 'Пользователь с таким email уже существует.';
                        emailInput.style.borderColor = 'red';
                    }
                });
        }
        
        function checkPhoneExists(phone) {
            fetch(`/validate-phone/?phone=${encodeURIComponent(phone)}`)
                .then(r => r.json())
                .then(data => {
                    if (data.exists && phoneInput.value === phone) {
                        phoneError.textContent = 'Пользователь с таким номером телефона уже существует.';
                        phoneInput.style.borderColor = 'red';
                    }
                });
        }
    }
});