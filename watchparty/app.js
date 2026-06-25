/* BeThatHost — Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      name: "Bildschirm & Setup",
      emoji: "📺",
      blurb: "Großes Bild, großer Sound — mach das Wohnzimmer zum Stadion.",
      img: IMG + "hf_20260618_151141_1eb7f076-2c9f-4a92-9133-307761760f8c.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { name: "Mini-Beamer (Full HD)", desc: "Macht aus jeder Wand eine Großleinwand.", q: "Mini Beamer Full HD" },
        { name: "Beamer-Leinwand", desc: "Für ein gestochen scharfes Bild.", q: "Beamer Leinwand 100 Zoll" },
        { name: "Bluetooth-Soundbar", desc: "Damit der Jubel auch richtig knallt.", q: "Soundbar Bluetooth TV" },
        { name: "Streaming-Stick", desc: "Fire TV & Co. für die WM-Übertragung.", q: "Streaming Stick Fire TV" },
        { name: "HDMI-Kabel (lang)", desc: "Beamer flexibel im Raum platzieren.", q: "HDMI Kabel 5m" }
      ]
    },
    {
      key: "food",
      name: "Essen & Snacks",
      emoji: "🌮",
      blurb: "Nachos, Wings & Fingerfood, das man ohne Tor-Verpassen schnappt.",
      img: IMG + "hf_20260618_151400_aed3e59f-6306-4ada-9f78-fb7904cf9f2a.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { name: "Snack- & Dip-Schalen", desc: "Alles griffbereit auf dem Tisch.", q: "Snack Dip Schalen Set" },
        { name: "Tortilla-Chips (Großpackung)", desc: "Die Basis für die Nacho-Schlacht.", q: "Tortilla Chips Grosspackung" },
        { name: "Nacho-Käsesauce", desc: "Warm, cremig, Spieltag-Pflicht.", q: "Nacho Kaesesauce" },
        { name: "Hot-Dog-Maker", desc: "Selbstbau-Station für die Halbzeit.", q: "Hot Dog Maker" },
        { name: "Servier-Etagere", desc: "Macht aus Snacks ein Buffet.", q: "Servier Etagere Party" }
      ]
    },
    {
      key: "drinks",
      name: "Getränke",
      emoji: "🍺",
      blurb: "Kaltes Bier, Softdrinks & eine Selbstbedienungs-Station.",
      img: IMG + "hf_20260618_151145_231825c6-7ada-4dc3-8b88-1bfb2db1d4f3.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { name: "Getränke-Kühlbox", desc: "Hält Bier & Softdrinks eiskalt.", q: "Getraenkekuehler Box gross" },
        { name: "Bier-Zapfanlage (Tisch)", desc: "Frisch gezapft direkt am Sofa.", q: "Bier Zapfanlage Tisch" },
        { name: "Mehrweg-Partybecher", desc: "Kein Abwasch-Berg zum Abpfiff.", q: "Partybecher Set wiederverwendbar" },
        { name: "Eiswürfelform XXL", desc: "Eis geht immer zuerst aus.", q: "Eiswuerfelform gross Silikon" },
        { name: "Flaschenöffner-Set", desc: "Damit nicht alle gleichzeitig suchen.", q: "Flaschenoeffner Set" }
      ]
    },
    {
      key: "decor",
      name: "Deko & Fan-Gear",
      emoji: "🇩🇪",
      blurb: "Fahnen, Wimpelketten & Fan-Gear in schwarz-rot-gold.",
      img: IMG + "hf_20260618_151154_afcd59b6-7195-447f-9f07-601ef2ce0468.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { name: "Deutschland-Fahne (groß)", desc: "Der Hingucker hinter dem Bildschirm.", q: "Deutschland Fahne gross" },
        { name: "Wimpelkette schwarz-rot-gold", desc: "Sofort Stadion-Stimmung.", q: "Wimpelkette Deutschland schwarz rot gold" },
        { name: "Fan-Schminke", desc: "Jeder kommt geschminkt an.", q: "Fan Schminke Deutschland" },
        { name: "Autofahnen-Set", desc: "Auch fürs Auto vor der Tür.", q: "Deutschland Autofahne Set" },
        { name: "Luftballons schwarz-rot-gold", desc: "Schnelle Deko für jeden Raum.", q: "Luftballons schwarz rot gold" }
      ]
    },
    {
      key: "games",
      name: "Tippspiel & Spiele",
      emoji: "🏆",
      blurb: "Spielplan an die Wand, ein Tippspiel und ein Spiel für die Halbzeit.",
      img: IMG + "hf_20260618_151157_71d1e854-e938-414d-9df0-8b654ee30799.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { name: "WM-Spielplan-Poster", desc: "Alle Spiele & Ergebnisse im Blick.", q: "Fussball Spielplan Poster" },
        { name: "Tippspiel-Block", desc: "Wer tippt am besten?", q: "WM Tippspiel Block" },
        { name: "Tischkicker", desc: "Das Halbzeit-Highlight.", q: "Tischkicker Tisch" },
        { name: "Party-Kartenspiel", desc: "Für die Verlängerung.", q: "Kartenspiel Party lustig" },
        { name: "Tröte / Ratsche", desc: "Lärm für jedes Tor.", q: "Fan Troete Ratsche" }
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
          '<a class="guide-link" href="' + cat.guide + '">Mehr Ideen &amp; Anleitung im Guide →</a>' +
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
