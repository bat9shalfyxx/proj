
document.addEventListener('DOMContentLoaded', function() {
// Фильтрация по статусу
    const statusBtns = document.querySelectorAll('.filter-status-btn');
    const applicationsList = document.getElementById('applications-list');
    const filterInput = document.getElementById('filter-skills-js');
    const applyBtn = document.getElementById('apply-filter-js');
    const resetBtn = document.getElementById('reset-filter-js');

    let currentStatus = 'all';
    let currentSkills = '';

    function filterApplications() {
        if (!applicationsList) return;
        
        const items = applicationsList.querySelectorAll('.profile-second-request-el');
        let visibleCount = 0;
        
        items.forEach(item => {
            const status = item.dataset.status;
            const skills = item.dataset.skills || '';
            
            let showByStatus = (currentStatus === 'all' || status === currentStatus);
            
            let showBySkills = true;
            if (currentSkills) {
                const skillList = currentSkills.split(',').map(s => s.trim().toLowerCase());
                showBySkills = skillList.some(skill => skills.includes(skill));
            }
            
            if (showByStatus && showBySkills) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        let noResultsMsg = document.querySelector('.no-results-message');
        if (visibleCount === 0 && items.length > 0) {
            if (!noResultsMsg) {
                const msg = document.createElement('div');
                msg.className = 'no-results-message';
                msg.innerHTML = `
                    <div class="profile-second-not-found">
                        <img src="{% static 'main/src/profile/search.svg' %}" alt="не найдено">
                        <h3>Ничего не найдено</h3>
                        <p>Попробуйте изменить условия поиска</p>
                        <button class="reset-filters" onclick="resetAllFilters()">Сбросить фильтры</button>
                    </div>
                `;
                applicationsList.appendChild(msg);
            }
        } else if (noResultsMsg) {
            noResultsMsg.remove();
        }
    }

    statusBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            statusBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentStatus = this.dataset.status;
            filterApplications();
        });
    });

    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            currentSkills = filterInput.value.trim();
            filterApplications();
        });
    }

    window.resetAllFilters = function() {
        currentStatus = 'all';
        currentSkills = '';
        filterInput.value = '';
        
        statusBtns.forEach(btn => {
            if (btn.dataset.status === 'all') {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        filterApplications();
    };

    if (resetBtn) {
        resetBtn.addEventListener('click', resetAllFilters);
    }
});