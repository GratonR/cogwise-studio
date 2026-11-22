# Nombres de Fermat — contrôle des frames (co-pilote étape 3/4, 2026-11-22)

Module `fermat_primes.py` : mur de 34 cloches (7 × 5), F0 → F33 dans l'ordre (décision 1/4, option A).
Ambiance retenue à l'étape 2 : B « Chiptune enquête » (120 BPM, note juste = ding carré, note fausse = buzzer qui plonge + caisse claire, groove coupé sur F33).
Durée prévue : **66,0 s** (toutes les notes sur une demi-seconde, 120 BPM). Première note à 1,0 s.

## Données (`fermat_primes.csv`)
- 34 lignes F0 → F33 : 5 premiers (1640), 28 non premiers (année de la 1re preuve, 1732 → 2001), F33 inconnu.
- 2e source complétée cette étape : F13 (Math. Comp. 29, 1975), F19 (rieselprime, Riesel 1962-11-16), F21/F25/F26/F27/F30/F32 (Wrathall, Math. Comp. 18, 1964 ; 1963 = année de découverte chez Keller ; F26 aussi rieselprime), F29 (Gostin & McLaughlin, Math. Comp. 38, 1982), F31 (Prime Curios t5k : 1er facteur trouvé le 12 avril 2001 par A. Kruppa, crible de T. Forbes ; + MathWorld).
- **Chaque facteur affiché est re-vérifié par le module au chargement** : `pow(2, 2^n, p) == p - 1` (22 facteurs, tous OK), et le nombre de chiffres = ⌊2ⁿ·log₁₀2⌋ + 1 (34 lignes OK). 641 × 6 700 417 = 2³² + 1 et 274 177 × 67 280 421 310 721 = 2⁶⁴ + 1 vérifiés.

## Points vérifiés sur les frames (t = 2,0 · 9,6 · 16,0 · 23,6 · 25,1 · 33,0 · 41,1 · 46,3 · 50,0 · 55 · 58 · 61 · 62 · 65 ; palette claire + sombre)
- HUD = CSV : F5 = 4,294,967,297 = 641 × 6,700,417 (Euler 1732) ; F7 « 39 DIGITS · NOT PRIME (1905) · PEPIN TEST. 1ST FACTOR: 1970 » ; F12 « 1,234 DIGITS · DIVISIBLE BY 114,689 (1877) » ; F13 « 2,467 DIGITS · DIVISIBLE BY 2,710,954,639,361 (1974) » ; F20 « 315,653 DIGITS · NO FACTOR KNOWN, EVEN TODAY (1987) » ; F27 « 40,403,563 DIGITS · DIVISIBLE BY 151,413,703,311,361 (1963) » ; F32 « 1,292,913,987 DIGITS (1963) » ; F33 « 2,585,827,973 DIGITS · PRIME? NOBODY KNOWS ».
- Compteur du bas RIGHT/WRONG/UNKNOWN = cloches jouées (5 / 28 / 1 à la fin). Frise « YEAR PROVEN » 1640 → 2026 : 1 point par nombre à son année (pile de 7 en 1963 qui ne touche plus le texte).
- Pas d'unité physique dans ce sujet (nombres purs) : règle SI/US sans objet.
- Lisibilité : 1er contrôle → étiquettes F-n qui chevauchaient la cloche du dessous et bannière qui cachait la dernière rangée ; mur passé en 7 × 5 avec étiquette dans la case, bannières déplacées sous le mur. Facteur qui « tombe » sur fond clair pour rester lisible.
- Outro : 5 RIGHT / 28 WRONG / 1 UNKNOWN (F33), « IS THERE A 6TH FERMAT PRIME? NOBODY HAS FOUND ONE IN 386 YEARS » (1640 → 2026), sources (Keller, MathWorld, Prime Pages, Math. Comp.).
- Aucun mot sur la fabrication.

## Rendu final (étape 4/4, 2026-11-22)
- Décision 3/4 : palette claire. ffprobe : 66,03 s, 1080×1920, piste audio OK. Planche contact relue (1 image / 4 s) : F5 Euler, F13, F20 sans facteur, F32 (diviseur 25,409,026,523,137 = 1479·2³⁴+1 vérifié), F33 « ? », outro 5/28/1 + sources. Couverture « Only the first 5 are prime » (t = 0,7 du main) lisible.
