# Geminids 2026 — contrôle avant rendu (2026-11-24, mode autonome, pitch v-v-20261123-0440-4)

## Donnée (modèle, annoncé « EXPECTED (MODEL) » à l'écran et dans l'outro)
Météores attendus par heure, nuit du 13 au 14 déc. 2026, vus de 40° N 75° W (EST), ciel parfait : HR = ZHR(t) · sin(hauteur du radiant), compté du crépuscule au lever de l'aube astronomiques.
Pas de comptage réel exploitable (pages IMO « live » et figures CARMELO inaccessibles en chiffres) → modèle standard IMO, dit tel quel à l'écran.

| Valeur à l'écran | Valeur CSV / calcul | Sources |
|---|---|---|
| ZHR 150 au pic | ZHR_MAX = 150 | IMO 2026 Meteor Shower Calendar (tableau 5) ; IGN Espagne (« up to 150 ») ; RMG/EarthSky donnent 120 (valeur prudente) |
| Pic 14 déc. 14:00 UT | PEAK | IMO calendar 2026 ; IGN (« centered at 14h universal time ») — EarthSky annonce 05:44 UT : écart noté, IMO retenu |
| Pic large (ZHR ≥ 100 sur ~11 h) | B = 0,78 /° | IMO (« ZHR of 100 and more over roughly 10–12 hours ») ; IGN (« broad peak of around 12 hours ») |
| Radiant 7h28 +33° | geminids_data.py | IMO calendar 2026 (α 112°, δ +33°) ; IMO Activity Outlook 13–19 déc. 2025 (07:28 +33) |
| 6:12 PM « dark enough », 5:36 AM dawn | crépuscule/aube astro (Soleil −18°) | PyEphem |
| 8:45 PM moonset, croissant ≈ 20 % | 20:45 EST, 20,8 % | PyEphem ; RMG + Farmers' Almanac (« sets around 9 p.m. »), IGN (« illumination of around 20 % ») |
| 1:55 AM Gemini au plus haut (82,9°) | max radiant_alt_deg | PyEphem ; EarthSky (« highest around 2 a.m. »), IMO (culmination 02h heure locale) |
| 94 / hour, 3:30 AM | max expected_per_hour = 94,1 à 03:30 | calcul du CSV |
| ≈ 690 en une nuit | cumulative = 692,3 | calcul du CSV ; 138 bips × 5 = 690 |
| 35 km/s · 22 mi/s | 35 km/s = 21,7 mi/s | IMO calendar 2026 + IGN (35 km/s) ; Farmers' Almanac (22 mi/s) |
| 3200 Phaethon, astéroïde rocheux (pas une comète) | — | RMG ; Farmers' Almanac (« rocky asteroid ») ; EarthSky (découvert 11 oct. 1983, IRAS ; « rock comet ») |

