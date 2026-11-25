# Vibe知识大赏 · 项目备份（2026-11-25）

额度用尽前的整体备份，下个月或换环境时照这里恢复。

## 目录
- `workspace/`：沙盒 /workspace/work/ 下每部作品和工具的全部源码与文本（cues.py、music.py、film.py、render.sh、script.md、publish.md、srt 等）。不含 mp4/png、论文原文。
  - 共用工具：`workspace/qa/popcheck.py`（渲染前防闪烁检查）、`workspace/sf/samp.py`（采样音色）、`workspace/research/`（分镜研究、anim_kit.py 动画手法库）、`workspace/_vibe_stage.py`（往本仓库拷作品的脚本）。
  - 2D 扁平新物种最新模板：`workspace/jellyfrog/`、`workspace/ghostfrog/`；字幕自适应时间轴模板 `workspace/hellchick/`。
- `assets/fonts/`：Noto Sans SC Black/Bold、Noto Serif SC（OFL）。放回各作品目录或改路径即可。
- `assets/soundfonts/GeneralUser-GS.sf2`：GM 音色库（`samp.py` 的 gm()/drum() 用）。
- 未上传：Salamander Grand Piano V3（713 MB，CC-BY 3.0），从 https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html 下载，解压到 `sf/salamander/`。
- `project-memory/vibe-knowledge-douyin.md`：项目记忆（作品清单、数据复盘、所有永久规则）。
- `project-memory/SKILL-vibe-knowledge-film.md`：工作流 skill 的要点。
- `project-memory/daily-topic-task.md`：每日选题定时任务的提示词。

## 现行规则速记（2026-11-25）
- 只做两个系列：新物种、稀有动物。全部 2D 扁平卡通卡点小短片；其余系列（动物打工人、超级士兵、3D 黏土）停做。
- 不生成封面。发布文案：标题 ≤20 字含标点、无冒号、问题句；不写置顶评论；标签 ≤5；不写章节时间点。
- 大重音只在 0 s 和 BIG2（≤20 s）；镜头抖动小；禁黑色描边；每句讲解专属场景；屏上名牌不重复字幕。
- 字幕停留 ≥ max(1.5 s, 字数/4) 且 ≥ 旁白+0.1 s；安全区 x180–900、y<1440。
- 中文旁白、直白（面向小朋友），不用英文人声；BGM 按题材定制；响度约 −15 LUFS；帧数 = 时长×30。
- 实体 ≥0.3 s 渐隐，渲前跑 popcheck.py；科学措辞不过度肯定（关联≠因果）。
- 渲染：沙盒 2 核、单命令 ≤120 s，分段渲染再 mux；mux 先写 /tmp；禁 pkill -f。

## 进行中
- 下一条：新物种《这只蝴蝶躲了200年？》Colobura cryptica（Sapkota 等，Zootaxa 2026；ScienceDaily 2026-11-12）。三只一模一样的蝴蝶，BIG2 切紫外模式翅膀亮出不同颜色；毛虫花纹对比。尚未开做（因额度暂停）。
