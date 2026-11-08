---
name: cogwise-daily-short
description: Produire et publier un short explicatif Cogwise (« how things work », anglais, DA manuel vintage) de A à Z — sujet, script, animation, voix ElevenLabs, montage, validation dans le Control Room, publication par API (YouTube, Meta) et Buffer (TikTok, Instagram, X). Utiliser pour la tâche quotidienne Cogwise ou dès qu'on demande « un nouvel épisode Cogwise ».
---

# Cogwise — routine d'un épisode

Cogwise = chaîne anglophone de shorts « how things work ». Une vidéo = un objet du quotidien expliqué
en coupe, style manuel vintage (papier crème, encre, rouge/moutarde/bleu-vert), voix off ElevenLabs « Jesse »,
sous-titres incrustés, 3 bruitages réels (`kit/cogwise/sfx/` : trait de crayon, souffle doux, marimba de fin), carte de fin hibou + wordmark COGWISE « HOW THINGS WORK ».

La tâche planifiée « Cogwise daily short » pilote tout (phases A → D) ; ses consignes priment sur ce fichier.
Ce fichier décrit le métier : comment bien faire un épisode.

**Règles non négociables**
- **Rythme : c'est le créateur qui décide.** Sujets variés, jamais de doublon.
- **Jamais de publication sans le « go »** donné dans le Control Room (carte « Vidéo à valider »).
- **Durée finale : cible 63–70 s, jamais sous 62 s, plafond 75 s** (décision du créateur, 2026-11-08, qui remplace « sous 60 s » du 06/11). Raison : le programme de rémunération TikTok (Creator Rewards) ne paie que les vidéos de plus d'une minute ; 62 s laisse une marge contre les ré-encodages qui rognent quelques images. Trop court → on ajoute un beat (un détail, une conséquence), trop long → on coupe du texte ; jamais on n'accélère ni ne ralentit la voix. Un format long (3–5 min, un appareil entier composant par composant) viendra plus tard, à part.
- **Exactitude** : chaque affirmation technique vérifiée sur ≥ 2 sources fiables avant d'écrire le script.
- **Contrôle physique du dessin** avant tout rendu final (voir étape 5).
- **Aucune mention d'IA** dans les titres, descriptions, légendes, hashtags ou tags (ni « AI voice », ni #AIvoice).
- **Unités : toujours le système international (°C, mètres, kg, km/h…) suivi de l'équivalent américain** (°F, pieds, livres, mph), dans la voix off (« minus eighteen Celsius, zero Fahrenheit ») comme à l'écran (« -18 °C · 0 °F »). Ne jamais dire « degrees » sans préciser l'échelle (demande du créateur, 2026-11-06).
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
- **10 à 12 beats, 145–165 mots au total** (débit réel de Jesse ≈ 2,5 mots/s → 58–66 s de voix + la fin). Une phrase courte par beat (8–14 mots). Toujours UNE seule idée : la minute en plus sert à montrer le mécanisme plus en détail (un plan de plus sur la pièce clé, une conséquence concrète), pas à empiler un deuxième sujet. La règle des 10 premières secondes reste la même.
- **Monter d'un cran d'abstraction** : un seul principe + 3 pièces maximum, le reste saute. Mieux vaut un mécanisme bien compris que cinq survolés. Chaque mot technique est soit expliqué en 4–5 mots, soit remplacé.
- **Les 10 premières secondes décident** : sur nos courbes YouTube, ~30 % des spectateurs partent avant 8 s et la moitié avant ~16 s. L'image doit bouger dès la 1re seconde (pas d'écran posé), l'accroche tient en une phrase, et le « secret » arrive avant 8 s.
- **Ne jamais accélérer la voix pour tenir la durée** : couper des mots. Au-delà de ~2,7 mots/s le débit est jugé trop rapide (retour du créateur sur l'ISS, 2026-11-05).
- **L'accroche (3 premières secondes) compte plus que tout** : la rétention chute au début. Paradoxe, chiffre choc ou question qui pique.
- **Une seule idée par épisode** (prospection du 8 nov. : les shorts qui percent n'ont qu'une révélation). Pas d'empilement Newton + Bernoulli + décrochage : on choisit LA chose surprenante et on la montre. Pas de « tip » final dans la vidéo : le détail en plus va dans le commentaire épinglé.
- **Titre et première phrase en anomalie / surprise**, jamais « How does X work? » : « Why your fridge has a hot back », « Your toilet has a hidden tube », « Why a Humvee has no ignition key ». La réponse visuelle apparaît à l'écran avant la 2e seconde. Le script doit tenir la promesse du titre (pas de clickbait).
- Série possible : « How you accidentally invented X » (le spectateur résout les problèmes jusqu'à l'invention), condensée en 63–70 s.
- Structure courte : accroche (≤ 3 s) → « the secret » (avant 8 s) → principe (carte) → 2–3 parties numérotées « 1 · PART » dans l'ordre du flux → 1 fait surprenant → récap « X = Y » → (outro automatique). La boucle/sécurité ne reste que si c'est le cœur du sujet.
- Ton : simple, vivant, tutoiement implicite (« your fridge »), zéro jargon non expliqué.
- Titres de beat EN MAJUSCULES courts ; 2 beats avec `card` (encart zoom) maximum, sans titre (l'encart a le sien).

### 4. Coder l'épisode `episodes/<slug>.py`
Copier le patron de `episodes/fridge.py` et `README.md` :
- `META` (slug, title YouTube ≤ 90 car. avec 1 emoji, description 2 lignes + hashtags, hashtags, sources).
- `draw_set(ctx)` : décor minimal (`window()`, `counter()` ou rien).
- Un dessin principal en coupe dans la zone y 300–1500, x ~250–900, animé par `state(t)` (fenêtres `win(t, a, b)` calées sur les débuts de beats = somme des `dur`).
- Étiquettes `tag()` numérotées + `highlight()` sur la partie expliquée ; flèches `wavy_arrow` pour chaleur/énergie/flux ; particules le long d'un chemin pour les fluides.
- `CARDS` (3–4) : `card_frame(...)` puis un mini-schéma animé lisible en 2 s.
- `SFX` : `pop` à chaque nouvelle étiquette, `click` pour un interrupteur (les deux → trait de crayon). Les encarts et la fin ont leur son automatiquement. `sizzle` et `HUM` sont ignorés en mode `samples` (par défaut ; `COGWISE_SFX=off` = voix seule).

### 5. Regarder avant de rendre — CONTRÔLE PHYSIQUE (obligatoire)
`python -m cogwise.run stills episodes/<slug>.py /tmp/stills <t…>` aux moments les plus chargés (chaque carte, chaque étiquette, récap, fin). Lire les PNG et vérifier, point par point, que le dessin dit la même chose que le script :
- sens du flux (d'où vient l'air, l'eau, le courant) ;
- sens des rotations et **signe des angles — repère écran, y vers le bas** (une aile a déjà été publiée nez vers le bas par erreur de signe) ;
- quelle face est en haut, ordre des pièces, flèches de force dans le bon sens, étiquettes au bon endroit ;
- puis la mise en page : chevauchements, textes coupés, zones.
Corriger et recommencer jusqu'à propre.

### 6. Voix + montage
`python -m cogwise.run build episodes/<slug>.py out/ --tts /tmp/cogwise_config.json`
(ElevenLabs avec horodatage par caractère → chaque beat démarre pile sur sa phrase). Si la durée sort de 62–75 s : ajouter ou retirer un beat (ou raccourcir des phrases), et relancer.

### 7. Vérifier
- Planche contact du MP4 final (ffmpeg `fps=1/4,tile`), la lire : sous-titres = voix, rien de coupé, carte de fin présente.
- Durée conforme, son présent (`ffprobe`), faits conformes aux sources.

### 8. Outbox
Copier `out/` dans `outbox/YYYY-MM-DD_<slug>/` + `episodes/<slug>.py`, commit, push.
URL publique de la vidéo : `https://raw.githubusercontent.com/<owner>/cogwise-studio/main/outbox/YYYY-MM-DD_<slug>/<slug>.mp4`.

### 9. Validation (obligatoire)
Carte « Vidéo à valider » dans le Control Room : vidéo, durée, sources, contrôle du dessin, et les textes par plateforme
(YouTube titre + description + tags ; TikTok/Instagram/Facebook légende + 3–5 hashtags dont #howthingswork ; X ≤ 250 car.). Légendes écrites dans la voix de Cog, la persona de la chaîne : voir `kit/PERSONA.md`.
Plus le **commentaire épinglé** (YouTube, Instagram, Facebook) : 1–2 phrases de Cog, un détail ou une astuce qui n'est pas dans la vidéo, puis une question simple qui invite à répondre (ex. « Ever heard your starter click without turning? 🔧 »). Pas de demande d'abonnement. On remplace ainsi toute phrase d'appel en fin de vidéo (qui rallongerait).
Notification push + e-mail. Puis **attendre** le « go » (ou les corrections → reprendre l'étape concernée).

### 10. Publication (après « go » seulement)
- YouTube : API officielle, upload résumable, catégorie Education, « made for kids » = non, public.
- Facebook : Reel via l'API Graph de Meta.
- TikTok, Instagram (Reel), X : API Buffer.
Relever les liens publiés ; une plateforme en échec = une carte « Blocage », on continue avec les autres.

### 11. Journal
Écrire le document `episodes/<slug>` du Control Room : liens, sources, texte de la voix off (sert à répondre aux commentaires), durée, mode.
Message final court : liens publiés.
