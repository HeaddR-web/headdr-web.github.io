/* BeThatHost — Hawaii / Tiki: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "leis",
      name: "Leis & tropische Outfits",
      emoji: "🌺",
      blurb: "Eine Blumenkette für jeden Gast am Eingang — und schon sind alle in Partylaune.",
      img: IMG + "hf_20260624_165008_d09530f8-c1de-4847-8b00-e00454634ac6.png",
      picks: [
        { name: "Hawaii-Blumenketten (Leis)", desc: "Bunte Ketten im Großpack — eine pro Gast als Begrüßung.", q: "Hawaii Blumenketten Leis Set" },
        { name: "Hawaiihemd & Baströcke", desc: "Der klassische Luau-Look, der auf jedem Foto funktioniert.", q: "Hawaiihemd Bastrock Kostuem" },
        { name: "Blüten-Haarschmuck", desc: "Hibiskus-Blüten fürs Haar — der letzte Insel-Touch.", q: "Hawaii Haarblume Set" }
      ]
    },
    {
      key: "deko",
      name: "Tiki-Deko",
      emoji: "🏝️",
      blurb: "Palmblätter, Fackeln und Wimpelketten verwandeln Wohnzimmer oder Garten in eine Strandbar.",
      img: IMG + "hf_20260624_165011_17d5fcd9-1bca-485e-9702-a3457113f075.png",
      picks: [
        { name: "Hawaii-Deko-Set", desc: "Palmblätter, Blüten & Wimpelketten — die ganze Insel-Kulisse in einer Lieferung.", q: "Hawaii Party Deko Set" },
        { name: "Tiki-Fackeln für den Garten", desc: "Bambus-Fackeln sorgen abends für echtes Strandbar-Flair.", q: "Tiki Fackeln Garten" },
        { name: "Aufblasbare Palmen", desc: "Großer Insel-Effekt für drinnen wie draußen.", q: "aufblasbare Palme Deko" }
      ]
    },
    {
      key: "drinks",
      name: "Tropische Drinks",
      emoji: "🍹",
      blurb: "Cocktails in Tiki-Bechern mit Schirmchen machen aus jedem Getränk ein Urlaubs-Erlebnis.",
      img: IMG + "hf_20260624_165014_0aa2ae33-4e7a-4f07-a967-e907eca69be0.png",
      guide: "/ratgeber/cocktail-shaker-set.html",
      picks: [
        { name: "Tiki-Becher & Schirmchen", desc: "Tiki-Mugs plus Schirmchen & Strohhalme — sofort Strandbar-Look.", q: "Tiki Becher Cocktailschirmchen" },
        { name: "Cocktail-Set für Zuhause", desc: "Shaker & Zubehör für Piña Colada oder Mai Tai.", q: "Cocktail Set Shaker" },
        { name: "Bunte Strohhalme", desc: "Wiederverwendbar und farbenfroh — der kleine Deko-Trick.", q: "Strohhalme bunt wiederverwendbar" }
      ]
    },
    {
      key: "musik",
      name: "Musik & Spiele",
      emoji: "🎶",
      blurb: "Etwas Musik und ein, zwei Spiele bringen die Party in Schwung — Limbo darf nicht fehlen.",
      img: IMG + "hf_20260624_165017_e936afdc-09e3-4983-bc7f-e303e492ffdf.png",
      picks: [
        { name: "Aufblasbare Deko & Limbo-Set", desc: "Palmen, Flamingos oder Limbo-Stab — Spaß und Action für alle.", q: "Hawaii Limbo aufblasbare Deko" },
        { name: "Bluetooth-Lautsprecher", desc: "Wetterfester Speaker für Strandbar-Playlists, drinnen wie draußen.", q: "Bluetooth Lautsprecher wasserdicht" },
        { name: "Hawaii-Partyspiele", desc: "Kleine Motto-Spiele für die ganze Runde.", q: "Hawaii Party Spiele" }
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
