const navList = document.querySelectorAll(".nav-link");

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

document.addEventListener("click", (e) => {
    if (!e.target.closest(".nav-link")) {
        hideAllDropdowns();
    }
});

window.addEventListener("resize", () => {
    const activeNavLink = document.querySelector(".nav-link.active");
    if (activeNavLink) {
        const dropdown = activeNavLink.querySelector(".nav-dropdown");
        if (dropdown && dropdown.style.display === "flex") {
            positionDropdown(activeNavLink, dropdown);
        }
    }
});



