/* BeThatHost — Ausstattung nach Kategorie mit direkten Amazon-Links.
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
      key: "games",
      name: "Spiele",
      emoji: "🎲",
      blurb: "Eisbrecher, Party-Kartenspiele und ein bisschen Chaos.",
      img: IMG + "hf_20260616_102523_ca7d067e-7c56-4964-9625-687b5f931af3.png",
      guide: "posts/girls-night-games.html",
      picks: [
        { name: "Party-Kartenspiel (Erwachsene)", desc: "Der einfachste Eisbrecher des Abends.", q: "Partyspiel Karten Erwachsene" },
        { name: "Wahrheit oder Pflicht (Deck)", desc: "Klassiker ohne Nachdenken.", q: "Wahrheit oder Pflicht Kartenspiel" },
        { name: "„Wer kennt mich am besten?\"", desc: "Für enge Freundinnen.", q: "Wer kennt mich am besten Spiel" },
        { name: "Trinkspiel-Set", desc: "Bringt sofort Stimmung.", q: "Trinkspiel Set Party" },
        { name: "Zeichen- & Rate-Spiel", desc: "Chaotisch und sehr fotogen.", q: "Zeichenspiel Partyspiel" }
      ]
    },
    {
      key: "drinks",
      name: "Drinks",
      emoji: "🍸",
      blurb: "Signature-Cocktails, Sekt und alles zum Servieren.",
      img: IMG + "hf_20260616_102525_a7a5a55a-e9b5-4787-9af4-e8c7d02ea6c7.png",
      guide: "posts/girls-night-drinks.html",
      picks: [
        { name: "Cocktail-Shaker-Set", desc: "Macht jeden Drink zum Event.", q: "Cocktail Shaker Set Edelstahl" },
        { name: "Coupé-/Cocktailgläser", desc: "Edel und wiederverwendbar.", q: "Sektglaeser Coupe Set" },
        { name: "Getränkespender", desc: "Self-Service für Batch-Cocktails.", q: "Getraenkespender mit Zapfhahn" },
        { name: "Cocktail-Sirup-Set", desc: "Im Handumdrehen neue Drinks.", q: "Cocktail Sirup Set" },
        { name: "Eiswürfelform XXL", desc: "Eis ist immer zuerst leer.", q: "Eiswuerfelform gross Silikon" }
      ]
    },
    {
      key: "snacks",
      name: "Snacks",
      emoji: "🍫",
      blurb: "Grazing-Boards, süße Häppchen und Popcorn ohne Ende.",
      img: IMG + "hf_20260616_102544_022496d0-9c73-4514-b18b-c66f4a3e3c95.png",
      guide: "posts/girls-night-snacks.html",
      picks: [
        { name: "Servierbrett (groß)", desc: "Die Basis für ein Grazing-Board.", q: "Servierbrett Holz gross" },
        { name: "Etagere", desc: "Macht aus Snacks ein Buffet.", q: "Etagere Servierstaender" },
        { name: "Dip-Schalen-Set", desc: "Süß, salzig, alles getrennt.", q: "Dip Schalen Set" },
        { name: "Popcornmaschine", desc: "Frisches Popcorn für den Filmabend.", q: "Popcornmaschine Heissluft" },
        { name: "Pralinen-Geschenkbox", desc: "Das süße Highlight.", q: "Pralinen Geschenkbox" }
      ]
    },
    {
      key: "themes",
      name: "Deko & Themes",
      emoji: "🎀",
      blurb: "Ballon-Girlanden, Lichterketten und ein hübsch gedeckter Tisch.",
      img: IMG + "hf_20260616_102545_a44fca4f-758a-4f44-b4b9-a88dc762ba52.png",
      guide: "posts/girls-night-themes.html",
      picks: [
        { name: "Luftballon-Girlande (Set)", desc: "Der Foto-Hintergrund des Abends.", q: "Luftballon Girlande Set rosa" },
        { name: "LED-Lichterkette warmweiß", desc: "Sofort gemütliche Stimmung.", q: "LED Lichterkette warmweiss innen" },
        { name: "Discokugel / Partylicht", desc: "Macht jeden Raum zur Tanzfläche.", q: "Discokugel LED Partylicht" },
        { name: "LED-Neonschild", desc: "Wirkt wie eine echte Location.", q: "LED Neonschild Wand" },
        { name: "Konfetti & Tischdeko", desc: "Die schnellen 5-Minuten-Akzente.", q: "Tischdeko Set Party rosa" }
      ]
    },
    {
      key: "pamper",
      name: "Pflege & Spa",
      emoji: "💅",
      blurb: "Gesichtsmasken, Bademäntel und ein Spa-Moment für daheim.",
      img: IMG + "hf_20260616_102526_b6c7850b-e9ee-4a5a-bf6d-b94f8de50618.png",
      guide: "posts/girls-night-pamper-spa.html",
      picks: [
        { name: "Gesichtsmasken-Set", desc: "Der Spa-Klassiker für alle.", q: "Gesichtsmasken Set Tuchmasken" },
        { name: "Spa-Stirnband & Scrunchies", desc: "Bequem und süß auf Fotos.", q: "Spa Stirnband Set" },
        { name: "Nagellack-Set", desc: "Mani-Pedi-Station für daheim.", q: "Nagellack Set" },
        { name: "Fußbad / Fußpflege-Set", desc: "Wellness bis in die Zehen.", q: "Fussbad Set Wellness" },
        { name: "Duftkerzen-Set", desc: "Die richtige Stimmung & Duft.", q: "Duftkerzen Set" }
      ]
    },
    {
      key: "movie",
      name: "Filmabend",
      emoji: "🎬",
      blurb: "Ein Beamer, kuschelige Decken und eine große Schüssel Popcorn.",
      img: IMG + "hf_20260616_102543_f5bfd8f6-713c-4afb-9c14-d0cef07ebcaa.png",
      guide: "posts/girls-night-movie-night.html",
      picks: [
        { name: "Mini-Beamer (Full HD)", desc: "Macht das Wohnzimmer zum Kino.", q: "Mini Beamer Full HD" },
        { name: "Kuscheldecken (weich, groß)", desc: "Das gemütliche Nest.", q: "Kuscheldecke weich gross" },
        { name: "Popcorn-Schalen-Set", desc: "Weil Popcorn Pflicht ist.", q: "Popcorn Schalen Set" },
        { name: "Sitzsack / Bodenkissen", desc: "Extra Plätze zum Lümmeln.", q: "Sitzsack gross" },
        { name: "Sternenhimmel-Projektor", desc: "Stimmungslicht für den Filmabend.", q: "Sternenhimmel Projektor LED" }
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
          '">Zum kompletten ' +
          esc(cat.name) +
          "-Guide →</a>" +
          "</div>" +
          "</article>"
      );
      grid.appendChild(card);
    });
  }

  document.addEventListener("DOMContentLoaded", render);
})();
