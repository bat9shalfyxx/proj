const regButton = document.querySelector(".header-right-profile-button");
const mainContent = document.querySelector(".switch-content");
const formPage = document.querySelector(".formPage");
const header = document.querySelector(".header");

header.addEventListener("click", (e) => {
    if (e.target.classList.contains("header-left-logo") || e.target.classList.contains("header-right-profile-logo")) {
        if (formPage.classList.contains("active")) {
            formPage.classList.remove("active");
            formPage.style.display = "none";
            mainContent.style.display = "block";
        }
    }
});

header.addEventListener("click", (e) => {
    e.preventDefault();

    if ((e.target === regButton || e.target === requestButton) && !formPage.classList.contains("active")) {
        formPage.classList.add("active");
        mainContent.style.display = "none";
        formPage.style.display = "grid";
    } else {
        formPage.classList.remove("active");
        formPage.style.display = "none";
        mainContent.style.display = "block";
    }

});

///////////////////////////////
//// ВОЙТИ - ЗАРЕГИСТРИРОВАТЬСЯ-ЗАЯВКИ
const signIn = document.querySelector(".sign-in");
const signUp = document.querySelector(".sign-up");

const signInForm = document.querySelector(".form-sign-in");
const signUpForm = document.querySelector(".form-sign-up");

const requestContent = document.querySelector(".request-form");
const regContent = document.querySelector(".reg-form");
// const regBlock = document.querySelector(".formPage-block");

signUpForm.style.display = "none";
requestContent.style.display = "none";

header.addEventListener("click", (e) => {
    e.preventDefault();

    if (e.target === requestButton) {
        requestContent.style.display = "grid";
        regContent.style.display = "none";
    } else if (e.target === regButton) {
        requestContent.style.display = "none";
        regContent.style.display = "grid";
    }
});

signIn.addEventListener("click", (e) => {
    e.preventDefault();

    if (e.target === signIn && !signIn.hasAttribute(".active")) {
        signIn.classList.add("active");
        signUp.classList.remove("active");

        signIn.style.color = "black";
        signUp.style.color = "var(--dark-gray-col)";

        signInForm.style.display = "grid";
        signUpForm.style.display = "none";
        requestContent.style.display = "none";
    }
});

signUp.addEventListener("click", (e) => {
    e.preventDefault();
    if (e.target === signUp && !signUp.hasAttribute(".active")) {
        signUp.classList.add("active");
        signIn.classList.remove("active");

        signUp.style.color = "black";
        signIn.style.color = "var(--dark-gray-col)";

        signInForm.style.display = "none";
        signUpForm.style.display = "grid";
        requestContent.style.display = "none";
    }
});
