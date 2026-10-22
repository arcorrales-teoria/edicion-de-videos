"""DeepFilterNet3 speech enhancement: python dfclean.py in.wav out.wav [atten_lim_db]"""
import sys, torch
from df.enhance import enhance, init_df, load_audio, save_audio
model, state, _ = init_df()                                   # DeepFilterNet3, 48 kHz
audio, _ = load_audio(sys.argv[1], sr=state.sr())
lim = float(sys.argv[3]) if len(sys.argv) > 3 else None
out = enhance(model, state, audio, atten_lim_db=lim)
save_audio(sys.argv[2], out, state.sr())
print('saved', sys.argv[2], tuple(out.shape))
