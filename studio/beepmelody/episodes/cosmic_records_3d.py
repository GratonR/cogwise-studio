"""BEEPMELODY — cosmic-timeline, rework r6 = A (Guillaume, 2026-11-14 17:12: "Le A est incroyable").
Same data (cosmic_records.csv), same music (Cosmic drive+, 124 BPM) and same timing as cosmic_records.py.
Only the scene changes: a 3D fly-through. At each record (= each note) the camera flies to the new farthest object,
the particle galaxy fills the screen and spins; star streaks get longer when the look-back jump is bigger.
A thin gauge on the left keeps the 'how far' readable (top = Big Bang, bottom = us).

    python3 cosmic_records_3d.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cosmic_records as M
from cosmic_records import *  # noqa
import cosmic_records_r6_mock as K
from cosmic_records_r6_mock import (Cam, put_galaxy, STAR3, STARC, depth_gauge, gauge_labels, zA, xyA, FLY)

M.BY_BANNER = 416                                   # banners below the galaxy, above the year clock

def cam_z(T, k):
    age = T - RT[k]
    a = ease(age / FLY); zp = zA(k - 1) if k else 0.0
    drift = 1.2 * min(1, age / 3) + 0.12 * max(0.0, age - 3)              # slow drift-in (also during the silence)
    return lerp(zp, zA(k), a) - 6.0 + min(drift, 3.0), a

def scene3d(c, T):
    k = rec_index(T)
    if T < HOOK: k = I_MOM if T > 0.2 else -1
    acc = np.zeros((AH, AW, 3), np.float32)
    if k < 0:
        c.art.paste(Image.fromarray(K.tonemap(acc, SKY))); c.a = ImageDraw.Draw(c.art); return
    if T < HOOK: cz, a = zA(k) - 6.0 + 0.4 * T, 1.0
    else: cz, a = cam_z(T, k)
    tx, ty = xyA(k)
    cam = Cam((tx * a, ty * a, cz), (tx, ty, zA(k)))
    # background stars, wrapped around the camera; streaks while flying, longer for big look-back jumps
    jump = (REC[k]["lb"] - (REC[k - 1]["lb"] if k else 0)) if T >= HOOK else 0
    warp_ = (1 - a) * min(1.0, 0.25 + jump / 3.0)
    S = STAR3.copy(); S[:, 2] = (S[:, 2] - cz) % 240 + 2 + cz
    x, y, z, ok = cam.proj(S)
    base = Image.new("RGB", (AW, AH), SKY); d = ImageDraw.Draw(base)
    if warp_ > 0.05:
        S2 = S.copy(); S2[:, 2] -= 40 * warp_
        x2, y2, _, ok2 = cam.proj(S2)
        for j in range(len(S)):
            if ok[j] and ok2[j]: d.line([x[j], y[j], x2[j], y2[j]], fill=mix([INK2, BLUE, INK][STARC[j]], SKY, .3))
    else:
        for j in range(len(S)):
            if ok[j] and 0 <= x[j] < AW and 0 <= y[j] < AH:
                d.point((x[j], y[j]), fill=mix([INK2, BLUE, INK][STARC[j]], SKY, .4 + .5 * min(1, z[j] / 200)))
    # galaxies: the new record (big, spinning) and the previous one flying past
    put_galaxy(acc, cam, k, (tx, ty, zA(k)), 3.6, 0.25 * T + k, 1.0)
    if k > 0 and a < 1: put_galaxy(acc, cam, k - 1, (*xyA(k - 1), zA(k - 1)), 4.6, 0.25 * T, 1 - a)
    v = np.floor((1 - np.exp(-acc * 1.6)) * 8) / 8
    img = np.clip(np.array(base, np.float32) + v * 255, 0, 255).astype(np.uint8)
    c.art.paste(Image.fromarray(img)); c.a = ImageDraw.Draw(c.art)
    if T >= HOOK: depth_gauge(c, T, k)

def labels3d(c):
    gauge_labels(c)

M.scene = scene3d
M.axis_labels = labels3d

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio":
        M.render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(M.render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(M.render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}.png")
    elif mode == "info":
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC})
    elif mode == "final":
        import subprocess
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(min(6, os.cpu_count() or 3)) as pool: print(pool.map(M.render_scene, [(i, out) for i in idxs]))
