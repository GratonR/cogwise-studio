---
name: cogwise-daily-short
description: Produire et publier un short explicatif Cogwise (« how things work », anglais, DA manuel vintage) de A à Z — sujet, script, animation, voix ElevenLabs, montage, validation par Guillaume, publication via Zapier. Utiliser pour la tâche quotidienne Cogwise ou dès que Guillaume demande « un nouvel épisode Cogwise ».
---

# Cogwise — routine d'un épisode (1 par jour)

Cogwise = chaîne anglophone de shorts « how things work ». Une vidéo = un objet du quotidien expliqué
en coupe, style manuel vintage (papier crème, encre, rouge/moutarde/bleu-vert), voix IA ElevenLabs,
sous-titres incrustés, effets sonores synthétisés, carte de fin hibou + wordmark COGWISE « HOW THINGS WORK ».

**Règles non négociables**
- **1 épisode par jour max.** Sujets variés : la politique YouTube « contenu inauthentique / produit en masse » sanctionne toute la chaîne.
- **Jamais de publication sans le « go » explicite de Guillaume** dans la conversation.
- **Durée finale 65–80 s** (> 61 s obligatoire pour TikTok Creator Rewards, Snapchat, Facebook).
- **Exactitude** : chaque affirmation technique vérifiée sur ≥ 2 sources fiables avant d'écrire le script.
- **Ne pas surcharger** l'image : un seul objet en coupe, 1–2 accessoires de décor max, pas de personnage.

## Où sont les choses
| Quoi | Où |
|---|---|
| Kit de rendu (code), épisodes, outbox vidéos | Repo GitHub `cogwise-studio` (compte Cogwise, public) — `add_repo` puis `git clone` |
| Clé ElevenLabs + voice_id | Google Drive Cogwise : `Cogwise/config/cogwise_config.json` (lire avec le connecteur Drive, ne JAMAIS committer) |
| Journal des épisodes (anti-doublon) | Google Drive Cogwise : `Cogwise/episodes_log.md` |
| Publication | Connecteur Zapier (actions YouTube, Instagram Business, Facebook Page, X, TikTok si dispo, Google Drive) |

Réseau : `api.elevenlabs.io` doit être autorisé dans Paramètres > Capacités ; GitHub est joignable par défaut.

## Étapes

### 0. Préparer l'atelier (2 min)
1. `add_repo` cogwise-studio (accès push), cloner, `pip install --break-system-packages -r requirements.txt`.
2. Lire `episodes_log.md` et `cogwise_config.json` sur le Drive Cogwise ; écrire la config dans `/tmp/cogwise_config.json` (hors repo).
3. Créer la liste de tâches : sujet → recherche → script → animation → images clés → voix + montage → vérif → outbox → validation → publication → journal.
Si un élément manque (connecteur, clé, repo), continuer tout ce qui est possible et dire précisément ce qui manque à la fin.

### 1. Choisir le sujet
- Un mécanisme du quotidien qu'on peut montrer **dans une seule vue en coupe** : électroménager (atout : Guillaume est technicien, utiliser son regard terrain), maison, véhicule, corps humain simple, infrastructure (chasse d'eau, serrure, micro-ondes, lave-vaisselle, frein à disque, ampoule LED, stylo bille, ascenseur, thermos, cocotte-minute…).
- Pas de doublon avec le journal ; alterner les catégories d'un jour à l'autre.
- Critère : « je l'utilise tous les jours mais je ne sais pas comment ça marche » + un moment « ah ! » (fait surprenant).

### 2. Vérifier les faits
WebSearch sur 2–3 sources fiables (fabricants, encyclopédies, sites techniques). Noter les URLs dans `META['sources']`.
Simplifier sans dire faux ; mention « Simplified educational model » déjà incrustée.

