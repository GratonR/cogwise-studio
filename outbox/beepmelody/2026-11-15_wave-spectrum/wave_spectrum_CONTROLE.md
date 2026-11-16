# wave-spectrum — contrôle des frames (étape 3/4, 2026-11-15)

Données : `wave_spectrum.csv`, 29 découvertes 1666 → 2023, 2 sources par ligne (NASA, NIST, NRAO, Nobel, LIGO/Caltech, Chandra, ESO, papiers DOI).
Changements vs la série candidate (étape 1) : Marconi 1901 retiré (fréquence débattue, signal fabriqué) ; ajoutés Jupiter 1955 (22,2 MHz),
Spoutnik 1957 (20,005 MHz), pulsar binaire Hulse–Taylor 1974 (orbite 7,75 h → onde gravitationnelle ≈ 7×10^-5 Hz), GW170817 en 2017.
Fréquences estimées marquées « est. » à l'écran (Newton, IR, UV, X, gamma, Krakatoa, chauves-souris, baleines).

Preview (palette sombre) : 0,6 / 2,6 / 7,4 / 15,2 / 18,2 / 31,8 / 36,4 / 41 / 46,2 / 51,6 / 52,9 / 55,7 / 56,7 / 59,5 / 66,5 s + palette claire 41 / 52,9 s.
- Durée prévue 68,6 s (8 + 105 + 10 + 12 temps à 118 BPM) ✔ 62–75 s. 29 notes = 29 lignes du CSV ; accroche : note la plus grave (0,25 s) puis la plus aiguë (2,3 s).
- 147 octaves : log2(3,4e29 / 1,8e-15) = 147,1 ✔. LHAASO 1,4 PeV / h = 3,4e29 Hz ✔. 694,3 nm → 432 THz ✔ ; 589 nm → 509 THz ✔ ; 587,6 nm → 510 THz ✔.
- Longueurs d'onde SI puis US : 14,6 m · 48 ft ; 13,5 m · 44 ft ; 15 m · 49 ft ; 21 cm · 8,3 in ; 3,7 m · 12 ft ; 7,35 cm · 2,9 in ; 1,3 mm · 0,05 in ; 66 cm · 26 in ✔ (pas d'équivalent US sous le mm).
- Axe : règle LOG « waves per second », gauche = lent, droite = rapide ✔ ; note plus aiguë = onde plus rapide (annoncé en pied de page).
- Lisibilité : bannières déplacées dans le bas de l'oscilloscope (elles chevauchaient la règle) ; anneaux sonores coupés au cadre ; grille gravité éclaircie. Rien de coupé, libellés ≤ 33 car. Aucune mention d'IA.
- Krakatoa : formulation prudente « logged 7 times » (les barographes ont enregistré l'onde jusqu'à 7 passages), pas « 7 tours ».

## Rendu final (étape 4/4, 2026-11-15)
- Visuel validé par Guillaume (étape 3 : « Ça me va », palette sombre).
- ffprobe : 68,67 s, 1080×1920, 30 fps, piste audio AAC ✔ (62–75 s).
- Planche contact relue : 29/29 notes, HUD/bannières/règle sans chevauchement, outro chiffres + sources lisible.
- Couverture : fond à 51,5 s (LIGO), titre « 147 OCTAVES OF WAVES », lisible, rien de coupé.

