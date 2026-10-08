// (function () {
//   'use strict';

//   const navList = document.querySelectorAll('.nav-link');

//   const hideAllDropdowns = () => {
//     navList.forEach(item => {
//       item.classList.remove('active');
//       const dropdown = item.querySelector('.nav-dropdown');
//       if (dropdown) {
//         dropdown.style.display = 'none';
//         dropdown.classList.remove('dropdown-right-aligned');
//       }
//     });
//   };

//   const positionDropdown = (element, dropdown) => {
//     const rect = element.getBoundingClientRect();
//     const viewportWidth = window.innerWidth;

//     let dropdownWidth;
//     if (viewportWidth <= 768) {
//       dropdownWidth = viewportWidth - 40;
//     } else if (viewportWidth <= 1024) {
//       dropdownWidth = 600;
//     } else {
//       dropdownWidth = 800;
//     }

//     dropdown.classList.remove('dropdown-right-aligned');

//     if (viewportWidth <= 768) {
//       dropdown.style.left = '50%';
//       dropdown.style.transform = 'translateX(-50%)';
//       dropdown.style.width = `${dropdownWidth}px`;
//     } else if (rect.left + dropdownWidth > viewportWidth) {
//       dropdown.classList.add('dropdown-right-aligned');
//     }
//   };

//   navList.forEach(el => {
//     el.addEventListener('click', e => {
//       if (e.target.tagName !== 'A') {
//         e.preventDefault();
//       }
//       e.stopPropagation();

//       const currentDropdown = el.querySelector('.nav-dropdown');

//       if (
//         el.classList.contains('active') &&
//         currentDropdown &&
//         currentDropdown.style.display === 'flex'
//       ) {
//         hideAllDropdowns();
//         return;
//       }

//       hideAllDropdowns();
//       el.classList.add('active');

//       if (currentDropdown) {
//         currentDropdown.style.display = 'flex';
//         positionDropdown(el, currentDropdown);
//       }
//     });
//   });

//   document.addEventListener('click', e => {
//     if (!e.target.closest('.nav-link')) {
//       hideAllDropdowns();
//     }
//   });

//   window.addEventListener('resize', () => {
//     const activeNavLink = document.querySelector('.nav-link.active');
//     if (activeNavLink) {
//       const dropdown = activeNavLink.querySelector('.nav-dropdown');
//       if (dropdown && dropdown.style.display === 'flex') {
//         positionDropdown(activeNavLink, dropdown);
//       }
//     }
//   });

//   const hiddenNavBtn = document.querySelector('.nav-hidden-btn');
//   const mobileNavList = document.querySelector('.nav-list');

//   if (hiddenNavBtn && mobileNavList) {
//     const toggleMobileMenu = () => {
//       if (mobileNavList.classList.contains('visible')) {
//         mobileNavList.style.display = 'grid';
//         document.body.style.overflow = 'hidden';
//         hideAllDropdowns();
//       } else {
//         mobileNavList.style.display = 'none';
//         document.body.style.overflow = '';
//       }
//     };

//     hiddenNavBtn.addEventListener('click', e => {
//       e.preventDefault();
//       e.stopPropagation();

//       mobileNavList.classList.toggle('visible');
//       toggleMobileMenu();
//     });

//     document.addEventListener('click', e => {
//       if (mobileNavList.classList.contains('visible')) {
//         if (!e.target.closest('.nav-list') && !e.target.closest('.nav-hidden-btn')) {
//           mobileNavList.classList.remove('visible');
//           mobileNavList.style.display = 'none';
//           document.body.style.overflow = '';
//         }
//       }
//     });

//     window.addEventListener('resize', () => {
//       if (window.innerWidth > 768) {
//         mobileNavList.classList.remove('visible');
//         mobileNavList.style.display = '';
//         document.body.style.overflow = '';
//       } else if (mobileNavList.classList.contains('visible')) {
//         mobileNavList.style.display = 'grid';
//       }
//     });

//     if (!mobileNavList.classList.contains('visible')) {
//       mobileNavList.style.display = 'none';
//     }
//   }

//   const forOrganizations = document.querySelector('.org-btn');
//   const forPersons = document.querySelector('.pers-btn');
//   const navLinks = document.querySelectorAll('.nav-link');

