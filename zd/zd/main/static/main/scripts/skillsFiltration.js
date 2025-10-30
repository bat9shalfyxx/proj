 const filterInputJs = document.getElementById('filter-skills-js');
    const applyFilterBtnJs = document.getElementById('apply-filter-js');
    const resetFilterBtnJs = document.getElementById('reset-filter-js');
    const applicationsListContainerJs = document.querySelector('.profile-second-request-list');

    // Объявляем allApplicationsData глобально, чтобы она была доступна везде
    let allApplicationsData = []; 
    let currentRenderedApplications = []; // Массив, который реально отображается

    // Функция для получения всех заявок из DOM
    function getAllApplicationsFromDOM() {
        const applicationElements = applicationsListContainerJs.querySelectorAll('.profile-second-request-el');
        const applicationsData = [];

        applicationElements.forEach(el => {
            const idElement = el.querySelector('h3');
            const id = idElement ? idElement.textContent.replace('Заявка № ', '').trim() : 'N/A';
            
            let organizationName = '';
            let solutionName = '';
            const skillListElement = el.querySelector('.skillList');
            const skillListText = skillListElement ? skillListElement.textContent.trim() : '';

            // Более надежный способ извлечения организации и решения
            // Ищем параграфы, которые НЕ имеют класс .skillList
            const nonSkillParagraphs = Array.from(el.querySelectorAll('p')).filter(p => !p.classList.contains('skillList'));
            
            if (nonSkillParagraphs.length > 0) {
                organizationName = nonSkillParagraphs[0].textContent.trim();
            }
            if (nonSkillParagraphs.length > 1) {
                solutionName = nonSkillParagraphs[1].textContent.trim();
            }

            applicationsData.push({
                id: id,
                organization_name: organizationName,
                solution_name: solutionName,
                skill_list_text: skillListText 
            });
        });
        return applicationsData;
    }

    // Функция для отображения заявок
    function renderApplicationsJs(applicationsToRender) {
        if (!applicationsListContainerJs) {
            console.error('Контейнер ".profile-second-request-list" не найден!');
            return;
        }
        applicationsListContainerJs.innerHTML = ''; // Очищаем текущий список

        if (applicationsToRender.length === 0) {
            applicationsListContainerJs.innerHTML = '<p>Нет заявок, соответствующих вашим критериям.</p>';
            return;
        }

        applicationsToRender.forEach(app => {
            const appElement = document.createElement('div');
            appElement.classList.add('profile-second-request-el');
            
            const skillsString = app.skill_list_text; // Уже строка

            appElement.innerHTML = `
                <h3>Заявка № ${app.id}</h3>
                <p>${app.organization_name}</p>
                <p>${app.solution_name}</p>
                <p class="skillList">${skillsString}</p>
            `;
            applicationsListContainerJs.appendChild(appElement);
        });
        // Обновляем массив, который реально отображается
        currentRenderedApplications = applicationsToRender; 
    }

    // Функция для парсинга строки навыков
    function parseSkillsString(skillsString) {
        if (!skillsString || typeof skillsString !== 'string') {
            return [];
        }
        return skillsString.split(/,\s*/)
                           .map(s => s.trim().toLowerCase())
                           .filter(s => s);
    }

    // Функция для применения фильтра
    function applyFilterJs() {
        const filterText = filterInputJs.value.trim().toLowerCase();
        
        // Получаем требуемые навыки
        const requiredSkills = parseSkillsString(filterText);

        let filteredApplications = [];

        if (requiredSkills.length === 0) {
            // Если нет требуемых навыков (поле пустое или содержит только разделители),
            // показываем ВСЕ заявки из полного списка allApplicationsData.
            filteredApplications = allApplicationsData;
        } else {
            // Фильтруем из ПОЛНОГО списка allApplicationsData
            filteredApplications = allApplicationsData.filter(app => {
                const appSkills = parseSkillsString(app.skill_list_text);
                return requiredSkills.some(reqSkill => appSkills.includes(reqSkill));
            });
        }
        // Рендерим ОТФИЛЬТРОВАННЫЙ список
        renderApplicationsJs(filteredApplications);
    }

    // Обработчики событий
    if (applyFilterBtnJs) {
        applyFilterBtnJs.addEventListener('click', applyFilterJs);
    }
    if (resetFilterBtnJs) {
        resetFilterBtnJs.addEventListener('click', () => {
            filterInputJs.value = ''; // Очищаем поле ввода
            applyFilterJs(); // Применяем пустой фильтр, что вернет все заявки
        });
    }

    // Инициализация при загрузке DOM
    document.addEventListener('DOMContentLoaded', () => {
        if (applicationsListContainerJs) {
            // 1. Получаем ВСЕ заявки из DOM при первой загрузке
            // Это нужно, чтобы у нас был полный список, на который можно ссылаться
            allApplicationsData = getAllApplicationsFromDOM();
            
            // 2. Изначально отображаем все заявки
            // currentRenderedApplications = [...allApplicationsData]; // Можно и так, но renderApplicationsJs сам обновит
            renderApplicationsJs(allApplicationsData);

            // 3. Если в URL есть параметр фильтра, можно применить его при загрузке
            // (Это потребует дополнительной логики для чтения URL-параметров)
        } else {
            console.error("Контейнер '.profile-second-request-list' не найден.");
        }
    });