#!/usr/bin/env python3
"""Stage Vibe知识大赏 works into clay3d-repo: code/, models/, shared/, audio list. Writes manifest JSON."""
import os, re, json, hashlib, shutil, sys, datetime, subprocess
W = "/workspace/work"
R = f"{W}/clay3d-repo"
SKIP_DIRS = {"clownfish3d", "howler", "murphy", "clay3d-repo", "brief"}
SHARED_DIRS = {"sf", "qa", "research", "styles", "distill", "distill_music"}
SERIES = {
 "新物种": "balrog exostoma frog ghostfrog jellyfrog glow killi mantis trapdoor webbug whale wormlion tilcayo drex hellchick seaamph muppet".split(),
 "动物打工人": "macaque macaque3d claybee".split(),
 "超级士兵": "simo york".split(),
 "脑洞-植物": "bolt sleep toad sneeze bun aliens zhu berry tomato flytrap grape mimosa treemuscle sunflower liver".split(),
}
NOTE = {  # judgment notes for INDEX
 "drex": "按内容归入（新种 D-rex，发布未带 #新物种）", "hellchick": "按内容归入（新种，发布未带 #新物种）",
 "seaamph": "按内容归入（新种，发布未带 #新物种）", "muppet": "按内容归入（发布标签未存档）",
 "tilcayo": "按内容归入（新野猫，发布未带 #新物种）", "macaque": "No.01 的 2D 初版",
 "macaque3d": "No.01 黏土 3D 成片；黏土模块已在仓库 engine/ characters/ props/ scenes/",
 "aliens": "娱乐加更（脑洞）", "border": "拿不准→其他（蚂蚁剧情，2.5D）", "bridge": "拿不准→其他（蚂蚁剧情，2.5D）",
 "zhanshou": "拿不准→其他（蚂蚁剧情，2.5D）", "dance": "恶搞片", "lizard": "拿不准→其他（化石新发现）",
 "salamander": "拿不准→其他", "snake": "拿不准→其他", "nobel": "拿不准→其他（16:9 早期测试）",
 "opto": "拿不准→其他（16:9 早期测试）",
}
TITLE_FALLBACK = {
 "berry": "《籽说了算》", "dance": "《火柴人跳舞》", "ufo": "《FBI 的 UFO 档案 1947–2026》", "horse": "《2026 双火马年（丙午）》",
 "macaque": "《动物打工人 No.01 爱看同事社交的猴子》（2D 版）", "opto": "（光遗传与抑郁，片名未存档）",
 "nobel": "（诺贝尔物理奖，片名未存档）", "zhu": "《混种》", "york": "一个不想打仗的农村神枪手，怎么让132名敌军投降？｜超级士兵 No.02",
 "sneeze": "《如果把喷嚏憋回去》", "horse ": "",
}
CODE_EXT = {".py", ".sh", ".md", ".json", ".txt", ".srt", ".geojson"}
EXCL_DIR_PARTS = {"__pycache__", "segs", "seg", "frames", "vox", "vo", "samples", "raw", "vids", "chk",
                  "clear_raw", "voxcache", "piper", "salamander", "clay", "tests_old"}
AUDIO_NAMES = {"bgm.wav", "bgm2.wav", "vo.wav", "music.wav", "bgm_only.wav", "mix.wav", "bed.wav"}

def series_of(d):
    for s, L in SERIES.items():
        if d in L: return s
    return "其他"

skipped = []  # (path, reason)
def rel(p): return os.path.relpath(p, W)

def code_files(d):
    out = []
    for root, dirs, files in os.walk(f"{W}/{d}"):
        parts = set(os.path.relpath(root, f"{W}/{d}").split(os.sep))
        if parts & EXCL_DIR_PARTS or any(x.startswith("tests") for x in parts):
            continue
        for f in files:
            p = os.path.join(root, f); ext = os.path.splitext(f)[1].lower()
            if ext in CODE_EXT:
                if os.path.getsize(p) > 2_000_000: skipped.append((rel(p), "文本文件 >2MB")); continue
                out.append(p)
    return out

def title_of(d):
    if d in TITLE_FALLBACK and TITLE_FALLBACK[d]: return TITLE_FALLBACK[d]
    p = f"{W}/{d}/publish.md"
    if os.path.exists(p):
        t = open(p, encoding="utf-8", errors="ignore").read()
        m = re.search(r"标题[\*：:\s]*\n?\s*([^\n]+)", t)
        if m:
            s = m.group(1).strip().strip("*").strip()
            if s: return s
    for f in ("cues.py", "film.py", "script.md", "mcues.py"):
        p = f"{W}/{d}/{f}"
        if os.path.exists(p):
            m = re.search(r"《[^》]{2,40}》", open(p, encoding="utf-8", errors="ignore").read())
            if m: return m.group(0)
    return "（未存档）"

def date_of(d):
    ts = [os.path.getmtime(p) for p in code_files(d)] or [os.path.getmtime(f"{W}/{d}")]
    tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.fromtimestamp(min(ts), tz).strftime("%Y-%m-%d")

def main():
    works = sorted(x for x in os.listdir(W) if os.path.isdir(f"{W}/{x}") and not x.startswith((".", "_"))
                   and x not in SKIP_DIRS and x not in SHARED_DIRS)
    man = {"works": [], "audio": [], "skipped": skipped}
    for d in works:
        s = series_of(d); dst = f"{R}/code/{s}/{d}"
        files = code_files(d)
        for p in files:
            q = os.path.join(dst, os.path.relpath(p, f"{W}/{d}")); os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(p, q)
        aud = []
        for f in sorted(os.listdir(f"{W}/{d}")):
            p = f"{W}/{d}/{f}"
            if f in AUDIO_NAMES:
                if os.path.getsize(p) > 95 * 2**20: skipped.append((rel(p), ">95MB")); continue
                aud.append(p)
        man["audio"] += aud
        man["works"].append({"dir": d, "series": s, "title": title_of(d), "date": date_of(d), "note": NOTE.get(d, ""),
                             "n_code": len(files), "audio": [os.path.basename(a).replace(".wav", ".flac") for a in aud]})
        # record skipped audio-ish / media in this work
        for root, dirs, fs in os.walk(f"{W}/{d}"):
            for f in fs:
                p = os.path.join(root, f); e = os.path.splitext(f)[1].lower()
                if e in {".wav", ".mp3"} and p not in aud:
                    skipped.append((rel(p), "中间音频/切片/旧版/音效分轨"))
    json.dump(man, open(f"{W}/_vibe_manifest.json", "w"), ensure_ascii=False, indent=1)
    print(len(works), "works;", len(man["audio"]), "audio")

if __name__ == "__main__":
    main()
