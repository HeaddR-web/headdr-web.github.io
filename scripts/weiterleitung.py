# -*- coding: utf-8 -*-
"""Erkennt Weiterleitungsseiten (seit 02.11.2026: Domain ist nur noch Shop).

Alte Inhaltsseiten sind durch minimale Weiterleitungen auf "/" ersetzt und
tragen <meta name="bth-weiterleitung" content="shop">. Alle Pruefungen und
Generatoren, die nur fuer echte Inhaltsseiten gelten (Picks, Related, TOC,
FAQ, Brotkrume, Werbeplatz, Bilder, Meta), ueberspringen solche Seiten.
Echte Seiten werden dadurch nicht weniger streng geprueft: wer die Markierung
auf eine echte Seite setzt, macht aus ihr eine Weiterleitung (ohne Inhalt).
"""
import os
import re
import sys

# scripts/ liegt nicht immer im Importpfad (importlib-Aufrufe aus anderen Skripten).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MARKE_RE = re.compile(r'<meta\s+name="bth-weiterleitung"\s+content="shop"\s*/?>')
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ist_weiterleitung(pfad):
    voll = pfad if os.path.isabs(pfad) else os.path.join(WURZEL, pfad)
    try:
        with open(voll, encoding="utf-8", errors="ignore") as f:
            return bool(MARKE_RE.search(f.read(4096)))
    except OSError:
        return False