## Frames contrôlées (out_geminids/t*.png, planche contact.png)
0,4 s titre · 16,5 s moonset · 22 s Phaethon · 27 s 35 km/s · 42,6 s 1:55 AM · 50,3 s 94/hour · 60,8 s dawn · outro.
- Chiffres affichés = CSV (HUD : taux interpolé, cumul « SO FAR », 0 après l'aube → « TOO BRIGHT »).
- Axe du graphe : le haut = plus de météores/heure, 0–100, 6PM → MIDNIGHT → 6AM. Unités SI puis US (35 km/s · 22 mi/s).
- Lisibilité : HUD ligne 3 raccourcie (chevauchement corrigé), étiquettes d'axe remontées (coupées en v0), constellation réduite à Castor–Pollux (la projection panoramique étirait la figure). Rien de coupé, aucune mention d'IA.
## Son (règle 23/11)
loop: Dm9–Bbmaj7–Fmaj7–Cadd9 96 BPM · 1 h de nuit = 2 mesures · data → combien de notes d'un motif fixe de 2 mesures sonnent dans l'heure (degré dans l'accord, 1,5 octave) · courbe (hauteur du radiant) → filtre du pad + entrée kick/basse/hats/caisse claire · break : 2 AM (radiant au plus haut) · drop : 3–4 AM, lead à l'octave + arpège à 3:30 · carillon à chaque heure · aube : accord de ré majeur.
Mesure : part d'énergie 2–8 kHz ≤ 2,9 % sur tous les passages (le plus chargé 47,5–52,5 s : 2,6 %), pic 0,60 : pas de sirène ni d'aigu strident.
## Rendu
67,50 s (ffprobe), 1080×1920, piste audio. Couverture « One night of Geminids » à 50,3 s.

## Retouche v2 (24/11, remarque de Guillaume : « Vérifiez tous les chiffres. Expliquer mieux l'expérience au début. Vérifiez les visuels -> rotation décor, angles etc... » ; portée : visuels, données, textes)
### Chiffres re-vérifiés (≥ 2 sources chacun)
- Pic 14 déc. 2026 14:00 UT, jusqu'à 150/h, pic large ~12 h : IGN (« centered at 14h universal time », « up to 150 », « broad peak of around 12 hours ») + Star Walk 2026 (« December 14 at approximately 14:00 GMT », « up to 150 », « more than 100 meteors per hour can last 10–12 hours »). EarthSky donne 5:44 UT et ZHR 120 : minoritaire, on garde IMO/IGN/Star Walk.
- 35 km/s · 22 mi/s : NASA (« 22 miles (35 kilometers) per second ») + IGN (35 km/s). 35 km/s = 21,7 mi/s ✓.
- 3200 Phaethon, astéroïde : NASA (« 3200 Phaethon (an asteroid or a possible "rock comet") ») + EarthSky + Star Walk.
- Lune ≈ 20 % : IGN + Star Walk ; PyEphem 20,3 % (18 h) → 20,8 % (01 UT). Coucher : 8:48 PM (corrigé, était 8:45).
- Radiant au plus haut 1:55 AM, 82,9° : PyEphem ; EarthSky (« highest around 2 a.m. »). Lever du radiant au NE (az 48,6° à 6:12 PM) → bannière corrigée « GEMINI RISES IN THE NORTHEAST » (était « in the east »).
- CSV régénéré par geminids_data.py : identique à la v1 (94,1/h à 3:30, 692,3 au total, 138 bips). Étoiles nommées (RA/Dec J2000) recontrôlées sur le catalogue Yale.
### Intro
0–2,5 s accroche ; 2,5–9,2 s carte explicative ligne par ligne : où on est (côte Est US, 40° N 75° W, ciel parfait), la nuit entière du crépuscule à l'aube, 1 heure = 5 s, 1 bip = 5 étoiles filantes (nombre attendu), la caméra suit Gémeaux (NE → S → O). Puis « GEMINI RISES IN THE NORTHEAST / EVERY METEOR FLIES OUT FROM ITS RADIANT ».
### Visuels
- v1 : panorama fixe az/alt étiré ×3 en vertical (angles faux, constellations déformées, décor figé). v2 : projection conforme (Mercator az/alt, mêmes px en x et y à l'horizon) : angles et formes vrais ; caméra qui suit le radiant (azimut lissé ±1 h) ; le sol, les arbres, la cabane et la boussole sont ancrés en azimut et tournent avec la vue ; les étoiles tournent d'est en ouest comme en vrai.
- Météores le long de grands cercles partant du radiant (longueur à l'écran plafonnée près du zénith). Figure complète des Gémeaux (Castor, Pollux et les deux corps), Orion en pâle. Croissant de Lune orienté vers le Soleil (hors champ : elle est à l'ouest, derrière nous ; la bannière le dit).
- Bannières du début de nuit et de l'aube remontées (y 200) : elles ne cachent plus le radiant. Chevauchement « moonset » / « Phaethon » supprimé.
- Frames contrôlées : 0,8 · 3,5 · 5,5 · 7,6 · 8,5 · 10,5 · 12 · 16,6 · 17 · 22,4 · 27 · 40 · 42,8 · 47 · 50,3 · 56 · 61 · 64 · 66,5 s + planche contact du MP4 final.
### Identique
Musique (music.wav identique bit à bit, md5 0df2fe48…), données (CSV identique), durée 67,5 s, tempo.
