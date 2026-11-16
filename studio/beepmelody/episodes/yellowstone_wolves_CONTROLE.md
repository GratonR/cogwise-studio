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

## Retravail son (PHASE R, carte decision-yellowstone-wolves-r1 → choix F) — 2026-11-16
- Remarque de Guillaume : « Pas terrible le son ». Nouvelle musique F « lo-fi sauvage » : 86 BPM swingué, Rhodes Fmaj7–Em7–Dm7–Cmaj9, kick/snare boom-bap, basse ronde, vinyle ; glockenspiel = une année (hauteur = loups, pentatonique de fa, échelle log), petites notes de Rhodes = meutes (une par meute), « tape stop » grave = chute ≥ 25 % (2005, 2008), accord de cloches + cymbale + hurlement = record 2003.
- Le tempo passe de 92 à 86 BPM : la timeline visuelle suit (mêmes temps par année), aucune triche de tempo. Durée : 71,17 s (ffprobe), dans 62–75 s.
- Repères : record 2003 à 0:18, chute 2005 (171 → 118) à 0:23, chute 2008 à 0:30, 2025 à 1:01. Légendes mises à jour.
- Correction visuelle : la 2e ligne de l'encart d'intro (« EVERY PIXEL WOLF = ONE WOLF COUNTED ») était coupée en bas → encart agrandi (512–552), vérifié à t = 3 s.
- Planche contact relue (2 / 12,9 / 18,3 / 21,4 / 23,1 / 29,8 / 45 / 61 / 64,5 / 69,5 s) : chiffres HUD = CSV (1999 118/11, 2003 174/13, 2004 171/16, 2005 118/13, 2008 124/12, 2015 98/10, 2025 84/7+1), bannières et récap 21 / 174 / 84 lisibles, rien de coupé. Données et visuels inchangés par ailleurs.
- Niveaux audio : RMS ~0,17, crête 0,89, aucun écrêtage.
