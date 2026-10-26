// Shared behaviour for every page: the mobile menu and the installable-app service worker.

const menuBtn = document.querySelector(".menu-btn");
const links = document.getElementById("nav-links");

if (menuBtn && links) {
  const setOpen = (open) => {
    menuBtn.setAttribute("aria-expanded", String(open));
    links.classList.toggle("open", open);
  };
  menuBtn.addEventListener("click", () => setOpen(menuBtn.getAttribute("aria-expanded") !== "true"));
  // Close after choosing a link, or on Escape
  links.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && links.classList.contains("open")) { setOpen(false); menuBtn.focus(); }
  });
}

for (const el of document.querySelectorAll("[data-year]")) el.textContent = new Date().getFullYear();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => { /* the site works without it */ });
  });
}
