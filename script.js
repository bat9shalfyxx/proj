class ContentSwitcher {
    constructor() {
        this.currentContent = "organization";
        this.contentContainer = document.querySelector(".switch-content");
        this.contentFiles = {
            organization: "./content/organization.html",
            individual: "./content/individual.html",
        };

        if (!this.contentContainer) {
            console.error("Контейнер .switch-content не найден!");
            return;
        }

        this.init();
    }

    init() {
        console.log("Инициализация ContentSwitcher...");
        this.setupHeaderLinks();
        this.loadContent(this.currentContent);
        this.bindEvents();
        console.log("ContentSwitcher инициализирован");
    }

    // Настройка ссылок в header
    setupHeaderLinks() {
        const headerLinks = document.querySelectorAll(".header-left-info a");
        if (headerLinks.length >= 2) {
            headerLinks[0].dataset.content = "organization";
            headerLinks[0].classList.add("active");
            headerLinks[1].dataset.content = "individual";

            console.log("Ссылки в header настроены");
        } else {
            console.error("Не найдены ссылки в header!");
        }
    }

    // Загрузка контента из файла
    async loadContent(contentType) {
        try {
            this.contentContainer.classList.add("loading");

            const response = await fetch(this.contentFiles[contentType]);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const content = await response.text();

            // Добавляем плавный переход
            this.contentContainer.style.opacity = "0";

            setTimeout(() => {
                this.contentContainer.innerHTML = content;
                this.contentContainer.style.opacity = "1";
                this.contentContainer.classList.remove("loading");

                // Обновляем активную ссылку
                this.updateActiveLink(contentType);

                // Инициализируем функциональность для загруженного контента
                this.initContentFeatures();
            }, 300);

            this.currentContent = contentType;
        } catch (error) {
            console.error("Ошибка загрузки контента:", error);
            this.contentContainer.classList.remove("loading");
            this.contentContainer.innerHTML = `
                <div class="error-message">
                    <h3>Ошибка загрузки контента</h3>
                    <p>Не удалось загрузить ${contentType} контент</p>
                    <button onclick="contentSwitcher.loadContent('default')">Вернуться к основному</button>
                </div>
            `;
        }
    }

    // Обновление активной ссылки
    updateActiveLink(contentType) {
        document.querySelectorAll(".header-left-info a").forEach((link) => {
            link.classList.remove("active");
        });

        document.querySelector(`[data-content="${contentType}"]`).classList.add("active");
    }

    // Привязка событий
    bindEvents() {
        document.addEventListener("click", (e) => {
            // Обработка кликов по ссылкам в header
            if (e.target.closest(".header-left-info a")) {
                e.preventDefault();
                const contentType = e.target.closest("a").dataset.content;
                if (contentType && contentType !== this.currentContent) {
                    this.loadContent(contentType);
                }
            }
        });
    }

    // Инициализация функциональности для загруженного контента
    initContentFeatures() {
        // Инициализируем навигацию для organization контента
        if (this.currentContent === "organization") {
            this.initNavigation();
        }

        // Инициализируем карточки для individual контента
        if (this.currentContent === "individual") {
            this.initIndividualCards();
        }
    }

    // Инициализация навигации (из предыдущего кода)
    initNavigation() {
        const navList = document.querySelectorAll(".nav-link");
        if (!navList.length) return;

        // Функция для скрытия всех dropdown
        function hideAllDropdowns() {
            navList.forEach((item) => {
                item.classList.remove("active");
                const dropdown = item.querySelector(".nav-dropdown");
                if (dropdown) {
                    dropdown.style.display = "none";
                    dropdown.classList.remove("dropdown-right-aligned");
                }
            });
        }

        // Функция для определения позиции dropdown
        function positionDropdown(element, dropdown) {
            const rect = element.getBoundingClientRect();
            const dropdownWidth = 600;
            const viewportWidth = window.innerWidth;

            dropdown.classList.remove("dropdown-right-aligned");

            if (rect.left + dropdownWidth > viewportWidth) {
                dropdown.classList.add("dropdown-right-aligned");
            }
        }

        navList.forEach((el) => {
            el.addEventListener("click", (e) => {
                e.preventDefault();

                const currentDropdown = el.querySelector(".nav-dropdown");

                if (el.classList.contains("active") && currentDropdown && currentDropdown.style.display === "flex") {
                    hideAllDropdowns();
                    return;
                }

                hideAllDropdowns();

                el.classList.add("active");

                if (currentDropdown) {
                    currentDropdown.style.display = "flex";

                    positionDropdown(el, currentDropdown);
                }
            });
        });

        // Обработчик клика вне навигации для скрытия dropdown
        document.addEventListener("click", (e) => {
            if (!e.target.closest(".nav-link")) {
                hideAllDropdowns();
            }
        });

        // Обработчик изменения размера окна для корректного позиционирования dropdown
        window.addEventListener("resize", () => {
            const activeNavLink = document.querySelector(".nav-link.active");
            if (activeNavLink) {
                const dropdown = activeNavLink.querySelector(".nav-dropdown");
                if (dropdown && dropdown.style.display === "flex") {
                    positionDropdown(activeNavLink, dropdown);
                }
            }
        });
    }

    // Инициализация карточек для физических лиц
    initIndividualCards() {
        const cards = document.querySelectorAll(".individual-card");
        cards.forEach((card) => {
            card.addEventListener("click", () => {
                card.classList.toggle("active");
            });
        });

        const cardButtons = document.querySelectorAll(".card-button");
        cardButtons.forEach((btn) => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const cardTitle = btn.closest(".individual-card").querySelector("h3").textContent;
                alert(`Выбрано: ${cardTitle}`);
            });
        });

        const actionButtons = document.querySelectorAll(".action-button");
        actionButtons.forEach((btn) => {
            btn.addEventListener("click", () => {
                const action = btn.textContent;
                alert(`Выполнено действие: ${action}`);
            });
        });

        // Инициализация элементов списка возможностей
        const featureItems = document.querySelectorAll(".feature-item");
        featureItems.forEach((item) => {
            item.addEventListener("click", () => {
                const featureTitle = item.querySelector("h4").textContent;
                console.log(`Выбрана возможность: ${featureTitle}`);
            });
        });
    }
}

let contentSwitcher;
document.addEventListener("DOMContentLoaded", () => {
    contentSwitcher = new ContentSwitcher();
});

window.contentSwitcher = contentSwitcher;
