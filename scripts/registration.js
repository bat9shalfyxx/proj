document.addEventListener("DOMContentLoaded", () => {
    const regButton = document.querySelector(".header-right-profile-button");
    const mainContent = document.querySelector(".switch-content");
    const regContent = document.querySelector(".registration");

    regButton.addEventListener("click", (e) => {
        e.preventDefault();

        if (e.target === regButton && !regContent.classList.contains("active")) {
            regContent.classList.add("active");
            mainContent.style.display = "none";
            regContent.style.display = "grid";
        } else {
            regContent.classList.remove("active");
            regContent.style.display = "none";
            mainContent.style.display = "block";
        }
    });
});

//// ВОЙТИ - ЗАРЕГИСТРИРОВАТЬСЯ
document.addEventListener("DOMContentLoaded", () => {
    const signIn = document.querySelector(".sign-in");
    const signUp = document.querySelector(".sign-up");
    const signInForm = document.querySelector(".sign-in-form");
    const signUpForm = document.querySelector(".sign-up-form");
    const regBlock = document.querySelector(".registration-block");

    signUpForm.style.display = "none";

    signIn.addEventListener("click", (e) => {
        e.preventDefault();

        if (e.target === signIn && !signIn.hasAttribute(".active")) {
            regBlock.classList.add("reg-sign-in");
            regBlock.classList.remove("reg-sign-up");

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
            regBlock.classList.remove("reg-sign-in");
            regBlock.classList.add("reg-sign-up");

            signUp.classList.add("active");
            signIn.classList.remove("active");

            signUp.style.color = "black";
            signIn.style.color = "var(--dark-gray-col)";
            signInForm.style.display = "none";
            signUpForm.style.display = "grid";
        }
    });
});
