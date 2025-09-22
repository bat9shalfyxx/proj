const switchContent = (blockNum) => {
    const block1 = document.querySelector(`.block-${blockNum}`);
    block1.style.display = "block";

    for (let i = 1; i < 7; i++) {
        if (i === blockNum) {
            continue;
        }
        const blockToHide = document.querySelector(`.block-${i}`);
        blockToHide.style.display = "none";
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const sidebarEl = document.querySelector(".sidebar-list");
    const profileBlock = document.querySelector(".profile-block");

    sidebarEl.addEventListener("click", (e) => {
        e.preventDefault();

        if (e.target.classList.contains("sidebar-el") || e.target.classList.contains("sidebar-onclick")) {
            if (e.target.classList.contains("el-1")) {
                switchContent(1);
            }
            if (e.target.classList.contains("el-2")) {
                switchContent(2);
            }
            if (e.target.classList.contains("el-3")) {
                switchContent(3);
            }
            if (e.target.classList.contains("el-4")) {
                switchContent(4);
            }
            if (e.target.classList.contains("el-5")) {
                switchContent(5);
            }
            if (e.target.classList.contains("el-6")) {
                switchContent(6);
            }
        }
    });
});

// document.addEventListener("DOMContentLoaded", async () => {
//     const container = document.querySelector(".switch-content");
//     const profilePage = await fetch("./content/profilePage.html");
//     const profileContent = await profilePage.text();

//     const parser = new DOMParser();
//     const parsedProfilePage = parser.parseFromString(profileContent, "text/html");

//     const profileContainer = parsedProfilePage.querySelectorAll(".profileContainer");
//     const sidebarList = parsedProfilePage.querySelectorAll(".sidebar-list");
//     const sidebarEl = parsedProfilePage.querySelector(".sidebar-el");

//     container.innerHTML = `${profilePage}`
//     console.log(sidebarEl.textContent);

//     sidebarEl.addEventListener("click", (e) => {
//         e.preventDefault();
//         if (e.target == sidebarEl) console.log(1);
//     });
// });

// const el = document.querySelector(".sidebar-el");
// console.log(el.textContent);
