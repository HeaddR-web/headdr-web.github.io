/* BeThatHost — watchparty: Ausstattung nach Kategorie mit direkten Amazon-Produktlinks.
   Reines statisches JS (nur Rendering). Affiliate-Tag: cozylore-21.
   Produkte aus Stefanies Review (data/picks-final.json). */
(function () {
  "use strict";

  var AFF_TAG = "cozylore-21";

  function aff(p) {
    if (p.asin) return "https://www.amazon.de/dp/" + encodeURIComponent(p.asin) + "?tag=" + AFF_TAG;
    return "https://www.amazon.de/s?k=" + encodeURIComponent(p.q || p.name) + "&tag=" + AFF_TAG;
  }

  var CATEGORIES = [
    {
        "key": "food",
        "name": "Essen & Snacks",
        "emoji": "🌮",
        "blurb": "Nachos, Wings & Fingerfood, das man ohne Tor-Verpassen schnappt.",
        "img": "/assets/img/hf_20260618_151400_aed3e59f-6306-4ada-9f78-fb7904cf9f2a.jpg",
        "guide": "posts/world-cup-watch-party.html",
        "products": [
            {
                "name": "Snack- & Dip-Schalen",
                "desc": "Alles griffbereit auf dem Tisch.",
                "asin": "B07CMHJVNG"
            }
        ]
    },
    {
        "key": "decor",
        "name": "Deko & Fan-Gear",
        "emoji": "🇩🇪",
        "blurb": "Fahnen, Wimpelketten & Fan-Gear in schwarz-rot-gold.",
        "img": "/assets/img/hf_20260618_151154_afcd59b6-7195-447f-9f07-601ef2ce0468.jpg",
        "guide": "posts/world-cup-watch-party.html",
        "products": [
            {
                "name": "Deko-Set (schwarz-rot-gold)",
                "desc": "",
                "asin": "B0D63N5HVW"
            }
        ]
    },
    {
        "key": "games",
        "name": "Tippspiel & Spiele",
        "emoji": "🏆",
        "blurb": "Spielplan an die Wand, ein Tippspiel und ein Spiel für die Halbzeit.",
        "img": "/assets/img/hf_20260618_151157_71d1e854-e938-414d-9df0-8b654ee30799.jpg",
        "guide": "posts/world-cup-watch-party.html",
        "products": [
            {
                "name": "WM-Spielplan-Poster",
                "desc": "Alle Spiele & Ergebnisse im Blick.",
                "asin": "B0GVHP14W4"
            }
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

  // Kachel-Ableitung zu einem Originalbild (siehe scripts/build-images.py).
  function kachel(src, breite) {
    return src.replace(/^\/assets\/img\/(.+)\.jpg$/, "/assets/img/kachel/$1-" + breite + ".jpg");
  }

  function sprungZumAnker() {
    if (location.hash) {
      var t = document.getElementById(location.hash.slice(1));
      if (t) { t.scrollIntoView(); }
      else { var g = document.getElementById("build-grid"); if (g) setTimeout(function(){ g.scrollIntoView({ behavior: "auto", block: "start" }); }, 80); }  // entfernte Kategorie -> Produktbereich
  }
  }

  function render() {
    var grid = document.getElementById("build-grid");
    if (!grid) return;
    // Das Gitter steht schon als HTML in der Seite (fuer Crawler und ohne JS).
    // Es hier wegzuwerfen und neu zu bauen kostete bis September 2026 gleich
    // dreifach: das Layout sprang sichtbar (CLS 0,18 auf watchparty/), die
    // Kacheln wurden ein zweites Mal geladen - in voller Aufloesung statt als
    // Ableitung -, und alles, was build-faq.py in dasselbe Gitter geschrieben
    // hatte, verschwand fuer jeden Besucher mit JavaScript. Also nur noch
    // rendern, wenn wirklich nichts da ist.
    if (grid.querySelector(".cat-card")) {
      sprungZumAnker();
      return;
    }
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
          '<div class="cover"><img src="' + kachel(cat.img, 720) +
          '" srcset="' + kachel(cat.img, 480) + " 480w, " + kachel(cat.img, 720) +
          ' 720w" sizes="(max-width: 700px) 100vw, 360px"' +
          ' width="720" height="540" alt="" loading="lazy" fetchpriority="low" />' +
          '<span class="tag">' + esc(cat.name) + "</span>" +
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

    sprungZumAnker();
  }

  document.addEventListener("DOMContentLoaded", render);
})();
