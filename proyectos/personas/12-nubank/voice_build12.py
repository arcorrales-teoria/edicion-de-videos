import wave, json, subprocess, os, numpy as np
from edit12 import SEGS, OFF, TOTAL, WAVS, vb
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
SPEED = 1.05
src = {}
for k, f in WAVS.items():
    with wave.open(f) as w: sr = w.getframerate(); src[k] = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
FADE = int(0.012 * sr); FLOOR = -4.8
out = np.zeros((int(TOTAL * sr) + 4 * sr, 2), np.float32)
for i, ((s, a, b), o) in enumerate(zip(SEGS, OFF)):
    y = src[s][int(a * sr):int(b * sr)].copy()
    fi = int(0.025 * sr) if vb(s, a) - FLOOR > 4 else FADE          # voiced start -> slightly longer fade-in
    fo = int(0.07 * sr) if vb(s, b - 0.01) - FLOOR > 4 else FADE    # voiced tail -> natural 70 ms decay inside the take
    if i > 0: y[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi))[:, None]
    if i < len(SEGS) - 1: y[-fo:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, fo))))[:, None]
    d0 = int(o * sr); out[d0:d0 + len(y)] += y
out = out[:int(TOTAL * sr)]
n = int(0.25 * sr); out[-n:] *= np.linspace(1, 0, n)[:, None]
with wave.open('voice_raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
run = lambda a: subprocess.run(a, capture_output=True, text=True)
run(['ffmpeg', '-v', 'error', '-y', '-i', 'voice_raw.wav', '-af', 'highpass=f=80,afftdn=nr=8:nf=-45:tn=1', '-c:a', 'pcm_s16le', 'voice_dn.wav'])
r = run(['ffmpeg', '-i', 'voice_dn.wav', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
af = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
run(['ffmpeg', '-v', 'error', '-y', '-i', 'voice_dn.wav', '-af', af + f',atempo={SPEED}', '-ar', '48000', '-c:a', 'pcm_s16le', 'voice_s16.wav'])
print('voice built (%.2fx)' % SPEED)
