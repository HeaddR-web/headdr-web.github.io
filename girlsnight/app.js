/* Girls Night HQ — "Build your night" gamification engine.
   Pure static JS + localStorage. No backend, no tracking.
   Affiliate links use the Amazon Associates tag cozylore-21. */
(function () {
  "use strict";

  var AFF_TAG = "cozylore-21";
  var STORE_KEY = "girlsnight.plan.v1";

  // Amazon search affiliate link builder (no fake product names / prices).
  function amz(query) {
    return (
      "https://www.amazon.de/s?k=" +
      encodeURIComponent(query) +
      "&tag=" +
      AFF_TAG
    );
  }

  // Category data — covers (Higgsfield glam images), guides and curated picks.
  var IMG =
    "https://d8j0ntlcm91z4.cloudfront.net/user_3EzQWq2PztIpmRyoVyluIhbJYPZ/";

  var CATEGORIES = [
    {
      key: "games",
      name: "Games",
      emoji: "🎲",
      blurb: "Ice-breakers, party card games and a little friendly chaos.",
      img: IMG + "hf_20260615_161819_184c86f8-7b13-4286-9ae9-d22eba7d4181.png",
      guide: "posts/girls-night-games.html",
      picks: [
        { id: "g1", name: "Party card game (adults)", q: "party card game adults" },
        { id: "g2", name: "Truth or dare / conversation game", q: "truth or dare game adults" },
        { id: "g3", name: "Drinking game set", q: "drinking game set" }
      ]
    },
    {
      key: "drinks",
      name: "Drinks",
      emoji: "🍸",
      blurb: "Signature cocktails, bubbly and everything to pour them in.",
      img: IMG + "hf_20260615_161820_622fbb45-9400-4dd4-b1df-c391b1d7f91f.png",
      guide: "posts/girls-night-drinks.html",
      picks: [
        { id: "d1", name: "Cocktail shaker set", q: "cocktail shaker set" },
        { id: "d2", name: "Champagne / cocktail glasses", q: "champagne coupe glasses set" },
        { id: "d3", name: "Cocktail mixer kit", q: "cocktail mixer syrup set" }
      ]
    },
    {
      key: "snacks",
      name: "Snacks",
      emoji: "🍫",
      blurb: "Grazing boards, sweet treats and bottomless popcorn.",
      img: IMG + "hf_20260615_163559_030a2811-cea7-4dd4-8262-e40dd10832dc.jpeg",
      guide: "posts/girls-night-snacks.html",
      picks: [
        { id: "s1", name: "Grazing / charcuterie board", q: "grazing board serving platter" },
        { id: "s2", name: "Popcorn maker", q: "popcorn maker" },
        { id: "s3", name: "Chocolate gift box", q: "chocolate gift box" }
      ]
    },
    {
      key: "themes",
      name: "Deko & Themes",
      emoji: "🎀",
      blurb: "Balloon arches, neon glow and a sparkly themed table.",
      img: IMG + "hf_20260615_163600_b85fc10c-37e0-42c4-8ae9-38bdedfaabaf.jpeg",
      guide: "posts/girls-night-themes.html",
      picks: [
        { id: "t1", name: "Pink balloon arch kit", q: "pink balloon arch kit" },
        { id: "t2", name: "Disco ball / party lights", q: "disco ball party light" },
        { id: "t3", name: "LED neon sign", q: "led neon sign room" }
      ]
    },
    {
      key: "pamper",
      name: "Pamper & Spa",
      emoji: "💅",
      blurb: "Face masks, robes and a full at-home spa moment.",
      img: IMG + "hf_20260615_161824_657729c5-d58b-4150-8616-4615a11f2173.png",
      guide: "posts/girls-night-pamper-spa.html",
      picks: [
        { id: "p1", name: "Face mask set", q: "face mask set skincare" },
        { id: "p2", name: "Spa headband + scrunchies", q: "spa headband set" },
        { id: "p3", name: "Nail polish set", q: "nail polish set" }
      ]
    },
    {
      key: "movie",
      name: "Movie Night",
      emoji: "🎬",
      blurb: "A projector, cosy blankets and a big bowl of popcorn.",
      img: IMG + "hf_20260615_161825_5ce93708-e414-43a1-b0cc-df3c561765b7.jpeg",
      guide: "posts/girls-night-movie-night.html",
      picks: [
        { id: "m1", name: "Mini projector", q: "mini projector" },
        { id: "m2", name: "Soft throw blankets", q: "soft throw blanket" },
        { id: "m3", name: "Popcorn bowl set", q: "popcorn bowl set" }
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
          '">Read the full ' +
          esc(cat.name) +
          " guide →</a>" +
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
        '<div class="empty">Your night is empty so far. Tap <b>+ Add</b> on the picks above to start building your shopping list. ✨</div>';
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
          ? "Pick from each category to plan the perfect night."
          : done === total
          ? "Your night is fully planned — go grab the list! 🎉"
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
    toast("Added to your night ✨");
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
    if (!confirm("Clear your whole night?")) return;
    plan = [];
    save(plan);
    refresh();
    toast("Cleared");
  }
  function copyList() {
    if (!plan.length) return;
    var lines = ["My Girls Night HQ list:", ""];
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
    lines.push("Built at https://headdr-web.github.io/girlsnight/");
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
