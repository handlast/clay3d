# 《世界上最吵的陆地动物，80多年来又多了两个新成员？》台本 / 内部分镜

- 时长 79.5 s（2385 帧 @30fps）；大重音只在 0.0 s（吼声吹飞叶帘）和 BIG2 = 20.0 s（“会！…2 个新物种”）。
- 旁白 edge-tts zh-CN-YunjianNeural −5%，每句字幕起点 +0.1 s 开口（hook +0.55 s，避开 0 秒重击；big2 +0.15 s），不加速。
- 画风：照 frog/ 的 2D 扁平无描边（注：派单写“3D 黏土风”，但 frog/ 实为 2D 扁平，按 frog 实际风格做）。
- BGM：亚马孙吼声桑巴（G 混合利底亚，120 BPM，16% swing；尼龙吉他 partido-alto + Finger Bass 苏尔多线 + 马林巴/长笛 + agogo/沙锤/康加/cuíca + 合成吼声）。music.py 全读 cues.py。
- 字幕停留检查：cues.check() 无不达标项（每句 ≥ max(1.5 s, 字数/4) 且 ≥ 旁白+0.1 s）。

| # | key | 时间 | 字幕 | 专属场景 |
|---|---|---|---|---|
| 1 | hook | 00.00–03.50 | 陆地上最吵的动物， 长什么样？ | 黎明雨林，叶帘被 0 秒吼声吹飞，红毛吼猴张嘴大吼 + 超大“吼——！” |
| 2 | reveal | 03.50–07.50 | 吼猴！吼声能传 大约 5 公里 | 拉远全景树冠，声波圈一圈圈传过去，0–5 km 标尺逐格点亮，远处猴子竖耳“!” |
| 3 | why | 07.50–12.00 | 大声吼，是在说： “这片林子是我家！” | 两棵树两群猴隔着虚线领地线比嗓门（左红右黑），音量表，左树挂小房子牌 |
| 4 | throat | 12.00–16.50 | 喉咙里有块空心大骨头， 像个扩音罐 | 解剖挂图：侧面头部剖开，空心舌骨发光共鸣，声波放大；角落“人 vs 吼猴”舌骨对比 |
| 5 | q | 16.50–20.00 | 这么吵的猴子， 科学家还会漏掉吗？ | 黄昏雨林四处回声，野外名录本逐行打勾，最后一行虚线框“?”闪，放大镜扫页 |
| 6 | big2 | 20.00–25.00 | 会！亚马孙雨林里 又找到 2 个新物种！ | 白闪+重音：金色放射线、淡入亚马孙地图，大字“2”，金毛和红毛新种跳出带“新”角标，叶子爆散 |
| 7 | gold | 25.00–29.50 | 一种是金黄毛， 住在亚马孙西北部 | 桌山（Pantepui 平顶山）+瀑布，金毛吼猴从左入画；右上全南美小地图西北区闪烁+图钉；名牌 A. iroi |
| 8 | red | 29.50–34.00 | 一种是红褐毛， 住在亚马孙南部 | 蜿蜒河流的南部雨林，红毛吼猴从右入画；左上小地图南部区闪烁；名牌 A. matogrossensis |
| 9 | diff | 34.00–40.00 | 和亲戚长得很像，可连喉咙里 那块骨头的形状都不一样 | “找不同”两张相框：新种 vs 近亲，红圈圈毛色；下方 X 光条：舌骨开口椭圆 vs 半圆，≠ |
| 10 | river | 40.00–46.00 | 科学家认为，是一条条大河 把它们隔开了 | 俯视地图：大河一条条长出来，原本混在一起的点按河两岸变成金/红两色；沙漏 |
| 11 | dna | 46.00–50.00 | 科学家一共研究了 86 只吼猴的基因 | 实验台试管架，86 支样本管依次弹入，计数 0→86 滚动 |
| 12 | museum | 50.00–55.00 | 有的基因，来自博物馆 老标本上一点点干皮 | 博物馆展柜里的老标本（标签 Mycetes），镊子取下一点干皮放进试管，DNA 双螺旋升起；名牌“慕尼黑 · 博物馆” |
| 13 | genome | 55.00–59.50 | 这是第一次给吼猴家族 做全基因组分析 | 吼猴家族树 11 个头像，扫描线从上到下扫过，每个物种长出基因条码，“No.1”印章 |
| 14 | y1941 | 59.50–64.00 | 上一次给吼猴新种起名， 还是 1941 年 | 时间轴：左边泛黄 1941 名片，金点沿轴跑，年份 1941→2026 滚动+日历页飞，右边两张 2026 新名片 |
| 15 | danger | 64.00–69.50 | 可红褐毛吼猴住的地方， 森林消失得很快 | 俯视森林方格逐块渐变成农田，红毛吼猴担心；绳桥连起两块林子，妈妈背宝宝过桥 |
| 16 | card | 69.50–74.00 | 基因组：一种生物 全套的 DNA 说明书 | “一句话学会”知识卡：基因组＝一种生物全套的 DNA 说明书 + 翻页 DNA 书（此句不出字幕） |
| 17 | end | 74.00–79.50 | 你还知道哪些 超级大嗓门的动物？ | 回到开头黎明树冠（match cut），金毛、红毛轮流吼，气泡“谁的嗓门更大？”，文献卡，末 0.5 s 渐黑 |

