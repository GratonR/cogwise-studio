# life-timeline — rework angle « count » · contrôle des frames (co-pilote étape 3/4), 2026-11-11

Module `studio/beepmelody/episodes/life_count.py`, données `life_count.csv` (28 lignes, 2 sources par ligne, colonne check = ok).
Durée calculée : 64,9 s (122 BPM, intro 8 temps, comptages à 4 → 2 → 1 temps, drop sur les virus, outro 16 temps).

## Données recoupées (corrections par rapport à la série provisoire)
- Kakapos : 244 → **325** (DOC NZ, communiqué du 1er sept. 2026 ; ODT / Boston Globe).
- Rhinocéros de Java : ~50 (IRF State of the Rhino 2025, en baisse depuis 76 ; Phys.org/AFP 2024).
- Tigres sauvages : affichage « ≈5,500 » (IUCN 2022 : 3 726–5 578 ; GTF 2023 : 5 574).
- Baleines à bosse : « ≈84,000 ADULTS » (IUCN 2018 : 84 000 individus matures).
- Chimpanzés : « UP TO 300,000 » (IUCN : 172 700–299 700).
- Cellules humaines : « 30-37 TRILLION » (Sender 2016 ≈ 30 T ; Bianconi 2013 ≈ 37 T).
- Vaquitas ≈10 (6–8 vus en 2024, CIRVA/IUCN-CSG + Sea Shepherd).

## Frames vérifiées (1,6 · 4,6 · 14,3 · 32,5 · 40,5 · 44,9 · 47,0 · 49,6 · 51,9 · 55 · 58 · 61,5 s ; palette claire + nuit)
- HUD = CSV (valeur affichée, label, nombre de chiffres) sur chaque frame ; nombre écrit en entier = valeur du CSV (Decimal, pas d'arrondi flottant).
- Bannières calculées : 26 Md / 8,2 Md = 3,2 poulets par humain ; 3,04 T / 8,2 Md ≈ 371 arbres ; 2·10^16 / 8,2·10^9 ≈ 2,4 M fourmis ; 38 T bactéries ≈ 30–37 T cellules (Sender 2016) ; 10^31 virus > 1,2·10^30 cellules de bactéries + archées.
- Axe : bas = 1, haut = 10^30, « (LOG SCALE) » annoncé ; la courbe monte toujours (série triée).
- Corrigé pendant le contrôle : tilde illisible dans la police → glyphe ≈ ; titre du graphe coupé → « HOW MANY? (LOG SCALE) » ; lignes de sources de l'outro coupées → recoupées à ≤ 40 car. ; « FROM 1 DIGIT » → « FROM 2 DIGITS » (vaquitas = 10) ; graphe décalé à droite (étiquettes 10^30 collées au bord).
- Comptages sans unité : pas de conversion SI/US à faire.
- Aucun mot sur la fabrication.
