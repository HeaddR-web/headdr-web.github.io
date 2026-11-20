"""Schreibt den Shop ins Repo: die Startseite ist der Shop, dazu zwei Produktseiten (Stefanie, 02.11.2026).
Ziel: Shop für eigene 3D-Druck-Teile, verkauft über Etsy. Motto "alles kann individualisiert werden" ist die H1 der Startseite.
Aufbau wie ein Shopify-Shop: Produktraster, Produktseite mit Bild links, Farbwahl, Namensvorschau und Akkordeon.
Seit 19.11.2026 ist die Startseite ein Katalog (Variante A, Stefanie): Filter nach Anlass, zwölf Kacheln, davon zwei
gezeichnete Muster mit Produktseite und zehn gekennzeichnete Platzhalter ohne Seite und ohne Link.
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


# Beispielname der Startseite: steht ohne Eingabe in jeder Kachel, im Kopf und im Ablauf
BEISPIEL = "Tom"

# Platzhalter fürs Sortiment (Stefanie 19.11.2026: „platzhalter dürfen live“). Beispiele, bis ihre echte Liste steht:
# gezeichnet wie die Muster, Name aus der Namensleiste, kein Druck im Bild, keine Produktseite, kein Link.
# Je Teil: Titel, Anlässe (Schlüssel aus ANLAESSE), Form, Beispielfarbe aus SPULEN.
ANLAESSE = [("hochzeit", "Hochzeit"), ("jga", "JGA"), ("geburtstag", "Geburtstag")]
PLATZHALTER = [
    ("Tischnummer-Aufsteller", ["hochzeit"], "nummer", "Waldgrün"),
    ("Geschenkanhänger mit Namen", ["geburtstag"], "tag", "Sand"),
    ("Anstecker mit Namen", ["jga"], "anstecker", "Rosé"),
    ("Mini-Wegweiser für die Feier", ["hochzeit"], "pfeil", "Sand"),
    ("Lesezeichen mit Namen", ["geburtstag"], "lesezeichen", "Waldgrün"),
    ("Fotohalter mit Namen", ["hochzeit"], "foto", "Kreide"),
    ("JGA-Crew-Schild", ["jga"], "crew", "Rosé"),
    ("Zahlen-Aufsteller zum Geburtstag", ["geburtstag"], "zahl", "Sand"),
    ("Danke-Schild als Gastgeschenk", ["hochzeit"], "danke", "Waldgrün"),
    ("Türschild mit Namen", ["geburtstag"], "tuer", "Kreide"),
]
# Fläche der Kachel, Löcher und Ösen zeigen sie
KACHEL = "#e3eadf"


def platz_bild(form, farbe, id_, name=BEISPIEL):
    """Gezeichneter Platzhalter auf 300 x 240. Jeder Name trägt data-mitte, sonst setzt das Skript zwei Zeilen ins Leere."""
    _, grund, linie, _t = next(s for s in SPULEN if s[0] == farbe)
    schrift = "#f7f6f1" if farbe == "Waldgrün" else "#1d2420"
    fuellung = f"url(#{id_})"
    muster = [schichten(id_, 4, (grund, linie))]

    def n(maximal, feld, x, y, mitte, fill=schrift):
        return name_text(name, maximal, feld, 0.52, x, y, fill, mitte=mitte)

    def wort(x, y, size, inhalt, fill=schrift, extra=""):
        return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family=\'{DISPLAY}\' font-size="{size}" '
                f'font-weight="800" fill="{fill}"{extra}>{inhalt}</text>')

    if form == "nummer":
        teile = [f'<rect x="90" y="30" width="120" height="160" rx="6" fill="{fuellung}"/>',
                 f'<rect x="76" y="186" width="148" height="16" rx="3" fill="{linie}"/>',
                 wort(150, 106, 72, "7"), n(26, 108, 150, 160, 151)]
    elif form == "tag":
        teile = [f'<path d="M58 78 H196 L242 120 L196 162 H58 Z" fill="{fuellung}" stroke="#00000018"/>',
                 f'<circle cx="208" cy="120" r="8" fill="{KACHEL}" style="fill: var(--kachel, {KACHEL})"/>',
                 '<path d="M216 120 C 250 110, 262 72, 286 60" stroke="#9aa39d" stroke-width="3" fill="none"/>',
                 n(40, 118, 124, 134, 120)]
    elif form == "anstecker":
        teile = [f'<circle cx="150" cy="118" r="82" fill="{fuellung}" stroke="{linie}" stroke-width="5"/>',
                 '<circle cx="150" cy="118" r="68" fill="none" stroke="#ffffff80" stroke-width="2"/>',
                 n(38, 112, 150, 126, 116)]
    elif form == "pfeil":
        muster.append(schichten(id_ + "b", 4, SPULEN[0][1:3]))
        teile = ['<rect x="144" y="40" width="12" height="166" rx="2" fill="#b9a57f"/>',
                 f'<path d="M58 38 H210 L240 74 L210 110 H58 Z" fill="{fuellung}"/>',
                 n(30, 140, 136, 85, 74),
                 f'<path d="M236 118 H92 L64 144 L92 170 H236 Z" fill="url(#{id_}b)"/>']
    elif form == "lesezeichen":
        teile = [f'<rect x="122" y="16" width="56" height="194" rx="6" fill="{fuellung}" transform="rotate(14 150 113)"/>',
                 '<path d="M176 22 C 196 6, 206 30, 222 20" stroke="#b9a57f" stroke-width="3" fill="none"/>',
                 f'<g transform="rotate(-76 150 113)">{n(34, 150, 150, 125, 113)}</g>']
    elif form == "foto":
        teile = ['<rect x="92" y="22" width="116" height="84" rx="2" fill="#fffdf8" stroke="#00000024" transform="rotate(-4 150 64)"/>',
                 '<path d="M104 96 L132 66 L152 86 L166 74 L196 96 Z" fill="#9fb59a" transform="rotate(-4 150 64)"/>',
                 '<rect x="146" y="104" width="8" height="46" fill="#9aa39d"/>',
                 f'<rect x="64" y="146" width="172" height="60" rx="6" fill="{fuellung}" stroke="#00000024"/>',
                 n(28, 150, 150, 186, 176)]
    elif form == "crew":
        teile = [f'<path d="M54 66 Q150 36 246 66 V174 Q150 204 54 174 Z" fill="{fuellung}"/>',
                 f'<path d="M126 82 L132 64 L142 76 L150 58 L158 76 L168 64 L174 82 Z" fill="{schrift}" opacity="0.8"/>',
                 n(34, 150, 150, 142, 130)]
    elif form == "zahl":
        teile = [wort(150, 134, 116, "30", fuellung, f' stroke="{linie}" stroke-width="2"'),
                 '<rect x="62" y="142" width="176" height="80" rx="4" fill="#1d2420"/>',
                 n(24, 156, 150, 190, 182, "#f7f6f1")]
    elif form == "danke":
        teile = [f'<rect x="44" y="52" width="212" height="134" rx="67" fill="{fuellung}"/>',
                 f'<path d="M150 98 C 136 86, 124 76, 134 66 C 141 60, 148 64, 150 70 C 152 64, 159 60, 166 66 C 176 76, 164 86, 150 98 Z" fill="{schrift}"/>',
                 n(26, 140, 150, 152, 142)]
    elif form == "tuer":
        teile = [f'<rect x="50" y="56" width="200" height="128" rx="14" fill="{fuellung}" stroke="#00000024"/>',
                 f'<circle cx="72" cy="78" r="5" fill="{KACHEL}" style="fill: var(--kachel, {KACHEL})"/><circle cx="228" cy="78" r="5" fill="{KACHEL}" style="fill: var(--kachel, {KACHEL})"/>',
                 n(52, 164, 150, 140, 122)]
    else:
        raise SystemExit(f"Platzhalter-Form {form} unbekannt, nichts geschrieben")
    return (f'<svg class="shop-svg-platz"{probe_attr(True, name)} viewBox="0 0 300 240" aria-hidden="true" focusable="false">'
            f'<defs>{"".join(muster)}</defs>'
            '<ellipse cx="150" cy="212" rx="106" ry="9" fill="#000" opacity="0.09"/>'
            + "".join(teile) + "</svg>")


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


# Startseite: ein Feld für die ganze Seite (Stefanie 16.11.2026, „Dein Name überall“). Es schreibt den
# vorderen Halter, den Anhänger und jede Textstelle mit data-namen um, deshalb nur so lang, wie der Anhänger erlaubt.
# Leer, damit Feld und Bild nicht verschiedene Beispielnamen zeigen.
START_PROBE = {"label": "Dein Name", "wert": "", "max": 10,
               "hilfe": "Bis zu 10 Zeichen, gespeichert wird nichts."}


def probeleiste(f):
    """Namensfeld der Startseite als eigene Leiste zwischen Kopf und Produkten. Sie klebt oben, damit man den Namen
    auch weiter unten noch ändern kann (Kritiker Runde 1, 16.11.2026). Der Platzhalter zeigt den Namen, der ohne Eingabe dasteht."""
    return f"""      <div class="shop-leiste">
        <div class="shop-innen shop-leiste-raster">
          <label class="shop-leiste-kopf" for="probe-name">{f['label']}</label>
          <input class="shop-feld shop-leiste-feld" id="probe-name" type="text" maxlength="{f['max']}" value="{f['wert']}" placeholder="{BEISPIEL}" autocomplete="off" spellcheck="false" enterkeyhint="done" aria-describedby="probe-hilfe" />
          <p class="shop-leiste-hilfe" id="probe-hilfe">{f['hilfe']}</p>
        </div>
      </div>"""


def namen(klasse=""):
    """Textstelle, die den Namen aus dem Feld übernimmt. Leer und ohne Skript steht der Beispielname da."""
    return f'<span class="shop-namen{" " + klasse if klasse else ""}" data-namen="{BEISPIEL}">{BEISPIEL}</span>'


# Farbwahl färbt das Teil um, das Namensfeld schreibt den Namen in jede Stelle mit data-probe
# und in jede Textstelle mit data-namen.
# Beides druckt neu, aber nur die Stelle selbst. Platzhalter haben keine Druckmaske, dort steht der Name sofort.
SKRIPT = """    <script>
      (function () {
        var ruhig = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var stellen = document.querySelectorAll("[data-probe]"), worte = document.querySelectorAll("[data-namen]");
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
          Array.prototype.forEach.call(worte, function (n) {
            var w = eingabe || n.dataset.namen;
            if (n.textContent !== w) n.textContent = w;
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

# {beispiel}: auf der Startseite steht dort der Name aus dem Feld, auf den Produktseiten nichts
SCHRITTE = [("Auf Etsy bestellen", "Im Etsy-Listing gibst du den Namen oder Text an{beispiel}, bezahlst und bekommst die Bestellbestätigung."),
            ("Druck und Versand", "Entworfen von BeThatHost, gedruckt bei einem 3D-Druck-Partner. Den Versand an dich übernehmen wir selbst.")]


def dl(paare):
    return ('<dl class="shop-daten">'
            + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in paare) + "</dl>")


def punkte():
    tupfer = "".join(f'<i style="--c: {f}"></i>' for _, f, _, _ in SPULEN)
    return f'<p class="shop-punkte"><span aria-hidden="true">{tupfer}</span>{len(SPULEN)} Beispielfarben</p>'


def karte(p, id_, ebene="h2", druck=True, quer=False, bild=None, probe=False):
    """Produktkarte wie im Shop-Raster: Bild, Titel, Preis. Der Titel-Link deckt die ganze Karte ab."""
    return f"""          <li class="shop-karte{' shop-karte-quer' if quer else ''}">
            <div class="shop-karte-bild">
              <span class="shop-chip">Gezeichnetes Muster</span>
              {bild or p['bild'](id_, druck, probe)}
            </div>
            <div class="shop-karte-text">
              <{ebene} class="shop-karte-titel"><a href="/shop/{p['slug']}.html">{p['titel']}</a></{ebene}>
              <p class="shop-karte-preis">{PREIS}</p>
              <p class="shop-karte-satz">{p['satz']}</p>
              {punkte()}
            </div>
          </li>"""


# Kachelton der Platzhalter nach Materialfarbe: höchstens drei gleiche Kacheln nebeneinander (Gate R2, 19.11.2026)
TOENE = {"Waldgrün": "waldgruen", "Sand": "sand", "Rosé": "rose", "Kreide": "kreide"}


def katalog_karte(titel, anlaesse, bild, slug=None, ton=None):
    """Kachel im Katalog der Startseite. Mit slug ein gezeichnetes Muster mit Produktseite, ohne ein Platzhalter:
    kein Link, kein Hover, der Status ist eine ruhige Zeile statt eines Knopfs, damit nichts einen Kauf vortäuscht."""
    muster = slug is not None
    unbekannt = [a for a in anlaesse if a not in dict(ANLAESSE)]
    if unbekannt:
        raise SystemExit(f"Anlass {unbekannt} unbekannt, nichts geschrieben")
    anlass = ", ".join(n for k, n in ANLAESSE if k in anlaesse)
    titel_html = f'<a href="/shop/{slug}.html">{titel}</a>' if muster else titel
    # Preis und Etsy-Status nur an den Mustern, für die Platzhalter steht beides einmal über ihrer Gruppe
    kauf = (f'\n                <p class="shop-karte-preis">{PREIS}</p>'
            '\n                <p class="shop-karte-status">Bald auf Etsy</p>') if muster else ""
    if ton is not None and ton not in TOENE:
        raise SystemExit(f"Kachelton {ton} unbekannt, nichts geschrieben")
    klasse = "" if muster else " shop-karte-platzhalter" + (f" shop-ton-{TOENE[ton]}" if ton else "")
    return f"""            <li class="shop-karte{klasse}" data-anlass="{' '.join(anlaesse)}">
              <div class="shop-karte-bild">
                <span class="shop-chip{' shop-chip-muster' if muster else ''}">{'Muster' if muster else 'Platzhalter'}</span>
                {bild}
              </div>
              <div class="shop-karte-text">
                <p class="shop-karte-anlass">{anlass}</p>
                <h3 class="shop-karte-titel">{titel_html}</h3>{kauf}
              </div>
            </li>"""


def katalog():
    # Kurzname im Katalog: der klickbare Titel bleibt einzeilig (Gate 49), der volle Name steht auf der Produktseite
    muster = [katalog_karte(PRODUKTE[0]["kurz"], ["hochzeit", "geburtstag"],
                            halter("k0", name=BEISPIEL, probe=True), PRODUKTE[0]["slug"]),
              katalog_karte(PRODUKTE[1]["kurz"], ["jga"], anhaenger("k1", name=BEISPIEL.upper(), probe=True), PRODUKTE[1]["slug"])]
    platz = [katalog_karte(t, a, platz_bild(form, farbe, f"p{i}"), ton=farbe) for i, (t, a, form, farbe) in enumerate(PLATZHALTER)]
    karten = muster + platz
    knoepfe = "\n".join(
        f'              <button type="button" class="shop-filter-knopf" data-filter="{k}" aria-pressed="{"true" if k == "alle" else "false"}">{n}</button>'
        for k, n in [("alle", "Alle")] + ANLAESSE)
    # Sprungziele der Kopfzeile: ein Anker je Anlass, das Filterskript liest ihn aus der Adresse
    anker = "".join(f'<span class="shop-anker" id="{k}"></span>' for k, _ in ANLAESSE)
    return f"""      <section class="shop-sortiment shop-katalog" id="sortiment" aria-labelledby="sortiment-titel">
        <div class="shop-innen">
          {anker}
          <div class="shop-filterleiste">
            <h2 class="shop-sortiment-titel" id="sortiment-titel">Sortiment</h2>
            <div class="shop-filter" role="group" aria-label="Nach Anlass filtern">
{knoepfe}
            </div>
            <p class="shop-anzahl" id="shop-anzahl" aria-live="polite">{len(karten)} Teile</p>
          </div>
          <!-- Die zwei gezeichneten Muster groß vorn, die Platzhalter kleiner dahinter (Gate R2, 19.11.2026) -->
          <ul class="shop-raster shop-raster-katalog shop-raster-muster" aria-label="Muster">
{chr(10).join(muster)}
          </ul>
          <p class="shop-gruppe" id="gruppe-bald">Bald im Sortiment · Platzhalter, Preise und Etsy-Links folgen</p>
          <ul class="shop-raster shop-raster-katalog shop-raster-bald" aria-labelledby="gruppe-bald">
{chr(10).join(platz)}
          </ul>
        </div>
      </section>"""


# Filter nach Anlass: blendet Kacheln aus, zählt mit und folgt der Adresse (/#jga aus der Kopfzeile).
# Eine fremde Adresse wie #bestellung lässt den Filter stehen, nur #sortiment zeigt wieder alles.
FILTER = """    <script>
      (function () {
        var knoepfe = document.querySelectorAll(".shop-filter-knopf"), karten = document.querySelectorAll(".shop-katalog [data-anlass]");
        var anzahl = document.getElementById("shop-anzahl");
        if (!knoepfe.length || !anzahl) return;
        var gueltig = Array.prototype.map.call(knoepfe, function (b) { return b.dataset.filter; });
        function zeigen(anlass) {
          var n = 0;
          Array.prototype.forEach.call(karten, function (k) {
            var an = anlass === "alle" || k.dataset.anlass.split(" ").indexOf(anlass) >= 0;
            k.hidden = !an;
            if (an) n++;
          });
          Array.prototype.forEach.call(knoepfe, function (b) { b.setAttribute("aria-pressed", b.dataset.filter === anlass ? "true" : "false"); });
          anzahl.textContent = n + (n === 1 ? " Teil" : " Teile");
        }
        function ausAdresse() {
          var h = location.hash.slice(1);
          if (h === "sortiment") zeigen("alle");
          else if (gueltig.indexOf(h) >= 0) zeigen(h);
        }
        Array.prototype.forEach.call(knoepfe, function (b) {
          b.addEventListener("click", function () {
            var f = b.dataset.filter;
            zeigen(f);
            if (history.replaceState) history.replaceState(null, "", f === "alle" ? location.pathname : "#" + f);
          });
        });
        window.addEventListener("hashchange", ausAdresse);
        ausAdresse();
      })();
    </script>
"""


def ablauf():
    beispiel = f", zum Beispiel {namen()}"
    schritte = "\n".join(f'            <li><span class="shop-nr" aria-hidden="true">{i}</span><div><h3>{t}</h3><p>{x.format(beispiel=beispiel)}</p></div></li>'
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


def nav():
    """Kategorien wie im Shop: jeder Anlass springt in den gefilterten Katalog der Startseite."""
    ziele = [(f"/#{k}", n) for k, n in ANLAESSE] + [("/#sortiment", "Alle Produkte")]
    return "\n".join(f'          <a href="{h}">{n}</a>' for h, n in ziele)


# Etsy-Hinweis oben rechts: kein Link, solange es den Etsy-Shop nicht gibt (Plan: Kaufknopf täuscht nichts vor)
TASCHE = ('<svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true" focusable="false">'
          '<path d="M4 7h12l-1 10H5z M7.5 7V5.5a2.5 2.5 0 0 1 5 0V7" fill="none" stroke="currentColor" '
          'stroke-width="1.8" stroke-linejoin="round"/></svg>')


def seite(pfad, url_pfad, titel, beschreibung, koerper, skript="", kopf="", robots=None, titel_voll=None):
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
        <nav aria-label="Sortiment">
{nav()}
        </nav>
        <span class="shop-etsy-pill">{TASCHE}Etsy-Shop · bald</span>
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
# Seit 19.11.2026 Katalog (Variante A): Kopf als Salbei-Band, Namensleiste, Filter nach Anlass, zwölf Kacheln.
# Der Kopf ist flach, damit die Muster über der Falz stehen; die Platzhalter erklärt nur die Zeile über ihrem Raster (Kritiker Runde 1)
seite("index.html", "", "3D-Druck-Teile, individuell für dich",
      "Party-Teile aus dem 3D-Drucker mit deinem Namen, für Hochzeit, JGA und Geburtstag. "
      "Platzkartenhalter und JGA-Anhänger, bald mehr. Bestellt wird über Etsy.",
      f"""      <section class="shop-kopf shop-kopf-band" aria-labelledby="titel">
        <div class="shop-innen shop-kopf-zeile">
          <p class="shop-mono">{" · ".join(n for _, n in ANLAESSE)}</p>
          <h1 id="titel">Alles lässt sich individualisieren</h1>
          <p class="shop-kopf-fuer">Zum Beispiel für {namen("shop-namen-gross")}</p>
        </div>
      </section>
{probeleiste(START_PROBE)}
{katalog()}
{ablauf()}""", kopf=PINTEREST, skript=SKRIPT + FILTER)

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
{chr(10).join(f'                    <li><strong>{t}.</strong> {x.format(beispiel="")}</li>' for t, x in SCHRITTE)}
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
      </section>""", skript=SKRIPT)

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
