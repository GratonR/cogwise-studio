# mersenne-list — contrôle des frames (étape 3/4, 2026-11-22)

Décisions co-pilote : 1 = « liste » (« In 1644 a friar listed 11 special numbers. 5 were wrong. »), 2 = A · De la plume à la machine (clavecin + orgue ré mineur, puis chiptune carré sur pulsation 104 BPM à partir de 1952).
Module : `mersenne_list.py` (variante `ML_VARIANT=era` par défaut, `parch` = parchemin clair tout du long). Données : `mersenne_list_draft.csv` (57 lignes, 2 sources par ligne).
Durée prévue (`info`) : 71,0 s — acte 1 9,6 s · acte 2 (corrections + scène Cole) 23,1 s · acte 3 33,1 s (40 premiers, horloge 0,4 s / an, 1952 → 2024) · outro 5,2 s. Dans 62–75 s, tempo non triché.

Frames vues : 1.5 / 4.0 / 5.0 / 8.0 / 11.0 / 13.0 / 14.6 / 18.0 / 21.0 / 21.6 / 22.6 / 23.6 / 26.3 / 29.5 / 33.0 / 40.0 / 45.0 / 50.5 / 57.0 / 63.0 / 68.5 / 69.0 s (+ variante parchemin 33.0 / 50.5 / 63.0 / 68.5).

## Vérifié point par point
- Liste 1644 : 2, 3, 5, 7, 13, 17, 19, 31, 67, 127, 257 = CSV (Archibald « Mersenne's Numbers » + PrimePages glossary). Erreurs : 67 et 257 composés, 61, 89, 107 manquants → « 5 WERE WRONG · 2 NOT PRIME · 3 MISSING ».
- Corrections (dates = Archibald, notes 8, 9, 13, 14, 17) : Lucas M127 premier 1876 (« THE LIST WAS RIGHT », non compté comme erreur corrigée) ; Pervushin M61 1883 ; Cole M67 1903 (Bull. AMS déc. 1903 ; séance d'octobre 1903 à New York) ; Powers M89 1911 et M107 1914 ; Lehmer M257 composé 1931 (Sphinx, mai 1931 ; Kraitchik 1922 sans garantie). Compteur « MISTAKES FIXED » 0 → 5 = 61, 67, 89, 107, 257.
- « 287 YEARS TO FIX ONE LIST (1644-1931) » = 1931 − 1644. « 21 YEARS OF NOTHING » = 1931 → 1952. « 232 YEARS » = 1644 → 1876.
- Tableau de Cole : 2^67 − 1 = 147 573 952 589 676 412 927 = 193 707 721 × 761 838 257 287 (vérifié par calcul dans le module, `assert`). Anecdote muette écrite « THE STORY GOES ».
- « Friar » : Mersenne frère minime (MacTutor, Stanford Encyclopedia).
- Acte 3 : 40 tickets = CSV (rang, exposant, nombre de chiffres, découvreur/machine) ; ordre = date de découverte (M110503 #29 arrive en 1988 après #30/#31, idem #47 avant #45/#46 en 2008 : c'est la réalité). Le HUD dit « NEW MERSENNE PRIME » (pas « le plus grand ») pour cette raison. Dernier : 2^136 279 841 − 1, 41 024 320 chiffres, oct. 2024, ticket « NEW » (rang 52 provisoire chez GIMPS, on écrit « largest prime known »).
- Bannières acte 3 : « 1952: 5 IN ONE YEAR · ONE MACHINE (SWAC) » (5 lignes SWAC 1952 du CSV) ; « 1996: A HOME PC FINDS ONE (PENTIUM 90 MHZ) » (#35 Armengaud, GIMPS) ; « 41,024,320 DIGITS ».
- Pas d'unité physique : pas de conversion SI/US nécessaire.
- Sens : frise 1644 → 2024 de gauche à droite, une marque par événement (vert = premier confirmé/trouvé, rouge = composé, ambre = trouvé par machine). Hauteur de note = log(p) (actes 1-2) / log(chiffres) (acte 3).
- Lisibilité : corrigé pendant le contrôle — ticket final qui se chevauchait (« NEW M136,279,841 »), tickets masqués sous la bannière finale, bloc DATA qui cachait la carte graphique à l'outro, compteur d'erreurs qui comptait Lucas, roulement des années pendant la scène Cole. Rien de coupé, HUD/bannières/page sans chevauchement.
- Aucune mention d'IA ni de fabrication.
