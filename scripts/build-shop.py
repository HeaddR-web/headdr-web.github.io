"""Schreibt den Shop ins Repo: die Startseite ist der Shop, dazu zwei Produktseiten (Stefanie, 02.11.2026).
Ziel: Shop für eigene 3D-Druck-Teile, verkauft über Etsy. Motto "alles kann individualisiert werden" ist die H1 der Startseite.
Aufbau wie ein Shopify-Shop: Produktraster, Produktseite mit Bild links, Farbwahl, Namensvorschau und Akkordeon.
Aufbau aus Richtung A "Schicht für Schicht", Farbe und Schrift seit 02.11.2026 "Salbei" mit Bricolage Grotesque.
Die Druck-Animation läuft nur noch klein im Produktbild.
Nur Platzhalter: keine Preise, keine Fotos, keine Etsy-Links. Die Teile sind gezeichnet, die Farben Beispiele.
Impressum und Datenschutz bekommen Kopf und Fuß des Shops, ihr Rechtstext bleibt Zeichen für Zeichen, wie er ist.
Das CSS aus assets/style.css steht eingebettet im Kopf jeder Seite, eine Änderung dort wirkt erst nach einem Lauf hier.
Shop-HTML nur hier ändern, nie von Hand im Repo.
Aufruf: python3 scripts/build-shop.py [--pruefen]
--pruefen schreibt nichts und endet mit 1, wenn eine Seite nicht zum Generator passt
(Konsistenz-Check Punkt 22, fängt eine Änderung an style.css ohne Generatorlauf)."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Pfad im Repo -> fertiges HTML, geschrieben oder verglichen wird erst am Ende
AUSGABE = {}
BASIS = "https://bethathost.de"

# Pinterest-Bestätigung der Domain: stand auf der alten Startseite, der Wert kommt aus dem Impressum
_pinterest = re.search(r'<meta name="p:domain_verify" content="[0-9a-f]+"\s*/?>',
                       (REPO / "impressum.html").read_text(encoding="utf-8"))
if not _pinterest:
    raise SystemExit("p:domain_verify fehlt im Impressum, Startseite nicht gebaut")
PINTEREST = "\n    " + _pinterest.group(0)

# Tempo auf dem Handy (Gate R13, 02.11.2026): das CSS steht im Kopf statt als blockierende Datei.
# Quelle bleibt assets/style.css, dazu nur die @font-face-Blöcke der Schriften, die style.css nennt.
_css = (REPO / "assets/style.css").read_text(encoding="utf-8")
_schriften = [b for b in re.findall(r"@font-face\s*\{[^}]*\}",
                                    (REPO / "assets/fonts/fonts.css").read_text(encoding="utf-8"))
              if re.search(r'font-family:\s*("[^"]+")', b).group(1) in _css
              and ("italic" not in b or "italic" in _css)]
STIL = "    <style>\n" + "\n".join(_schriften) + "\n" + _css + "    </style>"

# Platzhalter für die Pflichtangaben nach Art. 19 GPSR, wird mit dem echten Listing zur Liste
GPSR = ("Hersteller, Postanschrift, E-Mail, Produktkennung und Sicherheitshinweise stehen hier, "
        "sobald das Etsy-Listing steht.")
HERSTELLUNG = ("Herstellung", "entworfen von BeThatHost, gedruckt bei einem 3D-Druck-Partner, "
               "von uns selbst versendet")
PREIS = "Preis folgt"
PREIS_HINWEIS = "Endpreis, Versand laut Etsy-Listing"


# Ein Hinweis unter dem Kaufknopf statt dreier verstreuter (Kritiker Runde 1, 02.11.2026)
def hinweis(angabe):
    return ('<p class="shop-etsy-hinweis">Das Bild ist gezeichnet und die Farben sind Beispiele, Fotos und echte '
            'Farben folgen nach dem Musterdruck. Sobald das Etsy-Listing steht, führt der Knopf dorthin, '
            f'{angabe} gibst du dort bei der Bestellung an.</p>')


# Beispielfarben bis zum Musterdruck: Name, Grundfarbe, dunkle Schichtlinie, Text auf dem Anhänger
SPULEN = [
    ("Waldgrün", "#2f5d46", "#24493a", "#f7f6f1d9"),
    ("Salbei", "#9fb59a", "#7f9a7a", "#0000008c"),
    ("Kreide", "#f7f6f1", "#cfcabd", "#0000008c"),
    ("Sand", "#d9c7a3", "#b9a57f", "#0000008c"),
    ("Rosé", "#e8b4b0", "#c98f8a", "#0000008c"),
]

DISPLAY = '"Bricolage Grotesque", "Arial Narrow", sans-serif'


def schichten(id_, abstand, fest=None):
    """Füllmuster mit Schichtlinien, die Farben kommen per CSS aus --teil und --teil-dunkel.
    Mit fest (Grund, Linie) bleiben sie fest: Musterinhalte erben keine Variablen der Gruppe, die sie nutzt."""
    farbe, linie = fest or ("#2f5d46", "#24493a")
    k_farbe, k_linie = ("", "") if fest else (' class="t-farbe"', ' class="t-linie"')
    return (f'<pattern id="{id_}" width="8" height="{abstand}" patternUnits="userSpaceOnUse">'
            f'<rect{k_farbe} width="8" height="{abstand}" fill="{farbe}"/>'
            f'<rect{k_linie} y="{abstand - 1}" width="8" height="1" fill="{linie}"/></pattern>')


def hell(farbe):
    """Helle Oberseite des Sockels, wie color-mix(in srgb, Farbe 78%, #fff) im CSS."""
    return "#" + "".join(f"{round(int(farbe[i:i + 2], 16) * 0.78 + 255 * 0.22):02x}" for i in (1, 3, 5))


def groesse(name, maximal, feld, faktor):
    """Schriftgröße, bei der der Name in die Fläche passt. Dieselbe Formel rechnet das Skript beim Tippen."""
    return min(maximal, feld / (len(name) * faktor))


def name_text(name, maximal, feld, faktor, x, y, fill, klasse="t-name", mitte=None):
    """data-y ist die Grundlinie für eine Zeile, data-mitte die Mitte, um die das Skript zwei Zeilen setzt."""
    return (f'<text class="{klasse}" x="{x}" y="{y}" text-anchor="middle" font-family=\'{DISPLAY}\' '
            f'font-size="{groesse(name, maximal, feld, faktor):.1f}" font-weight="800" fill="{fill}" '
            f'data-max="{maximal}" data-feld="{feld}" data-faktor="{faktor}" data-y="{y}" data-mitte="{mitte}">{name}</text>')


def duese(x, y):
    """Druckkopf: die Gruppe steigt Lage für Lage, der Block darin fährt je Lage einmal quer (--weg)."""
    return f'<g class="t-duese"><rect class="t-kopf" x="{x}" y="{y}" width="12" height="6" rx="1.5" fill="#1d2420"/></g>'


def druck_attr(druck):
    # data-druck: gedruckt wird erst im Fenster (DRUCKSTART), ohne Skript steht der Name fertig da
    return ' data-druck=""' if druck else ""


def probe_attr(probe, name, gross=False):
    # data-probe: hier schreibt das Namensfeld hinein, leer steht wieder der Beispielname da
    if not probe:
        return ""
    return f' data-probe="{name}"' + (' data-gross=""' if gross else "")


VERLAUF = ('<linearGradient id="{}k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffdf8"/>'
           '<stop offset="1" stop-color="#f1ebe0"/></linearGradient>')


# Im Bild druckt sich der Name Lage für Lage: eine Maske wächst von unten, die Düse fährt mit nach oben
# Keine Tischnummer auf der Karte: in kleinen Karten lag sie unter 14 px (Gate R5, 02.11.2026)
def halter(id_, name="Lena", druck=True, probe=False):
    return f"""<svg class="shop-svg-halter"{druck_attr(druck)}{probe_attr(probe, name)} viewBox="0 0 300 230" aria-hidden="true" focusable="false">
              <defs>{schichten(id_, 4)}{VERLAUF.format(id_)}
                <mask id="{id_}d" maskUnits="userSpaceOnUse" x="-86" y="0" width="172" height="128"><rect class="t-druck" x="-86" y="42" width="172" height="42" fill="#fff"/></mask></defs>
              <ellipse cx="150" cy="214" rx="132" ry="10" fill="#000" opacity="0.10"/>
              <g transform="translate(150 40) skewX(-4)">
                <rect x="-86" y="0" width="172" height="128" rx="3" fill="url(#{id_}k)" stroke="#00000014"/>
                <g mask="url(#{id_}d)">{name_text(name, 34, 150, 0.52, 0, 74, "#2a2420", mitte=62)}</g>
                {duese(-80, 78)}
              </g>
              <path class="t-hell" d="M30 168 L270 168 L282 182 L18 182 Z" fill="#5d816f"/>
              <rect x="18" y="182" width="264" height="28" rx="3" fill="url(#{id_})"/>
              <rect x="58" y="166" width="184" height="5" rx="2" fill="#00000030"/>
            </svg>"""


# Startseite: drei Halter wie auf einem gedeckten Tisch, sie drucken nacheinander (Kritiker Runde 1, 02.11.2026).
# Je Halter: Name, Lage im Bild, Maßstab, Verzögerung, Beispielfarbe. Tom steht vorn und wird zuletzt gezeichnet.
# Tom nimmt den Probenamen und ist deshalb etwas größer, sonst bräche am Handy schon ein Name mit neun Buchstaben um.
REIHE = [("Lena", 70, 0, 0.62, 0, SPULEN[0]), ("Oma", 344, 0, 0.62, 0.35, SPULEN[4]),
         ("Tom", 192, 78, 0.72, 0.7, SPULEN[3])]


def halter_reihe(id_, druck=True, probe=False):
    teile = []
    vorn = len(REIHE) - 1
    for i, (name, tx, ty, mass, verzug, (_, grund, dunkel, _t)) in enumerate(REIHE):
        teile.append(f"""<g transform="translate({tx} {ty}) scale({mass})" style="--verzug: {verzug}s"{probe_attr(probe and i == vorn, name)}>
                <mask id="{id_}d{i}" maskUnits="userSpaceOnUse" x="-86" y="0" width="172" height="128"><rect class="t-druck" x="-86" y="34" width="172" height="62" fill="#fff"/></mask>
                <ellipse cx="150" cy="214" rx="132" ry="10" fill="#000" opacity="0.10"/>
                <g transform="translate(150 40) skewX(-4)">
                  <rect x="-86" y="0" width="172" height="128" rx="3" fill="url(#{id_}k)" stroke="#00000014"/>
                  <g mask="url(#{id_}d{i})">{name_text(name, 64, 150, 0.52, 0, 88, "#2a2420", mitte=65)}</g>
                  {duese(-80, 90)}
                </g>
                <path d="M30 168 L270 168 L282 182 L18 182 Z" fill="{hell(grund)}"/>
                <rect x="18" y="182" width="264" height="28" rx="3" fill="url(#{id_}s{i})"/>
                <rect x="58" y="166" width="184" height="5" rx="2" fill="#00000030"/>
              </g>""")
    muster = "".join(schichten(f"{id_}s{i}", 4, (s[1], s[2])) for i, (*_, s) in enumerate(REIHE))
    return f"""<svg class="shop-svg-reihe"{druck_attr(druck)} viewBox="70 12 460 228" aria-hidden="true" focusable="false">
              <defs>{muster}{VERLAUF.format(id_)}</defs>
              {(chr(10) + '              ').join(teile)}
            </svg>"""


def anhaenger(id_, name="BRAUT", druck=True, probe=False):
    # Der Ring läuft durch die Bohrung: hinten ganz, vorn nur der obere Teil über dem Anhänger
    ring = '<circle cx="58" cy="40" r="30" fill="none" stroke="url(#{0}m)" stroke-width="5"{1}/>'
    return f"""<svg class="shop-svg-anhaenger"{druck_attr(druck)}{probe_attr(probe, name, gross=True)} viewBox="0 0 260 120" aria-hidden="true" focusable="false">
              <defs>{schichten(id_, 3)}<linearGradient id="{id_}m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f2f2f2"/><stop offset=".5" stop-color="#9a9a9a"/><stop offset="1" stop-color="#dcdcdc"/></linearGradient>
                <clipPath id="{id_}c"><rect x="0" y="0" width="260" height="59"/></clipPath>
                <mask id="{id_}d" maskUnits="userSpaceOnUse" x="96" y="24" width="150" height="70"><rect class="t-druck" x="96" y="42" width="150" height="38" fill="#fff"/></mask></defs>
              <ellipse cx="140" cy="108" rx="110" ry="7" fill="#000" opacity="0.10"/>
              {ring.format(id_, "")}
              <rect x="50" y="24" width="196" height="70" rx="35" fill="url(#{id_})"/>
              <circle cx="80" cy="59" r="9" fill="#00000026"/>
              {ring.format(id_, f' clip-path="url(#{id_}c)"')}
              <g mask="url(#{id_}d)">{name_text(name, 30, 140, 0.6, 164, 70, "#24493a", "t-name t-linie", mitte=60)}
                {name_text(name, 30, 140, 0.6, 163, 69, "#f7f6f1d9", "t-name t-text", mitte=59)}</g>
              {duese(98, 74)}
            </svg>"""


def spulen():
    knoepfe = "\n".join(
        f'              <button type="button" class="shop-spule" aria-pressed="{"true" if i == 0 else "false"}" '
        f'data-farbe="{name}" data-teil="{f}" data-dunkel="{d}" data-text="{t}" style="--c: {f}"><i></i>{name}</button>'
        for i, (name, f, d, t) in enumerate(SPULEN))
    return f"""            <div class="shop-option" role="group" aria-labelledby="farbe-titel">
              <p class="shop-option-kopf"><span id="farbe-titel">Farbe</span> <span id="farbe-wahl" class="shop-wahl">{SPULEN[0][0]}</span></p>
              <div class="shop-spulen-reihe">
{knoepfe}
              </div>
            </div>"""


def probefeld(f, klasse="shop-option"):
    """Namensfeld, das ins Bild schreibt. Wohin, sagen die Stellen mit data-probe, nicht das Feld."""
    return f"""            <div class="{klasse}">
              <label class="shop-option-kopf" for="probe-name">{f['label']}</label>
              <input class="shop-feld" id="probe-name" type="text" maxlength="{f['max']}" value="{f['wert']}" autocomplete="off" spellcheck="false" enterkeyhint="done" aria-describedby="probe-hilfe" />
              <p class="shop-hilfe" id="probe-hilfe">{f['hilfe']}</p>
            </div>"""


# Startseite: ein Feld für den vorderen Halter und den Anhänger, deshalb nur so lang, wie der Anhänger erlaubt
# (Stefanie 03.11.2026). Leer, damit Feld und Bild nicht verschiedene Beispielnamen zeigen.
START_PROBE = {"label": "Name zum Ausprobieren", "wert": "", "max": 10,
               "hilfe": "Der Name erscheint auf dem vorderen Halter und auf dem Anhänger, bis zu 10 Zeichen. Gespeichert wird nichts."}


# Farbwahl färbt das Teil um, das Namensfeld schreibt den Namen in jede Stelle mit data-probe.
# Beides druckt neu, aber nur die Stelle selbst: in der Reihe der Startseite bleiben Lena und Oma stehen.
SKRIPT = """    <script>
      (function () {
        var ruhig = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var stellen = document.querySelectorAll("[data-probe]");
        function neu(s) {
          var teile = s.querySelectorAll(".t-druck, .t-duese, .t-kopf");
          s.style.setProperty("--verzug", "0s");
          Array.prototype.forEach.call(teile, function (t) { t.style.animation = "none"; });
          void s.getBoundingClientRect();
          Array.prototype.forEach.call(teile, function (t) { t.style.animation = ""; });
        }
        function imFenster(bild) {
          var r = bild.getBoundingClientRect();
          return r.bottom > 0 && r.top < window.innerHeight;
        }
        // Liegt ein gedrucktes Bild gerade außerhalb des Fensters, druckt es den neuen Namen erst beim Hinscrollen,
        // sonst liefe der Neudruck ungesehen ab (Kritiker Runde 1, 03.11.2026)
        var wartend = [], spaeter = "IntersectionObserver" in window && new IntersectionObserver(function (eintraege) {
          eintraege.forEach(function (e) {
            if (!e.isIntersecting) return;
            spaeter.unobserve(e.target);
            wartend = wartend.filter(function (s) {
              if ((s.ownerSVGElement || s) !== e.target) return true;
              neu(s);
              return false;
            });
          });
        }, { threshold: 0.4 });
        function nachdrucken(s) {
          if (ruhig) return;
          var bild = s.ownerSVGElement || s;
          // Noch nie gedruckt: was gerade zu sehen ist, druckt jetzt ganz, der Rest wartet auf DRUCKSTART beim Hinscrollen
          if (!bild.classList.contains("druckt")) {
            if (imFenster(bild)) bild.classList.add("druckt");
            return;
          }
          if (spaeter && !imFenster(bild)) {
            if (wartend.indexOf(s) < 0) wartend.push(s);
            spaeter.observe(bild);
            return;
          }
          wartend = wartend.filter(function (x) { return x !== s; });
          neu(s);
        }
        function alleNachdrucken() {
          Array.prototype.forEach.call(stellen, nachdrucken);
        }
        // Weitertippen in einen laufenden Neudruck: anhalten, damit der neue Name ganz dasteht, bis die Pause um ist.
        // Nur Bilder, die schon gedruckt haben, ein wartendes Bild weiter unten druckt sonst beim Hinscrollen nicht mehr.
        function anhalten(s) {
          if (ruhig || !(s.ownerSVGElement || s).classList.contains("druckt")) return;
          Array.prototype.forEach.call(s.querySelectorAll(".t-druck, .t-duese, .t-kopf"), function (t) { t.style.animation = "none"; });
        }
        var knoepfe = document.querySelectorAll(".shop-spule"), wahl = document.getElementById("farbe-wahl");
        Array.prototype.forEach.call(knoepfe, function (k) {
          k.addEventListener("click", function () {
            if (k.getAttribute("aria-pressed") === "true") return;
            Array.prototype.forEach.call(knoepfe, function (x) { x.setAttribute("aria-pressed", x === k ? "true" : "false"); });
            var s = document.body.style;
            s.setProperty("--teil", k.dataset.teil);
            s.setProperty("--teil-dunkel", k.dataset.dunkel);
            s.setProperty("--teil-text", k.dataset.text);
            if (wahl) wahl.textContent = k.dataset.farbe;
            alleNachdrucken();
          });
        });
        var feld = document.getElementById("probe-name"), warte, rahmen;
        if (!feld || !stellen.length) return;
        function breiteVon(t) {
          var zeilen = t.querySelectorAll("tspan"), l = 0;
          if (!zeilen.length) return t.getComputedTextLength();
          Array.prototype.forEach.call(zeilen, function (z) { l = Math.max(l, z.getComputedTextLength()); });
          return l;
        }
        // Die Schätzung nimmt eine mittlere Zeichenbreite, breite Buchstaben wie W sprengen sie. Deshalb nachmessen.
        function einpassen(t, g, breite) {
          t.setAttribute("font-size", g.toFixed(1));
          var l = breiteVon(t);
          if (l > breite) {
            g = Math.floor(g * breite / l * 10) / 10;
            t.setAttribute("font-size", g.toFixed(1));
          }
          return g;
        }
        // Läge der Name auf dem Bildschirm unter 14 px, steht er in zwei Zeilen (Kritiker Runde 1, 02.11.2026)
        function schreiben(t, w) {
          var breite = +t.dataset.feld, faktor = +t.dataset.faktor, max = +t.dataset.max;
          t.textContent = w;
          t.setAttribute("y", t.dataset.y);
          var g = einpassen(t, Math.min(max, breite / (w.length * faktor)), breite);
          // Die Hover-Anhebung der Karte steckt mit in getScreenCTM, sie zählt nicht, sonst stünde der Name danach unter 14 px
          var m = t.getScreenCTM(), svg = t.ownerSVGElement, r = svg.getBoundingClientRect();
          var anhebung = svg.clientWidth && r.width ? r.width / svg.clientWidth : 1;
          var boden = m ? 14.5 * anhebung / Math.hypot(m.a, m.b) : 0;
          if (g >= boden || w.length < 2) return;
          // Die Schätzung rechnet eher zu breit. Passt der Name mit 14,5 px gemessen in die Fläche, bleibt er einzeilig.
          if (breiteVon(t) * boden / g <= breite) {
            t.setAttribute("font-size", boden.toFixed(1));
            return;
          }
          // Trennstellen: Leerzeichen und nach einem Bindestrich, sonst Silben vor dem letzten Mitlaut vor einem
          // Selbstlaut (Maxi-milian, Wil-helmina), ch, ck, ph, th und sch bleiben zusammen (Ste-phan, Mi-scha)
          var laut = /[aeiouyäöü]/i, mitlaut = /[b-df-hj-np-tv-xzß]/i, mitte = Math.ceil(w.length / 2);
          function baustein(i) {
            var r = w.slice(i, i + 3).toLowerCase();
            return r === "sch" ? 3 : /^(ch|ck|ph|th)/.test(r) ? 2 : 1;
          }
          var orte = [{ teile: [w.slice(0, mitte) + "-", w.slice(mitte)], mitte: true }];
          for (var i = 1; i < w.length; i++) {
            if (w[i] === " ") orte.push({ teile: [w.slice(0, i), w.slice(i + 1)], frei: true });
            else if (w[i - 1] === "-" && i > 1) orte.push({ teile: [w.slice(0, i), w.slice(i)], frei: true });
            else if (mitlaut.test(w[i]) && laut.test(w.slice(0, i)) && laut.test(w[i + baustein(i)] || "")
                     && baustein(i - 1) === 1 && (i < 2 || baustein(i - 2) < 3)) orte.push({ teile: [w.slice(0, i) + "-", w.slice(i)] });
          }
          function zeilen(teile) {
            t.textContent = "";
            // Namensraum vom Textfeld, eine ausgeschriebene Adresse hielte der Fremd-Host-Wächter für einen Abruf
            teile.forEach(function (s) {
              var z = document.createElementNS(t.namespaceURI, "tspan");
              z.setAttribute("x", t.getAttribute("x"));
              z.textContent = s;
              t.appendChild(z);
            });
          }
          // Jede Trennstelle wird mit 14,5 px gemessen. Vorn steht, was passt, erst Leerzeichen und Bindestrich, dann Silben,
          // die Mitte im Wort nur als Notlösung. Bei gleichem Rang gewinnt die schmalere, passt keine, auch.
          function rang(k) { return k.passt ? (k.frei ? 0 : k.mitte ? 2 : 1) : 3; }
          t.setAttribute("font-size", boden.toFixed(1));
          var beste = null;
          orte.forEach(function (k) {
            zeilen(k.teile);
            k.l = breiteVon(t);
            k.passt = k.l <= breite;
            if (!beste || rang(k) < rang(beste) || (rang(k) === rang(beste) && k.l < beste.l)) beste = k;
          });
          var teile = beste.teile;
          zeilen(teile);
          g = einpassen(t, Math.min(max, breite / (Math.max(teile[0].length, teile[1].length) * faktor)), breite);
          if (g < boden) {
            g = boden;
            t.setAttribute("font-size", g.toFixed(1));
          }
          // Passt selbst die beste Trennung mit 14,5 px nicht (zehn breite Versalien am kleinsten Handy),
          // wird die Zeile schmaler statt kleiner
          Array.prototype.forEach.call(t.querySelectorAll("tspan"), function (z) {
            if (z.getComputedTextLength() <= breite) return;
            z.setAttribute("textLength", breite);
            z.setAttribute("lengthAdjust", "spacingAndGlyphs");
          });
          var c = +t.dataset.mitte, z = t.querySelectorAll("tspan");
          z[0].setAttribute("y", (c - 0.165 * g).toFixed(1));
          z[1].setAttribute("y", (c + 0.885 * g).toFixed(1));
        }
        // Druckmaske und Düse folgen dem Namen, damit auch zwei Zeilen ganz gedruckt werden
        function anpassen(s, texte) {
          var oben = Infinity, unten = -Infinity, maske = s.querySelector(".t-druck"), kopf = s.querySelector(".t-kopf");
          Array.prototype.forEach.call(texte, function (t) {
            var b = t.getBBox();
            oben = Math.min(oben, b.y);
            unten = Math.max(unten, b.y + b.height);
          });
          if (!isFinite(oben) || !maske) return;
          var y = oben - 2, h = unten - oben + 4;
          maske.setAttribute("y", y.toFixed(1));
          maske.setAttribute("height", h.toFixed(1));
          if (kopf) kopf.setAttribute("y", (y + h - 6).toFixed(1));
          s.style.setProperty("--hub", -h.toFixed(1) + "px");
        }
        function setzen() {
          var eingabe = feld.value.replace(/\\s+/g, " ").trim();
          Array.prototype.forEach.call(stellen, function (s) {
            var w = eingabe || s.dataset.probe, texte = s.querySelectorAll(".t-name");
            if (s.hasAttribute("data-gross")) w = w.toUpperCase();
            Array.prototype.forEach.call(texte, function (t) { schreiben(t, w); });
            anpassen(s, texte);
          });
        }
        feld.addEventListener("input", function () {
          Array.prototype.forEach.call(stellen, anhalten);
          setzen();
          clearTimeout(warte);
          warte = setTimeout(alleNachdrucken, 300);
        });
        window.addEventListener("resize", function () {
          cancelAnimationFrame(rahmen);
          rahmen = requestAnimationFrame(setzen);
        });
        setzen();
        // Erst mit der echten Schrift stimmt die Messung, vorher misst der Browser die Ersatzschrift
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(setzen);
      })();
    </script>
"""

# Gedruckt wird erst, wenn das Bild ins Fenster kommt, sonst wäre die Startseiten-Reihe unten schon fertig
DRUCKSTART = """    <script>
      (function () {
        var bilder = document.querySelectorAll("svg[data-druck]");
        if (!("IntersectionObserver" in window)) {
          Array.prototype.forEach.call(bilder, function (b) { b.classList.add("druckt"); });
          return;
        }
        var beobachter = new IntersectionObserver(function (eintraege) {
          eintraege.forEach(function (e) {
            if (!e.isIntersecting) return;
            e.target.classList.add("druckt");
            beobachter.unobserve(e.target);
          });
        }, { threshold: 0.4 });
        Array.prototype.forEach.call(bilder, function (b) { beobachter.observe(b); });
      })();
    </script>
"""

PRODUKTE = [
    {
        "slug": "platzkartenhalter",
        "titel": "Platzkartenhalter mit Namen",
        "kurz": "Platzkartenhalter",
        "satz": "Ein Halter je Gast, mit dem Namen gedruckt. Für Hochzeit und Geburtstag.",
        "seitentitel": "Platzkartenhalter mit Namen",
        "beschreibung": "Platzkartenhalter mit Namen aus dem 3D-Drucker, für Hochzeit und Geburtstag. "
                        "Ansehen bei BeThatHost, bestellen über Etsy.",
        "daten": [("Anlass", "Hochzeit, Geburtstag"), ("Personalisierung", "ein Name je Halter"),
                  HERSTELLUNG],
        "offen": "Material, Maße und Set folgen nach dem Musterdruck.",
        "probe": {"label": "Name zum Ausprobieren", "wert": "Lena", "max": 14,
                  "hilfe": "Nur eine Vorschau, nichts wird gespeichert. Lange Namen bricht die Vorschau um, der Musterdruck zeigt, wie sie auf dem Halter stehen."},
        "angabe": "den Namen",
        "bild": lambda id_, druck=True, probe=False: halter(id_, druck=druck, probe=probe),
    },
    {
        "slug": "jga-anhaenger",
        "titel": "JGA-Anhänger im Set",
        "kurz": "JGA-Anhänger",
        "satz": "Schlüsselanhänger im Set für die ganze Gruppe beim Junggesellenabschied.",
        "seitentitel": "JGA-Anhänger im Set",
        "beschreibung": "JGA-Schlüsselanhänger im Set aus dem 3D-Drucker, für die ganze Gruppe. "
                        "Ansehen bei BeThatHost, bestellen über Etsy.",
        "daten": [("Anlass", "Junggesellenabschied"), HERSTELLUNG],
        "offen": "Personalisierung, Material, Maße und Set folgen nach dem Musterdruck. Geplant ist ein Ring aus Metall.",
        "probe": {"label": "Text zum Ausprobieren", "wert": "BRAUT", "max": 10,
                  "hilfe": "Nur eine Vorschau, nichts wird gespeichert. Wie viel Text auf den Anhänger passt, steht nach dem Musterdruck fest."},
        "angabe": "den Text",
        "bild": lambda id_, druck=True, probe=False: anhaenger(id_, druck=druck, probe=probe),
    },
]

SCHRITTE = [("Auf Etsy bestellen", "Im Etsy-Listing gibst du den Namen oder Text an, bezahlst und bekommst die Bestellbestätigung."),
            ("Druck und Versand", "Entworfen von BeThatHost, gedruckt bei einem 3D-Druck-Partner. Den Versand an dich übernehmen wir selbst.")]


def dl(paare):
    return ('<dl class="shop-daten">'
            + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in paare) + "</dl>")


