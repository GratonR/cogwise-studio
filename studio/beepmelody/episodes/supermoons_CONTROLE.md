# Super-lunes — contrôle des frames (co-pilote étape 3/4, 2026-11-19)

Module `supermoons.py` (scène : Terre, lumière du Soleil à gauche, la Lune à chaque pleine lune sur une orbite ovale schématique
« NOT TO SCALE » qui tourne une fois par 411,8 j ; arc doré = zone « 90 % du périgée »). Musique : choix B « Marée » (118,3 BPM calé sur le cycle).
`info` : 69,74 s (intro 3,5 · 1900-32 14,4 · 1932-64 14,4 · 1964-96 14,4 · 1996-2026 + fin 17,45 · outro 5,58), 506 notes, 32 « closest ».

Frames lues (night) : 2,6 · 5,4 · 8,93 · 9,6 · 25,5 · 38 · 40,3 · 56,12 · 56,8 · 61 · 62,4 · 66 · 68 ; light : 9,6 · 38 · 56,12.

Chiffres = CSV (DE421 ; PyEphem ≤ 2,9 km ; Espenak ≤ 4 km) :
- #15 2 mars 1904 : 357 655 km · 222 237 mi ✓ ; #48 4 janv. 1912 : 356 375 km · 221 441 mi ✓ (le plus proche 1900-2026) ;
- 26 janv. 1948 : 356 490 km, aucune plus proche avant le 25 nov. 2034 (356 446 km, DE421 = PyEphem, table Espenak) ✓ ;
- #471 14 nov. 2016 : 356 520 km · 221 531 mi, plus proche depuis 1948 ✓ ; #506 24 nov. 2026 : 360 765 km · 224 169 mi ✓ ;
- fantômes : 24 déc. 2026 (356 738), 22 janv. 2027 (357 644), 20 févr. 2027 (363 306) : rel ≥ 0,90 → « 1ST OF 4 IN A ROW » ✓.
- 2034 dans l'outro : 356 446 km · 221 485 mi ✓ (« closest coming up », pas « aussi proche que 1912 » : corrigé).

Corrigé pendant le contrôle : distance de la Lune interpolée entre pleines lunes (HUD 356 375 / scène 358 116 au flash) → la scène montre
maintenant la dernière pleine lune exacte (HUD = scène au flash) ; légende de la frise qui chevauchait le compteur ; bannières trop hautes
sur l'étiquette de la Lune ; lunes fantômes sur l'étiquette ; flash blanc illisible en palette claire (→ corail) ; orbite recentrée.
SI puis US partout ; axes : frise 1900 → 2027 gauche → droite, trait plus haut = plus proche ; rien de coupé ; aucune mention d'IA.
