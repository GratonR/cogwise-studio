"""BEEPMELODY · HOW HIGH HAVE HUMANS EVER BEEN? (v4) — same data, picture and arrangement as altitude_v3,
with a softer lead voice (Guillaume, 2026-11-08: « le bip est trop strident »).

What changes vs v3 (sound only, the video is identical):
- the record notes ("digit"), the quick climb notes and arpeggio ("edigit") and the high chimes are taken OUT of
  the event list given to the shared engine (pi_audio.py, unmodified) and rendered here by `soft_lead.py`;
- the soft lead is one octave lower (top note A5 = 880 Hz instead of A6), a rounded tone (sine + soft triangle,
  gentle 2nd harmonic, low-passed around 2.5 kHz), 8 ms attack instead of 3 ms, and sits back in the mix;
- the chimes become a low, short glockenspiel (one octave down, no 3rd partial).
Usage (from studio/this-melody-is/engine):
  MOD=altitude_v4 python3 pi_audio.py $OUT/backing.wav
  python3 ../../beepmelody/episodes/soft_lead.py altitude_v4 $OUT/backing.wav $OUT/music.wav
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from altitude_v3 import *            # noqa: F401,F403  (data, scenes, render, EV built by v3)
import altitude_v3 as _v3

LEAD_KINDS = ("digit", "edigit", "chime")
LEAD = [e for e in _v3.EV if e[1] in LEAD_KINDS]       # rendered by soft_lead.py
EV = [e for e in _v3.EV if e[1] not in LEAD_KINDS]     # what the shared engine plays
LEAD_OUTRO = list(_v3.OUTRO_DIGITS)
OUTRO_DIGITS = []                                     # engine's own outro beeps off; soft_lead plays them
LEAD_SHIFT = -12                                      # one octave down
