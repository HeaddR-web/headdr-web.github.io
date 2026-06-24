/* BeThatHost — Spieleabend: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "spiele",
      name: "Die Spiele",
      emoji: "🎲",
      blurb: "Die Mischung macht's: ein längeres Hauptspiel und schnelle Karten für jede Runde.",
      img: IMG + "hf_20260624_161743_62cdabb9-9094-4286-8455-47b547cb8f1c.png",
      picks: [
        { name: "Brettspiel-Klassiker", desc: "Ein bekanntes Gesellschaftsspiel als Herzstück des Abends.", q: "Gesellschaftsspiel Bestseller Erwachsene" },
        { name: "Party-Kartenspiel", desc: "Der schnelle Eisbrecher — in zwei Minuten erklärt.", q: "Partyspiel Karten Erwachsene" },
        { name: "Familien-Brettspiel", desc: "Funktioniert in jeder Altersmischung.", q: "Brettspiel Familie" }
      ]
    },
    {
      key: "snacks",
      name: "Snacks zum Knabbern",
      emoji: "🍿",
      blurb: "Snacks, die man nebenbei isst, ohne die Karten vollzukrümeln, sind Gold wert.",
      img: IMG + "hf_20260624_161745_9bd3ecfe-8d73-435d-ae5a-d6b048e13028.png",
      picks: [
        { name: "Snackschalen-Set", desc: "Chips, Nüsse & Süßes griffbereit — jeder kommt ran.", q: "Snackschalen Set Party" },
        { name: "Popcorn-Maschine", desc: "Frisches Popcorn macht aus dem Abend ein Event.", q: "Popcornmaschine Heissluft" },
        { name: "Knabber-Box / Etagere", desc: "Verschiedene Snacks übersichtlich an einem Ort.", q: "Snack Etagere Servierschalen" }
      ]
    },
    {
      key: "runde",
      name: "Die gemütliche Runde",
      emoji: "🛋️",
      blurb: "Warmes Licht und genug Plätze machen aus dem Tisch einen gemütlichen Abend.",
      img: IMG + "hf_20260624_161748_87aab5b2-f97d-49e2-8d98-af4caaab336b.png",
      picks: [
        { name: "LED-Lichterkette warmweiß", desc: "Tauscht grelles Deckenlicht gegen gemütliche Stimmung.", q: "LED Lichterkette warmweiss innen" },
        { name: "Bodenkissen / Sitzsack", desc: "Extra Plätze zum Lümmeln, wenn die Runde größer wird.", q: "Bodenkissen gross Sitzkissen" },
        { name: "Sitzsack (Erwachsene)", desc: "Der bequemste Platz am ganzen Spieltisch.", q: "Sitzsack Erwachsene" }
      ]
    },
    {
      key: "wettkampf",
      name: "Für die Wettkämpfer",
      emoji: "🏆",
      blurb: "Damit es spannend bleibt: ein Quiz für die Klugen und ein Spiel für die Mutigen.",
      img: IMG + "hf_20260624_161752_c95bbcb9-a6e5-4374-833a-c6af9a27855a.png",
      picks: [
        { name: "Quiz- / Wissensspiel", desc: "Perfekt für größere Gruppen — jeder kann mitraten.", q: "Quizspiel Erwachsene" },
        { name: "Trinkspiel-Set", desc: "Bringt sofort gute Laune in lockere Runden.", q: "Trinkspiel Set Erwachsene" },
        { name: "Würfel-Partyspiel", desc: "Schnell, laut und immer für Stimmung gut.", q: "Wuerfelspiel Party" }
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
