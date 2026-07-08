/*
 * BeThatHost / Cozylore — Cookie-Consent-Layer (Vanilla JS, keine Abhaengigkeiten).
 *
 * Rechtsgrundlage: Art. 13 DSGVO, § 25 TDDDG (frueher § 15 TMG / TTDSG) — fuer
 * nicht technisch notwendige Dienste (Werbung, Social-Media-Einbindungen) ist
 * eine informierte, freiwillige, vorab eingeholte Einwilligung noetig, bevor
 * die Skripte laden und Cookies/IDs setzen.
 *
 * Verhalten:
 *  - Ohne gespeicherte Entscheidung: Banner mit zwei GLEICHWERTIGEN Buttons
 *    ("Nur notwendige" / "Akzeptieren"), kein Nudging, keine Vorauswahl.
 *  - "Akzeptieren": AdSense (adsbygoogle.js) + Pinterest (pinit.js) werden erst
 *    JETZT per Script-Injection nachgeladen.
 *  - "Nur notwendige": beide Skripte bleiben ungeladen.
 *  - Entscheidung liegt in localStorage (rein geraetelokal, keine Uebertragung
 *    an einen Server) und kann jederzeit ueber window.bthOpenConsentSettings()
 *    widerrufen/geaendert werden (siehe Footer-Link "Cookie-Einstellungen").
 */
(function () {
  "use strict";

  var STORAGE_KEY = "bth_consent";
  var ADSENSE_SRC =
    "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4473022510510415";
  var PINTEREST_SRC = "https://assets.pinterest.com/js/pinit.js";
  var BANNER_ID = "bth-consent-banner";
  var STYLE_ID = "bth-consent-style";

  function getConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setConsent(value) {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ value: value, ts: new Date().toISOString() })
      );
    } catch (e) {
      /* localStorage nicht verfuegbar (z. B. Privatmodus) — dann kein Speichern moeglich */
    }
  }

  function loadScriptOnce(src, attrs) {
    if (document.querySelector('script[src="' + src + '"]')) return;
    var s = document.createElement("script");
    s.src = src;
    s.async = true;
    for (var k in attrs) {
      if (Object.prototype.hasOwnProperty.call(attrs, k)) s.setAttribute(k, attrs[k]);
    }
    document.head.appendChild(s);
  }

  function activate() {
    loadScriptOnce(ADSENSE_SRC, { crossorigin: "anonymous" });
    loadScriptOnce(PINTEREST_SRC, { "data-pin-hover": "true" });
  }

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    var style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent =
      "#" + BANNER_ID + "{position:fixed;left:0;right:0;bottom:0;z-index:9999;" +
      "background:#241f1a;color:#f7f1e8;font-family:system-ui,-apple-system,sans-serif;" +
      "box-shadow:0 -4px 24px rgba(0,0,0,.25);}" +
      "#" + BANNER_ID + " .bth-consent-inner{max-width:960px;margin:0 auto;padding:16px 20px;" +
      "display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;}" +
      "#" + BANNER_ID + " .bth-consent-text{flex:1 1 320px;margin:0;font-size:.92rem;line-height:1.5;}" +
      "#" + BANNER_ID + " .bth-consent-text a{color:#f2c9b9;text-decoration:underline;}" +
      "#" + BANNER_ID + " .bth-consent-actions{display:flex;gap:10px;flex:0 0 auto;flex-wrap:wrap;}" +
      "#" + BANNER_ID + " .bth-consent-btn{font:inherit;font-size:.92rem;font-weight:600;" +
      "padding:10px 18px;border-radius:10px;border:1px solid #f7f1e8;background:transparent;" +
      "color:#f7f1e8;cursor:pointer;min-width:150px;}" +
      "#" + BANNER_ID + " .bth-consent-btn:hover{background:rgba(247,241,232,.12);}";
    document.head.appendChild(style);
  }

  function removeBanner() {
    var el = document.getElementById(BANNER_ID);
    if (el) el.parentNode.removeChild(el);
  }

  function renderBanner() {
    if (document.getElementById(BANNER_ID)) return;
    ensureStyles();
    var wrap = document.createElement("div");
    wrap.id = BANNER_ID;
    wrap.setAttribute("role", "dialog");
    wrap.setAttribute("aria-label", "Cookie-Einstellungen");
    wrap.innerHTML =
      '<div class="bth-consent-inner">' +
      '<p class="bth-consent-text">Wir nutzen Cookies bzw. Dienste von Drittanbietern (Werbung, Pinterest). ' +
      "Diese laden erst, wenn du zustimmst. Details in unserer " +
      '<a href="/datenschutz.html">Datenschutzerklärung</a>.</p>' +
      '<div class="bth-consent-actions">' +
      '<button type="button" class="bth-consent-btn" data-choice="necessary">Nur notwendige</button>' +
      '<button type="button" class="bth-consent-btn" data-choice="all">Akzeptieren</button>' +
      "</div></div>";
    document.body.appendChild(wrap);

    wrap.addEventListener("click", function (ev) {
      var btn = ev.target.closest ? ev.target.closest("[data-choice]") : null;
      if (!btn) return;
      var choice = btn.getAttribute("data-choice");
      setConsent(choice);
      removeBanner();
      if (choice === "all") activate();
    });
  }

  function init() {
    var consent = getConsent();
    if (consent && consent.value === "all") {
      activate();
    } else if (!consent) {
      renderBanner();
    }
    // consent.value === "necessary": bewusst nichts laden.
  }

  // Oeffentliche Funktion fuer den Widerrufs-/Aendern-Link (Footer, Datenschutzerklaerung).
  window.bthOpenConsentSettings = function () {
    renderBanner();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
