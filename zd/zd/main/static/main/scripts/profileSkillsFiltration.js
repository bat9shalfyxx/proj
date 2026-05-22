document.addEventListener("DOMContentLoaded", function () {
  const statusBtns = document.querySelectorAll(".filter-status-btn");
  const applyBtn = document.getElementById("apply-filter-js");
  const resetBtn = document.getElementById("reset-filter-js");
  const filterInput = document.getElementById("filter-skills-js");

  let currentStatus = "all";
  let currentSkills = "";

  function filterApplications() {
    const items = document.querySelectorAll(
      "#applications-list .profile-second-request-el",
    );
    let visibleCount = 0;

    items.forEach((item) => {
      const status = item.dataset.status;
      const skills = item.dataset.skills || "";

      let showByStatus = currentStatus === "all" || status === currentStatus;

      let showBySkills = true;
      if (currentSkills) {
        const skillList = currentSkills
          .toLowerCase()
          .split(",")
          .map((s) => s.trim());
        showBySkills = skillList.some((skill) => skills.includes(skill));
      }

      if (showByStatus && showBySkills) {
        item.style.display = "block";
        visibleCount++;
      } else {
        item.style.display = "none";
      }
    });

    let noResultsMsg = document.getElementById("no-results-message");
    if (visibleCount === 0 && items.length > 0) {
      if (!noResultsMsg) {
        const msgDiv = document.createElement("div");
        msgDiv.id = "no-results-message";
        msgDiv.className = "profile-second-not-found";
        msgDiv.innerHTML = `
                    <div class="not-found-block">
                        <img src="{% static 'main/src/profile/search.svg' %}" alt="не найдено">
                        <h3>Ничего не найдено</h3>
                    </div>
                    <p>Попробуйте изменить условия поиска</p>
                    <button class="reset-filters" onclick="resetFilters()">Сбросить фильтры</button>
                `;
        document.getElementById("applications-list").after(msgDiv);
      }
    } else if (noResultsMsg) {
      noResultsMsg.remove();
    }
  }

  statusBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      statusBtns.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      currentStatus = this.dataset.status;
      filterApplications();
    });
  });

  if (applyBtn) {
    applyBtn.addEventListener("click", function () {
      currentSkills = filterInput.value.trim();
      filterApplications();
    });
  }

  window.resetFilters = function () {
    currentStatus = "all";
    currentSkills = "";
    filterInput.value = "";

    statusBtns.forEach((btn) => {
      if (btn.dataset.status === "all") {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    filterApplications();
  };

  if (resetBtn) {
    resetBtn.addEventListener("click", resetFilters);
  }
});
