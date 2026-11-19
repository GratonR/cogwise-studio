# Lancements 2026 — contrôle des frames (co-pilote étape 3/4, 2026-11-19)

Module `launches2026.py` (globe néon, ambiance B « compte à rebours électro », 160 BPM, 1 jour = 1 croche = 0,1875 s).
Durée calculée : **68,6 s** (intro 3,0 · données 60,4 · outro 5,25). Musique rendue : 70,1 s avec la traîne (coupée par `-shortest`).

## Données
- 265 tentatives orbitales du 1er janv. au 18 nov. 2026 ; 257 réussies, 8 échecs. Starship ×4 exclus (suborbital), doublon Starfall du 23/06 exclu.
- Source 1 : keeptrack.space/launches/2026 (toutes les lignes).
- Source 2, janv.–juin : Wikipedia « 2026 in spaceflight » → total 154 = CSV 154, Falcon 77 = CSV 77, 6 échecs (PSLV-DL, LM-3B, Ceres-2, Kairos, Tianlong-3, New Glenn) = CSV.
  Écart mensuel connu : Wikipedia janv. 24 / juin 29 contre CSV 25 / 28 (même total semestriel ; probablement une ligne datée différemment). À relever, ne change pas l'écran (barres mensuelles = CSV).
- Source 2, juil.–nov. : orbitalradar.com/launch-database (consulté le 2026-11-19) : chaque ligne retrouvée par date + mission. Juil. 26, août 26, sept. 26 (hors Starship) = CSV.
  SpaceNexus (Launch Library 2) : août 26 tentatives dont 1 échec, SpaceX 14 = CSV ; sept. 27 chez eux contre 26 (CSV et orbitalradar) → on garde 26.
- Échecs (8) : 12/01 PSLV-DL · 16/01 Long March 3B · 17/01 Ceres-2 · 05/03 Kairos · 03/04 Tianlong-3 · 19/04 New Glenn · 10/08 Long March 7A · 15/11 Vulcan.

## Points vérifiés sur les frames (t = 1,8 · 5,5 · 11,1 · 23,6 · 24,8 · 35,0 · 46,9 · 62,95 · 66,6 · 68,0 s)
- Compteur = rang de la ligne du CSV (#100 = 26 avril, #200 = 22 août, #265 = Vulcan 15 nov.) ; « FAILED n » = échecs cumulés du CSV.
- Barres par mois (finales) 25 · 18 · 30 · 31 · 22 · 28 · 26 · 26 · 26 · 21 · 12 = CSV ; un trait rouge par échec au-dessus du mois.
- Légende finale USA 136 · CHINA 81 · NZ 17 · RU 15 · EU 7 · +9 (Inde 4, Japon 4, Corée 1) = 265. Pays = pays du pas de tir (Electron = Nouvelle-Zélande).
- Outro : 265 / 257 / 8 / mois record avril 31 (= Wikipedia avril 31). Sources à l'écran. Pas d'unité physique affichée (pas de SI/US à faire).
- Bannières : 8 échecs (rouge, écran qui tremble + flash rouge, batterie coupée une demi-mesure), 1er lancement, 4 lancements le 12 févr., #100, #200.
- Lisibilité : rien de coupé après correction (légende raccourcie, bloc sources remonté dans le panneau d'outro). Aucun mot sur la fabrication.
- Position des pas de tir : port spatial principal du lanceur (approximation à quelques centaines de km : Cap Canaveral / Vandenberg selon la mission, Wenchang / Jiuquan / Taiyuan / Xichang / mer selon la fusée chinoise, etc.). Les lancements de la face cachée sortent derrière le bord du globe.

## Rendu final (2026-11-19, étape 3 validée « Ça me va »)
- MP4 1080×1920, ffprobe 68,67 s (vidéo + audio), palette néon. Planche contact relue (1 image / 4 s) : compteurs, dates, « FAILED n », barres et légende pays croissent dans l'ordre du CSV ; bannières #100 (26 avr.), #200 (22 août), échecs ; outro 265 / 257 / 8 / avril 31. Rien de coupé.
- Couverture posée (« EVERY ROCKET OF 2026 », image à 0,7 = #200), relue.
