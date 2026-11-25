# Real-sample instruments for the Vibe BGM pipeline (no fluidsynth needed).
#   piano(m, dur, vel)                 -> Salamander Grand Piano (Yamaha C5, CC-BY 3.0, Alexander Holm)
#   gm(preset_name, m, dur, vel, ...)  -> GeneralUser GS SF2 preset (S. Christian Collins, free license)
# All return stereo float arrays (n, 2) at 44100 Hz. m = MIDI note number (already transposed).
import re, os, functools, numpy as np, soundfile as sf
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
SAL = os.path.join(HERE, "salamander")

def _resample(x, ratio, n_out, loop=None):
    """x: (len, ch). read positions = k*ratio; optional (ls, le) sustain loop."""
    pos = np.arange(n_out) * ratio
    if loop and (loop[1] - loop[0] < 8 or loop[1] > len(x) or loop[0] < 0): loop = None
    if loop:
        ls, le = loop; L = le - ls
        over = pos >= le
        pos[over] = ls + (pos[over] - ls) % L
    pos = pos[pos < len(x) - 1]
    i = pos.astype(int); f = (pos - i)[:, None]
    y = x[i] * (1 - f) + x[i + 1] * f
    if len(y) < n_out: y = np.vstack([y, np.zeros((n_out - len(y), x.shape[1]))])
    return y

# ---------------- Salamander ----------------
_REG = []
with open(os.path.join(SAL, "SalamanderGrandPiano-V3+20200602.sfz")) as fh:
    rel = False
    for ln in fh:
        if ln.startswith("<group>"): rel = "trigger=release" in ln
        if ln.startswith("<region>") and not rel and "pitch_keycenter" in ln:
            kv = dict(re.findall(r"(\w+)=(\S+)", ln))
            _REG.append((int(kv["lokey"]), int(kv["hikey"]), int(kv.get("lovel", 1)), int(kv.get("hivel", 127)), int(kv["pitch_keycenter"]), kv["sample"]))

@functools.lru_cache(maxsize=None)
def _flac(path):
    x, sr = sf.read(os.path.join(SAL, path), dtype="float32", always_2d=True); return x, sr

def piano(m, dur=2.0, vel=80, g=1.0, release=0.35):
    m = int(round(m)); vel = int(np.clip(vel, 1, 127))
    r = [z for z in _REG if z[0] <= m <= z[1] and z[2] <= vel <= z[3]] or [min(_REG, key=lambda z: abs(z[4] - m))]
    lo, hi, lv, hv, key, path = r[0]
    x, sr = _flac(path)
    n = int((dur + release) * SR)
    y = _resample(x, 2 ** ((m - key) / 12) * sr / SR, n)
    t = np.arange(n) / SR
    env = np.clip((dur + release - t) / release, 0, 1)        # damper release
    return y * env[:, None] * g

# ---------------- GeneralUser GS (SF2) ----------------
_SF = None
def _sf2():
    global _SF
    if _SF is None:
        import logging; logging.disable(logging.WARNING)
        from sf2utils.sf2parse import Sf2File
        _SF = Sf2File(open(os.path.join(HERE, "GeneralUser-GS.sf2"), "rb"))
    return _SF

@functools.lru_cache(maxsize=None)
def _sample_data(s):
    return np.frombuffer(s.raw_sample_data, dtype="<i2").astype(np.float32) / 32768.0

def _zones(preset, m, vel, bank=0):
    p = [p for p in _sf2().presets if p.name == preset and getattr(p, "bank", 0) == bank][0]
    out = []
    for pb in p.bags:
        if not pb.instrument: continue
        if pb.key_range and not (pb.key_range[0] <= m <= pb.key_range[1]): continue
        for ib in pb.instrument.bags:
            if not ib.sample: continue
            kr = ib.key_range or (0, 127); vr = ib.velocity_range or (0, 127)
            if kr[0] <= m <= kr[1] and vr[0] <= vel <= vr[1]: out.append((pb, ib))
    return out

def gm(preset, m, dur=1.0, vel=90, g=1.0, attack=None, release=0.3, decay=None, bank=0):
    """attack/release in s; decay = optional exponential decay rate (1/s) for plucked/struck sounds."""
    m = int(round(m)); n = int((dur + release) * SR); y = np.zeros((n, 2))
    for pb, ib in _zones(preset, m, vel, bank):
        s = ib.sample; x = _sample_data(s)[:, None]
        root = ib.base_note if ib.base_note is not None else s.original_pitch
        cents = (m - root) * 100 + (ib.tuning or 0) * 100 + (ib.fine_tuning or 0) + s.pitch_correction
        cents += (pb.tuning or 0) * 100 + (pb.fine_tuning or 0)
        loop = None
        if ib.sample_loop in (1, 3):
            ls = (ib.cooked_loop_start if ib.cooked_loop_start is not None else s.start_loop) - s.start
            le = (ib.cooked_loop_end if ib.cooked_loop_end is not None else s.end_loop) - s.start
            if le - ls > 32: loop = (ls, le)
        z = _resample(x, 2 ** (cents / 1200) * s.sample_rate / SR, n, loop)[:, 0]
        pan = {2: 0.7, 4: -0.7}.get(s.sample_type, 0.0)
        y[:, 0] += z * (1 - max(pan, 0)); y[:, 1] += z * (1 + min(pan, 0))
    t = np.arange(n) / SR
    env = np.clip((dur + release - t) / max(release, 1e-3), 0, 1)
    if attack: env *= np.clip(t / attack, 0, 1) ** 2
    if decay: env *= np.exp(-t * decay)
    return y * env[:, None] * (vel / 127) * g

def drum(note, vel=100, g=1.0, kit="Standard 1", dur=1.2):
    """GM drum map: 36 kick, 38 snare, 39 clap, 42 closed hat, 46 open hat, 49 crash, 45/47/50 toms, 76/77 woodblock, 81 open triangle."""
    return gm(kit, note, dur, vel, g, release=0.05, bank=128)
