# 《番茄会尖叫》shared timeline (s). Grid 120 BPM: beat 0.5, bar 2.
BEAT = 0.5; BAR = 2.0; DUR = 60.0
HOOK_CLICK = 0.0
HOOK_END = 2.6
COUNTER = [12.4 + 4.0 * (1 - (1 - i / 34) ** 0.5) for i in range(35)]  # accelerating 35 ticks 12.4-16.4
RISER = (27.0, 29.5)
SILENCE = (29.5, 30.0)
BURST = 30.0
BUBBLES = [36.5 + i * 0.5 for i in range(9)]
OUTRO = 56.0
LAST_CLICK = 59.0
