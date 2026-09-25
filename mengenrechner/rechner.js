/*
 * Party-Mengenrechner - rechnet aus Anlass, Gaestezahl und Dauer eine
 * Einkaufsliste. Alle Faustregeln stehen hier an einer Stelle (ANLAESSE,
 * GETRAENKE, EIS, GESCHIRR); der Text der Seite erklaert dieselben Zahlen.
 * Wer hier eine Regel aendert, aendert sie auch im Abschnitt "So rechnet
 * der Mengenrechner" - sonst rechnet das Werkzeug anders als die Seite sagt.
 *
 * Laedt nichts nach, setzt keine Cookies, speichert nichts. Der Zustand steht
 * nur in der URL (?anlass=grill&gaeste=12...), damit man eine Liste teilen kann.
 */
(function () {
  "use strict";

  // ---------- Faustregeln ------------------------------------------------
  // Mengen je "Esser": Erwachsene zaehlen 1, Kinder 0,5.
  // f(p) bekommt { esser, fleisch, veg, stunden } und liefert die Menge.
  var ANLAESSE = {
    grill: {
      name: "Grillabend",
      seite: "/grillabend/",
      teller: 2,
      alkoholAnteil: 1,
      mix: { bier: 0.6, wein: 0.3, sekt: 0.1 },
      essen: [
        { was: "Grillgut Fleisch & Würstchen (roh)", g: function (p) { return 300 * p.fleisch; } },
        { was: "Vegetarisches Grillgut (Halloumi, Gemüsespieße, Veggie-Würstchen)", g: function (p) { return 300 * p.veg; } },
        { was: "Grillgemüse & Maiskolben für alle", g: function (p) { return 100 * p.esser; } },
        { was: "Salate & Beilagen (2–3 Sorten)", g: function (p) { return 250 * p.esser; } },
        { was: "Brot & Baguette", g: function (p) { return 80 * p.esser; }, pack: [250, "Baguette"] },
        { was: "Grillsaucen & Dips", ml: function (p) { return 50 * p.esser; }, pack: [250, "Glas"] },
        { was: "Nachtisch (Obst, Eis)", g: function (p) { return 100 * p.esser; } },
        { was: "Grillkohle oder Briketts", g: function (p) { return Math.max(2500, 400 * p.esser); }, pack: [3000, "Sack à 3 kg"], ohnePuffer: true }
      ]
    },
    garten: {
      name: "Gartenparty mit Buffet",
      seite: "/gartenparty/",
      teller: 2,
      alkoholAnteil: 1,
      mix: { bier: 0.4, wein: 0.4, sekt: 0.2 },
      essen: [
        { was: "Fingerfood & Häppchen", st: function (p) { return (12 + 2 * Math.max(0, p.stunden - 3)) * p.esser; } },
        { was: "Salate", g: function (p) { return 150 * p.esser; } },
        { was: "Brot & Baguette", g: function (p) { return 60 * p.esser; }, pack: [250, "Baguette"] },
        { was: "Dips & Aufstriche", ml: function (p) { return 50 * p.esser; }, pack: [250, "Glas"] },
        { was: "Knabberzeug", g: function (p) { return 50 * p.esser; }, pack: [175, "Tüte"] },
        { was: "Obst & Dessert", g: function (p) { return 150 * p.esser; } }
      ]
    },
    brunch: {
      name: "Brunch",
      seite: "/brunch/",
      teller: 2,
      alkoholAnteil: 0.4,
      mix: { sekt: 1 },
      kaffee: 2.5,
      essen: [
        { was: "Brötchen & Croissants", st: function (p) { return 2 * p.esser; } },
        { was: "Aufschnitt & Käse", g: function (p) { return 120 * p.esser; } },
        { was: "Eier", st: function (p) { return 1.5 * p.esser; }, pack: [10, "Zehnerpackung"] },
        { was: "Butter", g: function (p) { return 20 * p.esser; }, pack: [250, "Stück à 250 g"] },
        { was: "Marmelade, Honig & Aufstriche", g: function (p) { return 30 * p.esser; } },
        { was: "Obst", g: function (p) { return 150 * p.esser; } },
        { was: "Joghurt & Müsli", g: function (p) { return 100 * p.esser; } }
      ]
    },
    geburtstag: {
      name: "Geburtstag zuhause",
      seite: "/geburtstag/",
      teller: 3,
      alkoholAnteil: 1,
      mix: { bier: 0.4, wein: 0.35, sekt: 0.25 },
      kaffee: 2,
      essen: [
        { was: "Kuchen & Torte (Stücke)", st: function (p) { return 1.5 * p.esser; }, pack: [12, "Kuchen à 12 Stück"] },
        { was: "Fingerfood & Häppchen fürs Abendbuffet", st: function (p) { return 10 * p.esser; } },
        { was: "Salate", g: function (p) { return 150 * p.esser; } },
        { was: "Brot & Baguette", g: function (p) { return 60 * p.esser; }, pack: [250, "Baguette"] },
        { was: "Dips & Aufstriche", ml: function (p) { return 40 * p.esser; }, pack: [250, "Glas"] }
      ]
    },
    cocktail: {
      name: "Cocktailabend",
      seite: "/cocktailabend/",
      teller: 1,
      alkoholAnteil: 1,
      mix: { cocktail: 0.85, sekt: 0.15 },
      eisExtra: 0.7,
      essen: [
        { was: "Nüsse, Chips & Knabberzeug", g: function (p) { return 80 * p.esser; }, pack: [175, "Tüte"] },
        { was: "Fingerfood", st: function (p) { return 6 * p.esser; } },
        { was: "Dips", ml: function (p) { return 40 * p.esser; }, pack: [250, "Glas"] }
      ]
    },
    spiele: {
      name: "Spiele- oder Filmabend",
      seite: "/spieleabend/",
      teller: 1,
      alkoholAnteil: 0.8,
      mix: { bier: 0.6, wein: 0.4 },
      essen: [
        { was: "Chips & Knabberzeug", g: function (p) { return 100 * p.esser; }, pack: [175, "Tüte"] },
        { was: "Süßes & Schokolade", g: function (p) { return 60 * p.esser; } },
        { was: "Popcorn-Mais", g: function (p) { return 25 * p.esser; }, pack: [500, "Packung à 500 g"] },
        { was: "Dips", ml: function (p) { return 50 * p.esser; }, pack: [250, "Glas"] },
        { was: "Fingerfood (optional, falls es kein Abendessen gibt)", st: function (p) { return 4 * p.esser; } }
      ]
    },
    maedels: {
      name: "Mädelsabend",
      seite: "/girlsnight/",
      teller: 1,
      alkoholAnteil: 1,
      mix: { wein: 0.55, sekt: 0.45 },
      essen: [
        { was: "Käse fürs Grazing-Board", g: function (p) { return 80 * p.esser; } },
        { was: "Salami & Schinken", g: function (p) { return 50 * p.esser; } },
        { was: "Cracker, Grissini & Brot", g: function (p) { return 60 * p.esser; } },
        { was: "Trauben, Beeren & Obst", g: function (p) { return 120 * p.esser; } },
        { was: "Nüsse & Oliven", g: function (p) { return 40 * p.esser; } },
        { was: "Schokolade & Süßes", g: function (p) { return 40 * p.esser; } },
        { was: "Dips & Aufstriche", ml: function (p) { return 40 * p.esser; }, pack: [250, "Glas"] }
      ]
    },
    fussball: {
      name: "WM- oder Fußball-Party",
      seite: "/watchparty/",
      teller: 1,
      alkoholAnteil: 1,
      mix: { bier: 0.85, wein: 0.15 },
      essen: [
        { was: "Würstchen oder Hotdogs", st: function (p) { return 1.5 * p.esser; } },
        { was: "Herzhaftes Fingerfood (Mini-Pizzen, Frikadellen, Wraps)", st: function (p) { return 8 * p.esser; } },
        { was: "Chips & Knabberzeug", g: function (p) { return 100 * p.esser; }, pack: [175, "Tüte"] },
        { was: "Dips", ml: function (p) { return 50 * p.esser; }, pack: [250, "Glas"] }
      ]
    }
  };

  // Getraenke in "Runden": in der ersten Stunde zwei Getraenke pro Person,
  // danach eins pro Stunde. Bei Hitze 30 Prozent mehr.
  var HITZE_FAKTOR = 1.3;
  var ALKOHOL_ANTEIL = { normal: 0.5, wenig: 0.25, kein: 0 };
  var KINDER_FAKTOR = 0.8; // Kinder trinken etwas weniger, nur alkoholfrei
  var GLAS_ALKOHOLFREI_L = 0.3;
  var GETRAENKE = {
    bier: { was: "Bier (0,5-l-Flaschen)", proRunde: 1, flasche: 1, kasten: 20 },
    wein: { was: "Wein (0,75-l-Flaschen)", proRunde: 1, flasche: 5 },
    sekt: { was: "Sekt oder Prosecco (0,75-l-Flaschen)", proRunde: 1, flasche: 7 },
    cocktail: { was: "Cocktails", proRunde: 1 }
  };
  var COCKTAIL = { spirituoseCl: 5, flascheCl: 70, fillerL: 0.12, limettenJe: 0.5, sirupMl: 20 };
  var EIS_KG = { normal: 0.25, hitze: 0.5 };
  var PUFFER = 1.1;

  // ---------- Hilfsfunktionen ---------------------------------------------
  function zahl(x, stellen) {
    return x.toLocaleString("de-DE", { maximumFractionDigits: stellen || 0 });
  }
  function aufrunden(x, schritt) {
    return Math.ceil(x / schritt - 1e-9) * schritt;
  }
  function gramm(g) {
    if (g >= 1000) return zahl(aufrunden(g, 100) / 1000, 1) + " kg";
    return zahl(aufrunden(g, 50)) + " g";
  }
  function milli(ml) {
    if (ml >= 1000) return zahl(aufrunden(ml, 100) / 1000, 1) + " l";
    return zahl(aufrunden(ml, 50)) + " ml";
  }
  function liter(l) {
    return zahl(aufrunden(l, 0.5), 1) + " l";
  }
  function stueck(n) {
    return zahl(Math.ceil(n - 1e-9)) + " Stück";
  }
  function packungen(menge, pack) {
    var n = Math.ceil(menge / pack[0] - 1e-9);
    return "≈ " + n + " × " + pack[1];
  }

  // ---------- Rechnen ------------------------------------------------------
  function rechne(e) {
    var a = ANLAESSE[e.anlass];
    var gaeste = e.erwachsene + e.kinder;
    var esser = e.erwachsene + 0.5 * e.kinder;
    var veg = Math.min(e.veg, e.erwachsene + e.kinder);
    var vegEsser = Math.min(veg, esser);
    var p = { esser: esser, fleisch: Math.max(0, esser - vegEsser), veg: vegEsser, stunden: e.stunden };
    var puffer = e.puffer ? PUFFER : 1;
    var gruppen = [];

    // Essen
    var essen = [];
    a.essen.forEach(function (it) {
      var f = it.ohnePuffer ? 1 : puffer;
      var menge, text;
      if (it.g) { menge = it.g(p) * f; text = gramm(menge); }
      else if (it.ml) { menge = it.ml(p) * f; text = milli(menge); }
      else { menge = it.st(p) * f; text = stueck(menge); }
      if (menge <= 0) return;
      essen.push({ was: it.was, menge: text, hinweis: it.pack ? packungen(menge, it.pack) : "" });
    });
    gruppen.push({ titel: "Essen", zeilen: essen });

    // Getraenke
    var runden = e.stunden + 1;
    var hitze = e.hitze ? HITZE_FAKTOR : 1;
    // Der Hitze-Aufschlag geht komplett ins Alkoholfreie: wer schwitzt,
    // trinkt mehr Wasser, nicht mehr Bier.
    var rundenErw = e.erwachsene * runden * puffer;
    var anteil = ALKOHOL_ANTEIL[e.alkohol] * a.alkoholAnteil;
    var alkRunden = rundenErw * anteil;
    var freiRunden = rundenErw * hitze - alkRunden + e.kinder * runden * KINDER_FAKTOR * hitze * puffer;
    var getraenke = [];
    var cocktails = 0;
    Object.keys(a.mix).forEach(function (sorte) {
      var n = alkRunden * a.mix[sorte];
      if (n <= 0) return;
      var g = GETRAENKE[sorte];
      if (sorte === "cocktail") { cocktails = n; return; }
      var flaschen = Math.ceil(n / g.flasche - 1e-9);
      var hinweis = g.kasten && flaschen >= g.kasten
        ? "≈ " + zahl(flaschen / g.kasten, 1) + " Kästen à " + g.kasten
        : "für rund " + zahl(Math.round(n)) + " Gläser";
      getraenke.push({ was: g.was, menge: flaschen + (flaschen === 1 ? " Flasche" : " Flaschen"), hinweis: hinweis });
    });
    if (cocktails > 0) {
      var c = Math.ceil(cocktails - 1e-9);
      var spirit = c * COCKTAIL.spirituoseCl;
      getraenke.push({ was: "Cocktails insgesamt", menge: c + " Drinks", hinweis: "Rezepte vorher festlegen, 2–3 Sorten reichen" });
      getraenke.push({ was: "Spirituosen (Rum, Gin, Tequila …)", menge: (function (n) { return n + (n === 1 ? " Flasche" : " Flaschen") + " à 0,7 l"; })(Math.ceil(spirit / COCKTAIL.flascheCl)), hinweis: zahl(spirit / 100, 2) + " l bei 5 cl pro Drink" });
      getraenke.push({ was: "Filler (Soda, Tonic, Saft)", menge: liter(c * COCKTAIL.fillerL), hinweis: "" });
      getraenke.push({ was: "Limetten", menge: stueck(c * COCKTAIL.limettenJe), hinweis: "" });
      getraenke.push({ was: "Zuckersirup", menge: milli(c * COCKTAIL.sirupMl), hinweis: "" });
    }
    var freiL = freiRunden * GLAS_ALKOHOLFREI_L;
    getraenke.push({ was: "Wasser, still & sprudelnd", menge: liter(freiL * 0.5), hinweis: "≈ " + Math.ceil(freiL * 0.5 / 1.5 - 1e-9) + " × 1,5-l-Flasche" });
    getraenke.push({ was: "Softdrinks, Saft & Schorle", menge: liter(freiL * 0.5), hinweis: "≈ " + Math.ceil(freiL * 0.5 / 1.5 - 1e-9) + " × 1,5-l-Flasche" });
    if (a.kaffee) {
      var tassen = gaeste * a.kaffee * puffer;
      getraenke.push({ was: "Kaffee", menge: Math.ceil(tassen) + " Tassen", hinweis: gramm(tassen * 8) + " Pulver, " + liter(gaeste * 0.1) + " Milch" });
    }
    gruppen.push({ titel: "Getränke", zeilen: getraenke });

    // Eis & Kuehlung
    var eisKg = gaeste * (e.hitze ? EIS_KG.hitze : EIS_KG.normal) + (a.eisExtra || 0) * e.erwachsene;
    gruppen.push({ titel: "Eis & Kühlung", zeilen: [
      { was: "Eiswürfel", menge: zahl(Math.ceil(eisKg)) + " kg", hinweis: "≈ " + Math.ceil(eisKg / 2 - 1e-9) + " × Beutel à 2 kg" }
    ] });

    // Geschirr & Verbrauch
    var glaeser = gaeste * 2 + (a.mix.sekt ? gaeste : 0);
    gruppen.push({ titel: "Geschirr & Verbrauchsmaterial", zeilen: [
      { was: "Teller", menge: stueck(gaeste * a.teller), hinweis: a.teller > 1 ? a.teller + " pro Gast (herzhaft, Nachtisch" + (a.teller > 2 ? ", Kuchen" : "") + ")" : "" },
      { was: "Gläser", menge: stueck(glaeser), hinweis: "Gläser werden abgestellt und vergessen, deshalb 2 pro Gast" },
      { was: "Besteck-Sets", menge: stueck(gaeste * 1.5), hinweis: "" },
      { was: "Servietten", menge: stueck(gaeste * 3), hinweis: "" },
      { was: "Müllbeutel (60 l)", menge: stueck(Math.ceil(gaeste / 8) + 1), hinweis: "einer für Pfand/Glas extra" }
    ] });

    return { anlass: a, gaeste: gaeste, gruppen: gruppen };
  }

  // ---------- Formular & Ausgabe ------------------------------------------
  var form = document.getElementById("rechner-form");
  var ziel = document.getElementById("rechner-ergebnis");
  if (!form || !ziel) return;

  function ganz(name, min, max, standard) {
    var v = parseInt(form.elements[name].value, 10);
    if (isNaN(v)) v = standard;
    return Math.min(max, Math.max(min, v));
  }

  function eingaben() {
    return {
      anlass: ANLAESSE[form.elements.anlass.value] ? form.elements.anlass.value : "grill",
      erwachsene: ganz("erwachsene", 1, 200, 10),
      kinder: ganz("kinder", 0, 100, 0),
      veg: ganz("veg", 0, 200, 0),
      stunden: ganz("stunden", 1, 12, 4),
      alkohol: ALKOHOL_ANTEIL.hasOwnProperty(form.elements.alkohol.value) ? form.elements.alkohol.value : "normal",
      hitze: form.elements.hitze.checked,
      puffer: form.elements.puffer.checked
    };
  }

  function el(tag, klasse, text) {
    var n = document.createElement(tag);
    if (klasse) n.className = klasse;
    if (text != null) n.textContent = text;
    return n;
  }

  var letzte = null;

  function zeige() {
    var e = eingaben();
    var r = rechne(e);
    letzte = { e: e, r: r };
    ziel.textContent = "";

    var kopf = el("p", "rl-kopf");
    kopf.textContent = r.anlass.name + " · " + r.gaeste + (r.gaeste === 1 ? " Gast" : " Gäste") +
      " · " + e.stunden + (e.stunden === 1 ? " Stunde" : " Stunden") + (e.puffer ? " · inkl. 10 % Puffer" : "");
    ziel.appendChild(kopf);

    r.gruppen.forEach(function (g) {
      ziel.appendChild(el("h3", "rl-gruppe", g.titel));
      var ul = el("ul", "rl-liste");
      g.zeilen.forEach(function (z) {
        var li = el("li");
        var links = el("span", "rl-was", z.was);
        var rechts = el("span", "rl-menge", z.menge);
        li.appendChild(links);
        li.appendChild(rechts);
        if (z.hinweis) li.appendChild(el("span", "rl-hinweis", z.hinweis));
        ul.appendChild(li);
      });
      ziel.appendChild(ul);
    });

    var weiter = el("p", "rl-weiter");
    weiter.appendChild(document.createTextNode("Deko, Spiele und Ausstattung für den Anlass: "));
    var a = el("a", null, r.anlass.name + " planen →");
    a.href = r.anlass.seite;
    weiter.appendChild(a);
    ziel.appendChild(weiter);

    // Zustand in die URL, damit der Link die Liste mitnimmt.
    try {
      var q = new URLSearchParams(location.search);
      q.set("anlass", e.anlass); q.set("gaeste", e.erwachsene); q.set("kinder", e.kinder);
      q.set("veg", e.veg); q.set("stunden", e.stunden); q.set("alkohol", e.alkohol);
      q.set("hitze", e.hitze ? "1" : "0"); q.set("puffer", e.puffer ? "1" : "0");
      history.replaceState(null, "", location.pathname + "?" + q.toString() + location.hash);
    } catch (err) { /* aeltere Browser: dann eben ohne Teilen-Link */ }
  }

  function ausUrl() {
    var q;
    try { q = new URLSearchParams(location.search); } catch (err) { return; }
    var setze = function (feld, wert) { if (wert != null && form.elements[feld]) form.elements[feld].value = wert; };
    if (q.get("anlass") && ANLAESSE[q.get("anlass")]) setze("anlass", q.get("anlass"));
    setze("erwachsene", q.get("gaeste"));
    setze("kinder", q.get("kinder"));
    setze("veg", q.get("veg"));
    setze("stunden", q.get("stunden"));
    if (ALKOHOL_ANTEIL.hasOwnProperty(q.get("alkohol"))) setze("alkohol", q.get("alkohol"));
    if (q.get("hitze") != null) form.elements.hitze.checked = q.get("hitze") === "1";
    if (q.get("puffer") != null) form.elements.puffer.checked = q.get("puffer") === "1";
  }

  function alsText() {
    if (!letzte) return "";
    var zeilen = ["Einkaufsliste – " + ziel.querySelector(".rl-kopf").textContent, ""];
    letzte.r.gruppen.forEach(function (g) {
      zeilen.push(g.titel.toUpperCase());
      g.zeilen.forEach(function (z) {
        zeilen.push("☐ " + z.was + ": " + z.menge + (z.hinweis ? " (" + z.hinweis + ")" : ""));
      });
      zeilen.push("");
    });
    zeilen.push("Berechnet mit dem Party-Mengenrechner: " + location.href);
    return zeilen.join("\n");
  }

  function meldung(text) {
    var m = document.getElementById("rechner-meldung");
    if (!m) return;
    m.textContent = text;
    window.setTimeout(function () { m.textContent = ""; }, 3000);
  }

  function kopiere(text, ok) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { meldung(ok); }, function () { meldung("Kopieren ging nicht – bitte markieren und kopieren."); });
    } else {
      meldung("Kopieren ging nicht – bitte markieren und kopieren.");
    }
  }

  form.addEventListener("input", zeige);
  form.addEventListener("change", zeige);
  form.addEventListener("submit", function (ev) { ev.preventDefault(); zeige(); });

  var knopfDruck = document.getElementById("rechner-drucken");
  var knopfKopie = document.getElementById("rechner-kopieren");
  var knopfTeilen = document.getElementById("rechner-teilen");
  if (knopfDruck) knopfDruck.addEventListener("click", function () { window.print(); });
  if (knopfKopie) knopfKopie.addEventListener("click", function () { kopiere(alsText(), "Liste kopiert – z. B. in WhatsApp oder die Notizen-App einfügen."); });
  if (knopfTeilen) knopfTeilen.addEventListener("click", function () {
    if (navigator.share) {
      navigator.share({ title: "Unsere Party-Einkaufsliste", url: location.href }).catch(function () {});
    } else {
      kopiere(location.href, "Link kopiert – wer ihn öffnet, sieht genau diese Liste.");
    }
  });

  document.documentElement.classList.add("rechner-js");
  ausUrl();
  zeige();
})();
