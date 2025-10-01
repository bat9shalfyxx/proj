const regButton = document.querySelector(".header-right-profile-button");
const mainContent = document.querySelector(".switch-content");
const formPage = document.querySelector(".formPage");
const header = document.querySelector(".header");
// formPage.style.display = "grid";

header.addEventListener("click", (e) => {
    if (e.target.classList.contains("header-left-logo") || e.target.classList.contains("header-right-profile-logo")) {
        if (formPage.classList.contains("active")) {
            formPage.classList.remove("active");
            formPage.style.display = "none";
            mainContent.style.display = "block";
        }
    }
});

regButton.addEventListener("click", (e) => {
    e.preventDefault();

    if (e.target === regButton && !formPage.classList.contains("active")) {
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
//// ВОЙТИ - ЗАРЕГИСТРИРОВАТЬСЯ
const signIn = document.querySelector(".sign-in");
const signUp = document.querySelector(".sign-up");
const signInForm = document.querySelector(".form-sign-in");
const signUpForm = document.querySelector(".form-sign-up");
const regBlock = document.querySelector(".formPage-block");
signUpForm.style.display = "none";

signIn.addEventListener("click", (e) => {
    e.preventDefault();

    if (e.target === signIn && !signIn.hasAttribute(".active")) {
        signIn.classList.add("active");
        signUp.classList.remove("active");

        signIn.style.color = "black";
        signUp.style.color = "var(--dark-gray-col)";
        signInForm.style.display = "grid";
        signUpForm.style.display = "none";
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
    }
});

////////////////////////////////////
////ЗАЯВКИ - РЕГЕСТРАЦИЯ (SWITCHING)
const requestHeader = document.querySelector(".request-head");
const regHeader = document.querySelector(".reg-head");
const requestContent = document.querySelector(".form-request");
requestContent.style.display = "none";
requestHeader.style.display = "none";

requestButton.addEventListener("click", (e) => {
    e.preventDefault();

    if (
        e.target === requestButton &&
        requestButton.classList.contains("request") &&
        !requestButton.classList.contains("active")
    ) {
        requestButton.classList.add("active");
        signIn.classList.contains("active") ? signIn.classList.remove("active") : signUp.classList.remove("active");
        signIn.style.display = "grid" ? (signIn.style.display = "none") : (signIn.style.display = "none");

        formPage.style.display = "grid";
        requestHeader.style.display = "grid";
        regHeader.style.display = "none";

        formPage.style.display = "grid";
        requestContent.style.display = "grid";
        mainContent.style.display = "none";
    } else {
        requestButton.classList.remove("active");
        signIn.classList.contains("active") ? (signIn.style.display = "grid") : (signIn.style.display = "grid");

        requestHeader.style.display = "none";
        regHeader.style.display = "grid";

        formPage.style.display = "none";
        requestContent.style.display = "none";
        mainContent.style.display = "block";
    }
});
