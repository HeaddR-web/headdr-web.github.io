/* BeThatHost — Motion-Schicht (Scroll-Reveal). Vanilla JS, kein Build.
   Respektiert prefers-reduced-motion und degradiert sauber (ohne JS bleibt alles sichtbar). */
(function () {
  "use strict";

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
    ".section-head, .post-card, .occ, .pick, .subscribe, .ad-slot, " +
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
