(function () {
  const KEY = "mh.mode";
  const buttons = document.querySelectorAll(".lang-toggle button");
  const body = document.body;

  function apply(mode) {
    body.classList.remove("mode-fr", "mode-la");
    if (mode === "fr") body.classList.add("mode-fr");
    if (mode === "la") body.classList.add("mode-la");
    buttons.forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));
    try { localStorage.setItem(KEY, mode); } catch (_) {}
  }

  buttons.forEach((b) =>
    b.addEventListener("click", () => apply(b.dataset.mode))
  );

  const saved = (function () {
    try { return localStorage.getItem(KEY); } catch (_) { return null; }
  })();
  apply(saved || "both");
})();
