# jupiter-moons — contrôle des frames (co-pilote étape 3, 2026-11-16)

Module `jupiter_moons.py` · données `jupiter_moons_draft.csv` (périodes IMCCE × NASA NSSDC × JPL SSD) +
`jupiter_moons_hits.csv` / `_pos.npz` (positions réelles, théorie de Lieske via Meeus ch. 44, PyMeeus ; `jupiter_moons_hits.py`).
JPL Horizons n'était pas joignable depuis l'environnement : les phases viennent de la théorie analytique (précision bien
meilleure que 1 px à l'écran), recalée sur une direction fixe dans l'espace (on retire la longitude héliocentrique de Jupiter).

## Données
- Fenêtre : 16 nov. 2026 → 16 mars 2027 (120 jours), horloge 1 s = 2 jours, durée totale 67,0 s.
- Tours mesurés sur 130 j vs période IMCCE : Io +0,005 %, Europe +0,003 %, Ganymède +0,016 %, Callisto −0,005 %. OK.
- Relation de Laplace L(Io) − 3 L(Europe) + 2 L(Ganymède) : 176,4° à 183,6° sur toute la fenêtre (théorie : 180°) → les
  trois ne s'alignent jamais du même côté : bannière « THE LOCK » exacte.
- Coups audibles (après l'entrée de chaque couche) : 111 = Io 67 · Europe 28 · Ganymède 12 · Callisto 4 (Callisto entre
  au jour 60 et joue 4 fois, comme demandé à l'étape 2). Premier coup à 1,33 s (< 1,5 s).

## Frames vérifiées (1.2, 3, 11, 13.6, 21, 31.5, 45, 52, 52.6, 59.6, 61, 63.5, 67 s ; palette sombre + claire à 31.5 / 52.6)
- Dates = J0 + jour : J21 = 7 déc. 2026, J41 = 27 déc., J62 = 17 janv. 2027, J89 = 13 févr., J103 = 27 févr., J118 = 14 mars. OK.
- Périodes affichées = CSV : 1,77 / 3,55 / 7,15 / 16,69 j ; heures 42,5 / 85,2 / 171,7 / 400,5 h. OK.
- Rapports : 3,551181 / 1,769138 = 2,007 ; 7,154553 / 1,769138 = 4,044. OK.
- Distances SI puis US : 421 800 km · 262 100 mi ; 671 100 · 417 000 ; 1 070 400 · 665 100 ; 1 882 700 · 1 169 900. OK.
- Compteurs de tours = CSV (ex. J21 : Io 11, Europe 0 ; J118 : 108 coups ; fin : 111). OK.
- Échelle : distances à l'échelle, tailles agrandies (Jupiter ×2, lunes en pixels fixes) → écrit en bas de l'écran.
- Lisibilité : HUD, bannière, bande « THE GROOVE » et pied ne se chevauchent pas ; ligne km du HUD raccourcie (débordait
  pour Ganymède/Callisto en v1). Halo de Jupiter réduit (faisait un anneau parasite). Aucun mot sur l'IA ou la fabrication.
- Reste à revoir au rendu complet : la fin (scène petite quand les 4 orbites sont là) et la variante claire si elle est choisie.

## Rendu complet (étape 4, 2026-11-16 23:50 UTC) — palette sombre validée (« Ça me va »)
- Correctif : Io restait invisible de 0,5 à 1,1 s (fondu d'entrée appliqué à Io au départ de l'horloge, et plantage de la frame 0,5 s) → Io toujours visible. Frames 0,5 / 0,8 / 1,2 s relues.
- Rendu scène par scène (lecture parallèle du .npz corrompue en multiprocessus).
- ffprobe : 67,03 s, 1080×1920, piste audio. Planche contact (1 image / 4 s) relue : dates, compteurs, périodes, km · mi conformes au CSV ; bannières « + GANYMEDE », « THE SLIP », « THE LOCK » lisibles ; fin = récap des 4 périodes + sources. Rien de coupé.
- Couverture : image à 45 s (« THE LOCK »), titre « 3 MOONS, 1:2:4 GROOVE ».

## Retravail r1 — musique R1 « Tambours chantants » (2026-11-17 08:2x UTC, choix de Guillaume, carte decision-jupiter-moons-r1)
- Remarque : « Trop bien mais améliore la musique. Les visuels 3d sont bons » → seule la piste change. Images reprises à l'identique
  (flux vidéo copié de la v1, couverture comprise), aucune donnée ni texte à l'écran modifiés.
- `jupiter_moons.py audio` produit désormais R1 (via `jupiter_moons_moods_r1.py --full`) ; l'ancienne C reste en `audio-c`.
- Harmonie Dm–Bb–F–C qui tourne sur chaque tour de Ganymède (18 changements), mélodie au marimba sur Io, kalimba sur Europe, basse sur Ganymède, gong + chœur sur Callisto.
- Synchro : les 111 coups sont posés à l'instant exact du passage (aucun recalage) ; énergie post/pré-coup médiane ×2,35.
- ffprobe : 67,03 s, 1080×1920, audio AAC. Loudness −20,3 LUFS (v1 : −19,4). Planche contact relue : identique à la v1.
