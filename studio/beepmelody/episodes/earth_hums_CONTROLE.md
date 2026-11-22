# Earth hums — contrôle des frames (co-pilote étape 3/4, 2026-11-22)

Module `earth_hums.py` (globe néon, ambiance B « télémétrie rétro », 120 BPM). Données `earth_hums.csv` (= earth_hums_draft.csv de l'étape 1).
Durée calculée : **67,2 s** (intro 4,0 · données 1957→2025 = 69 × 0,8 s = 55,2 · outro 8,0). Musique rendue : 68,2 s avec la traîne (coupée par `-shortest`).

## Règle
- 1 bip = 20 objets lancés. Le bip n sonne quand le total cumulé passe 20 × n (interpolation linéaire dans l'année) : 1 243 bips, premier bip en 1959 (cumul 24), 225 bips en 2025.
- Le « bip » de Spoutnik 1 (4 oct. 1957, son radio recréé) ouvre l'intro et revient seul après le silence final ; il n'est pas compté comme un bip de données.
- Points sur le globe : 1 point = 1 bip ; orbites illustratives (inclinaison/hauteur aléatoires), cyan avant 2022, or à partir de 2022.

## Données (2 sources, voir CSV)
- UNOOSA (registre ONU) via Our World in Data, maj 2026-02-25 : total 24 865. Recoupé avec GCAT (J. McDowell, charges utiles, 2026-10-26) : 25 278 (+1,7 %). On affiche UNOOSA.
- Cumul fin 2021 = 12 124 ; 2022-2025 = 12 741 (51,2 %) ; moitié = 12 433 franchie en 2022.
- Plateau 1965-2012 : min 72 (2005), max 170 (1990) — la carte de l'étape 1 disait « 100 à 170 » : corrigé à l'écran en « 72 TO 170 A YEAR ».
- 2019 = 586, 2020 = 1 274 (× 2,17 : « MORE THAN DOUBLE ») ; 2025 = 4 510 (record).

## Points vérifiés sur les frames (t = 0,5 · 3,0 · 30,6 · 56,2 · 58,6 · 59,1 · 60,5 · 62,0 · 66,0 s + variante claire 57,1 / 58,6)
- 30,6 s (1990, 0,25 de l'année) : cumul 3 976 + 42 = 4 018 = HUD ; 16,2 % ✓.
- 56,2 s (2022) : barre « HALF » franchie, flash or, bannière « HALF · 12,433 OF 24,865 · 2022 » ✓.
- 58,6 s (2025) : bannière « 4,510 · IN 2025 · RECORD » ✓ ; 59,1 s : cumul 24 301 = 21 455 (fin 2024) + 0,63 × 4 510 ✓.
- Outro : 24 865 / 1957-2021 · 65 ans · 12 124 / 2022-2025 · 4 ans · 12 741 / 51,2 % ✓ ; question « WHAT WILL 2026 ADD? » ; sources à l'écran.
- Frise du bas : lancements par an en échelle linéaire (le haut = plus grand), barres 2022-2025 en or. Pas d'unité physique (pas de SI/US à faire).
- Lisibilité : HUD / compteur / bannière / frise sans chevauchement ; le label « HALF » sous le repère des 50 % ; rien de coupé. Aucun mot sur la fabrication.
- Accroche : titre à 0,5 s, règle « EVERY BEEP = 20 OBJECTS LAUNCHED » à 1,8 s, 1er bip de Spoutnik à 0,25 s.