## 科学口径（对照原文）
- Batista R, Semedo TBF, Beck RMD … Boubli JP (2026) Genome-wide analyses reveal recent diversification and hidden diversity in Amazonian howler monkeys, including two new species. Commun Biol, doi:10.1038/s42003-026-11187-8。Received 2025-10-27，Accepted 2026-10-05，Published 2026-10-30（Article in Press，CC BY）。
- 86 只：原文 Methods “We analysed 86 individuals (… including 35 previously published …)”；UCE 系统树用了 83 只。全基因组覆盖 13 个公认种中的 11 个。
- “第一次全基因组分析”：IFLScience 原话 “the first genome-wide study on the genus Alouatta”。
- A. iroi（Pantepui red howler）：背毛亮黄褐到浅金褐，四肢暗红褐；分布亚马孙西北部（Rio Branco 与 Rio Cauaburi 之间、Rio Negro 以北）；模式产地 Aracá 桌山山脚。
- A. matogrossensis（Mato Grosso red howler）：背毛亮红褐；分布亚马孙南部（Rio Madeira 东岸至 Rio Teles Pires 西岸）；模式产地 Alta Floresta。
- 舌骨不同：原文诊断特征含雄性舌骨孔形状（iroi 近椭圆 vs 近亲 A. macconnelli 半圆；matogrossensis 半圆 vs A. sara 椭圆）。片中只说“形状不一样”。
- 大河隔离：原文 “geographical barriers (e.g., Amazonian rivers …)”；片中加“科学家认为”。
- 干皮：IFLScience “DNA … obtained from bits of dried skin on two mounted specimens at the Zoologische Staatssammlung München”；原文为 Mycetes barbatus / M. discolor 的模式标本。
- 5 公里、陆地最吵：IFLScience（“considered to be the world's loudest land animal … heard as far as 5 kilometers”）。片中说“被叫作/大约”。
- 舌骨扩音：Dunn et al. 2015 Curr Biol 25:2839（greatly enlarged hyoid；共鸣腔为作者推断）→ 片中“像个扩音罐”。
- “85 年”：IFLScience 说 85 年；Salford 新闻稿说上一个新种 A. puruensis Lönnberg 1941 是“84 years”前（且本文认为 puruensis 是 A. juara 的同物异名）。数字两家不一致 → 标题改“80多年来”，片中只说“上一次……还是 1941 年”。
- 森林消失：Salford 新闻稿称 matogrossensis 栖息地是“world's fastest-deforesting regions”之一；绳桥画面对应 IFLScience 配图（Alta Floresta 人工树冠桥上的母猴背幼崽）。
