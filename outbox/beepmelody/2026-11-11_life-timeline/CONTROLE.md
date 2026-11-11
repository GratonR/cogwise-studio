# life-timeline — contrôle des frames (étape 3/4, avant rendu complet)

Module `studio/beepmelody/episodes/life_timeline.py`, données `life_timeline.csv` (31 événements, 2 sources par ligne).
Durée calculée : 66,9 s (intro 4,6 · microbes 16,2 · Cambrien→Permien 15,0 · dinosaures 9,2 · nous 13,8 · outro 8,1). 104 BPM.

## Données recoupées (changements par rapport au brouillon de l'étape 1)
- Lignes « TO VERIFY » résolues ou retirées : « first Snowball Earth » et « Snowball Earth again » retirées (pas des formes de vie) ; « first amphibians » retirée (doublon des tétrapodes).
- Signes de vie 3 800 → ~3 700 Ma (Nutman 2016 Nature + Rosing 1999 Science) ; cellules complexes 2 000 → ~1 650 Ma (plus anciens fossiles d'eucaryotes, Knoll / Miao 2024).
- Poissons 500 → ~518 Ma (Chengjiang, NHM + Shu 1999) ; arthropodes 450 → « first land animal (a millipede) » ~428 Ma (Guinness + Wilson & Anderson 2004).
- Forêts 360 → ~386 Ma (Stein 2020) ; dinosaures 233 → ~231 Ma (Eoraptor) ; primates 60 → ~55 Ma (Archicebus).
- Extinctions : % = Barnosky et al. 2011 (Nature, tableau 1) via OWID (86, 75, 96, 80, 76) ; dates ICS 2024-12 (Dévonien = limite Frasnien/Famennien 372,15 → « ~372 » ; Ordovicien « ~444 »).

## Point par point (frames lues)
- 2,6 s (intro) : titre lisible, « every beep = a new kind of life / broken note = mass extinction », horloge vide à 00:00. OK.
- 11,9 s (oxygène) : 2 400 Ma → 11:18:46 (= (4540−2400)/4540 × 24 h) ; « ~2.4 BN YEARS AGO ». OK.
- 21,3 s (Cambrien) : 538,8 Ma → 21:09:06 ; bannière « animals show up at 9 pm ». OK.
- 24,6 s (extinction 1) : 21:39:10, « 86% of species gone », 1/5, repère rouge sur le zoom. OK.
- 34,0 s (extinction 3) : 251,9 Ma → 22:40:06, 96 %, 3/5. OK.
- 51,3 s (Homo sapiens) : 0,3 Ma → 23:59:54.3, « 6 seconds before midnight » (5,7 s arrondi). OK.
- 55,0 s (aujourd'hui) : 24:00:00, « ~8.7 million species (est.) » (Mora 2011). OK.
- Outro : 5 / 96 % / 21:09 / 23:59:54, sources en 4 lignes (corrigé : la ligne débordait à gauche).
- Axes : frise 4,54 Ga → maintenant de gauche à droite ; zoom 540 Ma → maintenant ; étiquettes % alternées en hauteur (96 % et 80 % se chevauchaient).
- Lisibilité : libellés 00:00/06:00/12:00/18:00 éloignés du cadran (ils mordaient sur le bord) ; bannières déplacées entre cadran et frise ; rien de coupé.
- Unités : âges en millions/milliards d'années (pas d'équivalent US pertinent). Estimations marquées « ~ » / « est. ». Aucun mot sur la fabrication.

## Étape 4 — rendu final, variante nuit (décision 3 de Guillaume : « dark »)
- `LIFE_DARK=1` : mêmes données, même mise en page ; frames relues à 2,6 / 21,3 / 34,0 / 51,3 / 55,0 / 62 s : contrastes OK, rouge des extinctions lisible, rien de coupé.
- Rendu final 1080×1920 h264 + AAC, ffprobe 66,93 s (fenêtre 62–75 s OK). Planche contact (1 image / 5 s) relue : horloges = CSV (ex. 518 Ma → 21:15:42).

## v2 — correction de Guillaume (11 nov.) : « il manque l'échelle du vivant (milliards d'espèces, d'individus, de cellules) »
- Nouvel angle : « Life almost ended 5 times. Now: ~10^30 cells. » Même série (31 événements, inchangée) + l'échelle d'aujourd'hui.
- `life_counts.csv` (2 sources par ligne) : bannières « today » sur 4 formes de vie — poissons ~36 000 espèces (Catalog of Fishes CAS + FishBase), arbres ~3 000 milliards (Crowther 2015 Nature + Yale), mammifères ~6 500 espèces (Burgin 2018 J. Mammalogy + MDD), oiseaux ~11 000 espèces (IOC + BirdLife).
- Nouvelle scène « LIFE TODAY, COUNTED » (54,2 → 64,6 s) : 1 nombre = 1 note, hauteur = nombre de chiffres (log10), barre = nombre de chiffres (« (LOG) » à l'écran) : ~8,7 M espèces (Mora 2011 + Dalhousie) · 8,2 milliards d'humains (ONU WPP 2024 + UN News) · ~50 milliards d'oiseaux sauvages (Callaghan 2021 PNAS + NatGeo) · ~3 000 milliards d'arbres · ~20 millions de milliards de fourmis (Schultheiss 2022 PNAS + Phys.org) · ~10^30 cellules microbiennes (Whitman 1998 PNAS 4–6e30 + Flemming & Wuertz 2019 ~1,2e30 → « ~ »). Crash + arpège sur 10^30.
- Frames relues : 1,5 / 2,6 / 22,4 (36 000) / 29,3 (3 trillion) / 37,4 (6 500) / 40,8 (11 000) / 53,5 / 59,0 / 62,5 / 66,0 / 68,0 s. Corrigé : 2e ligne du titre coupée à droite → « NOW: ~10^30 CELLS » ; libellés de la scène de comptage passés sous les nombres (chevauchement).
- Unités : comptes sans unité physique (pas de SI/US). Estimations marquées « ~ » / « EST. ». Aucun mot sur la fabrication.
- Rendu final 1080×1920 h264 + AAC, ffprobe 70,40 s (62–75 s OK), planche contact v2 relue.