def punkte():
    tupfer = "".join(f'<i style="--c: {f}"></i>' for _, f, _, _ in SPULEN)
    return f'<p class="shop-punkte"><span aria-hidden="true">{tupfer}</span>{len(SPULEN)} Beispielfarben</p>'


def karte(p, id_, ebene="h2", druck=True, quer=False, bild=None, probe=False, feld=""):
    """Produktkarte wie im Shop-Raster: Bild, Titel, Preis. Der Titel-Link deckt die ganze Karte ab,
    nur ein Feld unter dem Bild liegt darüber."""
    return f"""          <li class="shop-karte{' shop-karte-quer' if quer else ''}">
            <div class="shop-karte-bild">
              <span class="shop-chip">Gezeichnetes Muster</span>
              {bild or p['bild'](id_, druck, probe)}
            </div>
{feld + chr(10) if feld else ''}            <div class="shop-karte-text">
              <{ebene} class="shop-karte-titel"><a href="/shop/{p['slug']}.html">{p['titel']}</a></{ebene}>
              <p class="shop-karte-preis">{PREIS}</p>
              <p class="shop-karte-satz">{p['satz']}</p>
              {punkte()}
            </div>
          </li>"""


def ablauf():
    schritte = "\n".join(f'            <li><span class="shop-nr" aria-hidden="true">{i}</span><div><h3>{t}</h3><p>{x}</p></div></li>'
                         for i, (t, x) in enumerate(SCHRITTE, 1))
    return f"""      <section class="shop-ablauf" id="bestellung" aria-labelledby="ablauf">
        <div class="shop-innen shop-ablauf-streifen">
          <h2 id="ablauf">So läuft die Bestellung</h2>
          <ol class="shop-schritte">
{schritte}
          </ol>
          <p class="shop-ablauf-fuss">Herstellerangaben nach GPSR stehen bei jedem Produkt. Solange die Listings noch nicht stehen, sind sie Platzhalter.</p>
        </div>
      </section>"""


