/* BeThatHost — Valentinstag: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "atmosphaere",
      name: "Die romantische Atmosphäre",
      emoji: "🕯️",
      blurb: "Romantik ist zu 90 % Licht: Deckenlicht dimmen, Kerzen an, warme Lichterkette auf.",
      img: IMG + "hf_20260624_163729_b1d57286-c23c-4d57-91f0-a5b8ec81f81d.png",
      picks: [
        { name: "Duftkerzen-Set", desc: "Warmes Kerzenlicht und ein dezenter Duft — die Basis jeder Date Night.", q: "Duftkerzen Set romantisch Rose" },
        { name: "LED-Lichterkette warmweiß", desc: "Ums Fenster oder hinter dem Tisch — der weiche Schimmer wie im Film.", q: "LED Lichterkette warmweiss innen" },
        { name: "Rosenblätter (Deko)", desc: "Ein paar Blätter auf dem Tisch — sofort romantisch.", q: "Rosenblaetter Deko" }
      ]
    },
    {
      key: "tisch",
      name: "Der gedeckte Tisch für zwei",
      emoji: "🌹",
      blurb: "Ein liebevoll gedeckter Tisch macht aus dem Abendessen ein Dinner.",
      img: IMG + "hf_20260624_163732_af5d6c4e-6735-4d67-8003-7cf2144a6105.png",
      picks: [
        { name: "Kerzenständer-Set", desc: "Der Mittelpunkt des Tisches — und das schönste Licht.", q: "Kerzenstaender Set gold Tischdeko" },
        { name: "Infinity-Rosenbox", desc: "Echte Rosen, die jahrelang halten — die Geste, die nicht welkt.", q: "Infinity Rosenbox" },
        { name: "Stoffservietten", desc: "Der kleine Touch, der den Tisch sofort hochwertig macht.", q: "Stoffservietten Set" }
      ]
    },
    {
      key: "dinner",
      name: "Dinner & Drinks",
      emoji: "🍽️",
      blurb: "Gemeinsam kochen verbindet — Fondue oder Raclette ist perfekt, ohne Küchenstress.",
      img: IMG + "hf_20260624_163735_d86a82cb-e25a-4e06-a536-eccfb71cc7e2.png",
      guide: "/ratgeber/raclette-fondue-set.html",
      picks: [
        { name: "Fondue- / Raclette-Set (2 Pers.)", desc: "Das ideale Date-Night-Dinner: gemütlich, interaktiv, ohne Stress.", q: "Raclette Fondue Set 2 Personen" },
        { name: "Sektgläser-Set", desc: "Zum Anstoßen auf den Abend — im richtigen Glas.", q: "Sektglaeser 2er Set" },
        { name: "Weingläser-Set", desc: "Für den guten Tropfen zum Dinner.", q: "Weinglaeser Set" }
      ]
    },
    {
      key: "ueberraschung",
      name: "Die süße Überraschung",
      emoji: "🎁",
      blurb: "Zum Abschluss eine kleine Geste, die in Erinnerung bleibt.",
      img: IMG + "hf_20260624_163737_13a201e4-7913-4049-9ffa-3116d343778c.png",
      picks: [
        { name: "Pralinen-Geschenkbox", desc: "Das klassische süße Finale — liegt schon bereit, wenn der Abend startet.", q: "Pralinen Geschenkbox" },
        { name: "Sternenhimmel-Projektor", desc: "Sanfter Sternenhimmel an der Decke — überraschend romantisch.", q: "Sternenhimmel Projektor LED" },
        { name: "Foto-Geschenk / Bilderrahmen", desc: "Eine persönliche Erinnerung, die bleibt.", q: "Bilderrahmen Geschenk Paar" }
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
