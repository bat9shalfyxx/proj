(function () {
  'use strict';

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrfToken = getCookie('csrftoken');

  document.addEventListener('DOMContentLoaded', function () {
    const notificationIcon = document.getElementById('notificationIcon');
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    const notificationsList = document.getElementById('notificationsList');
    const notificationBadge = document.getElementById('notificationBadge');
    const markAllReadBtn = document.getElementById('markAllRead');

    let isOpen = false;

    function loadNotifications() {
      fetch('/api/notifications/')
        .then(response => response.json())
        .then(data => {
          updateBadge(data.unread_count);
          renderNotifications(data.notifications);
        })
        .catch(error => console.error('Ошибка загрузки уведомлений:', error));
    }

    function updateBadge(count) {
      if (count > 0) {
        notificationBadge.style.display = 'flex';
        notificationBadge.textContent = count > 99 ? '99+' : count;
      } else {
        notificationBadge.style.display = 'none';
      }
    }

    function renderNotifications(notifications) {
      if (!notificationsList) return;

      if (notifications.length === 0) {
        notificationsList.innerHTML = '<div class="notification-empty">У вас нет уведомлений</div>';
        return;
      }

      notificationsList.innerHTML = notifications
        .map(notif => {
          // Проверяем, что ссылка существует и не ведет на null
          let link = notif.link || '#';

          // Дополнительная проверка на null/invitation/null
          if (link.includes('/null/')) {
            link = '#';
            console.warn('Invalid link detected:', link);
          }

          return `
              <div class="notification-item ${!notif.is_read ? 'unread' : ''}" 
                   data-id="${notif.id}" 
                   data-link="${link}">
                  <div class="notification-title">${escapeHtml(notif.title)}</div>
                  <div class="notification-message">${escapeHtml(notif.message)}</div>
                  <div class="notification-time">${notif.created_at}</div>
              </div>
          `;
        })
        .join('');

      document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function (e) {
          e.stopPropagation();
          const notifId = this.dataset.id;
          const link = this.dataset.link;

          markAsRead(notifId);

          if (link && link !== '#') {
            window.location.href = link;
          } else {
            console.warn('No valid link for notification');
          }
        });
      });
    }

    function markAsRead(notificationId) {
      fetch(`/api/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      }).then(() => loadNotifications());
    }

    function markAllAsRead() {
      fetch('/api/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
      }).then(() => loadNotifications());
    }

    if (notificationIcon) {
      notificationIcon.addEventListener('click', function (e) {
        e.stopPropagation();
        isOpen = !isOpen;
        notificationsDropdown.style.display = isOpen ? 'flex' : 'none';
        if (isOpen) {
          loadNotifications();
        }
      });
    }

    document.addEventListener('click', function (e) {
      if (
        isOpen &&
        !notificationsDropdown.contains(e.target) &&
        !notificationIcon.contains(e.target)
      ) {
        isOpen = false;
        notificationsDropdown.style.display = 'none';
      }
    });

    if (markAllReadBtn) {
      markAllReadBtn.addEventListener('click', markAllAsRead);
    }

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    loadNotifications();

    setInterval(loadNotifications, 30000);
  });
})();
