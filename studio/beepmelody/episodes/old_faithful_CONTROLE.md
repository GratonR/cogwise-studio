# old-faithful — contrôle des frames (étape 3/4 co-pilote, 2026-11-19)

Module `old_faithful.py` · données `old_faithful_draft.csv` (299 éruptions, Azzalini & Bowman 1990, lues dans MASS/CRAN + Rdatasets, copies identiques) · contexte `old_faithful_facts.csv` (NPS + USGS + Hurwitz et al. 2014).
Décisions : étape 1 = A (scène vivante « A GEYSER THAT KEEPS TIME », ≈ 80 éruptions), étape 2 = C → C1 → C1a (marimba « tout bois », 124 BPM).
Épisode : éruptions n° 1 → 80 (94 h 18 min de geyser). 1 min de geyser = 0,0093 s (1 h = 0,56 s, écrit à l'écran), notes calées sur la double-croche à 124 BPM.
Durée calculée : 65,6 s (intro 3,6 · jour 1 11,4 · jour 2 14,8 · jour 3 12,0 · jour 4 + tenue 15,9 · outro 8,0). Musique test : 67,1 s (queue coupée à la vidéo).

## Frames contrôlées (T en s)
| T | Ce qu'on voit | Vérif |
|---|---|---|
| 2,6 | Titre + règle : EVERY NOTE = ONE ERUPTION / THE GAP = THE REAL WAIT / 1 HOUR OF WAITING = 0.56 S / TALLER JET = LONGER ERUPTION | 60 × 0,0093 = 0,558 s ✓ ; la hauteur du jet est annoncée comme durée, pas comme hauteur mesurée ✓ |
| 8,3 | #12 · 50 MIN · LONG BURST 5.5 MIN · +12 H 50 · bannière SHORT BURST -> SHORT WAIT (1.8 MIN OF WATER, THEN 50 MIN) | CSV : #11 1,8333 min, #12 attente 50, durée 5,45 ; cumul 770 min ✓ |
| 10,6 | #15 · 90 MIN · 4.4 MIN · +16 H 43 · LONG BURST -> LONG WAIT (4.9 MIN, THEN 90 MIN) | CSV : #14 4,8667, #15 attente 90 / 4,3833 ; cumul 1003 min ✓ |
| 16,4 | #24 · 58 MIN · ~4 MIN (NIGHT, EST.) · ciel de nuit | CSV : durée codée 4 (nuit) → « est. » ✓ |
| 36,3 | #54 · 43 MIN · 4.3 MIN · +62 H 52 · bannière 43 MIN / SHORTEST WAIT OF ALL 299 | min des 299 = 43 (n° 54) vérifié par script ✓ |
| 40,9 | #60 · 71 MIN · ~4 MIN (NIGHT, EST.) · +70 H 19 | CSV ✓ |
| 41,6 | #61 · 108 MIN · SHORT BURST 2.0 MIN · +72 H 07 · bannière 108 MIN / LONGEST WAIT OF ALL 299 | max des 299 = 108 (n° 61) ✓ ; 1,95 min arrondi au dixième supérieur (corrigé : affichait 1.9) |
| 55,0 | #80 · 79 MIN · 4.2 MIN · +94 H 18 · bannière TODAY: ~90 MIN / SLOWER, AND MORE REGULAR / NPS ~90 MIN · USGS 94 +/- 10 MIN | 5658 min = 94 h 18 ✓ ; NPS ~90 (50–127), USGS 94 ± 10, Hurwitz 2001–2011 : 91–93 min, 4 % d'attentes courtes → « plus régulier » ✓ |
| 63,0 | 80 ERUPTIONS · 94 HOURS · 72 MIN AVERAGE WAIT 1985 · 43 SHORTEST · 108 LONGEST · ~90 TODAY · question · DATA: AZZALINI & BOWMAN 1990, 299 ERUPTIONS 1-15 AUG 1985, TODAY: NPS, USGS | moyenne des 299 = 72,3 ✓ |

- Unités : minutes et heures uniquement (pas de mesure SI/US à convertir à l'écran).
- Graphe du bas : une barre = l'attente avant chaque éruption, axe 40–110 min (le haut = plus long), repères 60 et 90 ; couleur = durée de l'éruption précédente (teal courte, orange longue). Moyennes 299 : après courte 55,6 min, après longue 81,2 min.
- Ciel de nuit : uniquement autour des éruptions dont la durée est codée « nuit » dans la source (pas d'heure inventée).
- Horloge du Visitor Center : l'aiguille tourne avec le temps de geyser cumulé (pas une heure réelle).
- Lisibilité corrigée pendant le contrôle : bassin chaud caché par le graphe (remonté à côté du cône), légende du graphe coupée en bas (remontée), étiquettes 40/60/90 superposées (40 retiré), arrondi 1,95 → 2.0.
- Aucun mot sur l'IA ou la fabrication.
