# This Melody Is… — render engine

Pixel-art data-sonification shorts (1080x1920, 30 fps). Every visual event is also a sound event.

- `v2.py` — base drawing helpers (pixel font VT323, header panel, backgrounds, compose 180x320 art + 360x640 text layers)
- `pi.py` — π episode + shared FX/glitch engine; `phi.py` — φ episode; `econst.py` — e episode
- `pop.py` / `pop2.py` (3 min 24) / `pop3.py` (56 s) / `pop4.py` (1 min 28) — "This Melody Is Us" (world population on a pixel globe; needs `../geo/land_clean.npy`)
- `pi_audio.py` — event-driven chiptune synth (reads the episode module's event list)

Render an episode (needs python3, numpy, pillow, scipy, ffmpeg):

    MOD=pop4 python3 pi_audio.py out/music.wav
    python3 pop4.py render out
    python3 pop4.py final out this_melody_is_us.mp4

Preview frames: `python3 pop4.py preview out boom:5 plague:3`. Env: `PI_FX` (effects strength), `POP_STYLE` (`v1` default, `cine`, `neon`).
