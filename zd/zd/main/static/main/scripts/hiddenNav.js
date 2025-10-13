const hiddenNavBtn = document.querySelector(".nav-hidden-btn");
const mobileNavList = document.querySelector(".nav-list")

hiddenNavBtn.addEventListener("click", (e) => {
    e.preventDefault();

    mobileNavList.classList.toggle("visible");

    if (mobileNavList.classList.contains("visible")) {
        mobileNavList.style.display = "grid"
    } else {
        mobileNavList.style.display = "none"
    }
});
