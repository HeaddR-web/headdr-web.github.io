/* BeThatHost — JGA (Junggesellinnenabschied): Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "teambride",
      name: "Der Team-Bride-Look",
      emoji: "👰",
      blurb: "Ein einheitlicher Look macht die Gruppe zum Team — und die Braut zum Star.",
      img: IMG + "hf_20260624_164719_c969223d-503f-4715-89b6-31ce3b7763a2.png",
      picks: [
        { name: "Team-Bride Shirts & Schärpen", desc: "Einheitlich für die Gruppe — sofort erkennbar und perfekt für Fotos.", q: "Team Bride Schaerpen Set JGA" },
        { name: "Braut-Schärpe mit Schleier", desc: "Die Braut bekommt ihren eigenen Look als Hauptperson.", q: "Braut Schaerpe Schleier JGA" },
        { name: "Team-Bride Buttons", desc: "Kleine Anstecker als Extra fürs ganze Team.", q: "Team Bride Buttons Anstecker" }
      ]
    },
    {
      key: "deko",
      name: "Deko & Foto-Requisiten",
      emoji: "📸",
      blurb: "Etwas Deko und Foto-Props machen den Tag besonders und liefern die schönsten Erinnerungen.",
      img: IMG + "hf_20260624_164722_21edd279-3e86-4f33-b354-4e9f78201554.png",
      picks: [
        { name: "JGA-Deko-Set (Roségold)", desc: "Ballons, Banner & Girlanden für Start-Brunch oder Zimmer-Überraschung.", q: "JGA Deko Set rosegold" },
        { name: "Photo-Booth-Set", desc: "Schilder, Brillen & Props für lustige Gruppenfotos.", q: "Photo Booth Requisiten JGA" },
        { name: "Ballongirlande (Roségold)", desc: "Der Foto-Hintergrund für den großen Tag.", q: "Ballongirlande rosegold" }
      ]
    },
    {
      key: "spiele",
      name: "Spiele & Aufgaben",
      emoji: "🎯",
      blurb: "Ein bisschen Programm hält den Tag in Schwung — am besten vorher absprechen.",
      img: IMG + "hf_20260624_164726_9cecda20-502b-4072-8cc7-258f26950ef6.png",
      picks: [
        { name: "JGA-Spiele & Aufgaben-Karten", desc: "Fertige Challenge-Karten — einfach ziehen und loslegen.", q: "JGA Spiele Aufgaben Karten" },
        { name: "Verkaufsbauchladen", desc: "Der Klassiker für unterwegs — bringt die Kasse für den Abend ein.", q: "JGA Bauchladen" },
        { name: "JGA-Rubbellose", desc: "Kleine Aufgaben zum Freirubbeln — schneller Spaß für die Gruppe.", q: "JGA Rubbellose Aufgaben" }
      ]
    },
    {
      key: "anstossen",
      name: "Anstoßen & Survival-Kit",
      emoji: "🥂",
      blurb: "Zum Start wird angestoßen — und ein kleines Survival-Kit rettet später den Tag.",
      img: IMG + "hf_20260624_164729_6008dbb3-dc98-4324-a63b-75f686d22afe.png",
      picks: [
        { name: "Prosecco-Gläser (oder To-go)", desc: "Schicke Gläser oder bruchsichere Becher zum Anstoßen.", q: "Sektglaeser Set JGA" },
        { name: "JGA-Survival-Kit", desc: "Die Notfall-Box: Pflaster, Kaugummi, Haargummi & Co.", q: "JGA Survival Kit" },
        { name: "Flachmann (graviert)", desc: "Eine Erinnerung für die Braut zum Anstoßen.", q: "Flachmann graviert Braut" }
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