//   const orgsArr = ['Организации', 'ОНОИО', 'Проекты', 'Обучение и карьера', 'Новости', 'Форум'];
//   const persArr = [
//     'Лидеры информации',
//     'Академия инноваторов',
//     //   'Новатор Москвы',
//     'Обучение и карьера',
//     'Мероприятия',
//     'Сообщество',
//   ];

//   const chooseFor = (option, type) => {
//     if (!option) return;

//     option.addEventListener('click', e => {
//       e.preventDefault();

//       const targetArray = type === 'persons' ? persArr : orgsArr;

//       navLinks.forEach((el, i) => {
//         const link = el.querySelector('h1');
//         if (link && targetArray[i]) {
//           link.textContent = targetArray[i];
//         }
//       });

//       hideAllDropdowns();

//       if (mobileNavList && mobileNavList.classList.contains('visible')) {
//         mobileNavList.classList.remove('visible');
//         mobileNavList.style.display = 'none';
//         document.body.style.overflow = '';
//       }
//     });
//   };

//   if (forOrganizations) chooseFor(forOrganizations, 'orgs');
//   if (forPersons) chooseFor(forPersons, 'persons');

//   window.hideAllDropdowns = hideAllDropdowns;

//   // Выпадающий список по кнопке "Перейти"
//   document.querySelectorAll('[data-dropdown-toggle]').forEach(btn => {
//     btn.addEventListener('click', e => {
//       e.preventDefault();
//       e.stopPropagation();

//       const targetId = btn.getAttribute('data-dropdown-toggle');
//       const target = document.getElementById(targetId);
//       if (!target) return;

//       // Закрываем другие такие же списки
//       document.querySelectorAll('.nav-dropdown-links.open').forEach(el => {
//         if (el !== target) el.classList.remove('open');
//       });

//       // Переключаем текущий
//       target.classList.toggle('open');
//     });
//   });

