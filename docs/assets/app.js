(function () {
  const MODE_KEY = "mh.mode";
  const VERN_KEY = "mh.vern";
  const body = document.body;
  const buttons = document.querySelectorAll(".lang-toggle button");

  // Pages /la/ : forcer le mode "la" (pas de vernaculaire).
  const path = window.location.pathname;
  const isLatinPage = path.startsWith("/la/") || path === "/la";

  // Mémorise la langue choisie d'après le path.
  const m = path.match(/^\/([a-z]{2})\/?$/);
  if (m) {
    try { localStorage.setItem(VERN_KEY, m[1]); } catch (_) {}
  }

  function applyMode(mode) {
    if (isLatinPage) mode = "la";
    body.classList.remove("mode-vern", "mode-la");
    if (mode === "vern") body.classList.add("mode-vern");
    if (mode === "la") body.classList.add("mode-la");
    buttons.forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));
    try { localStorage.setItem(MODE_KEY, mode); } catch (_) {}
  }

  buttons.forEach((b) => b.addEventListener("click", () => applyMode(b.dataset.mode)));

  let saved;
  try { saved = localStorage.getItem(MODE_KEY); } catch (_) {}
  applyMode(saved || (isLatinPage ? "la" : "both"));
})();