## Retravail r1 — rendu v2 (2026-11-15, son C + visuel C)
- Remarque de Guillaume (21:07) : « change le son et les visuels… faire matcher le son avec l'onde ? … visuels funky 3D ? ».
  Étape 2 → C (synthwave 98 BPM, chaque onde joue sa vraie note ramenée de N octaves, trémolo selon la fréquence, basse en octaves qui suit l'onde).
  Étape 3 → C (terrain fil de fer 3D qui ondule à la vitesse de l'onde ; gravité = toile de l'espace-temps ; LIGO : deux trous noirs qui spiralent puis fusionnent).
- Donnée corrigée : trou noir de Persée 1,8e-15 → 1,62e-15 Hz = si bémol 57 octaves sous le do central (233,08 Hz / 2^57), comme le disent Chandra et NASA ;
  il joue donc bien un B♭ (MIDI 46). 147 octaves : log2(3,4e29 / 1,62e-15) = 147,2 ✔. Affichage inchangé (« ~2×10^-15 HZ »).
- Notes réelles vérifiées : baleine 400 Hz → sol 4 (vraie hauteur) ; étoiles à neutrons ~100 Hz → sol 2 (vraie hauteur) ; LIGO = vrai chirp 35 → 250 Hz.
- Tempo 98 BPM, écarts retimés (6 + 88 + 8 + 10 temps) : durée 67,97 s ✔ 62–75 s, 29 notes = 29 lignes du CSV.
- Frames preview 0,6 / 2,6 / 7,2 / 13,4 / 29,5 / 34,8 / 44,6 / 49,3 / 50 / 51,5 / 54,5 / 55,6 / 57,7 / 62 / 66 s : HUD, bannières, règle et pied de page sans chevauchement ;
  anneau EHT déplacé sous le HUD (il était caché) ; crêtes plus serrées pour les ondes rapides (gamma) que pour les lentes ✔ ; rien de coupé ; aucune mention d'IA.
- ffprobe : 67,97 s, 1080×1920, 30 fps, AAC ✔. Planche contact relue. Couverture : fond 50,3 s (LIGO), « 147 OCTAVES OF WAVES ».
- Repères : Spoutnik 0:28 · trou noir 0:44 · LIGO 0:49 · LHAASO 0:55.

## Retravail r2 — rendu v3 (2026-11-16, visuels A « voyage » + son A « sources réelles »)
- Remarque de Guillaume (15 nov., 23:05) : innover sur les angles et mouvements de caméra, sur la représentation des ondes, pousser le son en restant réaliste.
  Étape 3 → A (r3) : route 3D du spectre, la caméra voyage d'une découverte à la suivante puis tourne autour de la source (contre-plongée pour le son, hauteur d'œil pour la lumière, plongée pour la gravité).
  Étape 2 → A (r4) : lit synthwave 98 BPM conservé, chaque onde jouée par le timbre de sa vraie source, sur sa vraie note (radio = souffle + porteuse, Spoutnik = bip marche/arrêt, pulsar = tics, fond cosmique = neige, laser = son pur, X/gamma = crépitement Geiger, baleine/éléphant/chauve-souris = forme de leur cri, LIGO = vrai chirp 35 → 250 Hz).
- Donnée : trou noir de Persée 3,23e-15 Hz (période ~10 millions d'années, Chandra) ; écart log2(3,4e29 / 3,23e-15) = 146,2 → « 146 OCTAVES » partout (accroche, bannière finale, outro, couverture). Ligne HUD raccourcie : « ONE WAVE EVERY ~10 MILLION YEARS » (l'ancienne était coupée). Bannière : « B-FLAT, 57 OCTAVES BELOW MIDDLE C » (formulation de Chandra).
- Frames preview 0,6 / 2,8 / 4,2 / 7,2 / 15,5 / 28,6 / 29,4 / 34,9 / 44,7 / 49,6 / 50,5 / 51,8 / 54,4 / 55,2 / 56,5 / 58 / 59,2 / 62,5 / 66 s : chiffres = CSV, unités SI puis US (15 m · 49 ft ; 7,35 cm · 2,9 in ; 1,3 mm · 0,05 in), règle LOG lent → rapide, crêtes plus serrées pour les ondes rapides ; légende de caméra masquée sous les bannières et pendant l'accroche ; rien de coupé ; aucune mention d'IA.
- Rendu : ffprobe 68,0 s, 1080×1920, 30 fps, AAC ✔ (62–75 s), 29 notes = 29 lignes du CSV ; niveau moyen −18,9 dB, crête −1,9 dB. Planche contact relue. Couverture : fond 50,3 s (LIGO), « 146 OCTAVES OF WAVES ».
- Repères : Spoutnik 0:29 · trou noir 0:44 · LIGO 0:49 · LHAASO 0:55.
