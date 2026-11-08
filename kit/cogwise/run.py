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
    ap.add_argument('--starts', help='META.json of a previous build: reuse its beat_starts with --voice (no TTS, no alignment)')
    ap.add_argument('--no-stems', action='store_true', help='do not export stems/ for the Montage tab')
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
                                           cfg.get('model_id', 'eleven_multilingual_v2'),
                                           speed=float(cfg.get('speed', 1.0)))
        tempo = float(cfg.get('tempo', 1.0))   # post time-stretch (pitch kept), e.g. 1.1 = 10% faster
        if abs(tempo - 1.0) > 1e-3:
            import subprocess
            tmp = vpath + '.tmp.mp3'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vpath, '-filter:a', f'atempo={tempo}',
                            '-b:a', '128k', tmp], check=True)
            os.replace(tmp, vpath)
            starts = [s / tempo for s in starts]; vlen = voice._duration(vpath)
    elif a.voice and a.starts:
        # re-render with the exact timing of a previous build (montage level 2): no TTS, no alignment
        if os.path.abspath(a.voice) != os.path.abspath(vpath): shutil.copy(a.voice, vpath)
        starts = json.load(open(a.starts))['beat_starts']; vlen = voice._duration(vpath)
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
    meta_path = os.path.join(a.out, f"{slug}_meta.json")
    json.dump(meta, open(meta_path, 'w'), indent=2)
    if not a.no_stems:
        # separate tracks + light previews for the Control Room "Montage" tab (see tools/stems.py)
        import subprocess
        tools = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tools', 'stems.py')
        subprocess.run([sys.executable, tools, 'make', '--video', silent, '--track', f'voice={vpath}', '--track', f'sfx={sfx}',
                        '--meta', meta_path, '--out', os.path.join(a.out, 'stems')], check=True)
    os.remove(silent); os.remove(sfx)
    print("final", final, round(ep.length, 2), "s")
    if ep.length < 62:
        print("WARNING: under 62 s -> METHOD.md wants 63-70 s (TikTok rewards need > 1 min); add a beat (never slow the voice).")
    elif ep.length > 75:
        print("WARNING: over 75 s -> METHOD.md ceiling is 75 s; cut text (never speed up the voice).")

if __name__ == '__main__':
    main()
