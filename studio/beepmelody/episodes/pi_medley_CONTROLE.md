# Chocs de π · retravail r1 « trois expériences » — contrôle des frames (étape 3/4, 2026-11-20)

Module `pi_medley.py` (données et instants : `pi_medley_data.py`, graines fixes 27 et 7). Ambiance retenue (r1 étape 2) : B « Labo électro », 140 BPM.
Durée calculée : **71,0 s** (acte 1 0–22 · acte 2 22–44 · acte 3 44–65,8 · outro 5,2 s). Musique : 71,5 s (RMS régulier par tranche de 5 s, pas de trou).

## Données (= écran)
- Acte 1 : 3 · 31 · 314 · 3 141 · 31 415 chocs (niveaux 1→5, rapports 1 · 100 · 10 000 · 1 000 000 · 100 000 000). Le module re-simule chaque niveau et **s'arrête (assert) si un compte diffère** des événements de `pi_medley_data` ou des chiffres de π. Masses SI puis US : 100 KG · 220 LB ; 1 000 000 KG · 2.2 MILLION LB ; 100 000 000 KG · 220 MILLION LB.
- Acte 2 : 1 400 aiguilles, 891 croisent → 2 × 1 400 / 891 = **3,1425** (affiché à 4 décimales). Aiguille = écart des lattes (20 px = 20 px) ; le croisement vient de la donnée (y, θ), la position le long de la latte et la bande sont tirées à part (affichage seul).
- Acte 3 : 6 000 fléchettes, 4 712 dedans → 4 × 4 712 / 6 000 = **3,1413**. Quart de disque centré en bas à gauche, rayon = côté du carré.
- Compteurs live vérifiés aux frames (t = 20,5 : 31 404 chocs ; 32 : 180 aiguilles / 119 → 3,0252 ; 43,2 : 1 348 / 854 → 3,1569 ; 56 : 5 915 / 4 646 → 3,1418, 4 × 4 646 / 5 915 = 3,1418 ✓).

## Frames relues (t = 1 · 2 · 3 · 4 · 12 · 20,5 · 21,8 · 22,3 · 32 · 43,2 · 43,9 · 44,3 · 56 · 65,4 · 67 · 70 ; palette claire 12 · 32 · 56)
- Titre « 3 EXPERIMENTS. 1 NUMBER. » + « LISTEN TO PI » avant 1 s, premiers chocs dès 0,6 s ; règle « EVERY BEEP = ONE … » sous le compteur à chaque acte.
- « SLOW MOTION » sur les niveaux 2 à 5 ; « SIMULATION » sur les actes 2 et 3 ; outro : « NEEDLES + DARTS: SIMULATED DROPS », « BLOCKS: EXACT, NO FRICTION ».
- Bandeau du bas « 3 WAYS TO FIND PI » : niveau en cours (chocs du niveau, pas le cumul — corrigé après 1er contrôle), estimations live, « TRUE PI 3.14159… » pour comparer.
- 1er contrôle : à la fin de l'acte 2 tout le plateau était doré (illisible) → les aiguilles de plus de 1,5 s s'estompent, les nouvelles restent vives.
- Rien de coupé, pas de chevauchement HUD / bannière / bandeau. Pas de glyphe π dans la police : écrit « PI », « ≈ » dessiné.
- Sources dans l'outro : Galperin 2003 · Buffon 1777 · Metropolis & Ulam 1949. Aucun mot sur la fabrication.
