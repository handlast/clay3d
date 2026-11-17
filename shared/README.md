# shared/ · 各作品共用的工具与研究

- `sf/samp.py`：采样器。读 SFZ / SF2 音色并逐音符渲染，用来合成 BGM。
- `sf/vox.py`：Piper TTS 人声切片工具（英文人声采样用，后来不再使用）。
- `qa/popcheck.py`：音频爆音 / 削波自检。
- `research/`：动画手法调研（`anim_techniques.md`、`anim_kit.py`）、分镜研究（`storyboard_study.md`）、标签实验记录（`tag_experiment.md`）、黏土渲染基准测试脚本。黏土原型的早期版本没有收录，正式版在根目录 `engine/`、`scenes/office.py`、`demos/boil_demo.py`、`docs/clay3d.md`。
- `styles/`：A–G 七种画风样张脚本（群聊体、绘本、像素、剪纸、黏土、黏土 3D 等）。
- `distill/`：动画缓动库蒸馏笔记。第三方仓库的原始抓取（raw/）没有收录。
- `distill_music/`：BGM 混音链 A/B 对比 demo 与笔记。

## 第三方音色与模型（未收录，需自行下载）

`sf/samp.py` 运行时要求把以下文件放在 `shared/sf/` 下。按各自许可，这里不再分发：

| 资源 | 来源 | 许可 |
|---|---|---|
| Salamander Grand Piano V3（SFZ+FLAC，`salamander/`） | Alexander Holm 原作，FreePats 整理：http://freepats.zenvoid.org/Piano/acoustic-grand-piano.html | CC BY 3.0 |
| GeneralUser GS（`GeneralUser-GS.sf2`） | S. Christian Collins：https://schristiancollins.com/generaluser.php | GeneralUser GS License（免费使用，详见作者页面） |
| Piper TTS 声音模型（`piper/*.onnx`） | https://github.com/rhasspy/piper （声音模型在 Hugging Face rhasspy/piper-voices） | 各声音模型的许可不同，详见模型卡 |

另外，音效库 Sonniss GDC 2026 免费包（`/workspace/sfx`）的许可禁止转售原始音效，所以也不入库。
