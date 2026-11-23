# polar-night — contrôle des frames (étape 3/4, 2026-11-22)

Décisions co-pilote : 1 = A « Two cities, one sun. One of them goes silent » (équinoxe → équinoxe, 23 sept. 2026 → 22 sept. 2027) ; 2 = A · Duo clair (84 BPM : Tromsø = marimba qui descend et raccourcit, Quito = synthé doux, aurore pendant le silence, note tenue au soleil de minuit).
Module : `polar_night.py` (variante `PN_VARIANT=clear` par défaut, `dusk` = cadre sombre et ciels de crépuscule). Données : `polar_night_draft.csv` (365 jours).
Durée prévue (`info`) : 67,6 s — 365 jours à 6 jours/s (60,7 s, premier jour à 0,6 s) + fin 0,9 s + outro 5,4 s. Dans 62–75 s.

Frames vues : 1.2 / 5.0 / 9.0 / 11.0 / 11.7 / 13.8 / 17.0 / 20.0 / 20.3 / 21.6 / 22.0 / 24.5 / 31.0 / 41.0 / 42.0 / 43.0 / 46.0 / 52.0 / 61.5 / 64.0 / 64.5 s (+ variante dusk 13.8 / 43.0).

## Vérifié point par point
- Étiquettes de ville = CSV (ex. 19 oct. Tromsø 8,55 h → « 8 H 33 MIN » ; 15 janv. 0,62 h → « 37 MIN » ; 27 janv. 4,15 h → « 4 H 09 MIN » ; 4 juin 24 h → « NO SUNSET » ; Quito 12,10–12,14 h → « 12 H 06 » à « 12 H 08 »).
- « 48 DAYS WITHOUT A SUNRISE » = 48 jours à 0 h dans le CSV (28 nov. 2026 → 14 janv. 2027) ; « 68 DAYS WITHOUT A SUNSET » = 68 jours à 24 h (19 mai → 25 juil. 2027). Calcul sur horizon marin ; l'office du tourisme donne ~27 nov. → ~15 janv. et ~20 mai → ~22 juil. (relief, définition) : on affiche les nombres du calcul, la source le précise (« SEA HORIZON »).
- « SAME NOTE. FOR NOW. 12 H 15 VS 12 H 07 » = 23 sept. (12,25 h / 12,11 h). Fin : 22 sept. 12 h 26 vs 12 h 07 → « ALMOST THE SAME NOTE ».
- Arc du soleil : largeur = durée du jour du CSV, hauteur = altitude de midi (déclinaison approchée, illustratif) ; un jour court garde un soleil bas visible (réfraction), arc fermé au-dessus de l'horizon pendant le soleil de minuit, pas de soleil pendant la nuit polaire (aurore à la place).
- Graphe du bas : 0 → 24 h, une marque par jour joué, curseur = jour courant ; Tromsø corail, Quito or (légende au-dessus).
- Latitudes : 69.6° N / 0.2° S (CSV : 69,6492 N ; 0,2299 S). Pas d'unités à convertir (heures).
- Lisibilité : corrigé pendant le contrôle — date du HUD qui chevauchait la légende (légende déplacée au-dessus du graphe), montagnes qui cachaient le soleil bas, bannières qui cachaient le soleil de Quito (remontées sur le fjord), bannière « THE SUN IS BACK » placée dans le ciel pour laisser voir le soleil qui revient. Rien de coupé.
- Aucune mention d'IA ni de fabrication.

## Étape 3 retravaillée (2026-11-22, remarque de Guillaume : « Cadre jour nuit au fil de la video »)
Nouveau réglage `PN_FRAME` : `tromso` (défaut proposé : cadre + cases suivent la durée du jour à Tromsø, lissée sur ±4 jours ; nuit = bleu marine, jour = crème, soleil de minuit = crème doré), `split` (moitié haute suit Tromsø, moitié Quito reste en jour), `edge` (seul le cadre extérieur change, cases crème), `none` (ancien rendu).
Frames vues (3 variantes) : 1.2 / 5.0 / 8.0 / 9.0 / 11.7 / 15.0 / 20.3 / 26.0 / 31.0 / 43.0 / 49.0 / 52.0 / 61.5 / 64.5 s.
- Les cases passent d'un coup clair ↔ sombre au seuil (~6 h de jour lissé) : une 1re version en fondu donnait ~3 s de cases grises au texte gris, corrigée. Texte lisible partout.
- Données, chiffres, bannières, musique et durée (67,6 s) inchangés.

