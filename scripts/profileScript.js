document.addEventListener("DOMContentLoaded", async () => {
    const profilePage = await fetch("./content/profilePage.html");
    const profileContent = await profilePage.text();

    const parser = new DOMParser();
    const parsedProfilePage = parser.parseFromString(profileContent, "text/html");

    const profileContainer = parsedProfilePage.querySelectorAll(".profileContainer");
    const sidebarList = parsedProfilePage.querySelectorAll(".sidebar-list");
    const sidebarEl = parsedProfilePage.querySelector(".sidebar-el");
    console.log(sidebarEl.textContent);

    sidebarEl.addEventListener("click", (e) => {
        e.preventDefault();
        if (e.target == sidebarEl) console.log(1);
    });
});
