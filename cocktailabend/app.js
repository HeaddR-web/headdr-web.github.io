/* BeThatHost — Cocktailabend: Ausstattung nach Kategorie mit direkten Amazon-Produktlinks.
   Reines statisches JS (nur Rendering). Affiliate-Tag: cozylore-21.
   Produkte aus Stefanies Review (data/picks-final.json). */
(function () {
  "use strict";

  var AFF_TAG = "cozylore-21";
  var IMG = "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/";

  // Direkter Produktlink (/dp/ASIN). Fallback auf Suche, falls mal keine ASIN.
  function aff(p) {
    if (p.asin) return "https://www.amazon.de/dp/" + encodeURIComponent(p.asin) + "?tag=" + AFF_TAG;
    return "https://www.amazon.de/s?k=" + encodeURIComponent(p.q || p.name) + "&tag=" + AFF_TAG;
  }

  var CATEGORIES = [
    {
      key: "bar",
      name: "Bar-Ausstattung",
      emoji: "🍸",
      blurb: "Das Werkzeug, mit dem aus deiner Küche eine Hausbar wird.",
      img: IMG + "hf_20260618_154209_c552fe72-9c08-4cf4-80bb-d214f4ee3d85.png",
      guide: "posts/cocktailabend-zuhause.html",
      products: [
        { name: "Cocktail-Shaker-Set", desc: "Das Herzstück jeder Hausbar.", asin: "B0DG5B8TQX" },
        { name: "Cocktail-Rezeptbuch", desc: "", asin: "3625195704" }
      ]
    },
    {
      key: "glasses",
      name: "Gläser & Servieren",
      emoji: "🥂",
      blurb: "Die richtigen Gläser machen aus jedem Drink ein Erlebnis.",
      img: IMG + "hf_20260616_170510_5ff5ca06-fdfb-4288-9e95-2d27a1f57d66.png",
      guide: "posts/cocktailabend-zuhause.html",
      products: [
        { name: "Coupé-Gläser-Set", desc: "Edel für jeden Signature-Drink.", asin: "B0FRLT2KV5" },
        { name: "Strohhalme (wiederverwendbar)", desc: "", asin: "B07HML5H91" },
        { name: "Aperitif-Gläser", desc: "", asin: "B084HCZRCG" }
      ]
    },
    {
      key: "mixer",
      name: "Zutaten & Mixer",
      emoji: "🍋",
      blurb: "Sirupe, Bitters und Filler für richtig gute Drinks.",
      img: IMG + "hf_20260616_170508_7fcabce5-2573-474e-881a-ea2123bde7e3.png",
      guide: "posts/cocktailabend-zuhause.html",
      products: [
        { name: "Cocktail-Sirup-Set", desc: "Im Handumdrehen neue Drinks.", asin: "B0CKTLMYJW" },
        { name: "Cocktail-Glitzer", desc: "", asin: "B0D8ST7K4B" }
      ]
    },
    {
      key: "snacks",
      name: "Snacks & Fingerfood",
      emoji: "🫒",
      blurb: "Kleine Häppchen, die perfekt zum Aperitif passen.",
      img: IMG + "hf_20260618_154211_e1c275b4-48dc-4942-93bc-c1b677ccfc2f.png",
      guide: "posts/cocktailabend-zuhause.html",
      products: [
        { name: "Servierbrett", desc: "Für ein schickes Grazing-Board.", asin: "B0H1M3Z4N7" }
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
      var picks = cat.products
        .map(function (p, idx) {
          return (
            '<div class="hero-pick">' +
            (idx === 0 ? '<span class="hp-label">Unser Pick</span>' : "") +
            '<span class="hp-name">' + esc(p.name) + "</span>" +
            (p.desc ? '<span class="hp-desc">' + esc(p.desc) + "</span>" : "") +
            '<a class="hp-btn" href="' + aff(p) +
            '" rel="sponsored nofollow noopener" target="_blank">Preis auf Amazon prüfen →</a>' +
            "</div>"
          );
        })
        .join("");
      var card = el(
        '<article class="cat-card" id="cat-' + cat.key + '" style="scroll-margin-top:90px">' +
          '<div class="cover" style="background-image:url(\'' + cat.img + "')\">" +
          '<span class="tag">' + cat.emoji + " " + esc(cat.name) + "</span>" +
          "</div>" +
          '<div class="cat-body">' +
          '<p class="blurb">' + esc(cat.blurb) + "</p>" +
          picks +
          '<a class="guide-link" href="' + cat.guide + '">Zum Guide →</a>' +
          "</div>" +
          "</article>"
      );
      grid.appendChild(card);
    });

    if (location.hash) {
      var t = document.getElementById(location.hash.slice(1));
      if (t) { t.scrollIntoView(); }
      else { var g = document.getElementById("build-grid"); if (g) setTimeout(function(){ g.scrollIntoView({ behavior: "auto", block: "start" }); }, 80); }  // entfernte Kategorie -> Produktbereich
    }
  }

  document.addEventListener("DOMContentLoaded", render);
})();