## Rendu final (étape 4/4, 2026-11-22)
Décision 3b : A · tout l'écran suit Tromsø (`PN_FRAME=tromso`). Rendu `POP_STYLE=v1 PI_FX=0.8 PN_FRAME=tromso`.
ffprobe : 67,57 s, 1080×1920, piste audio présente. Planche contact (1 image / 4 s) relue : nuit et aurore de 11 à 20 s, soleil de minuit doré de 40 à 52 s, fin crème « ALMOST THE SAME NOTE », écran de fin avec la source ; rien de coupé. Couverture : « Two cities, one sun » sur l'image à 15 s (aurore), lisible.

## Retravail « One cities » — étape 3/4 Tromsø seule (2026-11-23)
Décisions : r1 = une seule ville (Tromsø) ; r2 = B « 48 Days of Night. Then 68 Days of Day » (miroir, compteur 0 h → 24 h) ; r3 = A · Marimba claire 84 BPM (une seule voix, note tenue sous le soleil de minuit, aurore pendant le silence).
Module : `polar_night_solo.py` (mêmes données `polar_night_draft.csv`, même horloge 6 jours/s). `info` : 67,57 s ; 254 notes de marimba + 68 ticks (soleil de minuit, note tenue) ; 48 jours muets ; cadre jour/nuit qui suit Tromsø (décision 3b conservée).
Frames vues : 1.2 / 2.0 / 3.0 / 5.0 / 6.0 / 9.0 / 11.7 / 12.6 / 13.0 / 15.0 / 19.7 / 20.6 / 28.0 / 33.0 / 40.4 / 41.4 / 42.0 / 46.0 / 55.0 / 61.4 / 62.0 / 62.2 / 64.5 s (+ variante compteur en haut, écartée : elle cache l'arc du soleil d'été et les aurores).
- Compteur = CSV : 26 sept. 11,83 h → « 11 H 50 MIN » ; 19 oct. 8,55 → « 8 H 33 » ; 25 oct. 7,65 → « 7 H 39 » ; 12 nov. 4,67 → « 4 H 40 » ; 15 janv. 0,62 → « 37 MIN » ; 21 janv. 2,84 → « 2 H 50 » ; 6 mars 10,27 → « 10 H 16 » ; 5 avr. 14,56 → « 14 H 34 » ; 15 août 18,11 → « 18 H 07 » ; 22 sept. 12,43 → « 12 H 26 ». 0 h → « NO SUNRISE · 0 H OF SUN », 24 h → « NO SUNSET · 24 H OF SUN ». Jauge 0 → 24 h, repère à 12 h.
- Bannières miroir (même boîte, même taille) : « 48 DAYS OF NIGHT · 28 NOV TO 14 JAN » (48 jours à 0 h dans le CSV) / « 68 DAYS OF DAY · 19 MAY TO 25 JUL » (68 jours à 24 h). « -9.8 MIN EVERY DAY · 15 OCT TO 15 NOV » et « +8.6 MIN EVERY DAY · 2 MAR TO 1 APR » calculés sur le CSV (moyenne). « THE SUN IS BACK · 15 JAN: 37 MIN », « BACK TO 12 H · 22 SEP: 12 H 26 MIN ».
- Écart horizon mer / relief (visittromso.no : ~27 nov. → ~15 janv., ~20 mai → ~22 juil.) : l'écran affiche les chiffres du calcul, la source dit « SEA HORIZON ».
- Corrigé pendant le contrôle : la flèche « → » n'existe pas dans la police (remplacée par « TO »), « ALL DAY » ambigu sous « NO SUNRISE » (remplacé par « 0 H OF SUN » / « 24 H OF SUN »).
- Lisibilité : rien de coupé, pas de chevauchement HUD/bannière/compteur/graphe ; texte clair sur fond sombre la nuit. Pas d'unité à convertir (heures). Aucune mention d'IA ni de fabrication.
