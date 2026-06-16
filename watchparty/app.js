/* Watch Party HQ — Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      img: IMG + "hf_20260616_102543_f5bfd8f6-713c-4afb-9c14-d0cef07ebcaa.png",
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
      img: IMG + "hf_20260616_102544_022496d0-9c73-4514-b18b-c66f4a3e3c95.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { name: "Snack- & Dip-Schalen", desc: "Alles griffbereit auf dem Tisch.", q: "Snackschalen Set Party" },
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
      img: IMG + "hf_20260616_102525_a7a5a55a-e9b5-4787-9af4-e8c7d02ea6c7.png",
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
      img: IMG + "hf_20260616_102545_a44fca4f-758a-4f44-b4b9-a88dc762ba52.png",
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
      img: IMG + "hf_20260616_102523_ca7d067e-7c56-4964-9625-687b5f931af3.png",
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
      var picksHtml = cat.picks
        .map(function (p) {
          return (
            '<li>' +
            '<span class="pick-name">' +
            esc(p.name) +
            '<small class="pick-desc">' +
            esc(p.desc) +
            "</small></span>" +
            '<a class="add-btn" href="' +
            amz(p.q) +
            '" rel="sponsored nofollow" target="_blank">Amazon →</a>' +
            "</li>"
          );
        })
        .join("");
      var card = el(
        '<article class="cat-card">' +
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
          '<ul class="picks">' +
          picksHtml +
          "</ul>" +
          '<a class="guide-link" href="' +
          cat.guide +
          '">Zum kompletten Watch-Party-Guide →</a>' +
          "</div>" +
          "</article>"
      );
      grid.appendChild(card);
    });
  }

  document.addEventListener("DOMContentLoaded", render);
})();
