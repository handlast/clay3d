# agent simulation of Argentine ant workers: MOVE / CONTACT / PASS / FIGHT / DEAD / RETREAT
import numpy as np, math, os
MOVE, CONTACT, FIGHT, DEAD, PASS, RETREAT = 0, 1, 2, 3, 4, 5
FPS = 30

def curve(p0, p1, wig, seed, n=60):
    rng = np.random.default_rng(seed); p0 = np.array(p0, float); p1 = np.array(p1, float)
    t = np.linspace(0, 1, n); d = p1 - p0; nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
    off = np.zeros(n)
    for k in range(1, 4): off += rng.uniform(-1, 1) * wig / k * np.sin(np.pi * k * t + rng.uniform(0, 6.28)) * np.sin(np.pi * t)
    return p0 + d * t[:, None] + nrm * off[:, None]

def path_point(P, cum, s):
    s = np.clip(s, 0, cum[-1]); i = np.clip(np.searchsorted(cum, s) - 1, 0, len(P) - 2)
    u = (s - cum[i]) / np.maximum(cum[i + 1] - cum[i], 1e-9)
    return P[i] + (P[i + 1] - P[i]) * u[..., None]

def run(cfg, cache=None):
    if cache and os.path.exists(cache): return dict(np.load(cache))
    rng = np.random.default_rng(cfg.get("seed", 1))
    T0, T1 = cfg["t0"], cfg["t1"]; dt = 1.0 / FPS * cfg.get("timescale", 1.0)
    warm = cfg.get("warm", 0.0)
    nfr = int(round((T1 - T0) * FPS)); nwarm = int(warm / dt)
    paths = [np.asarray(p, float) for p in cfg["paths"]]; cums = [np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]) for p in paths]
    pcol = cfg["path_colony"]; N = cfg["n"]
    pid = rng.integers(0, len(paths), N)
    if "path_weights" in cfg: pid = rng.choice(len(paths), N, p=np.array(cfg["path_weights"]) / sum(cfg["path_weights"]))
    col = np.array([pcol[p] for p in pid])
    L = np.array([cums[p][-1] for p in pid])
    s = rng.uniform(-cfg.get("spawn_spread", 0.0), 1.0, N) * L * cfg.get("fill", 1.0)   # progress along path (negative = not yet spawned)
    lat = rng.normal(0, cfg.get("lat", 0.8), N)
    spd = rng.uniform(*cfg.get("speed", (5, 9)), N)
    x = np.zeros(N); z = np.zeros(N); hd = np.zeros(N)
    for i in range(N):
        p = path_point(paths[pid[i]], cums[pid[i]], np.array([max(s[i], 0)]))[0]; q = path_point(paths[pid[i]], cums[pid[i]], np.array([max(s[i], 0) + 1]))[0]
        d = q - p; hd[i] = math.atan2(d[1], d[0]); nn = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        x[i], z[i] = p + nn * lat[i]
    st = np.full(N, MOVE); tim = np.zeros(N); phase = rng.uniform(0, 1, N); aa = rng.uniform(0, 6, N); ab = rng.uniform(0, 6, N)
    mand = np.zeros(N); clus = np.full(N, -1); immune = np.zeros(N); wander = rng.normal(0, 1, N)
    clusters = {}; cid = 0
    pf = cfg.get("p_fight", 0.0); pf_t = cfg.get("fight_after", -1e9)
    border = cfg.get("border")    # dict: func z_b(x) and band: ants arriving wander along it
    dead_pre = cfg.get("dead_litter", 0)
    out = {k: np.zeros((nfr, N + dead_pre), np.float32) for k in ("x", "z", "hd", "ph", "aa", "ab", "mand", "st", "vis")}
    if dead_pre:
        lx = rng.uniform(*cfg["litter_x"], dead_pre); lz = np.array([border["zb"](v) for v in lx]) + rng.normal(0, cfg.get("litter_w", 3), dead_pre)
        lh = rng.uniform(0, 6.28, dead_pre)
    tsim = T0 - nwarm * dt
    for step in range(-nwarm, nfr):
        tnow = tsim
        active = (s >= 0) & (st != DEAD)
        # --- movement for MOVE/PASS/RETREAT ---
        mv = active & np.isin(st, (MOVE, PASS, RETREAT))
        for i in np.nonzero(mv)[0]:
            P = paths[pid[i]]; cu = cums[pid[i]]
            if border is not None and s[i] >= cu[-1] - 0.5:
                # arrived: patrol along the border with wandering
                wander[i] += rng.normal(0, 0.6) * dt * 3
                hd[i] += (wander[i] * 0.9) * dt * 2.0
                zb = border["zb"](x[i]); side = -1 if col[i] == 0 else 1
                # keep near own side of border
                pull = (zb + side * border.get("off", 1.0) - z[i])
                desired = math.atan2(pull * 0.15 + math.sin(hd[i]) * 0.5, math.cos(hd[i]))
                hd[i] += (desired - hd[i]) * 0.1
            else:
                ds = spd[i] * dt * (-1 if st[i] == RETREAT else 1)
                s[i] += ds
                tgt = path_point(P, cu, np.array([max(s[i], 0) + 2.0 * (1 if st[i] != RETREAT else -1)]))[0]
                p0 = path_point(P, cu, np.array([max(s[i], 0)]))[0]
                d = tgt - p0; nn = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
                tgt = tgt + nn * (lat[i] + 0.6 * math.sin(tnow * 1.3 + i))
                desired = math.atan2(tgt[1] - z[i], tgt[0] - x[i])
                dh = (desired - hd[i] + math.pi) % (2 * math.pi) - math.pi
                hd[i] += dh * min(1, 6 * dt) + rng.normal(0, 0.05)
            if s[i] >= 0:
                v = spd[i] * dt
                x[i] += math.cos(hd[i]) * v; z[i] += math.sin(hd[i]) * v
                phase[i] = (phase[i] + v / 0.55) % 1.0
            if st[i] == PASS and tnow > tim[i]: st[i] = MOVE
            if st[i] == RETREAT and tnow > tim[i]: st[i] = MOVE
        # not yet spawned: advance progress
        ns = s < 0; s[ns] += spd[ns] * dt
        # --- contacts ---
        cand = np.nonzero(active & (st == MOVE) & (tnow > immune))[0]
        if len(cand) > 1:
            X = x[cand]; Z = z[cand]
            hx = X + np.cos(hd[cand]) * 1.0; hz = Z + np.sin(hd[cand]) * 1.0
            D = np.hypot(hx[:, None] - hx[None, :], hz[:, None] - hz[None, :]); np.fill_diagonal(D, 99)
            ii, jj = np.nonzero(D < cfg.get("contact_r", 1.3))
            used = set()
            for a_, b_ in zip(ii, jj):
                i, j = cand[a_], cand[b_]
                if i in used or j in used or i >= j: continue
                used.add(i); used.add(j)
                st[i] = st[j] = CONTACT; tim[i] = tim[j] = tnow + rng.uniform(0.5, 1.1)
                clus[i] = j; clus[j] = i
                # face each other
                hd[i] = math.atan2(z[j] - z[i], x[j] - x[i]); hd[j] = hd[i] + math.pi
        # --- contact resolution ---
        for i in np.nonzero(active & (st == CONTACT))[0]:
            aa[i] += dt * 9; ab[i] += dt * 8
            if tnow > tim[i]:
                j = clus[i]
                if st[j] != CONTACT: st[i] = PASS; tim[i] = tnow + 1.5; immune[i] = tnow + 2.0; continue
                if col[i] != col[j] and tnow > pf_t and rng.random() < pf:
                    cid += 1; tend = tnow + rng.uniform(*cfg.get("fight_dur", (3, 9)))
                    clusters[cid] = {"m": [i, j], "c": np.array([(x[i] + x[j]) / 2, (z[i] + z[j]) / 2]), "end": tend, "v": rng.normal(0, 1, 2)}
                    st[i] = st[j] = FIGHT; clus[i] = clus[j] = cid
                elif col[i] != col[j]:
                    st[i] = st[j] = RETREAT; tim[i] = tim[j] = tnow + 1.2; immune[i] = immune[j] = tnow + 2.5
                    hd[i] += math.pi; hd[j] += math.pi
                else:
                    for k in (i, j): st[k] = PASS; tim[k] = tnow + 1.0; immune[k] = tnow + 2.0; lat[k] += rng.choice((-0.8, 0.8)); hd[k] += rng.uniform(-0.5, 0.5)
        # --- joining fights ---
        if clusters:
            mvj = np.nonzero(active & (st == MOVE))[0]
            for c_, C in list(clusters.items()):
                if len(C["m"]) >= cfg.get("max_cluster", 6): continue
                d = np.hypot(x[mvj] - C["c"][0], z[mvj] - C["c"][1])
                for k in mvj[d < cfg.get("join_r", 3.0)]:
                    if rng.random() < cfg.get("p_join", 0.08) and st[k] == MOVE:
                        C["m"].append(k); st[k] = FIGHT; clus[k] = c_
        # --- fight dynamics ---
        for c_, C in list(clusters.items()):
            C["v"] += rng.normal(0, 1.2, 2) * dt * 3; C["v"] *= 0.97
            C["c"] = C["c"] + C["v"] * dt * 0.8
            m = [k for k in C["m"] if st[k] == FIGHT]; n = len(m)
            for r, k in enumerate(m):
                ang = 2 * math.pi * r / n + 0.4 * math.sin(tnow * 3 + k)
                rad = 0.75 + 0.15 * n
                tx = C["c"][0] + math.cos(ang) * rad; tz = C["c"][1] + math.sin(ang) * rad
                x[k] += (tx - x[k]) * 0.25 + rng.normal(0, 0.06); z[k] += (tz - z[k]) * 0.25 + rng.normal(0, 0.06)
                hd[k] = math.atan2(C["c"][1] - z[k], C["c"][0] - x[k]) + rng.normal(0, 0.15)
                phase[k] = (phase[k] + rng.uniform(0.05, 0.25)) % 1
                mand[k] = 0.5 + 0.5 * math.sin(tnow * 14 + k)
                aa[k] += dt * 14; ab[k] += dt * 13
            if tnow > C["end"] or n < 2:
                nd = 1 + (n > 3) * (rng.random() < 0.5)
                for k in rng.permutation(m)[:nd] if n >= 2 else []:
                    st[k] = DEAD; mand[k] = 0.3
                for k in m:
                    if st[k] == FIGHT: st[k] = PASS; tim[k] = tnow + 1.5; immune[k] = tnow + 2.5; mand[k] = 0; hd[k] += rng.uniform(-1, 1)
                del clusters[c_]
        # antenna idle sweep
        idle = active & np.isin(st, (MOVE, PASS, RETREAT)); aa[idle] += dt * 4; ab[idle] += dt * 4.4
        if step >= 0:
            o = step
            out["x"][o, :N] = x; out["z"][o, :N] = z; out["hd"][o, :N] = hd; out["ph"][o, :N] = phase
            out["aa"][o, :N] = aa; out["ab"][o, :N] = ab; out["mand"][o, :N] = mand; out["st"][o, :N] = st
            out["vis"][o, :N] = (s >= 0)
            if dead_pre:
                out["x"][o, N:] = lx; out["z"][o, N:] = lz; out["hd"][o, N:] = lh; out["st"][o, N:] = DEAD; out["vis"][o, N:] = 1
        tsim += dt
    out["col"] = np.concatenate([col, rng.integers(0, 2, dead_pre)]).astype(np.float32)
    if cache: np.savez_compressed(cache, **out)
    return out
