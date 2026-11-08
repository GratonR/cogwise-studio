# studio/ — one folder per channel

Cogwise lives in `kit/` (historical). Every other channel gets `studio/<slug>/`:

```
studio/<slug>/
  METHOD.md     production method (format, duration, episode structure, checks before render)
  PERSONA.md    public voice (captions, pinned comment, replies)
  README.md     what is still to wire
  engine/       render engine — only if the format has no engine yet
```

## Formats

`FORMATS.json` lists the production formats that already have a working engine.
When a channel is created in the Control Room, its concept carries `format: <id>`:

| id | engine | sound |
|---|---|---|
| `explainer-voice` | `kit/cogwise` | ElevenLabs voice + SFX |
| `data-sonification` | `studio/this-melody-is/engine` | chiptune synth driven by the same event list as the picture |

The Studio task ("kit" action) reuses the engine of the chosen format instead of writing a new one,
and only creates a new engine when `format` is `new`. A new engine that works becomes a new entry here.
