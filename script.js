const navList = document.querySelectorAll(".nav-link");

navList.forEach((el) => {
    el.addEventListener("click", (e) => {
        e.preventDefault();

        navList.forEach((item) => {
            item.classList.remove("active");
            const dropdown = item.querySelector(".nav-dropdown");
            if (dropdown) {
                dropdown.style.display = "none";
            }
        });

        el.classList.add("active");

        const dropdown = el.querySelector(".nav-dropdown");
        if (dropdown) {
            dropdown.style.display = "block";
        }
    });
});
