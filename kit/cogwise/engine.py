"""Cogwise episode engine.

An episode is a Python module that defines:
  META   = dict(slug=..., title=..., description=..., hashtags=[...])
  BEATS  = [dict(dur=5.5, title="UPPERCASE TITLE" or None, caption="Narration line.", card=None or 'name'), ...]
           (the engine appends the brand/outro beat itself)
  draw(ctx, t, E)          -> draws the stage (foreground) at DESIGN time t. E = Episode helper (E.beat, E.lt ...)
  draw_set(ctx)            -> optional static props drawn once over the base set (window, counter ...)
  CARDS  = {'name': fn(ctx, t, lt, a)}  -> inset card content (call style.card_frame first)
  SFX    = [(design_t, 'pop'|'click'|'whoosh'|'sizzle'|'ding'), ...]   optional
  HUM    = [(design_t0, design_t1), ...]                                 optional machine hum
  ANCHOR = (560, 1500)     optional: point the stage shrinks toward when a card is shown
  CAM(t) -> (cx, cy, zoom) optional camera on the stage (design time): (540, 900, 1) = no move
  draw_hud(ctx, t, E)      optional overlay drawn on top of everything except captions (counters, big words)
  OUTRO = False            optional: no brand beat at the end (loop-friendly); a small mark stays top-right

Design time = the timeline written in BEATS (durations you choose).
Real time   = the voice-over timeline. The engine warps design -> real beat by beat,
so every beat starts exactly when its caption is spoken.
"""
import importlib.util, os, sys, math, subprocess, json
import cairo
from . import style as S

LEAD = 0.12     # beat visuals start this much before the words
TAIL = 1.9      # seconds after the voice ends (end card + bell)
BRAND_DUR = 4.0

