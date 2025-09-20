const regButton = document.querySelector(".header-right-profile-button");

regButton.addEventListener("click", (e) => {
    e.preventDefault();

    regButton.classList.add("active");
});
