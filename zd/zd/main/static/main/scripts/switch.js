const container = document.querySelector(".switch-content");
const hubPage = document.querySelector(".hubPage");
const profilePage = document.querySelector(".profilePage");

const hubIcon = document.querySelector(".header-left-logo");
const profileIcon = document.querySelector(".header-right-profile-logo");

document.addEventListener("DOMContentLoaded", () => {
    hubIcon.style.display = "block";
    profilePage.style.display = "none";

    hubIcon.addEventListener("click", (e) => {
        e.preventDefault();

        if (e.target === hubIcon) {
            hubPage.style.display = 'block';
            profilePage.style.display = 'none';
        }
    })

    profileIcon.addEventListener("click", (e) => {
        e.preventDefault();

        if (e.target === profileIcon) {
            profilePage.style.display = 'block';
            hubPage.style.display = 'none';
        }
    })
})




// const pullOut = async () => {
//     const hubPage = await fetch("./content/hubPage.html");
//     const profilePage = await fetch("./content/profilePage.html");

//     const hubContent = await hubPage.text();
//     const profileContent = await profilePage.text();

//     return { hubContent, profileContent };
// };

// document.addEventListener("DOMContentLoaded", async () => {
//     const { hubContent, profileContent } = await pullOut();

//     container.innerHTML = `${profileContent}`;

//     profileIcon.addEventListener("click", (e) => {
//         e.preventDefault();

//         if (e.target == profileIcon && !profileIcon.classList.contains("active")) {
//             hubIcon.classList.remove("active");
//             profileIcon.classList.add("active");
//             container.innerHTML = `${profileContent}`;
//         }
//     });

//     hubIcon.addEventListener("click", (e) => {
//         e.preventDefault();

//         if (e.target == hubIcon && !hubIcon.classList.contains("active")) {
//             hubIcon.classList.add("active");
//             profileIcon.classList.remove("active");
//             container.innerHTML = `${hubContent}`;
//         }
//     });
// });



// class ContentSwitcher {
//     constructor() {
//         this.currentContent = "organization";
//         this.contentContainer = document.querySelector(".switch-content");
//         this.contentFiles = {
//             organization: "./content/hubPage.html",
//             individual: "./content/profilePage.html",
//         };
//         this.init();
//     }

//     init() {
//         this.setupHeaderLinks();
//         this.loadContent(this.currentContent);
//         this.bindEvents();
//     }

//     setupHeaderLinks() {
//         const headerLinks = document.querySelectorAll(".header-left-info a");
//         if (headerLinks.length >= 2) {
//             headerLinks[0].dataset.content = "organization";
//             headerLinks[0].classList.add("active");
//             headerLinks[1].dataset.content = "individual";
//         }
//     }

//     async loadContent(contentType) {
//         try {
//             this.contentContainer.classList.add("loading");

//             const response = await fetch(this.contentFiles[contentType]);
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }

//             const content = await response.text();

//             this.contentContainer.style.opacity = "0";

//             setTimeout(() => {
//                 this.contentContainer.innerHTML = content;
//                 this.contentContainer.style.opacity = "1";
//                 this.contentContainer.classList.remove("loading");

//                 this.updateActiveLink(contentType);
//             }, 30);

//             this.currentContent = contentType;
//         } catch (error) {
//             console.error("Ошибка загрузки контента:", error);
//             this.contentContainer.classList.remove("loading");
//         }
//     }

//     updateActiveLink(contentType) {
//         document.querySelectorAll(".header-left-info a").forEach((link) => {
//             link.classList.remove("active");
//         });

//         document.querySelector(`[data-content="${contentType}"]`).classList.add("active");
//     }

//     bindEvents() {
//         document.addEventListener("click", (e) => {
//             if (e.target.closest(".header-left-info a")) {
//                 e.preventDefault();
//                 const contentType = e.target.closest("a").dataset.content;
//                 if (contentType && contentType !== this.currentContent) {
//                     this.loadContent(contentType);
//                 }
//             }
//         });
//     }
// }

// let contentSwitcher;
// document.addEventListener("DOMContentLoaded", () => {
//     contentSwitcher = new ContentSwitcher();
// });

// window.contentSwitcher = contentSwitcher;
