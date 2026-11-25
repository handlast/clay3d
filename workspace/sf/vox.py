# English vocal samples via Piper TTS (rhasspy voices, local onnx). say(text, voice) -> mono float array at SR (cached wav).
import os, subprocess, hashlib, wave, numpy as np, sys
SR = 44100
V = {"ryan": "/workspace/work/sf/piper/en_US-ryan-high.onnx", "lessac": "/workspace/work/sf/piper/en_US-lessac-high.onnx"}
def say(text, voice="ryan", speed=1.0):
    h = hashlib.md5(f"{text}|{voice}|{speed}".encode()).hexdigest()[:10]; p = f"/workspace/work/sf/voxcache/{h}.wav"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p):
        env = dict(os.environ); env["PYTHONPATH"] = "/workspace/.pylib"
        subprocess.run([sys.executable, "-m", "piper", "-m", V[voice], "-f", p, "--length-scale", str(1 / speed)], input=text.encode(), env=env, check=True, capture_output=True)
    with wave.open(p) as w: sr = w.getframerate(); y = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32768
    y = np.interp(np.arange(int(len(y) * SR / sr)) * sr / SR, np.arange(len(y)), y)
    nz = np.where(np.abs(y) > 0.01)[0]
    return y[max(0, nz[0] - 200): nz[-1] + 2000] if len(nz) else y
def fx(y, pitch=1.0, lofi=0.0, drive=1.0):
    if pitch != 1.0: y = np.interp(np.arange(0, len(y) - 1, pitch), np.arange(len(y)), y)
    if lofi: k = int(1 + lofi * 6); y = np.repeat(y[::k], k)[: len(y)]; y = np.round(y * (64 / lofi)) / (64 / lofi)
    if drive != 1.0: y = np.tanh(y * drive) / np.tanh(drive)
    return y / (np.abs(y).max() + 1e-9)
