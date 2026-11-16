# yellowstone-wolves — contrôle des frames (co-pilote étape 3/4, 2026-11-16)

Module `yellowstone_wolves.py`, données `yellowstone_wolves.csv` (31 années, 2 sources par ligne). Durée calculée : 66,5 s (92 BPM, 2,5 temps par année, +2 temps après le record et chaque chute).

## Données (recoupement terminé)
- 1996 : 51 retenu (résumé du rapport NPS 1995-96 « 51 wolves in nine packs ») ; 52 = tableau wolf97 (inclut des loups en enclos).
- 2004 : 171 retenu (rapport NPS 2004 « at least 171 wolves in 16 packs ») ; 169 = déduit du rapport 2005.
- 1995–2000 et 2016 : deux rapports NPS distincts qui se recoupent (pas de source indépendante en ligne pour la ligne exacte) — noté dans la colonne check.
- 1995–1999 = Grand Yellowstone (GYA), 2000+ = dans le parc : écrit dans le HUD (« GREATER YELLOWSTONE » / « INSIDE THE PARK »), bannière en 2000, pointillé sur le graphe, ligne dans la source de fin.
- 1997 : pas de total de meutes publié → HUD « PACKS: N/A » (aucune pluck de meute).

## Frames vérifiées (t = 2,4 / 4,6 / 12,6 / 17,5 / 22,1 / 28,3 / 43,0 / 57,6 / 64,0 s)
- HUD = CSV : 1995 21 loups 3 meutes GYA ; 2000 119 / 8 ; 2003 174 / 13 ; 2005 118 / 13 ; 2008 124 / 12 ; 2016 108 / 11 ; 2025 84 / « 7 PACKS + 1 GROUP ». Nombre de loups pixel = valeur du CSV.
- Bannières : « 171 -> 118 » (2004→2005, mortalité des louveteaux, maladie suspectée : rapport NPS 2005) ; « 171 -> 124 » « -27 % » (1 − 124/171 = 27,5 %) ; record 174 (rapport NPS 2020 : maximum 2003) ; « DOWN FROM 108 IN 2024 ».
- Unités : comptages (sans unité physique : pas de conversion SI/US à faire).
- Graphe : linéaire 0–200, le haut = plus de loups, ligne pointillée = changement de base en 2000.
- Lisibilité : rien de coupé, pas de chevauchement HUD/bannière/graphe ; texte lisible à 540 px.
- Aucun mot sur l'IA ou la fabrication.

## Rendu final (palette crépuscule, décision étape 3 = b) — 2026-11-16
- PALETTE par défaut passée à `dusk` dans le module.
- ffprobe : 66,53 s, 1080×1920, audio AAC (music.wav 69,0 s, coupé par -shortest + fondu).
- Planche contact relue (1 image / 3 s) : HUD lisible sur fond sombre, bannières record 2003 / chutes 2005 & 2008 / 2025 lisibles, récap 21 / 174 / 84, crédits sources visibles, rien de coupé. Chiffres inchangés par rapport au contrôle de l'étape 3.
