// const regButton = document.querySelector(".header-right-profile-button");

// regButton.addEventListener("click", (e) => {
//     e.preventDefault();

//     regButton.classList.add("active");
// });

document.addEventListener("DOMContentLoaded", () => {
    const signIn = document.querySelector(".sign-in");
    const signUp = document.querySelector(".sign-up");
    const signInForm = document.querySelector(".sign-in-form");
    const signUpForm = document.querySelector(".sign-up-form");

    signUpForm.style.display = "none";

    if (signIn.hasAttribute(".active")) {
        signInForm.style.display = "grid";
        signUpForm.style.display = "none";
    }

    signIn.addEventListener("click", (e) => {
        if (e.target === signIn && !signIn.hasAttribute(".active")) {
            signIn.classList.add("active");
            signUp.classList.remove("active");

            signInForm.style.display = "grid";
            signUpForm.style.display = "none";
        }
    });
    signUp.addEventListener("click", (e) => {
        if (e.target === signUp && !signUp.hasAttribute("active")) {
            signUp.classList.add("active");
            signIn.classList.remove("active");

            signInForm.style.display = "none";
            signUpForm.style.display = "grid";
        }
    });
});
