# shanks-pi — contrôle des frames (étape 3/4, 2026-11-22)

Décisions co-pilote : 1 = A (« A man spent years on 707 digits of pi. The last 180 were wrong. », bureau de Shanks, rouleau qui vire au rouge à 528) ; 2 = C · Machine à calculer (128 BPM, clic + pluck = plume de Shanks, pluck clair = vrai π, kick 4/4, buzz carré pour les chiffres faux, cloche dorée pour les chiffres justes par hasard).
Module : `shanks_pi.py` (palette `SP_PAL=day` par défaut, parchemin clair ; variante `night` = bureau à la bougie). Données : `shanks_pi.csv` (707 lignes).
Durée prévue (`info`) : 67,2 s — accroche 0–2,9 s · décimales 1–527 à 15 / s (0,6 → 35,7 s) · 528 à 35,9 s + 1 s d'arrêt · 529–707 à 8,2 / s (36,9 → 58,6 s) · outro 59,2 → 67,2 s. Dans 62–75 s, tempo non triché (vitesses = celles des extraits validés à l'étape 2).

Frames vues : 0.3 / 1.0 / 2.0 / 3.5 / 8.0 / 16.0 / 26.5 / 35.5 / 35.95 / 36.1 / 36.3 / 37.5 / 39.5 / 40.0 / 43.0 / 49.0 / 55.0 / 58.7 / 61.3 / 62.0 / 63.5 / 66.0 / 66.5 / 67.0 s (+ variante night 16.0 / 36.3 / 63.5).

## Vérifié point par point
- Colonne « vrai π » du CSV recalculée dans le module (formule de Machin en entiers, `assert`) : identique sur les 707 décimales.
- Première divergence = décimale 528 : Shanks 5, π 4 (`assert`) → bannière « DIGIT 528 · HE WROTE 5. PI SAYS 4. » et zoom de l'outro (décimales 521–535, case rouge sur 528).
- 527 justes, 180 décimales de la partie fausse (528–707), dont 163 différentes et 17 identiques par hasard (531, 533, 540, 543, 560, 562, 564, 567, 570, 607, 613, 627, 636, 656, 684, 705, 707) = CSV = recherche (Engert + Math Lair). Compteurs du bas en fin : RIGHT 527 · WRONG 180 · BY LUCK 17 ; outro « 527 RIGHT / 180 WRONG (17 OF THEM MATCH PI BY LUCK) » : cohérents.
- « 20+ YEARS » (Hayes, American Scientist 2014 ; Engert « 20+ year period »). « 1853: 607 DIGITS / 1873: 707 » (Hayes ; MTAC 1947 ; MacTutor). « 1946: D. F. FERGUSON … DESK CALCULATOR » (Math. Gazette mai 1946 ; Wrench MTAC 1947 ; Hayes). « 73 YEARS » = 1946 − 1873. « ONE SKIPPED TERM, NEAR DIGIT 530 » (Hayes ; Ferguson via MTAC 1947).
- Pas d'unité physique : pas de conversion SI/US.
- Sens : le papier se lit ligne par ligne (20 décimales par ligne, numéro de la 1re décimale à gauche, « 3. » sur la 1re ligne) ; la barre du bas va de 1 à 707, repère à 528 ; vert = juste, rouge = faux, or = juste par hasard.
- Lisibilité : HUD, règle, écran, papier, bannières et barre du bas sans chevauchement ; les bannières masquent 2 lignes de papier pendant 1,5–2,8 s (voulu). Corrigé pendant le contrôle : compteur « RIGHT 544 » qui contredisait « 527 RIGHT » de l'outro, bannière « ALL WRONG » contredite par les chiffres dorés (→ « OFF TRACK »), chiffres de Shanks invisibles sur fond sombre (variante night).
- Son : 1 décimale = 1 coup par voix ; silence du fond à 528 (−0,15 → +0,95 s) ; batterie coupée à l'outro, accord final.
- Aucune mention d'IA ni de fabrication.

## Étape 4/4 — rendu final, palette « nuit » (décision de Guillaume, 22 nov. 14:26 UTC)
- Rendu `SP_PAL=night` (seule la palette change : mêmes données, même module, même musique C « Machine à calculer »).
- Frames nuit relues à 0,8 / 8 / 27 / 36,2 / 45 / 49,5 / 58,5 / 62 / 66,5 s : lisibilité OK sur fond sombre, rien de coupé.
- Compteurs cohérents : DIGIT n − 527 = WRONG (les « by luck » en sont un sous-ensemble) ; 595 → 68 dont 9, 632 → 105 dont 12, final 180 dont 17.
- ffprobe : 67,23 s, 1080×1920, 30 i/s, audio AAC. Couverture « 180 wrong digits of pi » (fond à 45 s), titre lisible, centre 3:4 propre.
