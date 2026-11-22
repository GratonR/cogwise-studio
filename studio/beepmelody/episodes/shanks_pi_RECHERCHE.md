# Shanks π · étape 1/4 co-pilote (2026-11-22) — données et sources

Pitch Rédac `pitches/p-mwrr1f0k1` : « A man spent years on 707 digits of pi. The last 180 were wrong. »

## Données — `shanks_pi.csv` (707 lignes : decimal, shanks, true, same, source)
- Valeur publiée par William Shanks en 1873 (Proc. R. Soc. London 21, p. 319), 707 décimales.
- Décimales 501–707 de Shanks : **deux sources identiques chiffre à chiffre** —
  engert.us « William Shanks 707 digits » (PDF, groupes de 5) et Math Lair `mathlair.allfunandgames.ca/shanks.php` (lignes de 100).
- Décimales 1–527 : identiques au vrai π (toutes les sources : « correct for the first 527 places »).
- Vrai π : calculé (mpmath, 760 chiffres), recoupé avec la table MacTutor (707 places) et Wrench 1947 (MTAC, 808D).
- Vérifié par script : première divergence à la **528e** décimale. Sur les 180 décimales 528–707, **163 diffèrent**
  et **17 tombent juste par hasard** (531, 533, 540, 543, 560, 562, 564, 567, 570, 607, 613, 627, 636, 656, 684, 705, 707).
- Note Engert : la version imprimée porte « 51100 » aux décimales 606–610 (une coquille possible, « 51111 » ailleurs) ; sans effet : zone déjà fausse.

## Faits datés (≥ 2 sources)
- 1853 : livre de Shanks, 607 décimales (Hayes 2014 ; MTAC 1947 ; The Pudding 2026).
- 1873 : extension à 707 décimales (MacTutor ; Hayes ; Math Lair ; Engert).
- À la main, sur « more than 20 years » (Hayes, American Scientist 2014 ; Engert « 20+ year period »).
- Erreur trouvée par D. F. Ferguson au calculateur de bureau : vérification 1945, publiée Math. Gazette mai 1946 (MTAC 1947 ; Hayes « 75 years later »). MacTutor dit 1944 → à l'écran : « 1946 ».
- Cause : un terme oublié vers la 530e décimale de arctan 1/5 (Hayes ; Ferguson dans MTAC 1947).

## Risque de doublon
- `pi-clacks` (chocs) déjà publié : autre sujet (π par collisions). Ici une seule erreur humaine qu'on entend.
- The Pudding, « The Afterlife of Pi » (nov. 2026) raconte Shanks en texte/graphe, pas en musique.
