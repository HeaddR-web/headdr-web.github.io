/* BeThatHost — girlsnight: Ausstattung nach Kategorie mit direkten Amazon-Produktlinks.
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
        "key": "games",
        "name": "Spiele",
        "emoji": "🎲",
        "blurb": "Eisbrecher, Party-Kartenspiele und ein bisschen Chaos.",
        "img": "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_102523_ca7d067e-7c56-4964-9625-687b5f931af3.png",
        "guide": "posts/girls-night-games.html",
        "products": [
            {
                "name": "Party-Kartenspiel (Erwachsene)",
                "desc": "Der einfachste Eisbrecher des Abends.",
                "asin": "B0914WWCSC"
            },
            {
                "name": "Hitster (Musik-Partyspiel)",
                "desc": "",
                "asin": "B0FBGF84ZJ"
            }
        ]
    },
    {
        "key": "drinks",
        "name": "Drinks",
        "emoji": "🍸",
        "blurb": "Signature-Cocktails, Sekt und alles zum Servieren.",
        "img": "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_102525_a7a5a55a-e9b5-4787-9af4-e8c7d02ea6c7.png",
        "guide": "posts/girls-night-drinks.html",
        "products": [
            {
                "name": "Gläser-Set",
                "desc": "",
                "asin": "B0DQ5SP9HN"
            }
        ]
    },
    {
        "key": "snacks",
        "name": "Snacks",
        "emoji": "🍫",
        "blurb": "Grazing-Boards, süße Häppchen und Popcorn ohne Ende.",
        "img": "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_102544_022496d0-9c73-4514-b18b-c66f4a3e3c95.png",
        "guide": "posts/girls-night-snacks.html",
        "products": [
            {
                "name": "Snackschalen",
                "desc": "",
                "asin": "B07CMHJVNG"
            }
        ]
    },
    {
        "key": "themes",
        "name": "Deko & Themes",
        "emoji": "🎀",
        "blurb": "Ballon-Girlanden, Lichterketten und ein hübsch gedeckter Tisch.",
        "img": "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_102545_a44fca4f-758a-4f44-b4b9-a88dc762ba52.png",
        "guide": "posts/girls-night-themes.html",
        "products": [
            {
                "name": "Luftballon-Girlande (Set)",
                "desc": "Der Foto-Hintergrund des Abends.",
                "asin": "B0DPWVW3CR"
            },
            {
                "name": "Deko-Set",
                "desc": "",
                "asin": "B0GHLGQXH6"
            }
        ]
    },
    {
        "key": "pamper",
        "name": "Pflege & Spa",
        "emoji": "💅",
        "blurb": "Gesichtsmasken, Bademäntel und ein Spa-Moment für daheim.",
        "img": "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_102526_b6c7850b-e9ee-4a5a-bf6d-b94f8de50618.png",
        "guide": "posts/girls-night-pamper-spa.html",
        "products": [
            {
                "name": "Gesichtsmasken-Set",
                "desc": "Der Spa-Klassiker für alle.",
                "asin": "B0CJYCSGZP"
            }
        ]
    },
    {
        "key": "fotos",
        "name": "Fotos & Erinnerungen",
        "emoji": "📸",
        "blurb": "Sofortbilder, die jede mit nach Hause nimmt — das Must-have für den Mädelsabend.",
        "img": "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260619_132412_f9b8320b-fb24-4b22-81a5-a6e22720dee0.jpeg",
        "guide": "posts/pyjama-party.html",
        "products": [
            {
                "name": "Sofortbildkamera",
                "desc": "Der Mädelsabend-Klassiker schlechthin — jede klebt ihr Foto später ins Album.",
                "asin": "B0C2J34N8G"
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
