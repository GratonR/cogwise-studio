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
