///////////////////////////////
//// ВОЙТИ - ЗАРЕГИСТРИРОВАТЬСЯ-ЗАЯВКИ
const header = document.querySelector(".header");
const signIn = document.querySelector(".sign-in");
const signUp = document.querySelector(".sign-up");

const signInForm = document.querySelector(".form-sign-in");
const signUpForm = document.querySelector(".form-sign-up");

const requestContent = document.querySelector(".request-form");
const regContent = document.querySelector(".reg-form");

const requestButton = document.querySelector('.req-btn')
const regButton = document.querySelector(".header-right-profile-button");

signIn.style.color = "#cbcbcb";
signUp.style.color = "#5c5c5c";

signUpForm.style.display = "none";
requestContent.style.display = "none";

document.addEventListener('DOMContentLoaded', () => {
    if (requestButton) {
        requestButton.addEventListener("click", (e) => {
            e.preventDefault(); 
            requestContent.style.display = "grid";
            regContent.style.display = "none";
        })
    }
    
    if (regButton) {
        // regButton.addEventListener("click", (e) => {
        //     e.preventDefault();  
        //     regContent.style.display = "grid";
        //     requestContent.style.display = "none";
        // })
    }
})

signIn.addEventListener("click", (e) => {
    e.preventDefault();
    console.log(1);

    if (e.target === signIn && !signIn.hasAttribute(".active")) {
        signIn.classList.add("active");
        signUp.classList.remove("active");

        signIn.style.color = "#cbcbcb";
        signUp.style.color = "#5c5c5c";

        signInForm.style.display = "grid";
        signUpForm.style.display = "none";
        requestContent.style.display = "none";
    }
});

signUp.addEventListener("click", (e) => {
    e.preventDefault();
    console.log(1);
    
    if (e.target === signUp && !signUp.hasAttribute(".active")) {
        signUp.classList.add("active");
        signIn.classList.remove("active");

        signUp.style.color = "#cbcbcb";
        signIn.style.color = "#5c5c5c";

        signInForm.style.display = "none";
        signUpForm.style.display = "grid";
        requestContent.style.display = "none";
    }
});