def nav(aktiv):
    return "\n".join(
        f'          <a href="/shop/{p["slug"]}.html"{" aria-current=\"page\"" if p["slug"] == aktiv else ""}>{p["kurz"]}</a>'
        for p in PRODUKTE)


def seite(pfad, url_pfad, titel, beschreibung, koerper, aktiv=None, skript="", kopf="", robots=None, titel_voll=None):
    # url_pfad None: Fehlerseite, ohne Canonical und nicht im Index
    if url_pfad is None:
        adresse = '    <meta name="robots" content="noindex" />'
    else:
        url = f"{BASIS}/{url_pfad}"
        adresse = f'    <link rel="canonical" href="{url}" />\n    <meta property="og:url" content="{url}" />'
        if robots:
            adresse += f'\n    <meta name="robots" content="{robots}" />'
    adresse += kopf
    html = f"""<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <title>{titel_voll or titel + " | BeThatHost"}</title>
    <meta
      name="description"
      content="{beschreibung}"
    />
{adresse}
    <meta property="og:title" content="{titel}" />
    <meta property="og:description" content="{beschreibung}" />
    <meta property="og:type" content="website" />
    <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/bricolage-grotesque-800.woff2" crossorigin />
    <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/hanken-grotesk.woff2" crossorigin />
    <script>document.documentElement.classList.add("js")</script>
{STIL}
  </head>
  <body class="shop">
    <a class="shop-sprung" href="#inhalt">Zum Inhalt</a>
    <header class="site">
      <div class="inner">
        <a class="brand" href="/">BeThatHost</a>
        <nav aria-label="Produkte">
{nav(aktiv)}
        </nav>
      </div>
    </header>

    <main id="inhalt" tabindex="-1">
{koerper}
    </main>

    <footer class="site">
      <div class="inner">
        <p>Bestellung und Bezahlung laufen über Etsy. Diese Seite hat keine eigene Kasse.</p>
        <p>© <span id="y"></span> BeThatHost · <a href="/impressum.html">Impressum</a> · <a href="/datenschutz.html">Datenschutz</a></p>
      </div>
    </footer>
    <script>
      document.getElementById("y").textContent = new Date().getFullYear();
    </script>
{DRUCKSTART}{skript}  </body>
</html>
"""
    AUSGABE[pfad] = html


