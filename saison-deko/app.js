/* BeThatHost — Saison-Deko: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "licht",
      name: "Warmes Licht statt greller Lampe",
      emoji: "💡",
      blurb: "Das Wichtigste an Herbst- und Winterstimmung ist das Licht — warm statt kühl.",
      img: IMG + "hf_20260624_164043_d253d143-3abb-460d-a1f7-86ab3eba2bdd.png",
      picks: [
        { name: "Duftkerzen-Set", desc: "Kerzenlicht und ein Duft nach Zimt oder Vanille — die Seele der kalten Jahreszeit.", q: "Duftkerzen Set Herbst" },
        { name: "Warmweiße Glühbirnen", desc: "Der unterschätzte Trick: 2700 K taucht den Raum in gemütliches Licht.", q: "Gluehbirne warmweiss E27" },
        { name: "Tischlampe (warmweiß)", desc: "Eine kleine Lichtinsel statt kalter Deckenlampe.", q: "Tischlampe warmweiss gemuetlich" }
      ]
    },
    {
      key: "textilien",
      name: "Kuschelige Textilien",
      emoji: "🧶",
      blurb: "Was man anfassen kann, macht Gemütlichkeit erst spürbar.",
      img: IMG + "hf_20260624_164046_e4d51bc3-c112-4b93-8a58-c2b0437ff6d5.png",
      picks: [
        { name: "Strick-Kuscheldecke", desc: "Übers Sofa drapiert ist sie Deko und Wärmespender zugleich.", q: "Kuscheldecke Strick gross" },
        { name: "Dekokissen-Set", desc: "Kissen in warmen Erdtönen geben dem Sofa sofort einen saisonalen Look.", q: "Dekokissen Set Herbst Erdtoene" },
        { name: "Weicher Teppich", desc: "Warm unter den Füßen — macht den Raum sofort gemütlicher.", q: "Teppich weich gemuetlich" }
      ]
    },
    {
      key: "akzente",
      name: "Natürliche Akzente",
      emoji: "🍂",
      blurb: "Ein bisschen Natur holt den Herbst herein — edel und pflegeleicht.",
      img: IMG + "hf_20260624_164048_03f73388-a7d3-4528-81b6-804f584a85f8.png",
      picks: [
        { name: "Trockenblumen / Pampasgras", desc: "In eine schöne Vase gestellt — der Deko-Trend, saisonlos haltbar.", q: "Trockenblumen Pampasgras Deko" },
        { name: "Türkranz (Herbst/Winter)", desc: "Setzt den ersten gemütlichen Akzent — schon bevor man drin ist.", q: "Tuerkranz Herbst" },
        { name: "Deko-Vase", desc: "Die passende Vase für Trockenblumen & Zweige.", q: "Vase Trockenblumen" }
      ]
    },
    {
      key: "stimmungslicht",
      name: "Stimmungslicht ohne Risiko",
      emoji: "🕯️",
      blurb: "Für Stellen, an denen echte Kerzen zu heikel sind — dieselbe Stimmung, ohne Brandgefahr.",
      img: IMG + "hf_20260624_164053_da55b0a3-1de3-4550-bf4d-52d7e7965326.png",
      picks: [
        { name: "LED-Kerzen (flammenlos)", desc: "Flackern wie echte Kerzen, sicher für Regal, Fenster oder Kinderzimmer.", q: "LED Kerzen flammenlos" },
        { name: "LED-Lichterkette warmweiß", desc: "Über Regale, ums Fenster oder in eine Vase — sanftes Leuchten überall.", q: "LED Lichterkette warmweiss innen" },
        { name: "Laterne / Windlicht", desc: "Gemütliches Licht zum Hinstellen — drinnen wie draußen.", q: "Laterne Windlicht Deko" }
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
