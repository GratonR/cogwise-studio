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

## Rendu final v3 (palette claire, choix de Guillaume à l'étape 3, 2026-11-11)
- `beepmelody_life_v3.mp4` : 1080×1920, ffprobe 64,93 s (fourchette 62–75 s respectée, tempo inchangé 122 BPM).
- Planche contact `contact_sheet_v3.png` relue : HUD = CSV sur chaque vignette (2/28 ≈50 rhinos → 28/28 ≈10^31 virus, 32 chiffres), bannières « THAT'S US », « ≈370 TREES », « MORE VIRUSES », récap et sources lisibles, rien de coupé.
- Stems : `stems_v3/` (music).

## v4 (retouches Guillaume, 11 nov.) — contrôle
- Nom de l'être vivant en GRAND (taille 40, vert, orange au moment de la note) juste au-dessus du nombre, dans le même cadre ; noms longs sur 2 lignes (« HUMAN CELLS / (ONE BODY) »). Rien de coupé (SAR11 (PELAGIBACTER) = 20 car., tient), pas de chevauchement avec les bannières ni le graphe (frames 4,3 / 12,3 / 24,2 / 32,4 / 44,1 / 50,6 / 51,6 / 56 / 64 s relues).
- Chiffres inchangés = CSV (ex. 1,300,000,000 moutons ; 2,9×10^27 = 28 chiffres ; 10^31 = 32 chiffres).
- Rythme : kick dès la 1re seconde, clap 2 et 4, open-hat à contretemps, double-croches de charley, percussion bois syncopée, basse log-drum plus forte, pompage (sidechain) des accords, échos de marimba en croches.
- Hauteur : 10^0→10^31 ramené sur Do3–Mi5 (max MIDI 76 ≈ 659 Hz, contre 108 ≈ 4,2 kHz en v3) ; arpège final plafonné ; timbre adouci sur les notes hautes (moins de partiel métallique, attaque plus douce). Énergie 1–5 kHz sur 46–52 s : 58 % (v3) → 3 % (v4).
- Durée 64,93 s, piste audio présente, planche contact relue.
