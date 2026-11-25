# 《捕蝇草会数数》shared timeline (s). 120 BPM grid.
BEAT = 0.5; DUR = 45.0
HOOK_TOUCH = [0.1, 0.4]; HOOK_SNAP = 0.5; HOOK_END = 2.6
T1 = 4.0; FORGET = 7.5
T2 = [9.5, 10.5]; SNAP2 = 10.55
T3 = 14.0; T4 = 16.5
RISER = (17.5, 19.5); SILENCE = (19.5, 20.0); BURST = 20.0  # touch 5
WIND = [25.0, 26.5]          # single touches, no snap
FLOOD = (30.0, 35.0)         # counts race up
PUMP = (35.0, 39.0)
OUTRO = 39.0; LAST_SNAP = 44.0
TOUCHES = HOOK_TOUCH + [T1] + T2 + [T3, T4, BURST]
