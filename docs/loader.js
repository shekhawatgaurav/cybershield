/* Independent of the dashboard: always release the page after three seconds. */
(() => {
  const root = document.documentElement;
  root.classList.add("page-loading");
  let finished = false;
  document.addEventListener("DOMContentLoaded", () => {
    if (!finished) document.getElementById("site-content").inert = true;
  }, {once: true});
  setTimeout(() => {
    finished = true;
    root.classList.remove("page-loading");
    const content = document.getElementById("site-content");
    if (content) content.inert = false;
  }, 3000);
})();
