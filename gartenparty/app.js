/* BeThatHost — Gartenparty: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "licht",
      name: "Licht & Beleuchtung",
      emoji: "💡",
      blurb: "Wenn die Sonne untergeht, lebt die Gartenparty vom Licht — warm und einladend.",
      img: IMG + "hf_20260622_091354_593cd1f2-eea0-45c1-abcc-da114bd9e929.jpeg",
      guide: "/ratgeber/outdoor-lichterkette.html",
      picks: [
        { name: "Outdoor-Lichterkette (wetterfest)", desc: "Der schnellste Weg zu warmer Biergarten-Stimmung über dem Tisch.", q: "Lichterkette aussen warmweiss wetterfest G40" },
        { name: "Solar-Gartenleuchten", desc: "Laden tagsüber, leuchten abends — ganz ohne Kabel.", q: "Solar Gartenleuchten Edelstahl Steckleuchten" },
        { name: "Solar-Tischlaternen", desc: "Gemütliches Licht direkt auf der Tafel.", q: "Solar Laterne Garten Tisch" },
        { name: "Feuerschale", desc: "Wärme und Lagerfeuer-Romantik, wenn es spät wird.", q: "Feuerschale Garten" }
      ]
    },
    {
      key: "sitzen",
      name: "Schatten & Sitzplätze",
      emoji: "⛱️",
      blurb: "Tagsüber Schatten, abends bequem — gemütliche Plätze halten die Gäste lange.",
      img: IMG + "hf_20260622_091405_fe7d4d87-ef9e-4dbc-90f0-2095ec261bef.jpeg",
      picks: [
        { name: "Sonnenschirm / Pavillon", desc: "Schatten über der Tafel und Schutz bei kurzem Sommerregen.", q: "Pavillon Garten 3x3 wasserdicht" },
        { name: "Outdoor-Sitzkissen", desc: "Machen harte Gartenstühle bequem — keiner steht zu früh auf.", q: "Outdoor Sitzkissen wasserdicht" },
        { name: "Sonnenschirm (groß)", desc: "Viel Schatten für die ganze Runde.", q: "Sonnenschirm Garten gross" }
      ]
    },
    {
      key: "drinks",
      name: "Getränke kühlen & servieren",
      emoji: "🍹",
      blurb: "Kalte Getränke in Reichweite — mit Self-Service musst du nicht ständig laufen.",
      img: IMG + "hf_20260622_091418_4cd04775-3c1d-46d4-be17-73e602eacb78.png",
      picks: [
        { name: "Getränkespender mit Zapfhahn", desc: "Limonade, Sangria oder Wasser mit Minze — jeder bedient sich selbst.", q: "Getraenkespender Glas Zapfhahn Holzstaender" },
        { name: "Getränke-Kühlbox", desc: "Hält Bier, Wein & Softdrinks den ganzen Abend eiskalt.", q: "Kuehlbox gross Camping" },
        { name: "Outdoor-Gläser (bruchsicher)", desc: "Kein Scherben-Risiko im Garten.", q: "Outdoor Glaeser Kunststoff Set" }
      ]
    },
    {
      key: "deko",
      name: "Musik & Sommer-Deko",
      emoji: "🎶",
      blurb: "Etwas Musik und sommerliche Details machen aus dem Garten eine Party-Location.",
      img: IMG + "hf_20260622_091441_f17b4852-3119-4e39-9723-b18cb2a99c06.jpeg",
      guide: "/ratgeber/bluetooth-lautsprecher-garten.html",
      picks: [
        { name: "Outdoor-Bluetooth-Lautsprecher", desc: "Wasserdicht und mit kräftigem Sound für draußen.", q: "Bluetooth Lautsprecher wasserdicht tragbar" },
        { name: "Sommerliche Tisch- & Gartendeko", desc: "Wimpelketten, Pompoms & Lampions geben sofort ein Motto.", q: "Gartenparty Deko Set Pompoms Wimpelkette" },
        { name: "Lampions / Laternen", desc: "Bunte Farbtupfer zwischen den Bäumen.", q: "Lampions Garten bunt" }
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
