"""Cogwise CLI.

  python -m cogwise.run stills  EPISODE.py OUTDIR t1 t2 ...      # look at key frames (design timeline)
  python -m cogwise.run preview EPISODE.py OUT.mp4               # silent render on the design timeline
  python -m cogwise.run build   EPISODE.py OUTDIR --tts CONFIG.json   # ElevenLabs voice + full assembly
  python -m cogwise.run build   EPISODE.py OUTDIR --voice VOICE.mp3   # existing voice, auto-aligned

`build` writes OUTDIR/<slug>.mp4 (final), <slug>.srt, <slug>_voice.mp3, <slug>_meta.json, <slug>_script.txt
CONFIG.json: {"elevenlabs_api_key": "...", "voice_id": "...", "model_id": "eleven_multilingual_v2"}
"""
import sys, os, json, argparse, shutil
from . import engine, audio, voice

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['stills', 'preview', 'build'])
    ap.add_argument('episode'); ap.add_argument('out')
    ap.add_argument('times', nargs='*', type=float)
    ap.add_argument('--tts'); ap.add_argument('--voice')
    a = ap.parse_args()
    mod = engine.load_episode(a.episode)

    if a.cmd == 'stills':
        for p in engine.stills(a.episode, a.out, a.times): print(p)
        return
    if a.cmd == 'preview':
        ep = engine.render_video(a.episode, a.out)
        print(f"preview {a.out} ({ep.length:.1f}s design timeline)"); return

    os.makedirs(a.out, exist_ok=True)
    slug = mod.META['slug']
    ep0 = engine.Episode(mod)
    captions = [b['caption'] for b in ep0.beats]
    words = len(" ".join(captions).split())
    print(f"script: {words} words")
    open(os.path.join(a.out, f"{slug}_script.txt"), 'w').write("\n".join(captions))
    vpath = os.path.join(a.out, f"{slug}_voice.mp3")
    if a.tts:
        cfg = json.load(open(a.tts))
        _, starts, vlen = voice.elevenlabs(captions, vpath, cfg['elevenlabs_api_key'], cfg['voice_id'],
                                           cfg.get('model_id', 'eleven_multilingual_v2'))
    elif a.voice:
        shutil.copy(a.voice, vpath)
        _, starts, vlen = voice.align_existing(captions, vpath)
    else:
        sys.exit("build needs --tts CONFIG.json or --voice FILE.mp3")
    print("voice", round(vlen, 2), "s; beat starts", [round(s, 2) for s in starts])
    silent = os.path.join(a.out, f"{slug}_silent.mp4")
    ep = engine.render_video(a.episode, silent, starts, vlen)
    sfx = os.path.join(a.out, f"{slug}_sfx.wav"); audio.build_sfx(ep, sfx)
    final = os.path.join(a.out, f"{slug}.mp4")
    audio.mux(silent, vpath, sfx, final, ep.length)
    ep.srt(os.path.join(a.out, f"{slug}.srt"))
    meta = dict(mod.META); meta.update(duration=round(ep.length, 2), words=words, beat_starts=starts)
    json.dump(meta, open(os.path.join(a.out, f"{slug}_meta.json"), 'w'), indent=2)
    os.remove(silent); os.remove(sfx)
    print("final", final, round(ep.length, 2), "s")
    if ep.length < 61:
        print("WARNING: under 61 s -> not eligible for TikTok Creator Rewards / Snapchat; lengthen the script.")

if __name__ == '__main__':
    main()
