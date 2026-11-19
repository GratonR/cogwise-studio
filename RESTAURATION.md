# Restaurer une vidéo publiée

Les médias lourds des épisodes déjà publiés sortent peu à peu du dépôt GitHub (limite ~1 Go).
Ils ne sont pas perdus : on peut les récupérer par trois voies, dans cet ordre.

## 1. Archive sur le PC de Guillaume (copie exacte, prioritaire)

`~/Videos/Studio-archive/` (dossier Vidéos du PC)

- `cogwise/`, `beepmelody/`, `_essais/`, `_drafts/` : copie de `outbox/` au 19/11/2026, octet pour octet.
- `_historique-supprime/` : les 40 fichiers déjà retirés du dépôt mais encore dans l'historique git
  (brake, fridge, jackhammer, lock ; BM ebola, kyoto-cherry, wave-spectrum, yellowstone-wolves, cosmic-timeline).

Une session Claude reliée au PC les remet dans le dépôt de travail avec la copie de fichiers du pont (device_stage_files),
même chemin relatif sous `outbox/`.

## 2. Nos propres plateformes (si l'archive manque)

Ce sont nos vidéos, publiées par nous : les reprendre sur nos comptes est légal.

- **Facebook / Instagram (API Meta)** : `GET /{video-id}?fields=source` (FB) ou `GET /{media-id}?fields=media_url` (IG)
  avec le jeton de page. Les identifiants sont dans le résultat de publication (`ids.facebook`, `ids.instagram`, liens dans `links`), repris dans `publog` du Control Room ; sinon `stats.py` liste les médias de la page.
  Qualité : le fichier ré-encodé par Meta (1080p), sans les pistes séparées.
- **YouTube** : YouTube Studio > Contenu > ⋮ > Télécharger (à la main, par Guillaume). L'API ne donne pas le fichier.
- **TikTok** : pas de téléchargement par API ; en dernier recours, l'appli TikTok sur nos propres vidéos.

## 3. Re-rendu

Les sources (scripts, CSV, `.py` d'épisode BM, voix alignées) restent dans le dépôt : un épisode peut être re-rendu.
Pour Cogwise la voix ElevenLabs est réutilisée depuis le `.mp3` archivé, jamais régénérée (crédits).

## Règle

Avant de retirer un média du dépôt : vérifier qu'il est dans l'archive PC (taille identique) **et** publié sur au moins une plateforme.