# ---------- Startseite = Shop ----------
# Motto von Stefanie (02.11.2026): alles kann individualisiert werden
seite("index.html", "", "3D-Druck-Teile, individuell für dich",
      "Eigene Teile aus dem 3D-Drucker, jedes lässt sich individualisieren. "
      "Platzkartenhalter und JGA-Anhänger, hier ansehen und auf Etsy kaufen.",
      f"""      <section class="shop-kopf" aria-labelledby="titel">
        <div class="shop-innen shop-kopf-raster">
          <div>
            <p class="shop-mono">3D-Druck-Shop · {len(PRODUKTE)} Produkte</p>
            <h1 id="titel">Alles lässt sich individualisieren</h1>
          </div>
          <p class="shop-lead">Platzkartenhalter und JGA-Anhänger aus dem 3D-Drucker, mit deinem Namen oder Text darauf. BeThatHost entwirft die Teile selbst, individualisieren lässt sich jedes. Was draufsteht, gibst du bei der Bestellung auf Etsy an.</p>
        </div>
      </section>
      <section class="shop-sortiment" aria-label="Produkte">
        <div class="shop-innen">
          <ul class="shop-raster shop-raster-start">
{karte(PRODUKTE[0], "k0", bild=halter_reihe("k0", probe=True), feld=probefeld(START_PROBE, "shop-option shop-karte-probe"))}
{karte(PRODUKTE[1], "k1", probe=True)}
          </ul>
        </div>
      </section>
{ablauf()}""", kopf=PINTEREST, skript=SKRIPT)

