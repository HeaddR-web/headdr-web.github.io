/* BeThatHost — Spa-Abend: Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      name: "Die Atmosphäre",
      emoji: "🕯️",
      blurb: "Spa beginnt im Kopf — und der schaltet erst ab, wenn das Licht stimmt.",
      img: IMG + "hf_20260624_163740_62d80cf1-5b9a-445c-aa32-afd7a3437ea7.png",
      picks: [
        { name: "Duftkerzen-Set", desc: "Warmes Licht und ein ruhiger Duft — das Herzstück jedes Wellness-Abends.", q: "Duftkerzen Set" },
        { name: "LED-Lichterkette warmweiß", desc: "Sanftes Licht ums Bad oder den Spiegel statt kühler Deckenlampe.", q: "LED Lichterkette warmweiss innen" },
        { name: "Aroma-Diffuser", desc: "Feiner Duft im Raum — Entspannung auf Knopfdruck.", q: "Aroma Diffuser" }
      ]
    },
    {
      key: "gesicht",
      name: "Gesichtspflege",
      emoji: "🧖",
      blurb: "Das Herzstück des Abends: eine Pflege-Runde fürs Gesicht.",
      img: IMG + "hf_20260624_163743_cafa4ae5-bd9f-46b3-9617-44969415eea2.png",
      picks: [
        { name: "Gesichtsmasken-Set", desc: "Verschiedene Tuchmasken für jeden Hauttyp — der Klassiker.", q: "Gesichtsmasken Set Tuchmasken" },
        { name: "Gesichtsroller (Jade)", desc: "Kühl über die Maske gerollt — entspannt und sieht edel aus.", q: "Gesichtsroller Jade Set" },
        { name: "Augenpads", desc: "Gekühlte Hydrogel-Pads gegen müde Augen — schneller Frische-Kick.", q: "Augenpads Hydrogel" }
      ]
    },
    {
      key: "bad",
      name: "Bad & Körper",
      emoji: "🛁",
      blurb: "Nichts entspannt so wie ein warmes Bad — danach ab in den Bademantel.",
      img: IMG + "hf_20260624_163747_3c7a1ff2-3296-441a-8a2f-4b7a95a04c3f.png",
      picks: [
        { name: "Badebomben-Set", desc: "Verwandeln das Badewasser in ein duftendes Erlebnis.", q: "Badebomben Set" },
        { name: "Weicher Bademantel", desc: "Flauschig nach dem Bad — wie im Wellness-Hotel.", q: "Bademantel weich Damen" },
        { name: "Fußsprudelbad", desc: "Wellness bis in die Zehen nach einem langen Tag.", q: "Fusssprudelbad Massage" }
      ]
    },
    {
      key: "haende",
      name: "Hände & Entspannung",
      emoji: "🍵",
      blurb: "Zum Ausklang: eine kleine Maniküre und ein warmer Tee.",
      img: IMG + "hf_20260624_163751_4308edd1-b703-4db8-b6e7-9450681aadec.png",
      picks: [
        { name: "Maniküre-Set", desc: "Alles für gepflegte Hände an einem Ort — die Selfcare-Routine zum Abschluss.", q: "Manikuere Set" },
        { name: "Wellness-Tee", desc: "Ein beruhigender Kräutertee rundet den Spa-Abend ab.", q: "Wellness Tee Set" },
        { name: "Handcreme-Set", desc: "Weiche Hände nach der Maniküre — der pflegende Abschluss.", q: "Handcreme Set" }
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
