const menuButtons = document.querySelectorAll(".menu-btn");
const sections = document.querySelectorAll(".section");

menuButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        menuButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        sections.forEach((sec) => sec.classList.remove("active"));

        document.getElementById(btn.dataset.target).classList.add("active");
    });
});

function showCalendar() {
    const dateSelector = document.querySelector(".date-selector");
    dateSelector.style.display = dateSelector.style.display === "none" ? "inline-block" : "none";
}
