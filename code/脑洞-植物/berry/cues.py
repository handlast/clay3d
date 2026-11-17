# Shared timeline (seconds) for picture and music. 120 BPM: beat 0.5 s, bar 2 s.
BPM = 120; BEAT = 0.5; BAR = 2.0; DUR = 90.0
HOOK_SEEDS = [3.0 + i * 0.25 for i in range(10)]          # seeds light, glock run up
ROLL_IN = 6.0; STOP1 = 7.5; TITLE = 8.0
REWIND = (11.0, 12.5)
PISTILS = [14.0 + i * 0.125 for i in range(16)]           # pistils pop on 16ths
POLLEN = [17.5 + i * 0.25 for i in range(10)]
SWELL = 22.0
SIGNAL = [26.5 + i * 0.5 for i in range(6)]               # seeds emit auxin
BUMPS = [29.75 + i * 0.5 for i in range(6)]
GRAY = [33.5 + i * 0.5 for i in range(4)]
DENT = 37.0
RISER2 = (40.0, 41.5); STOP2 = 41.5; HIT2 = 42.0
LAB = 45.0
PLUCK = [49.5 + i * 0.125 for i in range(8)]              # seeds removed
BREAK3 = (49.0, 53.0); BRUSH = 53.5; HIT3 = 55.0
CHART = [57.5 + i * 0.25 for i in range(8)]
GAUGE = (65.5, 68.0)
BEE = (69.0, 72.5)
COLD = (73.0, 76.0)
CHECK = 79.5
FINALE = [82.0 + i * 0.125 for i in range(16)]
END = 86.0
