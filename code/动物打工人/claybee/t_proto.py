import sys, time, math, numpy as np, cv2
sys.path.insert(0, ".")
import world as Wd
from world import cp, cf
def shot(name, build, cam, tgt):
    Wd.reset(); faces = build()
    PI, PF, GR, G0, G1 = Wd.arr()
    L = np.array([-0.5, 0.8, 0.5]); L /= np.linalg.norm(L)
    t0 = time.time()
    img, dep, mask, info = cf.render_faces(720, 1280, 1080, 1920, np.array(cam, float), np.array(tgt, float), math.radians(44), L, PI, PF, GR, G0, G1,
                                           np.ones(7, np.int64), 0.0, faces, ss=2.0)
    focus = float(np.linalg.norm(np.array(cam) - np.array(faces[0][0])))
    out = cf.post_faces(img, dep, focus, mask)
    cv2.imwrite(f"tests/proto_{name}.png", out[..., ::-1]); print(name, round(time.time() - t0, 1), len(PI), info, flush=True)
    return out, info
def b1():
    Wd.hive(0, extra=("board",))
    A = Wd.bumblebee(-0.35, 0.2, 0.75, 0.2, "look", arms=(0.3, -0.2))
    B = Wd.bumblebee(0.45, 0.0, 0.75, -0.25, "happy", role="queen")
    return [(A["face"], A["face_r"]), (B["face"], B["face_r"])]
def b2():
    Wd.hive(0, extra=("moon",))
    br = Wd.brood(0.0, 0.0, 1.2, 1.0)
    A = Wd.bumblebee(0.0, 0.05, 0.7, 0.0, "sleepy", lie=1.0, y=0.25)
    return [(A["face"], A["face_r"])]
w = sys.argv[1:]
if "b1" in w: shot("b1", b1, (0, 1.2, 4.2), (0, 0.85, 0))
if "b2" in w: shot("b2", b2, (0, 1.5, 3.2), (0, 0.6, 0))
