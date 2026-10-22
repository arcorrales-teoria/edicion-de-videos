"""Cover = the video's own title frame (feed style since 20 oct 2026): my face + 'teoría by andrés corrales' + title, in this video's look."""
import sys, os
sys.argv = [sys.argv[0]] + sys.argv[1:]
import render23 as R
from render23 import fx, Image
t_face = float(sys.argv[1]) if len(sys.argv) > 1 else 2.6
out = sys.argv[2] if len(sys.argv) > 2 else 'portada.jpg'
for fi, t, fr in R.frames([t_face]):
    full = fx.resize_f(fr, (0, 0, fx.SW, fx.SH), (R.W, R.H)); sdr = full.copy(); hdr = full.copy()
    arr, surf, ctx = fx.new_layer(); R.title(ctx, t, force=True); surf.flush(); fx.layer_over(sdr, hdr, arr)
    Image.fromarray(fx.to8(sdr)).save(out, quality=94)
    Image.fromarray(fx.to8(sdr)).crop((0, 285, 1080, 1635)).resize((540, 675)).save(out.replace('.jpg', '_4x5.jpg'), quality=85)
print('saved', out)
