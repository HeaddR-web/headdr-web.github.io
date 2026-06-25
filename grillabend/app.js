/* BeThatHost — Grillabend: Ausstattung nach Kategorie mit direkten Amazon-Links.
   Reines statisches JS (nur Rendering, kein State). Affiliate-Tag: cozylore-21. */
(function () {
  "use strict";

  var AFF_TAG = "cozylore-21";

  // Amazon-Such-Affiliate-Link (keine erfundenen Produktnamen / Preise).
  function amz(query) {
    return "https://www.amazon.de/s?k=" + encodeURIComponent(query) + "&tag=" + AFF_TAG;
  }

  // Geteilte Higgsfield-Bildbasis.
  var IMG = "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/";

  // Kategorien + kuratierte, eigenständige Produkt-Ideen (jede mit kurzer Begründung).
  var CATEGORIES = [
    {
      key: "setup",
      name: "Das Grill-Setup",
      emoji: "🔥",
      blurb: "Herzstück ist der Grill — plus Besteck, mit dem du sicher nah rankommst.",
      img: IMG + "hf_20260624_160329_7214d372-94d8-4c3d-a544-89b3ebd87a0e.png",
      picks: [
        { name: "Grill (Holzkohle)", desc: "Ein solider Holzkohlegrill bringt das echte Grill-Aroma.", q: "Holzkohlegrill" },
        { name: "Grillbesteck-Set", desc: "Zange, Wender & Gabel mit langem Griff — sicher statt herumstochern.", q: "Grillbesteck Set Edelstahl" },
        { name: "Grillkohle & Anzünder", desc: "Damit die Glut schnell und zuverlässig kommt.", q: "Grillkohle Anzuendkamin" },
        { name: "Grillthermometer", desc: "Punktgenau garen statt raten.", q: "Grillthermometer Fleisch" }
      ]
    },
    {
      key: "wuerzen",
      name: "Würzen & Zubereiten",
      emoji: "🧂",
      blurb: "Der Geschmack kommt von guten Gewürzen — und nichts fällt durch den Rost.",
      img: IMG + "hf_20260624_160332_b4e1c2c8-8535-4ed1-8a10-1940c93a83dc.png",
      picks: [
        { name: "BBQ-Gewürz- / Rub-Set", desc: "Verschiedene Grillgewürze von süßlich bis scharf für Abwechslung.", q: "Grill Gewuerz Set BBQ" },
        { name: "Grillschalen / Grillkorb", desc: "Damit Gemüse, Halloumi & Garnelen gelingen.", q: "Grillkorb Grillschalen" },
        { name: "Marinier-Set & Grillpinsel", desc: "Marinade gleichmäßig auftragen — mehr Aroma.", q: "Marinier Set Grillpinsel Silikon" }
      ]
    },
    {
      key: "servieren",
      name: "Servieren & kühlen",
      emoji: "🍽️",
      blurb: "Bruchsicher servieren und Getränke kalt halten — ohne ständig reinzulaufen.",
      img: IMG + "hf_20260624_160335_55d48800-07b0-4f6d-8fc0-3f94e7a5860d.png",
      picks: [
        { name: "Outdoor-Geschirr-Set", desc: "Bruchsicheres Melamin-Geschirr — kein Scherben-Risiko im Garten.", q: "Outdoor Geschirr Set Melamin" },
        { name: "Getränke-Kühlbox", desc: "Hält Bier & Softdrinks den ganzen Abend eiskalt.", q: "Kuehlbox gross" },
        { name: "Servierplatten & Tabletts", desc: "Alles in einem Gang an den Tisch.", q: "Servierplatten Tablett Set" }
      ]
    },
    {
      key: "atmosphaere",
      name: "Garten-Atmosphäre",
      emoji: "🌿",
      blurb: "Licht und bequeme Plätze machen aus dem Essen im Garten einen langen Abend.",
      img: IMG + "hf_20260622_091354_593cd1f2-eea0-45c1-abcc-da114bd9e929.jpeg",
      guide: "/ratgeber/outdoor-lichterkette.html",
      picks: [
        { name: "Outdoor-Lichterkette (wetterfest)", desc: "Zaubert in Sekunden Biergarten-Stimmung über dem Tisch.", q: "Lichterkette aussen warmweiss" },
        { name: "Outdoor-Sitzkissen", desc: "Machen harte Gartenstühle bequem — keiner steht zu früh auf.", q: "Outdoor Kissen wasserdicht" },
        { name: "Feuerschale", desc: "Wärme und Lagerfeuer-Romantik, wenn es spät wird.", q: "Feuerschale Garten" }
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

    // Pinterest-Deeplinks: nach dem Rendern direkt zur angesteuerten Kategorie springen (#cat-…)
    if (location.hash) {
      var t = document.getElementById(location.hash.slice(1));
      if (t) t.scrollIntoView();
    }
  }

  document.addEventListener("DOMContentLoaded", render);
})();
