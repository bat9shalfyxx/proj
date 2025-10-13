console.log("switch.js executed");

const container = document.querySelector(".switch-content");
const hubPage = document.querySelector(".hubPage");
const profilePage = document.querySelector(".profilePage");

const hubIcon = document.querySelector(".header-left-logo");
const profileIcon = document.querySelector(".header-right-profile-logo");
const requestButton = document.querySelector(".req-btn");


hubPage.style.display = "block";
profilePage.style.display = "none";

hubIcon.addEventListener("click", (e) => {
    e.preventDefault();

    if (e.target === hubIcon) {
        requestButton.classList.remove("request");

        hubPage.style.display = "block";
        profilePage.style.display = "none";
    }
});

profileIcon.addEventListener("click", (e) => {
    e.preventDefault();

    if (e.target === profileIcon) {
        requestButton.classList.add("request");

        profilePage.style.display = "block";
        hubPage.style.display = "none";
    }
});
