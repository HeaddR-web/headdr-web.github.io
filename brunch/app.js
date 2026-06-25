/* BeThatHost — Brunch: Ausstattung nach Kategorie mit direkten Amazon-Links.
   Reines statisches JS (nur Rendering, kein State). Affiliate-Tag: cozylore-21. */
(function () {
  "use strict";

  var AFF_TAG = "cozylore-21";

  function amz(query) {
    return "https://www.amazon.de/s?k=" + encodeURIComponent(query) + "&tag=" + AFF_TAG;
  }

  var IMG = "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/";

  var CATEGORIES = [
    {
      key: "buffet",
      name: "Serviere wie ein Buffet",
      emoji: "🍽️",
      blurb: "Das Geheimnis eines entspannten Brunchs: ein Buffet, an dem sich alle selbst nehmen.",
      img: IMG + "hf_20260624_161730_0e543bb8-abc0-43bf-a380-acb6ffd15211.png",
      picks: [
        { name: "Servier-Etagere", desc: "Macht aus losen Tellern ein Buffet und spart Platz — größter Effekt fürs kleinste Geld.", q: "Etagere Servierstaender 3 Etagen" },
        { name: "Brunch-Geschirr-Set", desc: "Einheitliches Geschirr wirkt sofort edel und stimmig.", q: "Fruehstuecksgeschirr Set" },
        { name: "Servierplatten-Set", desc: "Für Käse, Aufschnitt & Obst — alles übersichtlich angerichtet.", q: "Servierplatten Set" }
      ]
    },
    {
      key: "highlights",
      name: "Highlights: Waffeln & Eier",
      emoji: "🧇",
      blurb: "Ein, zwei warme Gerichte machen aus dem Frühstück einen echten Brunch.",
      img: IMG + "hf_20260624_161733_af912ece-3c70-4515-bdaa-ddb8a5432f6d.png",
      picks: [
        { name: "Waffeleisen", desc: "Frische Waffeln sind das Brunch-Highlight — jeder backt sich seine selbst.", q: "Waffeleisen" },
        { name: "Eierkocher", desc: "Perfekt gekochte Eier auf den Punkt, ganz ohne Topf-Wache.", q: "Eierkocher" },
        { name: "Pancake-Maker", desc: "Fluffige Pancakes ohne Herd-Stress — Kinder lieben es.", q: "Pancake Maker" }
      ]
    },
    {
      key: "drinks",
      name: "Kaffee & Mimosas",
      emoji: "☕",
      blurb: "Ein Brunch ohne guten Kaffee ist kein Brunch — plus festlicher Touch mit Mimosas.",
      img: IMG + "hf_20260624_161738_61e65870-bff4-4b4f-9a3e-bac4fb4d9037.png",
      picks: [
        { name: "French Press / Kaffeebereiter", desc: "Macht guten Kaffee für die ganze Runde auf einmal.", q: "French Press Kaffeebereiter" },
        { name: "Glaskaraffe", desc: "Saft & Sekt aus einer schönen Karaffe serviert — der festliche Touch.", q: "Glaskaraffe Saft Set" },
        { name: "Sektgläser-Set", desc: "Für den festlichen Anstoß zum Brunch.", q: "Sektglaeser Set" }
      ]
    },
    {
      key: "tisch",
      name: "Der schön gedeckte Tisch",
      emoji: "🌸",
      blurb: "Die Kleinigkeiten machen den Unterschied und heben den Tisch sofort an.",
      img: IMG + "hf_20260624_161740_d5424949-f57a-44f9-ae21-2ef0aff47c53.png",
      picks: [
        { name: "Tischläufer (Leinen)", desc: "Zieht den Tisch optisch zusammen — die einfachste Aufwertung.", q: "Tischlaeufer Leinen" },
        { name: "Stoffservietten", desc: "Kleiner Touch, der viel hermacht und wiederverwendbar ist.", q: "Stoffservietten Set" },
        { name: "Blumenvase & Tischdeko", desc: "Frische Blumen machen jeden Brunch-Tisch lebendig.", q: "Blumenvase Tischdeko" }
      ]
    }
  ];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function el(html) {
    var d = document.createElement("div");
    d.innerHTML = html.trim();
    return d.firstChild;
  }

  function render() {
    var grid = document.getElementById("build-grid");
    if (!grid) return;
    grid.innerHTML = "";
    CATEGORIES.forEach(function (cat) {
      var hero = cat.picks[0];
      var more = cat.picks.length - 1;
      var card = el(
        '<article class="cat-card" id="cat-' + cat.key + '" style="scroll-margin-top:90px">' +
          '<div class="cover" style="background-image:url(\'' +
          cat.img +
          "')\">" +
          '<span class="tag">' +
          cat.emoji +
          " " +
          esc(cat.name) +
          "</span>" +
          "</div>" +
          '<div class="cat-body">' +
          '<p class="blurb">' +
          esc(cat.blurb) +
          "</p>" +
          '<div class="hero-pick">' +
          '<span class="hp-label">Unser Pick</span>' +
          '<span class="hp-name">' +
          esc(hero.name) +
          "</span>" +
          '<span class="hp-desc">' +
          esc(hero.desc) +
          "</span>" +
          '<a class="hp-btn" href="' +
          amz(hero.q) +
          '" rel="sponsored nofollow" target="_blank">Auf Amazon ansehen →</a>' +
          "</div>" +
          (more > 0
            ? '<p class="picks-label">Die komplette Liste — direkt shoppen:</p>' +
              '<ul class="picks">' +
              cat.picks
                .slice(1)
                .map(function (p) {
                  return (
                    '<li><span class="pick-name">' +
                    esc(p.name) +
                    "</span>" +
                    '<a class="add-btn" href="' +
                    amz(p.q) +
                    '" rel="sponsored nofollow" target="_blank">Ansehen</a></li>'
                  );
                })
                .join("") +
              "</ul>"
            : "") +
          (cat.guide
            ? '<a class="guide-link" href="' + cat.guide + '">Passenden Kaufratgeber lesen →</a>'
            : "") +
          "</div>" +
          "</article>"
      );
      grid.appendChild(card);
    });

    if (location.hash) {
      var t = document.getElementById(location.hash.slice(1));
      if (t) t.scrollIntoView();
    }
  }

  document.addEventListener("DOMContentLoaded", render);
})();