# Fehlerseite: unbekannte Adressen zeigen gleich die Produkte, ohne Zeitschaltung
seite("404.html", None, "Seite nicht gefunden",
      "Diese Seite gibt es nicht mehr. Hier geht es weiter zum Shop für eigene Teile "
      "aus dem 3D-Drucker, jedes lässt sich individualisieren.",
      f"""      <section class="shop-kopf" aria-labelledby="titel">
        <div class="shop-innen shop-kopf-raster">
          <div>
            <p class="shop-mono">Fehler 404</p>
            <h1 id="titel">Diese Seite gibt es nicht mehr</h1>
          </div>
          <p class="shop-lead">Hier gibt es jetzt nur noch den Shop mit eigenen Teilen aus dem 3D-Drucker, jedes lässt sich individualisieren. <a href="/">Zur Startseite</a></p>
        </div>
      </section>
      <section class="shop-sortiment" aria-label="Produkte">
        <div class="shop-innen">
          <ul class="shop-raster shop-raster-eins shop-raster-fehler">
{chr(10).join(karte(p, f"f{i}", druck=False, quer=True) for i, p in enumerate(PRODUKTE))}
          </ul>
        </div>
      </section>""")

# Die alte Adresse /shop/ leitet auf die Startseite, wie die übrigen alten Seiten
AUSGABE["shop/index.html"] = ("""<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Weiterleitung zum Shop | BeThatHost</title>
    <link rel="canonical" href="https://bethathost.de/" />
    <meta name="robots" content="noindex" />
    <meta http-equiv="refresh" content="0; url=/" />
    <meta name="bth-weiterleitung" content="shop" />
  </head>
  <body>
    <p><a href="/">Weiter zum Shop</a></p>
  </body>
</html>
""")

