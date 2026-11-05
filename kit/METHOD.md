---
name: cogwise-daily-short
description: Produire et publier un short explicatif Cogwise (« how things work », anglais, DA manuel vintage) de A à Z — sujet, script, animation, voix ElevenLabs, montage, validation dans le Control Room, publication par API (YouTube, Meta) et Buffer (TikTok, Instagram, X). Utiliser pour la tâche quotidienne Cogwise ou dès qu'on demande « un nouvel épisode Cogwise ».
---

# Cogwise — routine d'un épisode

Cogwise = chaîne anglophone de shorts « how things work ». Une vidéo = un objet du quotidien expliqué
en coupe, style manuel vintage (papier crème, encre, rouge/moutarde/bleu-vert), voix off ElevenLabs « Jesse »,
sous-titres incrustés, effets sonores synthétisés, carte de fin hibou + wordmark COGWISE « HOW THINGS WORK ».

La tâche planifiée « Cogwise daily short » pilote tout (phases A → D) ; ses consignes priment sur ce fichier.
Ce fichier décrit le métier : comment bien faire un épisode.

**Règles non négociables**
- **Rythme : c'est le créateur qui décide.** Sujets variés, jamais de doublon.
- **Jamais de publication sans le « go »** donné dans le Control Room (carte « Vidéo à valider »).
- **Durée finale 65–80 s par défaut** (> 61 s pour TikTok Creator Rewards et Facebook). Une version courte (~40–45 s) est possible si elle est demandée.
- **Exactitude** : chaque affirmation technique vérifiée sur ≥ 2 sources fiables avant d'écrire le script.
- **Contrôle physique du dessin** avant tout rendu final (voir étape 5).
- **Aucune mention d'IA** dans les titres, descriptions, légendes, hashtags ou tags (ni « AI voice », ni #AIvoice).
- **Ne pas surcharger** l'image : un seul objet en coupe, 1–2 accessoires de décor max, pas de personnage.

## Où sont les choses
| Quoi | Où |
|---|---|
| Kit de rendu (code), épisodes, outbox vidéos | Repo GitHub `cogwise-studio` — `add_repo` puis `git clone` |
| Pilotage, demandes, épisodes, stats, commentaires | Appli « Cogwise Control Room » (base via l'outil ArtifactData) |
| Clés API (Buffer, YouTube, Meta…) et jeton YouTube | Google Drive Cogwise, dossier `Cogwise/config` (lire avec le connecteur Drive, ne JAMAIS committer ni afficher) |
| Clé ElevenLabs + voice_id | Drive : `Cogwise/config/elevenLabsCredentials.txt` → `/tmp/cogwise_config.json` (hors repo) |
| Publication | API YouTube Data (vidéo), API Graph Meta (Reel Facebook), API Buffer (TikTok, Instagram, X) |

Réseau : les domaines des API (ElevenLabs, Google, Meta, Buffer) doivent être autorisés dans Paramètres > Capacités ; GitHub est joignable par défaut.

## Étapes

### 0. Préparer l'atelier (2 min)
1. `add_repo` cogwise-studio (accès push), cloner, `pip install --break-system-packages -r requirements.txt`.
2. Lire les collections `episodes` et `ideas` du Control Room (anti-doublon) et écrire la config ElevenLabs dans `/tmp/cogwise_config.json`.
3. Si un élément manque (connecteur, clé, repo), continuer tout ce qui est possible et créer une carte « Blocage » dans le Control Room.

### 1. Choisir le sujet
- Proposé dans le Control Room, choisi par le créateur.
- Un mécanisme du quotidien qu'on peut montrer **dans une seule vue en coupe** : électroménager (regard de technicien de terrain), maison, véhicule, corps humain simple, infrastructure (chasse d'eau, serrure, micro-ondes, lave-vaisselle, frein à disque, ampoule LED, stylo bille, ascenseur, thermos, cocotte-minute…).
- Critère : « je l'utilise tous les jours mais je ne sais pas comment ça marche » + un moment « ah ! » (fait surprenant).

### 2. Vérifier les faits
WebSearch sur 2–3 sources fiables (fabricants, encyclopédies, sites techniques). Noter les URLs dans `META['sources']`.
Simplifier sans dire faux ; mention « Simplified educational model » déjà incrustée. Employer le vrai terme quand il existe (ex. « compressed air », pas seulement « squeezed air »).

### 3. Écrire le script (anglais)
- **13 à 15 beats, 185–215 mots au total** (≈ 2,8 mots/s → 66–77 s + carte de fin). Une phrase courte par beat (10–17 mots).
- **L'accroche (3 premières secondes) compte plus que tout** : la rétention chute au début. Paradoxe, chiffre choc ou question qui pique.
- Structure : accroche → « the secret » → principe physique (carte) → parties numérotées « 1 · PART » dans l'ordre du flux → 1 fait surprenant → boucle / sécurité / contrôle (carte) → récap « X = Y » → (outro automatique).
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

### 5. Regarder avant de rendre — CONTRÔLE PHYSIQUE (obligatoire)
`python -m cogwise.run stills episodes/<slug>.py /tmp/stills <t…>` aux moments les plus chargés (chaque carte, chaque étiquette, récap, fin). Lire les PNG et vérifier, point par point, que le dessin dit la même chose que le script :
- sens du flux (d'où vient l'air, l'eau, le courant) ;
- sens des rotations et **signe des angles — repère écran, y vers le bas** (une aile a déjà été publiée nez vers le bas par erreur de signe) ;
- quelle face est en haut, ordre des pièces, flèches de force dans le bon sens, étiquettes au bon endroit ;
- puis la mise en page : chevauchements, textes coupés, zones.
Corriger et recommencer jusqu'à propre.

### 6. Voix + montage
`python -m cogwise.run build episodes/<slug>.py out/ --tts /tmp/cogwise_config.json`
(ElevenLabs avec horodatage par caractère → chaque beat démarre pile sur sa phrase). Si la durée < 61 s : rallonger le script (1–2 beats) et relancer.

### 7. Vérifier
- Planche contact du MP4 final (ffmpeg `fps=1/4,tile`), la lire : sous-titres = voix, rien de coupé, carte de fin présente.
- Durée conforme, son présent (`ffprobe`), faits conformes aux sources.

### 8. Outbox
Copier `out/` dans `outbox/YYYY-MM-DD_<slug>/` + `episodes/<slug>.py`, commit, push.
URL publique de la vidéo : `https://raw.githubusercontent.com/<owner>/cogwise-studio/main/outbox/YYYY-MM-DD_<slug>/<slug>.mp4`.

### 9. Validation (obligatoire)
Carte « Vidéo à valider » dans le Control Room : vidéo, durée, sources, contrôle du dessin, et les textes par plateforme
(YouTube titre + description + tags ; TikTok/Instagram/Facebook légende + 3–5 hashtags dont #howthingswork ; X ≤ 250 car.). Légendes écrites dans la voix de Cog, la persona de la chaîne : voir `kit/PERSONA.md`.
Notification push + e-mail. Puis **attendre** le « go » (ou les corrections → reprendre l'étape concernée).

### 10. Publication (après « go » seulement)
- YouTube : API officielle, upload résumable, catégorie Education, « made for kids » = non, public.
- Facebook : Reel via l'API Graph de Meta.
- TikTok, Instagram (Reel), X : API Buffer.
Relever les liens publiés ; une plateforme en échec = une carte « Blocage », on continue avec les autres.

### 11. Journal
Écrire le document `episodes/<slug>` du Control Room : liens, sources, texte de la voix off (sert à répondre aux commentaires), durée, mode.
Message final court : liens publiés.
