const switchContent = (blockNum, target) => {
    if (target.classList.contains(`el-${blockNum}`)) {
        const block1 = document.querySelector(`.block-${blockNum}`);
        block1.style.display = "grid";

        for (let i = 1; i < 7; i++) {
            if (i === blockNum) {
                continue;
            }
            const blockToHide = document.querySelector(`.block-${i}`);
            blockToHide.style.display = "none";
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const sidebarEl = document.querySelector(".sidebar-list");
    const profileBlock = document.querySelector(".profile-block");

    sidebarEl.addEventListener("click", (e) => {
        e.preventDefault();

        if (e.target.classList.contains("sidebar-el") || e.target.classList.contains("sidebar-onclick")) {
            switchContent(1, e.target);
            switchContent(2, e.target);
            switchContent(3, e.target);
            switchContent(4, e.target);
            switchContent(5, e.target);
            switchContent(6, e.target);
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
