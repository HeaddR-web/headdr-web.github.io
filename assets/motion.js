/* BeThatHost — Motion-Schicht (Scroll-Reveal). Vanilla JS, kein Build.
   Respektiert prefers-reduced-motion und degradiert sauber (ohne JS bleibt alles sichtbar). */
(function () {
  "use strict";

  // ---------- Kategorie-Schnellnavigation (Chips) ----------
  // Baut aus den gerenderten Kategorie-Karten eine Sprung-Navigation oberhalb des Grids.
  // Läuft bewusst UNABHÄNGIG von der Motion-Schicht (auch bei prefers-reduced-motion).
  document.addEventListener("DOMContentLoaded", function () {
    var grid = document.getElementById("build-grid");
    if (!grid) return;

    function buildCatNav() {
      if (document.querySelector(".cat-nav")) return true;
      var cards = grid.querySelectorAll(".cat-card");
      if (!cards.length) return false;
      var nav = document.createElement("nav");
      nav.className = "cat-nav";
      nav.setAttribute("aria-label", "Kategorien");
      Array.prototype.forEach.call(cards, function (card) {
        if (!card.id) return;
        var tag = card.querySelector(".tag");
        var a = document.createElement("a");
        a.className = "cat-chip";
        a.href = "#" + card.id;
        a.textContent = tag ? tag.textContent.trim() : card.id;
        nav.appendChild(a);
      });
      grid.parentNode.insertBefore(nav, grid);
      return true;
    }

    // Karten werden von app.js erst nach dem Laden eingefügt → kurz nachfassen.
    if (!buildCatNav()) {
      var tries = 0;
      var iv = setInterval(function () {
        tries++;
        if (buildCatNav() || tries > 20) clearInterval(iv);
      }, 50);
    }
  });

  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }

  var io = new IntersectionObserver(
    function (entries) {
      each(entries, function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          io.unobserve(e.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.06 }
  );

  // Statische Elemente, die beim Reinscrollen eingeblendet werden.
  var SEL =
    ".section-head, .post-card, .occ, .occ-row, .pick, .subscribe, .ad-slot, " +
    "article > p, article > ul, article > h2, .chip, img.lead";

  function reveal(el, i) {
    if (el.classList.contains("reveal-init")) return;
    el.classList.add("reveal-init");
    el.style.transitionDelay = Math.min(i % 5, 5) * 60 + "ms";
    io.observe(el);
  }

  function scan(root) {
    each((root || document).querySelectorAll(SEL), reveal);
  }

  document.addEventListener("DOMContentLoaded", function () {
    scan(document);

    // Builder-Karten werden von app.js erst nach dem Laden eingefügt → mitnehmen.
    var grid = document.getElementById("build-grid");
    if (grid) {
      var mo = new MutationObserver(function () {
        each(grid.querySelectorAll(".cat-card"), reveal);
      });
      mo.observe(grid, { childList: true });
      setTimeout(function () {
        each(grid.querySelectorAll(".cat-card"), reveal);
      }, 60);
    }
  });
})();
