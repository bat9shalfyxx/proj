//// HIDING MENU
const menu = document.querySelectorAll(".menu-btn");
const menuBlock = document.querySelectorAll(".profile-menu-btn");

const sidebar = document.querySelector(".sidebar");
const profileBlock = document.querySelector(".profile-block");

menu.forEach((el) => {
    el.addEventListener("click", (e) => {
        e.preventDefault();

        if (window.innerWidth <= 1200) {
            if (e.target === el && !sidebar.classList.contains("visible")) {
                sidebar.classList.add("visible");

                sidebar.style.display = "block";
                profileBlock.style.display = "none";
            } else if (e.target === el) {
                sidebar.classList.remove("visible");

                sidebar.style.display = "none";
                profileBlock.style.display = "block";
            }
        }
    });
});

/// SWITCHING BLOCK-CONTENT
const switchContent = (blockNum, target) => {
    if (target.classList.contains(`el-${blockNum}`)) {
        const block1 = document.querySelector(`.block-${blockNum}`);
        block1.style.display = "grid";

        for (let i = 1; i < 7; i++) {
            if (i === blockNum) {
                continue;
            }
            const blockToHide = document.querySelector(`.block-${i}`);
            blockToHide.style.display = "none";
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const sidebarEl = document.querySelector(".sidebar-list");
    const profileBlock = document.querySelector(".profile-block");

    sidebarEl.addEventListener("click", (e) => {
        e.preventDefault();

        if (window.innerWidth <= 1200) {
            sidebar.classList.remove("visible");
            sidebar.style.display = "none";
            profileBlock.style.display = "block";
        }

        if (e.target.classList.contains("sidebar-el") || e.target.classList.contains("sidebar-onclick")) {
            switchContent(1, e.target);
            switchContent(2, e.target);
            switchContent(3, e.target);
            switchContent(4, e.target);
            switchContent(5, e.target);
            switchContent(6, e.target);
        }
    });
});

const toggleCalendar = (target) => {
        if (target.classList.contains("date-btn")) {
            const calendar = document.querySelector(".date-selector");
            calendar.style.display =
                calendar.style.display === "none" ? "inline-block" : "none";
        }
    };

function showCalendar() {
    const dateInput = document.querySelector(".date-selector");
    dateInput.style.display = "block";
    dateInput.focus(); // сразу открывает выбор даты
}

