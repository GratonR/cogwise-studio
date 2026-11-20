# Chocs de π — contrôle des frames (co-pilote étape 3/4, 2026-11-20)

Module `pi_clacks.py` (mur + petit bloc 1 kg + gros bloc, compteur géant, tableau des 6 niveaux en bas).
Ambiance retenue à l'étape 2 : B « Compteur mécanique » (120 BPM, chaque choc = clic métallique, gros coup au 1er choc de chaque niveau).
Durée calculée : **65,5 s** (intro 4 · niveaux 5,5 / 6,5 / 7,5 / 8,5 / 9,5 / 14,5 · outro 9,5), tout en temps entiers (120 BPM).

## Données
- Comptes 3 · 31 · 314 · 3 141 · 31 415 · 314 159 = CSV `pi_clacks.csv` = formule ⌈π/arctan√(m/M)⌉−1 (Galperin 2003 ; arXiv:2004.14796).
- Le module re-simule chaque niveau choc par choc au chargement et **s'arrête (assert) si le nombre diffère du CSV**.
- Rapports de masse : 1 · 100 · 10 000 · 1 000 000 · 100 000 000 · 10 000 000 000 (CSV). Petit bloc = 1 kg.

## Points vérifiés sur les frames (intro 2,6 · l1 0,5/2,6/5 · l2 2,5 · l3 3,5/5,6/7 · l4 3,5 · l5 4,5/5 · l6 7/9/13,5 · outro 6/7)
- Compteur = rang du choc dans la simulation à l'instant affiché ; fin de niveau = CSV (3, 314, 314 159 vus).
- Bannière de fin de niveau « PI = 3… / 3.14… / 3.14159… » = colonne pi_digits du CSV.
- Masses SI puis US : 1 kg · 2.2 lb ; 100 kg · 220 lb ; 10 000 kg · 22 046 lb ; 1 000 000 kg · 2.2 million lb ; 100 000 000 kg · 220 million lb ; 10 000 000 000 kg · 22 billion lb (1 kg = 2,20462 lb). Étiquette sur le bloc en tonnes (10 T … 10,000,000 T).
- Tableau du bas : niveaux faits en clair, niveau en cours « ... », à venir « ? ». 6 lignes, rien de coupé (lignes resserrées après 1er contrôle).
- Sens : mur à gauche, gros bloc arrive par la droite ; tailles des blocs non à l'échelle (le gros grossit avec le niveau). Caméra qui recule quand le gros bloc repart (il sortait de l'image au niveau 6 au 1er contrôle).
- « SLOW MOTION » affiché pendant les chocs des niveaux 2 à 6 (ralenti asinh, même déformation pour tous les chocs d'un niveau, ordre gardé).
- Écran : « IDEAL PHYSICS: NO FRICTION, NO ENERGY LOST ». Sources dans l'outro (Galperin 2003, simulation exacte). Pas de glyphe π dans la police : écrit « PI ».
- Aucun mot sur la fabrication.

## Rendu final (étape 4/4, 2026-11-20)
- Étape 3 validée par Guillaume (« Ça me va », palette sombre). Rendu complet : **65,53 s** (ffprobe ; 65,5 s + 1 frame de couverture), 1080×1920, audio AAC.
- Planche contact relue (1 image / 4 s) : compteur 1 · 3 · 31 · 314 · 3 141 · 31 415 · 314 159 cohérent avec le tableau du bas, kg puis lb, rien de coupé.
- Couverture : « 314,159 collisions spell pi » sur l'image de fin (58 s), où compteur et tableau affichent bien 314 159.
