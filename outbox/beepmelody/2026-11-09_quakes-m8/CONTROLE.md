# Contrôle — THE PLANET SNAPPED 100 TIMES (2026-11-09)

Données : `quakes_m8.csv` = les 100 séismes M ≥ 8 du catalogue USGS ANSS ComCat (requête minmagnitude=8, 1900-01-01 → 2026-11-09),
magnitudes affichées = USGS (arrondies au dixième, demi supérieur). Deuxième source par ligne (colonne source_2, `check`) :
- 84 lignes : NOAA NCEI Significant Earthquake Database, même date (±1 j), magnitude à ±0,25 près (1917 Samoa-Tonga : NOAA 8.3, USGS 8.0 → USGS affiché) ;
- 11 lignes 2010-2025 : ISC-GEM (tableau « plus fort séisme par an ») ;
- 1918 Chili : Vigny et al. 2024 (JSAES) ; 1941 Hyuga-nada : JMA ; 1965 mer de Céram : EMSC ; 1970 Pérou-Colombie : archive USGS « Historic earthquakes » ;
  2012 réplique océan Indien 8.2 : CEA ; 2013 Santa Cruz : publication Penn State/Caltech (Mw 8.0) ;
- À CONFIRMER (une seule source catalogue solide) : 1910 Taïwan 8.1 et 1972 Mindanao 8.0 (entrées ISC-GEM reprises par USGS),
  2021 Kermadec 8.1 et 2021 Sandwich du Sud 8.1 (liste annuelle Wikipédia en complément).

Frames vérifiées (t = 2.8, 4.9, 26, 28.6, 30.4, 37.6, 45.2, 51, 59.5, 66, 67 s) + planche contact :
- HUD = CSV : 1906 M 8.8, 20 km · 12 mi ; 1960 M 9.5, 25 km · 16 mi ; 1964 M 9.2 ; 1985 M 8.0, 33 km · 21 mi ; 2004 M 9.1, 30 km · 19 mi ;
  2018 Fidji 600 km · 373 mi ; 2025 M 8.8, 35 km · 22 mi, #100/100. Profondeur en km puis mi.
- Graphe : axe des années de gauche à droite, magnitude vers le haut (8.0 → 9.5), tiges = CSV.
- Bannières : 1906 « biggest so far », 1952 « first M 9 », 1960 « biggest ever recorded », 1964 « 3 giants in under 12 years »
  (nov. 1952 → mars 1964), 1985 « 7.5 years without an M8 » (août 1977 → mars 1985), 2004, 2011, #100.
- Outro : 5 séismes M ≥ 9 (1952, 1960, 1964, 2004, 2011) ; « each +1.0 = ~32× more energy » (USGS).
- Lisibilité : légende du bas corrigée (coupée en preview v1), rien de coupé ensuite ; aucune mention d'IA.
Durée finale 70,27 s (ffprobe), piste audio présente, max -1,0 dB.
