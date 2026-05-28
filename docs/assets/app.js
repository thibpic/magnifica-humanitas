(function () {
  const MODE_KEY = "mh.mode";
  const VERN_KEY = "mh.vern";
  const VATICAN_BASE = "https://www.vatican.va/content/leo-xiv";
  const ENCY_PATH = "/encyclicals/documents/20260515-magnifica-humanitas.html";

  const SUBTITLE = {
    fr: "Sur la protection de la personne humaine à l'ère de l'intelligence artificielle",
    en: "On the protection of the human person in the age of artificial intelligence",
    es: "Sobre la protección de la persona humana en la era de la inteligencia artificial",
    it: "Sulla protezione della persona umana nell'era dell'intelligenza artificiale",
    de: "Über den Schutz der menschlichen Person im Zeitalter der künstlichen Intelligenz",
    pt: "Sobre a proteção da pessoa humana na era da inteligência artificial",
    pl: "O ochronie osoby ludzkiej w erze sztucznej inteligencji",
  };
  const TOC_TITLE = {
    fr: "Sommaire",
    en: "Contents",
    es: "Índice",
    it: "Indice",
    de: "Inhalt",
    pt: "Índice",
    pl: "Spis treści",
  };
  const NOTES_LABEL = {
    fr: "Notes", en: "Notes", es: "Notas", it: "Note",
    de: "Anmerkungen", pt: "Notas", pl: "Przypisy",
  };

  const buttons = document.querySelectorAll(".lang-toggle button");
  const vernSelect = document.getElementById("vern-select");
  const body = document.body;
  const main = document.getElementById("main");
  const tocList = document.getElementById("toc-list");
  const tocTitle = document.getElementById("toc-title");
  const subtitleEl = document.getElementById("subtitle-vern");
  const vaticanLink = document.getElementById("vatican-link");

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function linkifyRefs(s) {
    return s.replace(/\[(\d+)\]/g, '<sup class="ref"><a href="#note-$1">[$1]</a></sup>');
  }
  function renderP(p) { return linkifyRefs(escapeHtml(p)); }

  let latinData = null;
  let vernData = null;

  async function loadLang(lang) {
    const resp = await fetch(`data/${lang}.json`);
    if (!resp.ok) throw new Error(`Failed to load ${lang}`);
    return resp.json();
  }

  function render() {
    if (!latinData || !vernData) return;

    // TOC
    const lang = vernData.lang;
    tocTitle.textContent = TOC_TITLE[lang] || "Index Capitum";
    tocList.innerHTML = vernData.chapters
      .map((c, i) => `<li><a href="#chap-${i}">${escapeHtml(c.title)}</a></li>`)
      .join("") + `<li><a href="#notes">${NOTES_LABEL[lang] || "Notes"}</a></li>`;

    // Chapters
    const html = vernData.chapters.map((vchap, ci) => {
      const lchap = latinData.chapters[ci];
      const rows = vchap.paragraphs.map((vp, pi) => {
        const lp = (lchap && lchap.paragraphs[pi]) || "";
        return `<div class="row">
          <p class="vern" lang="${lang}">${renderP(vp)}</p>
          <p class="la" lang="la">${renderP(lp)}</p>
        </div>`;
      }).join("");
      return `<section id="chap-${ci}" class="chapter">
        <div class="chap-titles">
          <h2 class="vern" lang="${lang}">${escapeHtml(vchap.title)}</h2>
          <h2 class="la" lang="la">${escapeHtml(lchap ? lchap.title : "")}</h2>
        </div>
        ${rows}
      </section>`;
    }).join("");

    // Notes (depuis la langue vernaculaire — les références biblio sont identiques)
    let notesHtml = "";
    if (vernData.notes && vernData.notes.length) {
      const items = vernData.notes.map((n) => {
        const m = n.match(/^\[(\d+)\]\s*(.*)$/);
        if (m) {
          return `<li id="note-${m[1]}"><span class="num">[${m[1]}]</span> ${escapeHtml(m[2])}</li>`;
        }
        return `<li>${escapeHtml(n)}</li>`;
      }).join("");
      notesHtml = `<section id="notes" class="chapter notes">
        <h2>${NOTES_LABEL[lang] || "Notes"}</h2>
        <ol class="notes-list">${items}</ol>
      </section>`;
    }

    main.innerHTML = html + notesHtml;
    subtitleEl.textContent = SUBTITLE[lang] || "";
    vaticanLink.href = `${VATICAN_BASE}/${lang}${ENCY_PATH}`;
    document.documentElement.setAttribute("lang", lang);
  }

  function applyMode(mode) {
    body.classList.remove("mode-vern", "mode-la");
    if (mode === "vern") body.classList.add("mode-vern");
    if (mode === "la") body.classList.add("mode-la");
    buttons.forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));
    try { localStorage.setItem(MODE_KEY, mode); } catch (_) {}
  }

  buttons.forEach((b) => b.addEventListener("click", () => applyMode(b.dataset.mode)));

  vernSelect.addEventListener("change", async () => {
    const lang = vernSelect.value;
    try { localStorage.setItem(VERN_KEY, lang); } catch (_) {}
    vernData = await loadLang(lang);
    render();
  });

  async function init() {
    let savedVern = "fr";
    let savedMode = "both";
    try {
      savedVern = localStorage.getItem(VERN_KEY) || "fr";
      savedMode = localStorage.getItem(MODE_KEY) || "both";
    } catch (_) {}
    vernSelect.value = savedVern;
    applyMode(savedMode);
    [latinData, vernData] = await Promise.all([loadLang("la"), loadLang(savedVern)]);
    render();
  }
  init();
})();