# ---------- Produktseiten ----------
for p in PRODUKTE:
    andere = [q for q in PRODUKTE if q is not p]
    seite(f"shop/{p['slug']}.html", f"shop/{p['slug']}.html", p["seitentitel"], p["beschreibung"],
          f"""      <div class="shop-innen">
        <nav class="shop-pfad" aria-label="Brotkrume">
          <ol>
            <li><a href="/">Shop</a></li>
            <li aria-current="page">{p['kurz']}</li>
          </ol>
        </nav>
        <div class="shop-pdp">
          <figure class="shop-galerie">
            <span class="shop-chip">Gezeichnetes Muster</span>
            {p['bild']("g0", probe=True)}
          </figure>
          <div class="shop-info">
            <p class="shop-mono">Eigener Entwurf · BeThatHost</p>
            <h1 id="titel">{p['titel']}</h1>
            <p class="shop-preis">{PREIS}</p>
            <p class="shop-preis-hinweis">{PREIS_HINWEIS}</p>
            <p class="shop-satz">{p['satz']}</p>
{spulen()}
{probefeld(p["probe"])}
            <div class="shop-kauf">
              <span class="shop-etsy">Etsy-Link folgt</span>
              {hinweis(p['angabe'])}
            </div>
            <ul class="shop-fakten">
              <li>Bestellung und Bezahlung über Etsy</li>
              <li>Versand laut Etsy-Listing</li>
              <li>Gedruckt bei einem 3D-Druck-Partner</li>
            </ul>
            <div class="shop-akkordeon">
              <details open>
                <summary>Details</summary>
                <div class="shop-akkordeon-inhalt">
                  {dl(p['daten'])}
                  <p class="shop-offen">{p['offen']}</p>
                </div>
              </details>
              <details>
                <summary>Bestellung und Versand</summary>
                <div class="shop-akkordeon-inhalt">
                  <ol class="shop-kurzschritte">
{chr(10).join(f'                    <li><strong>{t}.</strong> {x}</li>' for t, x in SCHRITTE)}
                  </ol>
                </div>
              </details>
              <details>
                <summary>Herstellerangaben (GPSR)</summary>
                <div class="shop-akkordeon-inhalt">
                  <p>{GPSR}</p>
                </div>
              </details>
            </div>
          </div>
        </div>
      </div>
      <section class="shop-weitere" aria-labelledby="weitere">
        <div class="shop-innen">
          <h2 id="weitere">Auch im Shop</h2>
          <ul class="shop-raster shop-raster-eins">
{chr(10).join(karte(q, f"w{i}", "h3", druck=False, quer=True) for i, q in enumerate(andere))}
          </ul>
        </div>
      </section>""", aktiv=p["slug"], skript=SKRIPT)