//   // Закрытие при клике вне
//   document.addEventListener('click', e => {
//     if (!e.target.closest('.nav-dropdown-links') && !e.target.closest('[data-dropdown-toggle]')) {
//       document.querySelectorAll('.nav-dropdown-links.open').forEach(el => {
//         el.classList.remove('open');
//       });
//     }
//   });
// })();
(function () {
  'use strict';

  const navList = document.querySelectorAll('.nav-link');

  const hideAllDropdowns = () => {
    navList.forEach(item => {
      item.classList.remove('active');
      const dropdown = item.querySelector('.nav-dropdown');
      if (dropdown) {
        dropdown.style.display = 'none';
        dropdown.classList.remove('dropdown-right-aligned');
      }
    });
    // Закрываем и вложенные списки
    document.querySelectorAll('.nav-dropdown-links.open').forEach(el => {
      el.classList.remove('open');
    });
  };

  const positionDropdown = (element, dropdown) => {
    const rect = element.getBoundingClientRect();
    const viewportWidth = window.innerWidth;

    let dropdownWidth;
    if (viewportWidth <= 768) {
      dropdownWidth = viewportWidth - 40;
    } else if (viewportWidth <= 1024) {
      dropdownWidth = 600;
    } else {
      dropdownWidth = 800;
    }

    dropdown.classList.remove('dropdown-right-aligned');

    if (viewportWidth <= 768) {
      dropdown.style.left = '50%';
      dropdown.style.transform = 'translateX(-50%)';
      dropdown.style.width = `${dropdownWidth}px`;
    } else if (rect.left + dropdownWidth > viewportWidth) {
      dropdown.classList.add('dropdown-right-aligned');
    }
  };

  navList.forEach(el => {
    el.addEventListener('click', e => {
      // Если клик по ссылке ВНУТРИ дропдауна — не мешаем переходу
      if (e.target.closest('.nav-dropdown a')) {
        return;
      }

      // Если клик по кнопке "Перейти" или по списку ссылок — не мешаем
      if (e.target.closest('[data-dropdown-toggle]') || e.target.closest('.nav-dropdown-links')) {
        return;
      }

      if (e.target.tagName !== 'A') {
        e.preventDefault();
      }
      e.stopPropagation();

      const currentDropdown = el.querySelector('.nav-dropdown');

      if (
        el.classList.contains('active') &&
        currentDropdown &&
        currentDropdown.style.display === 'flex'
      ) {
        hideAllDropdowns();
        return;
      }

      hideAllDropdowns();
      el.classList.add('active');

      if (currentDropdown) {
        currentDropdown.style.display = 'flex';
        positionDropdown(el, currentDropdown);
      }
    });
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.nav-link')) {
      hideAllDropdowns();
    }
  });

  window.addEventListener('resize', () => {
    const activeNavLink = document.querySelector('.nav-link.active');
    if (activeNavLink) {
      const dropdown = activeNavLink.querySelector('.nav-dropdown');
      if (dropdown && dropdown.style.display === 'flex') {
        positionDropdown(activeNavLink, dropdown);
      }
    }
  });

  // ============ БУРГЕР ============
  const hiddenNavBtn = document.querySelector('.nav-hidden-btn');
  const mobileNavList = document.querySelector('.nav-list');

  if (hiddenNavBtn && mobileNavList) {
    const toggleMobileMenu = () => {
      if (mobileNavList.classList.contains('visible')) {
        mobileNavList.style.display = 'grid';
        document.body.style.overflow = 'hidden';
        hideAllDropdowns();
      } else {
        mobileNavList.style.display = 'none';
        document.body.style.overflow = '';
      }
    };

    hiddenNavBtn.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      mobileNavList.classList.toggle('visible');
      toggleMobileMenu();
    });

    document.addEventListener('click', e => {
      if (mobileNavList.classList.contains('visible')) {
        if (!e.target.closest('.nav-list') && !e.target.closest('.nav-hidden-btn')) {
          mobileNavList.classList.remove('visible');
          mobileNavList.style.display = 'none';
          document.body.style.overflow = '';
        }
      }
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        mobileNavList.classList.remove('visible');
        mobileNavList.style.display = '';
        document.body.style.overflow = '';
      } else if (mobileNavList.classList.contains('visible')) {
        mobileNavList.style.display = 'grid';
      }
    });

    if (!mobileNavList.classList.contains('visible')) {
      mobileNavList.style.display = 'none';
    }
  }

  // ============ ПЕРЕКЛЮЧАТЕЛЬ ОРГ/ЛИЦА ============
  const forOrganizations = document.querySelector('.org-btn');
  const forPersons = document.querySelector('.pers-btn');
  const navLinks = document.querySelectorAll('.nav-link');

  const orgsArr = ['Организации', 'ОНОИО', 'Проекты', 'Обучение и карьера', 'Новости', 'Форум'];
  const persArr = [
    'Лидеры информации',
    'Академия инноваторов',
    'Обучение и карьера',
    'Мероприятия',
    'Сообщество',
  ];

  const chooseFor = (option, type) => {
    if (!option) return;
    option.addEventListener('click', e => {
      e.preventDefault();
      const targetArray = type === 'persons' ? persArr : orgsArr;
      navLinks.forEach((el, i) => {
        const link = el.querySelector('h1');
        if (link && targetArray[i]) {
          link.textContent = targetArray[i];
        }
      });
      hideAllDropdowns();
      if (mobileNavList && mobileNavList.classList.contains('visible')) {
        mobileNavList.classList.remove('visible');
        mobileNavList.style.display = 'none';
        document.body.style.overflow = '';
      }
    });
  };

  if (forOrganizations) chooseFor(forOrganizations, 'orgs');
  if (forPersons) chooseFor(forPersons, 'persons');

  // ============ КНОПКА "ПЕРЕЙТИ" ============
  document.querySelectorAll('[data-dropdown-toggle]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();

      const targetId = btn.getAttribute('data-dropdown-toggle');
      const target = document.getElementById(targetId);

      if (!target) {
        console.warn(`[dropdown] Элемент #${targetId} не найден. Проверьте id.`);
        return;
      }

      // Проверка на дубликаты id
      if (document.querySelectorAll(`#${targetId}`).length > 1) {
        console.warn(
          `[dropdown] Найдено несколько элементов с id="${targetId}". id должны быть уникальными!`
        );
      }

      document.querySelectorAll('.nav-dropdown-links.open').forEach(el => {
        if (el !== target) el.classList.remove('open');
      });

      target.classList.toggle('open');

      // Обновляем aria-expanded
      btn.setAttribute('aria-expanded', target.classList.contains('open'));
    });
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.nav-dropdown-links') && !e.target.closest('[data-dropdown-toggle]')) {
      document.querySelectorAll('.nav-dropdown-links.open').forEach(el => {
        el.classList.remove('open');
      });
    }
  });

  window.hideAllDropdowns = hideAllDropdowns;
})();
