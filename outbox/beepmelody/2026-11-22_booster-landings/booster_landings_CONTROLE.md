# booster-landings — CONTROLE (étape 3/4, 2026-11-22)

## Données (`booster_landings.csv`, 691 lignes, une par booster)
- Liste ligne à ligne des tentatives d'atterrissage Falcon 9 / Falcon Heavy (pas d'atterrissage = booster sacrifié = pas de ligne),
  du 10 janv. 2015 (CRS-5) au 21 nov. 2026 (USSF-317).
- Source 1 : listes Wikipedia des lancements Falcon (2010-2019, 2020-2022, 2023, 2024, 2025, 2026).
  Source 2 : liste Wikipedia des boosters (2015-2022), Space Explored 2023 + Gunter's Space Page (2023), Space Explored 2024 (2024),
  Gunter's Space Page (2025), journal et décomptes cumulés de Spaceflight Now (2026). 2026 recoupé aussi avec launches2026_research.csv
  (keeptrack.space / orbitalradar) : mêmes dates sauf Starlink 17-45 (23 ou 25 juin selon la source, sans effet sur les totaux).
- Totaux par année (tentatives / réussis / crashs) = ceux posés à l'étape 1 : 2015 3/1/2, 2016 8/5/3, 2017 14/14/0, 2018 14/12/2,
  2019 16/15/1, 2020 25/23/2, 2021 31/30/1, 2022 60/60/0, 2023 99/99/0, 2024 132/131/1, 2025 163/162/1.
- **Correction vs étape 1** : 2026 = 126 (et non 127) jusqu'à USSF-317. Total ligne à ligne : **691 tentatives, 678 réussis, 13 crashs**
  (l'étape 1 annonçait 692 / 679). Spaceflight Now dit « 679e atterrissage » parce qu'il compte le booster du 3 mars 2025 (Starlink 12-20,
  posé puis renversé par un feu) ; on le compte comme crash, comme Wikipedia et Gunter. NROL-136 (22 nov.) exclu : une seule source.
- Contrôles croisés : #100 = CRS-24 (21 déc. 2021), #200 = Transporter-8 (12 juin 2023), #300 = Starlink 6-53 (23 avr. 2024),
  #400 = Starlink 11-8 (21 janv. 2025) : identiques aux annonces de Spaceflight Now / Space.com. #500 et #600 tombent une ligne plus tard
  que chez Spaceflight Now (même raison : 12-20). Série record recalculée : 267 réussis d'affilée (16 fév. 2021 → 28 août 2024). Série en cours :
  264 depuis le 3 mars 2025.
- Cas limites comptés « réussi » : B1055 (Arabsat-6A, perdu en mer après l'atterrissage), B1058 (23 déc. 2023, renversé au retour).
- Tour : 14 nov. 2026, Starship Flight 15, premier vaisseau attrapé par la tour (Payload + Space.com, CSV de l'étape 1). Seul événement non-Falcon.

## Horloge
Un segment par année (YEARD), dates linéaires à l'intérieur de l'année : 2015 = 3,6 s … 2025 = 9,4 s. Les années chargées ont plus de
secondes, jamais moins de notes. Densité max : 17 notes/s (2025), proche de l'extrait de l'étape 2 (12/s). Durée totale 69,8 s.

## Frames contrôlées (LV=light et dusk)
0,9 s (titre + 1re note à 1,17 s : CRS-5, crash) · 4,75 s (1er atterrissage) · 19,4 s (crash Starlink L4) · 43,2 s (STREAK OVER) ·
62,6 s (la tour attrape le vaisseau) · 63,3 s (#678) · 66,5 s (outro) :
- HUD = nombre de réussis jusqu'à la note courante, crashs, date, mission : conforme au CSV.
- Frise du bas = réussis par année (traits rouges = crashs), valeurs finales 1, 5, 14, 12, 15, 23, 30, 60, 99, 131, 162, 126 = CSV.
- Outro : 678 / 13 sur 691 / 2015 = 1 sur 3 / 2025 = 162 (365/162 = 2,25 → « one every 2.3 days ») / 264 d'affilée : = CSV.
- Bannières ≤ 40 caractères (assert dans le module), rien de coupé, pas de chevauchement HUD / bannière / frise.
- Pas d'unité physique à l'écran (comptages seulement). Aucun mot sur la fabrication.

## Rendu final (étape 4/4, 2026-11-22 17:18Z) — variante crépuscule (LV=dusk, choix de Guillaume à l'étape 3)
- ffprobe : 69,87 s (couverture comprise), 1080×1920, audio AAC. Dans 62–75 s.
- Planche contact relue (1 / 4,8 / 19,4 / 43,2 / 55 / 62,6 / 63,3 / 67 s) : tour visible dès 1 s ; 43,2 s = 347 réussis, 12 crashs
  (2+3+2+1+2+1+1 = 12 au 28 août 2024), barre 2024 = 88 ; fin : 678 = 119 sur terre + 559 en mer, 13 crashs sur 691 ; frise finale
  1, 5, 14, 12, 15, 23, 30, 60, 99, 131, 162, 126 = CSV. Rien de coupé, textes lisibles sur le ciel violet-orange.
