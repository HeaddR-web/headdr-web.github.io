/* Watch Party HQ — "Build your watch party" gamification engine.
   Pure static JS + localStorage. No backend, no tracking.
   Affiliate links use the Amazon Associates tag cozylore-21. */
(function () {
  "use strict";

  var AFF_TAG = "cozylore-21";
  var STORE_KEY = "watchparty.plan.v1";

  // Amazon search affiliate link builder (no fake product names / prices).
  function amz(query) {
    return (
      "https://www.amazon.de/s?k=" +
      encodeURIComponent(query) +
      "&tag=" +
      AFF_TAG
    );
  }

  // Shared Higgsfield image base (reuses the beige hosting covers for visual consistency).
  var IMG =
    "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/";

  var CATEGORIES = [
    {
      key: "setup",
      name: "Screen & Setup",
      emoji: "📺",
      blurb: "Big picture, big sound — turn the living room into a stadium.",
      img: IMG + "hf_20260616_102543_f5bfd8f6-713c-4afb-9c14-d0cef07ebcaa.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { id: "u1", name: "Mini projector (Full HD)", q: "Mini Beamer Full HD" },
        { id: "u2", name: "Projector screen", q: "Beamer Leinwand 100 Zoll" },
        { id: "u3", name: "Bluetooth soundbar", q: "Soundbar Bluetooth TV" }
      ]
    },
    {
      key: "food",
      name: "Food & Snacks",
      emoji: "🌮",
      blurb: "Nachos, wings and finger food everyone can grab without missing a goal.",
      img: IMG + "hf_20260616_102544_022496d0-9c73-4514-b18b-c66f4a3e3c95.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { id: "f1", name: "Snack & dip serving bowls", q: "Snackschalen Set Party" },
        { id: "f2", name: "Tortilla chips (big pack)", q: "Tortilla Chips Grosspackung" },
        { id: "f3", name: "Hot dog maker", q: "Hot Dog Maker" }
      ]
    },
    {
      key: "drinks",
      name: "Drinks",
      emoji: "🍺",
      blurb: "Cold beer, soft drinks and a self-serve station so you stay on the sofa.",
      img: IMG + "hf_20260616_102525_a7a5a55a-e9b5-4787-9af4-e8c7d02ea6c7.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { id: "d1", name: "Drinks cooler box", q: "Getraenkekuehler Box gross" },
        { id: "d2", name: "Table beer dispenser", q: "Bier Zapfanlage Tisch" },
        { id: "d3", name: "Reusable party cups", q: "Partybecher Set wiederverwendbar" }
      ]
    },
    {
      key: "decor",
      name: "Deko & Deutschland-Fan-Gear",
      emoji: "🇩🇪",
      blurb: "German flags, black-red-gold bunting and fan gear that make it match day.",
      img: IMG + "hf_20260616_102545_a44fca4f-758a-4f44-b4b9-a88dc762ba52.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { id: "k1", name: "Germany flag (large)", q: "Deutschland Fahne gross" },
        { id: "k2", name: "Black-red-gold bunting", q: "Wimpelkette Deutschland schwarz rot gold" },
        { id: "k3", name: "Germany fan kit (scarf, face paint, car flags)", q: "Deutschland Fan Set WM" }
      ]
    },
    {
      key: "games",
      name: "Sweepstake & Games",
      emoji: "🏆",
      blurb: "A wall chart, a sweepstake and a table game for half-time.",
      img: IMG + "hf_20260616_102523_ca7d067e-7c56-4964-9625-687b5f931af3.png",
      guide: "posts/world-cup-watch-party.html",
      picks: [
        { id: "g1", name: "Wall chart / fixture poster", q: "Fussball Spielplan Poster" },
        { id: "g2", name: "Tabletop football game", q: "Tischkicker Tisch" },
        { id: "g3", name: "Party card game", q: "Kartenspiel Party lustig" }
      ]
    }
  ];

  // Flat lookup of every pick by id.
  var PICKS = {};
  CATEGORIES.forEach(function (cat) {
    cat.picks.forEach(function (p) {
      PICKS[p.id] = { id: p.id, name: p.name, q: p.q, cat: cat.key, catName: cat.name };
    });
  });

  // ---- state ----
  function load() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      var arr = raw ? JSON.parse(raw) : [];
      return Array.isArray(arr) ? arr.filter(function (id) { return PICKS[id]; }) : [];
    } catch (e) {
      return [];
    }
  }
  function save(arr) {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(arr));
    } catch (e) {}
  }
  var plan = load();

  function has(id) {
    return plan.indexOf(id) !== -1;
  }
  function plannedCategories() {
    var set = {};
    plan.forEach(function (id) {
      set[PICKS[id].cat] = true;
    });
    return Object.keys(set);
  }

  // ---- rendering ----
  function el(html) {
    var d = document.createElement("div");
    d.innerHTML = html.trim();
    return d.firstChild;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function renderBuild() {
    var grid = document.getElementById("build-grid");
    if (!grid) return;
    grid.innerHTML = "";
    var planned = plannedCategories();
    CATEGORIES.forEach(function (cat) {
      var isPlanned = planned.indexOf(cat.key) !== -1;
      var picksHtml = cat.picks
        .map(function (p) {
          var added = has(p.id);
          return (
            '<li>' +
            '<span class="pick-name">' +
            esc(p.name) +
            '<br><a href="' +
            amz(p.q) +
            '" rel="sponsored nofollow" target="_blank">view on Amazon →</a></span>' +
            '<button class="add-btn' +
            (added ? " added" : "") +
            '" data-pick="' +
            p.id +
            '">' +
            (added ? "✓ Added" : "+ Add") +
            "</button>" +
            "</li>"
          );
        })
        .join("");
      var card = el(
        '<article class="cat-card' +
          (isPlanned ? " is-planned" : "") +
          '" data-cat="' +
          cat.key +
          '">' +
          '<div class="cover" style="background-image:url(\'' +
          cat.img +
          "')\">" +
          '<span class="done">✓ Planned</span>' +
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
          '">Read the full watch-party guide →</a>' +
          "</div>" +
          "</article>"
      );
      grid.appendChild(card);
    });
  }

  function renderMyNight() {
    var wrap = document.getElementById("mynight-body");
    if (!wrap) return;
    if (!plan.length) {
      wrap.innerHTML =
        '<div class="empty">Your watch party is empty so far. Tap <b>+ Add</b> on the picks above to start building your shopping list. ⚽</div>';
      return;
    }
    var html = "";
    CATEGORIES.forEach(function (cat) {
      var items = cat.picks.filter(function (p) {
        return has(p.id);
      });
      if (!items.length) return;
      html += '<div class="group"><h3>' + cat.emoji + " " + esc(cat.name) + "</h3><ul>";
      items.forEach(function (p) {
        html +=
          '<li><span class="name">' +
          esc(p.name) +
          '</span><span class="actions">' +
          '<a class="shop" href="' +
          amz(p.q) +
          '" rel="sponsored nofollow" target="_blank">Shop →</a>' +
          '<button class="remove" data-remove="' +
          p.id +
          '" aria-label="Remove">×</button>' +
          "</span></li>";
      });
      html += "</ul></div>";
    });
    html +=
      '<div class="toolbar">' +
      '<button class="btn-ghost" id="copy-list">📋 Copy my list</button>' +
      '<button class="btn-ghost" id="clear-list">Clear all</button>' +
      "</div>" +
      '<p class="tiny">Saved on this device only. As an Amazon Associate we earn from qualifying purchases — at no extra cost to you.</p>';
    wrap.innerHTML = html;
  }

  function updateTracker() {
    var total = CATEGORIES.length;
    var done = plannedCategories().length;
    var pct = Math.round((done / total) * 100);
    var bar = document.getElementById("bar-fill");
    if (bar) bar.style.width = pct + "%";
    var lbl = document.getElementById("tracker-count");
    if (lbl) lbl.textContent = done + "/" + total;
    var hint = document.getElementById("tracker-hint");
    if (hint) {
      hint.textContent =
        done === 0
          ? "Pick from each category to plan the perfect match day."
          : done === total
          ? "Your watch party is fully planned — go grab the list! 🎉"
          : "Nice — " + (total - done) + " categories to go.";
    }
    var navc = document.getElementById("nav-count");
    if (navc) navc.textContent = plan.length;
  }

  function refresh() {
    renderBuild();
    renderMyNight();
    updateTracker();
  }

  // ---- toast ----
  var toastTimer;
  function toast(msg) {
    var t = document.getElementById("toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      t.classList.remove("show");
    }, 1800);
  }

  // ---- actions ----
  function addPick(id) {
    if (!PICKS[id] || has(id)) return;
    plan.push(id);
    save(plan);
    refresh();
    toast("Added to your watch party ⚽");
  }
  function removePick(id) {
    var i = plan.indexOf(id);
    if (i === -1) return;
    plan.splice(i, 1);
    save(plan);
    refresh();
  }
  function clearAll() {
    if (!plan.length) return;
    if (!confirm("Clear your whole watch party?")) return;
    plan = [];
    save(plan);
    refresh();
    toast("Cleared");
  }
  function copyList() {
    if (!plan.length) return;
    var lines = ["My Watch Party HQ list:", ""];
    CATEGORIES.forEach(function (cat) {
      var items = cat.picks.filter(function (p) {
        return has(p.id);
      });
      if (!items.length) return;
      lines.push(cat.emoji + " " + cat.name);
      items.forEach(function (p) {
        lines.push("  - " + p.name + " — " + amz(p.q));
      });
      lines.push("");
    });
    lines.push("Built at https://headdr-web.github.io/watchparty/");
    var text = lines.join("\n");
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () {
          toast("List copied 📋");
        },
        function () {
          window.prompt("Copy your list:", text);
        }
      );
    } else {
      window.prompt("Copy your list:", text);
    }
  }

  // ---- delegated events ----
  document.addEventListener("click", function (e) {
    var addBtn = e.target.closest("[data-pick]");
    if (addBtn) {
      addPick(addBtn.getAttribute("data-pick"));
      return;
    }
    var rm = e.target.closest("[data-remove]");
    if (rm) {
      removePick(rm.getAttribute("data-remove"));
      return;
    }
    if (e.target.id === "clear-list") clearAll();
    if (e.target.id === "copy-list") copyList();
  });

  document.addEventListener("DOMContentLoaded", refresh);
})();
