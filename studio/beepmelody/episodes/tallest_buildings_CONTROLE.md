# tallest-buildings — contrôle des frames (étape 3/4, 2026-11-20)

Frames vues : 2.0 / 4.2 / 13.5 / 19.6 / 21.0 / 37.0 / 47.0 / 52.0 / 57.2 / 61.0 s (+ variante crépuscule 21.0 / 52.0).
Durée prévue : 65,6 s (intro 3,2 · 1890→2026 à 1 an = 1 temps de 0,4 s · outro 8). 14 records.

## Données tranchées avant rendu (≥ 2 sources)
- WTC tour nord : **1971** (Skyscraper Museum : « Empire State #1 for forty years, until the completion of the North Tower in 1971 » ; Wikipedia/CTBUH 1971). 417 m · 1,368 ft.
- Sears : **1974**, 442 m · **1,451 ft** (CTBUH Skyscraper Center : 442.1 m, completion 1974, tallest 1974-1998 ; Dezeen 1974).
- Taipei 101 : **508 m** · 1,667 ft (CTBUH hauteur architecturale ; Dezeen 508). Le 509 m du Skyscraper Museum est à la pointe.
- Burj Khalifa : janv. **2010**, 828 m · 2,717 ft.
- Corrigés au passage : NY World 309 ft (au lieu de 308), 40 Wall 927 ft (au lieu de 928), Park Row 391 ft (CTBUH ; le musée dit 386 ft / 118 m).

## Vérifié point par point
- HUD = CSV pour les 14 records (m puis ft, rang #n/14, ville). Graduations : 100 m = 328 ft, 200 m = 656 ft, 400 m = 1,312 ft, 800 m = 2,625 ft (×3,28084).
- Bannières : « THEN 17 YEARS OF NOTHING » (avr. 1913 → avr. 1930), « 3 RECORDS IN 13 MONTHS » (avr. 1930 → mai 1931), « EMPIRE STATE #1 FOR 40 YEARS » (1931 → 1971), « FIRST RECORD OUTSIDE NEW YORK » (Sears, Chicago ; les 10 premiers sont à New York), « THE TITLE LEAVES THE USA » (1998, Skyscraper Museum), « +320 M IN ONE JUMP / +1,050 FT » (828 − 508 ; 2,717 − 1,667), « STILL #1 » ; compteur final « #1 FOR 16 YRS » (janv. 2010 → nov. 2026).
- Sens : hauteurs à l'échelle (linéaire, sol en bas), la caméra recule pour garder le champion dans le cadre ; silhouettes stylisées, hauteurs exactes.
- Lisibilité : grands titres ≤ 18 caractères, graduations à gauche et masquées sous les bannières, rien de coupé ; aucune mention de fabrication.

## Rendu final (étape 4, 2026-11-20)
- Durée ffprobe : 65,57 s · 1080×1920 · audio AAC. Planche contact relue (1 image / 4 s) : HUD = CSV, bannières à leur place, rien de coupé. Couverture posée (t = 52 s).

## Retravail r1 — « Rythme trop lent » → chaque étage = un tic (étape 3, 2026-11-20)
Horloge : 1 étage = 1 triple-croche à 150 BPM (0,05 s), boum tenu 2 temps (0,8 s), années vides sautées (« >> +17 YRS » dans le HUD, l'année défile pendant le boum). Ambiance A · Chantier gardée (décision r2).
Durée prévue : 71,85 s (intro 3,2 · 1 037 étages 51,85 · 13 tenues 10,4 · queue Burj 2,8 · outro 4,6) — dans 62–75 s, tempo non modifié.
Frames vues : 1.0 / 2.8 / 3.2 / 3.6 / 4.0 / 12 / 17.3 / 19 / 23.5 / 27 / 32.0 / 32.1 / 32.6 / 34.5 / 37 / 40 / 47 / 49.9 / 50 / 60 / 62.5 / 64.5 / 65.6 / 67 / 69 / 71 s.
- Compteur « FLOOR f / n » = colonne floors du CSV (CTBUH + 2e source) pour les 14 tours ; total affiché à l'outro 1,037 = somme du CSV.
- Années : l'année du record reste affichée au boum (roulement à partir de +0,25 s) ; sauts +4 · +5 · +9 · +1 · +4 · +17 · +1 MONTH · +1 · +40 · +3 · +24 · +6 · +6 · +16 (2010 → 2026) = écarts du CSV.
- Bannières recalées : « 17 YEARS, NO NEW RECORD / THEN NEW YORK GOES WILD » (1913 → 1930, 3 records en 13 mois ensuite), « MORE FLOORS THAN THE EMPIRE STATE (102) » au 103e étage du Burj (compte d'étages, pas de hauteur), les autres inchangées.
- Tour en chantier : silhouette coupée à l'étage courant (hauteur = fraction d'étages × hauteur architecturale, approximation visuelle ; la hauteur exacte est atteinte au boum), grue au sommet. Caméra : recule dès que la tour en chantier dépasse le champion.
- Lisibilité : graduations masquées sous la bannière d'intro et les bannières ; HUD 2 lignes (champion en haut, tour en chantier en bas) sans chevauchement ; aucune mention de fabrication.