def load_episode(path):
    spec = importlib.util.spec_from_file_location("episode", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    # Montage, level 2: COGWISE_OVERRIDES=overrides.json {"titles": ["NEW TITLE" | null, ...]} replaces beat
    # titles without touching captions (the voice-over stays valid, so no new TTS is needed).
    ov = os.environ.get("COGWISE_OVERRIDES")
    if ov and os.path.exists(ov):
        o = json.load(open(ov))
        for i, t in enumerate(o.get("titles") or []):
            if t is not None and i < len(mod.BEATS): mod.BEATS[i] = dict(mod.BEATS[i], title=(t.strip() or None))
    return mod

class Episode:
    def __init__(self, mod, starts=None, voice_len=None):
        self.mod = mod
        self.outro = getattr(mod, 'OUTRO', True)
        self.beats = [dict(b) for b in mod.BEATS]
        if self.outro:
            self.beats.append(dict(dur=BRAND_DUR, title=None, caption=S.OUTRO, card=None, brand=True))
        self.D = [0.0]
        for b in self.beats: self.D.append(self.D[-1] + b['dur'])
        self.design_len = self.D[-1]
        if starts is None:                      # preview on design timeline
            self.R = list(self.D)
        else:
            n = len(self.beats)
            assert len(starts) == n, f"need {n} beat start times, got {len(starts)}"
            self.R = [0.0] + [starts[i] - LEAD for i in range(1, n)] + [voice_len + (TAIL if self.outro else 0.5)]
        self.length = self.R[-1]
        self.cards = getattr(mod, 'CARDS', {})
        self.anchor = getattr(mod, 'ANCHOR', (560, 1500))
        self._bg = None
        self.beat = 0; self.lt = 0.0

    # ---- time mapping
    def to_design(self, t):
        t = min(max(t, 0.0), self.length - 1e-6)
        for i in range(len(self.R) - 1):
            if self.R[i] <= t < self.R[i+1]:
                u = (t - self.R[i]) / (self.R[i+1] - self.R[i])
                return self.D[i] + u * (self.D[i+1] - self.D[i])
        return self.D[-1] - 1e-6

    def to_real(self, td):
        for i in range(len(self.D) - 1):
            if self.D[i] <= td <= self.D[i+1]:
                u = (td - self.D[i]) / (self.D[i+1] - self.D[i])
                return self.R[i] + u * (self.R[i+1] - self.R[i])
        return self.R[-1]

    def beat_at(self, td):
        for i in range(len(self.beats)):
            if self.D[i] <= td < self.D[i+1]: return i
        return len(self.beats) - 1

    def beat_start(self, i): return self.D[i]

    # ---- rendering
    def background(self):
        if self._bg is None:
            s = cairo.ImageSurface(cairo.FORMAT_RGB24, S.W, S.H); c = cairo.Context(s)
            S.base_set(c)
            if hasattr(self.mod, 'draw_set'): self.mod.draw_set(c)
            S.grain(c)
            # re-draw caption band edge + disclaimer crisp over grain
            self._bg = s
        return self._bg

    def card_alpha(self, td):
        for i, b in enumerate(self.beats):
            if b.get('card'):
                v = S.win(td, self.D[i], self.D[i+1], 0.45)
                if v > 0: return v, b['card'], td - self.D[i]
        return 0.0, None, 0.0

    def frame(self, t_real):
        td = self.to_design(t_real)
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, S.W, S.H)
        ctx = cairo.Context(surf)
        ctx.set_source_surface(self.background()); ctx.paint()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        bi = self.beat_at(td); b = self.beats[bi]
        self.beat, self.lt = bi, td - self.D[bi]
        ca, card, lt = self.card_alpha(td)
        brand_a = S.ease((td - (self.D[-2] + 0.2)) / 0.6) if b.get('brand') else 0.0
        sc = min(S.lerp(1.0, 0.78, ca), S.lerp(1.0, 0.86, brand_a))
        ax, ay = self.anchor
        ctx.save(); ctx.translate(ax, ay); ctx.scale(sc, sc); ctx.translate(-ax, -ay)
        if hasattr(self.mod, 'CAM'):
            ctx.rectangle(0, 0, S.W, 1500); ctx.clip()      # camera moves never spill onto the floor/caption band
            cx, cy, z = self.mod.CAM(td)
            ctx.translate(540, 900); ctx.scale(z, z); ctx.translate(-cx, -cy)
        self.mod.draw(ctx, td, self)
        ctx.restore()
        if b.get('title'):
            ta = S.win(td, self.D[bi] if bi else -1, self.D[bi+1], 0.3)
            S.title(ctx, b['title'], ta * (1 - ca))
        if ca > 0 and card in self.cards:
            ctx.save(); ctx.translate(540, 380); s = S.lerp(0.92, 1.0, ca); ctx.scale(s, s); ctx.translate(-540, -380)
            self.cards[card](ctx, td, lt, ca)
            ctx.restore()
        S.end_card(ctx, td, brand_a)
        if hasattr(self.mod, 'draw_hud'): self.mod.draw_hud(ctx, td, self)
        if not self.outro: S.corner_mark(ctx)
        # captions follow real time
        ri = bi
        cap_a = S.win(t_real, self.R[ri] if ri else -1, self.R[ri+1] + (1 if b.get('brand') else 0), 0.2)
        S.caption(ctx, b['caption'], cap_a)
        return surf

    # ---- outputs
    def script_text(self):
        return " ".join(b['caption'] for b in self.beats)

    def srt(self, path, ends=None):
        def ts(x):
            ms = int(round(max(x, 0)*1000)); return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
        out = []
        for i, b in enumerate(self.beats):
            a = self.R[i] + (LEAD if i else 0); e = self.R[i+1] - 0.05
            out.append(f"{i+1}\n{ts(a)} --> {ts(e)}\n{b['caption']}\n")
        open(path, 'w').write("\n".join(out))

def _render_chunk(args):
    ep_path, starts, voice_len, f0, f1, out = args
    ep = Episode(load_episode(ep_path), starts, voice_len)
    tmp = out + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                          '-s', f'{S.W}x{S.H}', '-r', str(S.FPS), '-i', '-', '-c:v', 'libx264',
                          '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp],
                         stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(bytes(ep.frame(f / S.FPS).get_data()))
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError("ffmpeg failed on " + out)
    os.replace(tmp, out)
    return out

def render_video(ep_path, out_mp4, starts=None, voice_len=None, workers=None):
    from multiprocessing import Pool
    ep = Episode(load_episode(ep_path), starts, voice_len)
    nframes = int(round(ep.length * S.FPS))
    workers = workers or max(1, os.cpu_count() or 1)
    step = math.ceil(nframes / workers)
    jobs = [(ep_path, starts, voice_len, i, min(nframes, i + step), f"{out_mp4}.part{k}.mp4")
            for k, i in enumerate(range(0, nframes, step))]
    with Pool(len(jobs)) as pool:
        parts = pool.map(_render_chunk, jobs)
    lst = out_mp4 + '.list.txt'
    open(lst, 'w').write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out_mp4], check=True)
    for p in parts: os.remove(p)
    os.remove(lst)
    return ep

def stills(ep_path, out_dir, times, starts=None, voice_len=None):
    ep = Episode(load_episode(ep_path), starts, voice_len)
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for t in times:
        p = os.path.join(out_dir, f"still_{t:05.1f}.png"); ep.frame(t).write_to_png(p); paths.append(p)
    return paths
