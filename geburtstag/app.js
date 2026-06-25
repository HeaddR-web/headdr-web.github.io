/* BeThatHost — Geburtstag: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      name: "Deko, die sofort wirkt",
      emoji: "🎈",
      blurb: "Ein großer Blickfang reicht — Ballon-Girlande als Foto-Hintergrund und ein Banner.",
      img: IMG + "hf_20260624_162256_0fd533a9-eaa8-4104-91ff-f2e228ca4163.png",
      picks: [
        { name: "Luftballon-Girlande (Set)", desc: "Der Foto-Hintergrund des Abends — in Blush & Gold edel statt Kindergeburtstag.", q: "Luftballon Girlande Geburtstag" },
        { name: "Happy-Birthday-Banner", desc: "Sagt sofort: hier wird gefeiert — wiederverwendbar für jedes Jahr.", q: "Happy Birthday Banner Girlande" },
        { name: "Konfetti & Tischdeko", desc: "Die kleinen Farbtupfer, die den Tisch komplett machen.", q: "Konfetti Tischdeko Geburtstag" }
      ]
    },
    {
      key: "torte",
      name: "Die Torte in Szene setzen",
      emoji: "🎂",
      blurb: "Der große Moment: auf einer schönen Platte und mit Kerzen wird die Torte zum Mittelpunkt.",
      img: IMG + "hf_20260624_162259_18432d68-da6c-485a-8cdc-1f6167ac56c2.png",
      picks: [
        { name: "Tortenplatte / Etagere", desc: "Hebt die Torte aufs Podest — macht aus jedem Kuchen den Star.", q: "Tortenplatte mit Haube" },
        { name: "Geburtstagskerzen", desc: "Zahlenkerze oder Wunderkerzen — der Moment, auf den alle warten.", q: "Geburtstagskerzen" },
        { name: "Cake-Topper", desc: "Das i-Tüpfelchen für das beste Foto des Abends.", q: "Cake Topper Geburtstag" }
      ]
    },
    {
      key: "stimmung",
      name: "Stimmung & Musik",
      emoji: "🎶",
      blurb: "Licht und Musik machen aus einem Zimmer eine Feier.",
      img: IMG + "hf_20260624_162117_8cb8640b-a396-4700-9ea2-d66198c7c162.png",
      picks: [
        { name: "LED-Lichterkette warmweiß", desc: "Tauscht grelles Deckenlicht gegen Partystimmung.", q: "LED Lichterkette warmweiss innen" },
        { name: "Bluetooth-Lautsprecher", desc: "Eine kräftige, tragbare Box bringt die Playlist in jeden Raum.", q: "Bluetooth Lautsprecher Party" },
        { name: "LED-Partylicht / Discokugel", desc: "Ein bisschen Bewegung an der Wand — sofort Partygefühl.", q: "LED Partylicht Discokugel" }
      ]
    },
    {
      key: "unterhaltung",
      name: "Unterhaltung & kleine Geschenke",
      emoji: "🎁",
      blurb: "Ein Partyspiel als Eisbrecher und kleine Goodie-Bags zum Mitnehmen.",
      img: IMG + "hf_20260624_162119_c15a93ce-8706-4b5d-9cb2-ab12b660a12d.png",
      picks: [
        { name: "Party-Kartenspiel", desc: "Bringt die Runde sofort zum Lachen — ganz ohne Vorbereitung.", q: "Partyspiel Erwachsene Geburtstag" },
        { name: "Fotobox / Sofortbildkamera", desc: "Liefert die besten Erinnerungen und beschäftigt die Gäste von allein.", q: "Sofortbildkamera Instax" },
        { name: "Goodie-Bags", desc: "Kleine Tüten mit Süßem oder Mini-Geschenken — eine liebevolle Geste.", q: "Goodie Bags Geburtstag" }
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
