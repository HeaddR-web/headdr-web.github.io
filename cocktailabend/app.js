/* BeThatHost — Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "bar",
      name: "Bar-Ausstattung",
      emoji: "🍸",
      blurb: "Das Werkzeug, mit dem aus deiner Küche eine Hausbar wird.",
      img: IMG + "hf_20260616_102525_a7a5a55a-e9b5-4787-9af4-e8c7d02ea6c7.png",
      guide: "posts/cocktailabend-zuhause.html",
      picks: [
        { name: "Cocktail-Shaker-Set", desc: "Das Herzstück jeder Hausbar.", q: "Cocktail Shaker Set Edelstahl" },
        { name: "Barmaß (Jigger)", desc: "Für exakte Mengen.", q: "Barmass Jigger Edelstahl" },
        { name: "Barlöffel & Stößel", desc: "Rühren, muddeln, mixen.", q: "Barloeffel Stoessel Set" },
        { name: "Getränkespender mit Zapfhahn", desc: "Self-Service für Batch-Cocktails.", q: "Getraenkespender mit Zapfhahn" },
        { name: "Eiswürfelform XXL", desc: "Großes Eis schmilzt langsamer.", q: "Eiswuerfelform gross Silikon" }
      ]
    },
    {
      key: "glasses",
      name: "Gläser & Servieren",
      emoji: "🥂",
      blurb: "Die richtigen Gläser machen aus jedem Drink ein Erlebnis.",
      img: "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_170510_5ff5ca06-fdfb-4288-9e95-2d27a1f57d66.png",
      guide: "posts/cocktailabend-zuhause.html",
      picks: [
        { name: "Coupé-Gläser-Set", desc: "Edel für jeden Signature-Drink.", q: "Sektglaeser Coupe Set" },
        { name: "Highball-/Longdrink-Gläser", desc: "Für Spritz & Co.", q: "Longdrink Glaeser Set" },
        { name: "Tumbler-Gläser", desc: "Whisky, Negroni, Old Fashioned.", q: "Whisky Tumbler Glaeser Set" },
        { name: "Serviertablett", desc: "Drinks stilvoll herumreichen.", q: "Serviertablett gold" },
        { name: "Cocktailspieße & Strohhalme", desc: "Die Deko im Glas.", q: "Cocktailspiesse Strohhalme wiederverwendbar" }
      ]
    },
    {
      key: "mixer",
      name: "Zutaten & Mixer",
      emoji: "🍋",
      blurb: "Sirupe, Bitters und Filler für richtig gute Drinks.",
      img: "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/hf_20260616_170508_7fcabce5-2573-474e-881a-ea2123bde7e3.png",
      guide: "posts/cocktailabend-zuhause.html",
      picks: [
        { name: "Cocktail-Sirup-Set", desc: "Im Handumdrehen neue Drinks.", q: "Cocktail Sirup Set" },
        { name: "Bitters-Set", desc: "Der Profi-Twist.", q: "Cocktail Bitter Set" },
        { name: "Tonic & Filler", desc: "Die Basis für Longdrinks.", q: "Tonic Water Set" },
        { name: "Alkoholfreie Aperitifs", desc: "Damit alle mitmachen.", q: "alkoholfreier Aperitif" },
        { name: "Garnitur-Set (getrocknete Früchte)", desc: "Sieht aus wie aus der Bar.", q: "Cocktail Garnitur getrocknete Fruechte" }
      ]
    },
    {
      key: "snacks",
      name: "Snacks & Fingerfood",
      emoji: "🫒",
      blurb: "Kleine Häppchen, die perfekt zum Aperitif passen.",
      img: IMG + "hf_20260616_102544_022496d0-9c73-4514-b18b-c66f4a3e3c95.png",
      guide: "posts/cocktailabend-zuhause.html",
      picks: [
        { name: "Servierbrett (groß)", desc: "Für ein schickes Grazing-Board.", q: "Servierbrett Holz gross" },
        { name: "Dip-Schalen-Set", desc: "Oliven, Nüsse, Dips.", q: "Dip Schalen Set" },
        { name: "Etagere", desc: "Macht aus Snacks ein Buffet.", q: "Etagere Servierstaender" },
        { name: "Käsemesser-Set", desc: "Der Klassiker zum Aperitif.", q: "Kaesemesser Set" },
        { name: "Cocktail-Servietten", desc: "Kleine Akzente, große Wirkung.", q: "Cocktailservietten" }
      ]
    },
    {
      key: "ambiente",
      name: "Deko & Ambiente",
      emoji: "✨",
      blurb: "Licht, Duft und ein Barwagen, der die Stimmung macht.",
      img: IMG + "hf_20260616_102545_a44fca4f-758a-4f44-b4b9-a88dc762ba52.png",
      guide: "posts/cocktailabend-zuhause.html",
      picks: [
        { name: "LED-Lichterkette warmweiß", desc: "Sofort gemütliche Bar-Stimmung.", q: "LED Lichterkette warmweiss innen" },
        { name: "Duftkerzen-Set", desc: "Stimmung & Duft.", q: "Duftkerzen Set" },
        { name: "Cocktail-Karte / Tafel", desc: "Wie in der echten Bar.", q: "Cocktailkarte Tafel Deko" },
        { name: "Barwagen", desc: "Die mobile Hausbar.", q: "Barwagen gold" },
        { name: "Tischläufer (Leinen)", desc: "Edler gedeckter Tisch.", q: "Tischlaeufer Leinen" }
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
      var picksHtml = cat.picks
        .map(function (p) {
          return (
            '<li>' +
            '<span class="pick-name">' +
            esc(p.name) +
            '<small class="pick-desc">' +
            esc(p.desc) +
            "</small></span>" +
            '<a class="add-btn" href="' +
            amz(p.q) +
            '" rel="sponsored nofollow" target="_blank">Amazon →</a>' +
            "</li>"
          );
        })
        .join("");
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
          '<ul class="picks">' +
          picksHtml +
          "</ul>" +
          '<a class="guide-link" href="' +
          cat.guide +
          '">Zum kompletten Cocktailabend-Guide →</a>' +
          "</div>" +
          "</article>"
      );
      grid.appendChild(card);
    });

    // Pinterest-Deeplinks: nach dem Rendern direkt zur angesteuerten Kategorie springen (#cat-…)
    if (location.hash) {
      var t = document.getElementById(location.hash.slice(1));
      if (t) t.scrollIntoView();
    }
  }

  document.addEventListener("DOMContentLoaded", render);
})();
