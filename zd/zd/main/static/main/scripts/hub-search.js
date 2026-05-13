// static/main/scripts/hub-search.js

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.main-input input');
    const searchButton = document.querySelector('.main-input img');
    const projectsGrid = document.querySelector('.projects-grid');
    let searchTimeout;
    
    // Функция выполнения поиска
    function performSearch() {
        const query = searchInput.value.trim();
        
        // Показываем скелетон загрузки
        if (projectsGrid) {
            projectsGrid.innerHTML = `
                <div class="projects-skeleton">
                    ${Array(6).fill(0).map(() => `
                        <div class="skeleton-card">
                            <div class="skeleton-title"></div>
                            <div class="skeleton-text"></div>
                            <div class="skeleton-meta"></div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        // AJAX запрос к серверу
        fetch(`/api/projects/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateProjectsGrid(data.projects);
                    updateSearchResultsInfo(data.count, query);
                }
            })
            .catch(error => {
                console.error('Ошибка поиска:', error);
                if (projectsGrid) {
                    projectsGrid.innerHTML = '<div class="no-projects"><p>Ошибка при поиске. Попробуйте позже.</p></div>';
                }
            });
    }
    
    // Функция обновления сетки проектов
    function updateProjectsGrid(projects) {
        if (!projectsGrid) return;
        
        if (projects.length === 0) {
            projectsGrid.innerHTML = `
                <div class="no-projects">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                        <path d="M3 9l9-6 9 6v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/>
                        <polyline points="9 22 9 12 15 12 15 22"/>
                    </svg>
                    <h3>Ничего не найдено</h3>
                    <p>Попробуйте изменить поисковый запрос</p>
                </div>
            `;
            return;
        }
        
        projectsGrid.innerHTML = projects.map(project => `
            <div class="project-card" data-status="${project.status}">
                <div class="project-card-header">
                    <h3 class="project-title">
                        <a href="${project.url}">${escapeHtml(project.name)}</a>
                    </h3>
                    <span class="project-status status-${project.status}">
                        ${escapeHtml(project.status_display)}
                    </span>
                </div>
                <div class="project-description">
                    ${escapeHtml(project.description)}
                </div>
                <div class="project-meta">
                    <div class="meta-item">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 1a3 3 0 100 6 3 3 0 000-6zM2 8a6 6 0 1112 0A6 6 0 012 8z"/>
                        </svg>
                        <span>Автор: ${escapeHtml(project.creator)}</span>
                    </div>
                    <div class="meta-item">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 1a3 3 0 100 6 3 3 0 000-6zM2 8a6 6 0 1112 0A6 6 0 012 8z"/>
                        </svg>
                        <span>${project.participants_count} участников</span>
                    </div>
                    ${project.budget ? `
                    <div class="meta-item budget">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M1 3a1 1 0 011-1h12a1 1 0 011 1v10a1 1 0 01-1 1H2a1 1 0 01-1-1V3z"/>
                        </svg>
                        <span>${project.budget.toLocaleString()} ₽</span>
                    </div>
                    ` : ''}
                </div>
                <div class="project-footer">
                    <div class="project-dates">
                        ${project.start_date ? `<span>С: ${project.start_date}</span>` : ''}
                        ${project.end_date ? `<span>По: ${project.end_date}</span>` : ''}
                    </div>
                    <a href="${project.url}" class="btn-view">Подробнее</a>
                </div>
            </div>
        `).join('');
    }
    
    // Функция обновления информации о результатах
    function updateSearchResultsInfo(count, query) {
        const oldInfo = document.querySelector('.search-results-info');
        if (oldInfo) oldInfo.remove();
        
        if (query) {
            const filtersSection = document.querySelector('.filters-section');
            
            const infoDiv = document.createElement('div');
            infoDiv.className = 'search-results-info';
            infoDiv.innerHTML = `
                <div class="results-count">
                    Найдено <strong>${count}</strong> ${getDeclension(count, 'проект', 'проекта', 'проектов')}
                    по запросу «${escapeHtml(query)}»
                </div>
                <button class="clear-search" onclick="clearSearch()">Очистить</button>
            `;
            
            if (filtersSection) {
                filtersSection.after(infoDiv);
            } else if (projectsGrid) {
                projectsGrid.before(infoDiv);
            }
        }
    }
    
    // Функция очистки поиска
    window.clearSearch = function() {
        if (searchInput) {
            searchInput.value = '';
            performSearch();
        }
    };
    
    // Вспомогательная функция для склонения слов
    function getDeclension(number, one, two, five) {
        let n = Math.abs(number) % 100;
        if (n >= 5 && n <= 20) return five;
        n %= 10;
        if (n === 1) return one;
        if (n >= 2 && n <= 4) return two;
        return five;
    }
    
    // Вспомогательная функция для экранирования HTML
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Обработчики событий
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(performSearch, 300);
        });
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', function(e) {
            e.preventDefault();
            performSearch();
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }
});