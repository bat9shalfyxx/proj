// Функции для модального окна
function openEditModal() {
  const modal = document.getElementById("editProfileModal");
  if (modal) modal.style.display = "flex";
}

function closeEditModal() {
  const modal = document.getElementById("editProfileModal");
  if (modal) modal.style.display = "none";
}

// Закрытие по клику на оверлей
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("editProfileModal");
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) {
        closeEditModal();
      }
    });
  }

  // Превью загружаемого фото
  const imageInput = document.getElementById("id_profile_image");
  const currentAvatar = document.getElementById("currentAvatar");

  if (imageInput && currentAvatar) {
    imageInput.addEventListener("change", function (e) {
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
const penButton = document.querySelector(".pen");
if (penButton) {
  penButton.addEventListener("click", function (e) {
    e.preventDefault();
    openEditModal();
  });
}

// Обработчик отправки формы
const editForm = document.getElementById("editProfileForm");
if (editForm) {
  editForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const submitBtn = this.querySelector(".btn-save");
    const originalText = submitBtn ? submitBtn.textContent : "Сохранить";

    // Меняем текст кнопки и блокируем
    if (submitBtn) {
      submitBtn.textContent = "Сохранение...";
      submitBtn.disabled = true;
    }

    // Удаляем старые ошибки
    document.querySelectorAll(".field-error").forEach((el) => el.remove());
    document
      .querySelectorAll(".form-input")
      .forEach((el) => el.classList.remove("error"));

    const formData = new FormData(this);

    fetch(this.action, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Обновляем имя пользователя на странице
          const userNameElement = document.querySelector(
            ".profile-header-left h2",
          );
          if (userNameElement && data.username) {
            userNameElement.textContent = data.username;
          }

          // Обновляем фото, если оно изменилось
          if (data.profile_image) {
            const avatarImg = document.querySelector(".profile-header-img");
            if (avatarImg) avatarImg.src = data.profile_image;

            // Также обновляем фото в модальном окне
            const currentAvatarModal = document.getElementById("currentAvatar");
            if (currentAvatarModal) currentAvatarModal.src = data.profile_image;
          }

          closeEditModal();
          showNotification("Профиль успешно обновлен!", "success");
        } else {
          // Показываем ошибки под полями
          if (data.errors) {
            for (const [field, errors] of Object.entries(data.errors)) {
              const fieldElement = editForm.querySelector(`[name="${field}"]`);
              if (fieldElement) {
                fieldElement.classList.add("error");
                const errorDiv = document.createElement("div");
                errorDiv.className = "field-error";
                errorDiv.textContent = errors.join(", ");
                fieldElement.parentNode.insertBefore(
                  errorDiv,
                  fieldElement.nextSibling,
                );
              }
            }
          }
          showNotification(
            data.message || "Ошибка при сохранении профиля",
            "error",
          );
        }
      })
      .catch((error) => {
        console.error("Ошибка:", error);
        showNotification("Произошла ошибка при сохранении", "error");
      })
      .finally(() => {
        // Возвращаем кнопку в исходное состояние
        if (submitBtn) {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
        }
      });
  });
}

// Функция показа уведомлений
function showNotification(message, type) {
  // Удаляем старые уведомления
  const oldNotifications = document.querySelectorAll(".custom-notification");
  oldNotifications.forEach((notif) => notif.remove());

  const notification = document.createElement("div");
  notification.className = `custom-notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === "success" ? "#28a745" : "#dc3545"};
        color: white;
        border-radius: 8px;
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease;
    `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Добавляем стили для анимаций, если их нет
if (!document.querySelector("#notification-styles")) {
  const style = document.createElement("style");
  style.id = "notification-styles";
  style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        .field-error {
            color: #dc3545;
            font-size: 12px;
            margin-top: 5px;
            padding: 5px 10px;
            background: rgba(220, 53, 69, 0.1);
            border-radius: 6px;
            display: block;
        }
        .form-input.error {
            border-color: #dc3545 !important;
        }
    `;
  document.head.appendChild(style);
}
