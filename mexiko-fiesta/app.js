/* BeThatHost — Mexikanische Fiesta: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "deko",
      name: "Deko & Fiesta-Atmosphäre",
      emoji: "🌵",
      blurb: "Mexiko lebt von Farbe — Papel Picado und ein paar Kakteen, und die Stimmung ist da.",
      img: IMG + "hf_20260624_164655_eccb80b1-aed5-42cc-83a9-0ccd1f3638f8.png",
      picks: [
        { name: "Papel-Picado-Wimpelketten", desc: "Die bunten Scherenschnitt-Girlanden — das Erkennungszeichen jeder Fiesta.", q: "Papel Picado Girlande Mexiko Deko" },
        { name: "Mexiko-Deko-Set (Kaktus & Chili)", desc: "Kakteen, Chili-Lichterketten und Pompoms geben sofort das Motto.", q: "Mexiko Party Deko Set" },
        { name: "Bunte Tischdecke", desc: "Farbenfroher Untergrund fürs Buffet.", q: "Mexiko Tischdecke bunt" }
      ]
    },
    {
      key: "taco",
      name: "Das Taco-Buffet",
      emoji: "🌮",
      blurb: "Ein Taco- oder Fajita-Buffet zum Selbstbelegen — entspannt und sieht klasse aus.",
      img: IMG + "hf_20260624_164700_9ff8540c-a890-46bb-95e9-5041ab6242f0.png",
      picks: [
        { name: "Taco-Halter-Set", desc: "Tacos stehen aufrecht — kein Umkippen, sieht nach Restaurant aus.", q: "Taco Halter Set" },
        { name: "Buntes Fiesta-Partygeschirr", desc: "Pappteller & Becher in kräftigen Farben — bruchsicher und dekorativ.", q: "Mexiko Partygeschirr Set bunt" },
        { name: "Dip-Schalen-Set", desc: "Guacamole, Salsa & Käse übersichtlich angerichtet.", q: "Dip Schalen Set" }
      ]
    },
    {
      key: "margaritas",
      name: "Margaritas & Drinks",
      emoji: "🍹",
      blurb: "Der Signature-Drink der Fiesta ist die Margarita — im Salzrand-Glas unschlagbar.",
      img: IMG + "hf_20260624_164702_6d4f7de0-49ef-4580-99eb-adf634a62593.png",
      guide: "/ratgeber/cocktail-shaker-set.html",
      picks: [
        { name: "Margarita-Gläser-Set", desc: "Die klassische Form mit breitem Rand für den Salzrand.", q: "Margarita Glaeser Set" },
        { name: "Cocktail-Set für Margaritas", desc: "Shaker, Jigger & Co. für perfekt gemixte Margaritas.", q: "Cocktail Set Shaker" },
        { name: "Margarita-Salz / Rand-Set", desc: "Für den typischen Salz- oder Zuckerrand.", q: "Margarita Salz Rand" }
      ]
    },
    {
      key: "extras",
      name: "Fiesta-Extras & Spaß",
      emoji: "🎉",
      blurb: "Ein paar Motto-Extras machen aus dem Abendessen eine richtige Party.",
      img: IMG + "hf_20260624_164711_fb61b89b-a945-4ccb-aaca-183a321e6e25.png",
      picks: [
        { name: "Piñata", desc: "Der Klassiker für gute Laune: füllen, aufhängen, losschlagen.", q: "Pinata" },
        { name: "Sombreros & Accessoires", desc: "Sombreros, Maracas & Schnurrbärte — sofort sind alle im Motto.", q: "Sombrero Mexiko Party Accessoires" },
        { name: "Maracas-Set", desc: "Rhythmus und gute Laune für die ganze Runde.", q: "Maracas Set" }
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