### 3. Écrire le script (anglais)
- **13 à 15 beats, 185–215 mots au total** (≈ 2,8 mots/s → 66–77 s + carte de fin). Une phrase courte par beat (10–17 mots).
- Structure : accroche-question → « the secret » → principe physique (carte) → parties numérotées « 1 · PART » dans l'ordre du flux → 1 fait surprenant → boucle / sécurité / contrôle (carte) → récap « X = Y » → (outro automatique).
- Ton : simple, vivant, tutoiement implicite (« your fridge »), zéro jargon non expliqué.
- Titres de beat EN MAJUSCULES courts ; 3–4 beats avec `card` (encart zoom), sans titre (l'encart a le sien).

### 4. Coder l'épisode `episodes/<slug>.py`
Copier le patron de `episodes/fridge.py` et `README.md` :
- `META` (slug, title YouTube ≤ 90 car. avec 1 emoji, description 2 lignes + hashtags, hashtags, sources).
- `draw_set(ctx)` : décor minimal (`window()`, `counter()` ou rien).
- Un dessin principal en coupe dans la zone y 300–1500, x ~250–900, animé par `state(t)` (fenêtres `win(t, a, b)` calées sur les débuts de beats = somme des `dur`).
- Étiquettes `tag()` numérotées + `highlight()` sur la partie expliquée ; flèches `wavy_arrow` pour chaleur/énergie/flux ; particules le long d'un chemin pour les fluides.
- `CARDS` (3–4) : `card_frame(...)` puis un mini-schéma animé lisible en 2 s.
- `SFX` : `pop` à chaque nouvelle étiquette, `click` pour un interrupteur, `sizzle` chaleur ; `HUM` si une machine tourne.

### 5. Regarder avant de rendre
`python -m cogwise.run stills episodes/<slug>.py /tmp/stills <t…>` aux moments les plus chargés (chaque carte, chaque étiquette, récap, fin). Lire les PNG, corriger chevauchements / textes coupés / zones. Recommencer jusqu'à propre.

### 6. Voix + montage
`python -m cogwise.run build episodes/<slug>.py out/ --tts /tmp/cogwise_config.json`
(ElevenLabs avec horodatage par caractère → chaque beat démarre pile sur sa phrase). Si la durée < 61 s : rallonger le script (1–2 beats) et relancer.
Si ElevenLabs est indisponible : livrer `out/<slug>_script.txt` à Guillaume pour qu'il génère la voix, puis `--voice fichier.mp3` (alignement automatique).

### 7. Vérifier
- Planche contact du MP4 final (ffmpeg `fps=1/4,tile`), la lire : sous-titres = voix, rien de coupé, carte de fin présente.
- Durée 61–80 s, son présent (`ffprobe`), faits conformes aux sources.

### 8. Outbox
Copier `out/` dans `outbox/YYYY-MM-DD_<slug>/` + `episodes/<slug>.py`, commit, push.
URL publique de la vidéo : `https://raw.githubusercontent.com/<owner>/cogwise-studio/main/outbox/YYYY-MM-DD_<slug>/<slug>.mp4`.

### 9. Validation (obligatoire)
`SendUserFile` de la vidéo + `SendUserMessage` avec : sujet, durée, sources, et les textes par plateforme
(YouTube titre + description + tags ; TikTok/Instagram/Facebook légende + 3–5 hashtags ; X post ≤ 250 car.).
`PushNotification` « Épisode Cogwise prêt à valider ». Puis **attendre** « go » (ou corrections → reprendre l'étape concernée).

### 10. Publication (après « go » seulement)
Avec les actions Zapier, en passant l'URL raw GitHub comme fichier vidéo :
- YouTube : Upload Video — titre, description, tags, catégorie Education, « made for kids » = non, public. (Contenu animé non photoréaliste : pas de label IA obligatoire.)
- TikTok (si action dispo) : activer le label « AI-generated content » (voix IA). Sinon le dire, Guillaume poste depuis son téléphone.
- Instagram Reels (compte Business), Facebook Page (Reel), X (post + vidéo).
- Optionnel : Google Drive « Upload File » depuis l'URL → `Cogwise/archive/`.
Relever les liens publiés.

### 11. Journal
Ajouter une ligne à `Cogwise/episodes_log.md` (Drive) : date | slug | titre | catégorie | liens | sources.
Message final court : liens publiés + sujet proposé pour demain.
