///////////////////////////////
//// ВОЙТИ - ЗАРЕГИСТРИРОВАТЬСЯ-ЗАЯВКИ
document.addEventListener('DOMContentLoaded', function() {
    const signIn = document.querySelector(".sign-in");
    const signUp = document.querySelector(".sign-up");
    const signInForm = document.querySelector(".form-sign-in");
    const signUpForm = document.querySelector(".form-sign-up");
    const requestContent = document.querySelector(".request-form");
    const regContent = document.querySelector(".reg-form");
    const requestButton = document.querySelector('.req-btn');
    const regButton = document.querySelector(".header-right-profile-button");

    // Функция сброса
    function resetAllForms() {
        if (signInForm) signInForm.style.display = "none";
        if (signUpForm) signUpForm.style.display = "none";
        if (requestContent) requestContent.style.display = "none";
        if (regContent) regContent.style.display = "none";
    }

    function showSignInForm() {
        resetAllForms();
        signInForm.style.display = "grid";
        signIn.classList.add("active");
        signUp.classList.remove("active");
        signIn.style.color = "#cbcbcb";
        signUp.style.color = "#5c5c5c";
    }

    function showSignUpForm() {
        resetAllForms();
        signUpForm.style.display = "grid";
        signUp.classList.add("active");
        signIn.classList.remove("active");
        signUp.style.color = "#cbcbcb";
        signIn.style.color = "#5c5c5c";
    }

    function showRequestForm() {
        resetAllForms();
        if (requestContent) requestContent.style.display = "grid";
    }

    // Начальное состояние в зависимости от авторизации
    if (userAuthenticated) {
        showRequestForm();
    } else {
        showSignInForm();
    }

    // Обработчики переключения
    if (signIn) signIn.addEventListener("click", (e) => { e.preventDefault(); showSignInForm(); });
    if (signUp) signUp.addEventListener("click", (e) => { e.preventDefault(); showSignUpForm(); });

    // Обработчик кнопки заявки (если она есть на странице)
    if (requestButton && requestContent) {
        requestButton.addEventListener("click", (e) => {
            e.preventDefault();
            // Если мы уже на странице formPage, просто показываем заявку
            showRequestForm();
        });
    }
});