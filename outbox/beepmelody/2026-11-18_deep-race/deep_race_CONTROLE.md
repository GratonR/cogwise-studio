# deep-race — contrôle des frames (étape 3/4 co-pilote, 2026-11-18)

Module `deep_race.py` · données `deep_race_draft.csv` (45 records, 2 sources par ligne) · repères `deep_race_landmarks.csv`.
Décisions : étape 1 = A (caméra qui suit le couloir le plus profond, apnée et scaphandres en repère en haut), étape 2 = C (breakbeat 160 BPM).
Durée calculée : 66,4 s (intro 4,5 · 1930–1949 10,5 · 1950–1962 13,9 · 1963–2019 23,3 · tenue 6,0 · outro 8,3). Musique test : 68,4 s avec la queue de réverb, coupée à la vidéo.

## Frames contrôlées (T en s)
| T | Ce qu'on voit | Vérif |
|---|---|---|
| 0,3 / 2,8 | « 1930: 435 M DOWN. » / « 1960: 10,916 M. » / EVERY NOTE = A NEW DEPTH RECORD / 45 RECORDS 1930 TO 2019 | 435 m = CSV 1930-06-11 (NatGeo, Linda Hall) ; 10 916 m = CSV 1960-01-23 (Britannica, NHHC) ; 45 lignes, 1930→2019 ✓ |
| 8,6 | 923 M · 3,028 FT · 1934 · #5/45 · Beebe + Barton · BATHYSPHERE · bannière ALMOST 1 KM DOWN | = CSV ✓ |
| 14,5 | 1,372 M · 4,500 FT · 1949 · #10 · BENTHOSCOPE · EST. | = CSV (approx=1) ✓ |
| 21,0 | 183 M · 600 FT · 1956 · #16 · George Wookey, Royal Navy | = CSV ✓ |
| 23,9 | 10,916 M · 35,814 FT · 1960 · #19 · Piccard + Walsh · TRIESTE · US NAVY: 10,911 M · bannière THE VERY BOTTOM | = CSV, écart NHHC affiché ✓ |
| 36,0 | 100 M · 328 FT · 1976 · #31 · Mayol · NO-LIMITS SLED · bannière 100 M ON ONE BREATH | = CSV ✓ |
| 41,0 | 534 M · 1,752 FT · 1988 · #35 · COMEX / French Navy team · SATURATION DIVE · EST. | = CSV ✓ |
| 48,9 | 610 M · 2,000 FT · 2006 · #42 · Daniel P. Jackson, US Navy · HARD SUIT (ADS 2000) · bannière 2,000 FT IN A HARD SUIT / 610 M · US NAVY | = CSV ✓ |
| 50,8 | 253.2 M · 831 FT · 2012 · #44 · NOT RATIFIED · bannière DEEPEST BREATH-HOLD EVER | = CSV (ratified=0) ✓ |
| 53,0 | 10,934 M · 35,872 FT · 2019 · #45 · Vescovo · GUINNESS, ±3 M · bannière NEW RECORD! +18 M, 59 YEARS LATER | 10 934 − 10 916 = 18 ; 2019 − 1960 = 59 ✓ |
| 63,0 | DEEPEST EACH WAY : 253.2 M / 831 FT / 2012 NOT RATIFIED · 610 M / 2,000 FT / 2006 · 10,934 M / 35,872 FT / 2019 · sources | = CSV ✓ |

- Unités : SI puis US partout (HUD, bannières, repères LIGHT FADES 200 M / 656 FT, TITANIC 3,800 M / 12,500 FT, EVEREST 8,849 M / 29,032 FT). Écart m↔ft < 3 % sur les 45 lignes (script).
- Axe : profondeur vers le bas, échelle log annoncée « (LOG) », graduations 100 M / 1 KM / 10 KM ; la caméra dézoome quand les submersibles descendent (haut fixe à ~18 m).
- Chaque couloir ne fait que descendre (records monotones vérifiés par script : apnée 23, scaphandre 10, sous-marins 12).
- Lisibilité corrigée pendant le contrôle : étiquettes des repères déplacées dans une colonne à droite (elles croisaient les couloirs), Titanic au-dessus de sa ligne et Everest en dessous (chevauchement), bannière Trieste raccourcie (débordait à 40 px), bannières tenues 2,6 s même si un record suit (Trieste disparaissait après 0,75 s), noms longs raccourcis (Wookey, Jackson, Rhodes, Bollard, Zetterström), crédits de fin sur 3 lignes (coupés).
- Repères : NOAA + WHOI (200 m), NOAA + Britannica (Titanic), Britannica + National Geographic (Everest 8 848,86 m arrondi 8 849).
- Aucun mot sur l'IA ou la fabrication.
