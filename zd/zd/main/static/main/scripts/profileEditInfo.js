// Функции для модального окна
function openEditModal() {
  const modal = document.getElementById('editProfileModal');
  if (modal) {
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }
}

function closeEditModal() {
  const modal = document.getElementById('editProfileModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

// Закрытие по клику на оверлей
document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('editProfileModal');
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        closeEditModal();
      }
    });
  }
  // Превью загружаемого фото
  const imageInput = document.getElementById('id_profile_image');
  const currentAvatar = document.getElementById('currentAvatar');

  if (imageInput && currentAvatar) {
    imageInput.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          currentAvatar.src = event.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }
});

// Обработчик для кнопки редактирования (ручка)
document.addEventListener('DOMContentLoaded', function () {
  const penButton = document.querySelector('.pen');
  if (penButton) {
    penButton.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      openEditModal();
    });
  }
});

// Обработчик отправки формы
document.addEventListener('DOMContentLoaded', function () {
  const editForm = document.getElementById('editProfileForm');
  if (editForm) {
    editForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const submitBtn = this.querySelector('.btn-save');
      const originalText = submitBtn ? submitBtn.textContent : 'Сохранить';

      if (submitBtn) {
        submitBtn.textContent = 'Сохранение...';
        submitBtn.disabled = true;
      }

      // Удаляем старые ошибки
      document.querySelectorAll('.field-error').forEach(el => el.remove());
      document.querySelectorAll('.form-input').forEach(el => el.classList.remove('error'));

      const formData = new FormData(this);

      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Обновляем имя пользователя на странице
            const userNameElement = document.querySelector('.profile-header-left h2');
            if (userNameElement && data.username) {
              userNameElement.textContent = data.username;
            }

            // Обновляем фото, если оно изменилось
            if (data.profile_image) {
              const avatarImg = document.querySelector('.profile-header-img');
              if (avatarImg) avatarImg.src = data.profile_image;

              const currentAvatarModal = document.getElementById('currentAvatar');
              if (currentAvatarModal) currentAvatarModal.src = data.profile_image;
            }

            closeEditModal();
            showNotification('Профиль успешно обновлен!', 'success');
          } else {
            if (data.errors) {
              for (const [field, errors] of Object.entries(data.errors)) {
                const fieldElement = editForm.querySelector(`[name="${field}"]`);
                if (fieldElement) {
                  fieldElement.classList.add('error');
                  const errorDiv = document.createElement('div');
                  errorDiv.className = 'field-error';
                  errorDiv.textContent = errors.join(', ');
                  fieldElement.parentNode.insertBefore(errorDiv, fieldElement.nextSibling);
                }
              }
            }
            showNotification(data.message || 'Ошибка при сохранении профиля', 'error');
          }
        })
        .catch(error => {
          console.error('Ошибка:', error);
          showNotification('Произошла ошибка при сохранении', 'error');
        })
        .finally(() => {
          if (submitBtn) {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
          }
        });
    });
  }
});

// Функция показа уведомлений
function showNotification(message, type) {
  const notification = document.createElement('div');
  notification.className = `custom-notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 8px;
        z-index: 10000;
        font-size: 14px;
        animation: slideIn 0.3s ease;
    `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}
