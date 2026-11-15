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