# ---------- Impressum und Datenschutz ----------
# Kopf und Fuß wie im Shop (Kritiker Runde 1, 02.11.2026). Der Rechtstext wird nur umgehängt, nie geändert:
# beim ersten Lauf aus dem alten <main>, danach zwischen den Markern, so bleibt jeder weitere Lauf gleich.
RECHT = [("impressum.html", "Impressum", "Impressum, bethathost.de",
          "Impressum von BeThatHost, dem Shop für eigene Teile aus dem 3D-Drucker."),
         ("datenschutz.html", "Datenschutzerklärung", "Datenschutzerklärung, bethathost.de",
          "Datenschutzerklärung von BeThatHost, dem Shop für eigene Teile aus dem 3D-Drucker.")]
for datei, titel, titel_voll, beschreibung in RECHT:
    alt = (REPO / datei).read_text(encoding="utf-8")
    treffer = (re.search(r"<!-- recht-anfang -->\n(.*?)\n<!-- recht-ende -->", alt, re.S)
               or re.search(r"<main[^>]*>(.*)</main>", alt, re.S))
    if not treffer:
        raise SystemExit(f"Rechtstext in {datei} nicht gefunden, nichts geschrieben")
    seite(datei, datei, titel, beschreibung,
          f"""      <div class="shop-innen shop-recht">
<!-- recht-anfang -->
{treffer.group(1)}
<!-- recht-ende -->
      </div>""", kopf=PINTEREST, robots="noindex, follow", titel_voll=titel_voll)

if "--pruefen" in sys.argv:
    anders = [pfad for pfad, html in AUSGABE.items()
              if not (REPO / pfad).exists() or (REPO / pfad).read_text(encoding="utf-8") != html]
    if anders:
        print("nicht aktuell: " + ", ".join(anders))
        sys.exit(1)
    print(f"Shop-Seiten aktuell ({len(AUSGABE)} Dateien)")
else:
    for pfad, html in AUSGABE.items():
        (REPO / pfad).parent.mkdir(exist_ok=True)
        (REPO / pfad).write_text(html, encoding="utf-8")
    print(f"ok, {len(AUSGABE)} Dateien geschrieben")
