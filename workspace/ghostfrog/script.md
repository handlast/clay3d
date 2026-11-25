# 《这只青蛙的眼睛，上半红、下半铜绿？》台本 / 内部分镜

- 时长 94.0 s（2820 帧 @30fps）；大重音只在 0.0 s（眼睛睁开）和 BIG2 = 17.5 s（“一个新物种！”）。
- 旁白 edge-tts zh-CN-YunjianNeural −5%，每句字幕起点 +0.1 s 开口（hook +0.55 s，避开 0 秒重击；big2 +0.15 s），不加速。
- 画风：照 howler/frog 的 2D 扁平无描边（深色只用在瞳孔、嘴线、眼睑线）；暗部是同尺寸下移的色块，不是放大的描边。
- BGM：安第斯云雾林夜行“幽灵瓦伊诺”（E 小调 Em–D–C–B7，120 BPM，12% swing，huayno 长–短律动）：排箫主旋律 + 竖笛应答 + 尼龙吉他“查兰戈”扫弦 + 拨弦潜行 + 马林巴 + 木低音，bombo（底鼓+落地通鼓）、沙锤、木鱼夜里滴答；合成“呜——”幽灵滑音、蛙鸣、牛叫、牛铃、蹄声。music.py 全读 cues.py。
- 字幕停留检查：cues.check() 无不达标项（每句 ≥ max(1.5 s, 字数/4) 且 ≥ 旁白+0.1 s）。
- 防闪烁：popcheck lint 3 处均已确认（尺子刻度静态、网纹分支已改为渐显）；成片 luma 检测的 12 处全部落在 0.3 s 叠化或 BIG2 白闪内（亮背景↔暗背景换场），逐帧看过无跳变。

| # | key | 时间 | 字幕 | 专属场景 |
|---|---|---|---|---|
| 1 | hook | 00.00–05.00 | 这只青蛙的眼睛， 上半红、下半铜绿？ | 特写→近景：夜里落叶堆，一只巨大的眼睛 0 秒睁开（上红下青铜绿、黄眼白），盖在眼上的落叶被吹飞，超大字“一半红/一半铜绿”；2.3–3.7 s 拉远成整只蛙的脸 |
| 2 | leaf | 05.00–09.00 | 它趴在落叶堆里， 一动不动就“消失”了 | 中景：头灯光圈里的落叶地面，蛙从上一镜大小缩到中景，身体慢慢“融进”落叶（只剩眼睛），几片叶子飘落盖住它，金色虚线圈出两只眼睛 |
| 3 | night | 09.00–14.00 | 科学家戴着头灯， 从晚上 7 点找到凌晨 3 点 | 全景：云雾林夜景+溪流，科学家戴头灯慢走，光束扫地；右上闹钟 19:00 → 03:00（扇形累计夜色），光束里亮起两点红色眼反光 |
| 4 | q | 14.00–17.50 | 这只红眼小蛙， 到底是谁？ | 近景：头灯聚光下的蛙东张西望（狐疑脸），身后大“?”发光，右下“物种：？？？”身份卡滑入；滚奏+riser |
| 5 | big2 | 17.50–23.00 | 一个新物种！ 科学家今年才给它起名 | BIG2 重击+白闪：放射光、落叶爆散，蛙跳起，大字“新物种！”，红色“2026 命名”印章，学名牌 |
| 6 | eye | 23.00–29.00 | 认它就看眼睛：上半红， 下半青铜绿带褐色花纹 | 大特写：画笔把虹膜上半刷红、下半刷青铜绿，再长出褐色网纹，最后眼白变黄（箭头+“眼白：黄色”），左侧“上/下”色块 |
| 7 | name | 29.00–33.00 | 它的名字，意思是 “叶子里的幽灵” | 拉丁文词典卡：folia（叶子，落叶图标）+ spectrum（幽灵·影像，小幽灵图标）滑入，“+”，合成一张大卡 foliaspectrum + 半透明蛙 |
| 8 | ghost | 33.00–38.50 | 红眼睛、细长手指脚趾、 一身落叶色，像个影子 | 中景：落叶里一只半透明发光的“幽灵蛙”上下漂；依次：红眼睛虚线圈、手指脚趾伸长并发光、身体色块 = 落叶色块 |
| 9 | skin | 38.50–45.00 | 背上全是尖尖小疙瘩， 肚子橙色带花纹 | 俯视大特写：放大镜扫过背部，镜中是大小一样的尖小颗粒+W 形肩斑；蛙翻身（水平压扁再展开），放大镜看橙色肚子上的褐色网纹 |
| 10 | size | 45.00–51.50 | 选作代表的那只雌蛙， 身长 32.4 毫米 | 坐标纸（1 格=1 mm）：俯视蛙滑入，黄色尺子+红色量条从吻端涨到泄殖孔，读数 0→32.4 毫米，旁边一元硬币（直径 25 mm，同比例） |
| 11 | sex | 51.50–54.50 | 而且雌蛙 比雄蛙大一圈 | 同一张坐标纸：雄（蓝）与雌（粉）并排，同比例缩放，虚线标出两者吻端高度差+箭头，下方“23–26 毫米 / 30–33 毫米” |
| 12 | hole | 54.50–60.00 | 每一只都在树根下的洞旁， 一有危险就钻进去 | 剖面：地面上拱起的树根，下面是通往地下小洞室的通道；头灯光束扫来、蛙头上“!”，蛙一跳到洞口、顺通道滑进洞室，黑暗里只剩眼睛发光 |
| 13 | four | 60.00–64.00 | 这次科学家一共发现了 4 种新的小蛙 | 排排报到（2×2）：4 种新蛙依次蹦出带编号，学名牌 azulensis / chirimoto / foliaspectrum（金色高亮）/ nigrumcompletum，颜色按论文 |
| 14 | genus | 64.00–68.50 | 它们所在的蛙家族， 从 27 种变成了 31 种 | 标本柜：标着“Oreobates 属”的 35 格柜子，27 个旧抽屉依次亮起，再滑出 4 个发光的“新”抽屉，顶部计数 27 种 → 31 种 |
| 15 | devel | 68.50–72.50 | 这类蛙不当蝌蚪： 卵里直接钻出小青蛙 | 上下对比：上排“水里” 卵→蝌蚪→蛙；下排“地上” 卵里长出小蛙，蝌蚪被红叉划掉，小蛙从卵旁蹦出 |
| 16 | card | 72.50–78.00 | 直接发育：跳过蝌蚪， 在卵里直接长成小青蛙 | “一句话学会”知识卡：直接发育＝跳过蝌蚪，在卵里直接长成小青蛙 + 图示（此句不出底部字幕） |
| 17 | map | 78.00–84.00 | 全世界只在秘鲁 一个地方见过它 | 地图：南美→放大到秘鲁，红色定位点只有一个（圣马丁省 Canaan），脉冲圈+云雾飘过；右侧海拔计 0→约 2100 米 |
| 18 | cows | 84.00–89.00 | 它住的小树林又矮又小， 四周全是养牛的牧场 | 斜俯视：一小片矮林（细树、树蕨、竹子）被淡绿牧场包围，几头牛在四周吃草；“树冠不到 6 米”标尺；泥地上一串牛蹄印依次出现 |
| 19 | end | 89.00–94.00 | 你见过眼睛最特别的 动物是什么？ | 回扣开头：落叶堆里的蛙眨眼看镜头，气泡“?”，身体慢慢隐去只剩一双红绿眼睛发光；文献小字，末 0.6 s 渐黑 |

## 旁白全文
- hook：这只青蛙的眼睛，上半边红，下半边铜绿？
- leaf：它趴在落叶堆里，一动不动，就像消失了一样。
- night：科学家戴着头灯，从晚上七点找到凌晨三点。
- q：这只红眼睛的小蛙，到底是谁？
- big2：答案是：一个新物种！科学家今年才给它起好名字。
- eye：认它就看眼睛：上半红，下半青铜绿，还带褐色花纹。
- name：它的拉丁文名字，意思是：叶子里的幽灵。
- ghost：红眼睛、细长的手指脚趾、一身落叶色，像个影子。
- skin：背上全是一样大的尖尖小疙瘩，肚子是橙色的，带褐色花纹。
- size：选作代表的那只雌蛙，身长只有三十二点四毫米，比一元硬币宽一点。
- sex：而且雌蛙比雄蛙大一圈。
- hole：抓到的每一只，都在树根下的洞旁边，一有危险就钻进去。
- four：这次科学家一共发现了四种新小蛙。
- genus：它们所在的蛙家族，从二十七种变成了三十一种。
- devel：这类蛙不当蝌蚪，卵里直接钻出小青蛙。
- card：这叫直接发育：跳过蝌蚪，在卵里直接长成小青蛙。
- map：全世界只在秘鲁一个地方见过它：海拔两千一百米左右的云雾林。
- cows：它住的小树林又矮又小，四周全是养牛的牧场。
- end：你见过眼睛最特别的动物是什么？评论区告诉我！

## 科学口径（对照原文 /workspace/work/ore_paper.txt）
- 论文：Venegas PJ, Ttito JW, García-Ayachi LA, Gulman M, Valencia JD, Catenazzi A (2026) Four New Species of Direct-Developing Frogs, Genus Oreobates (Anura: Strabomantidae), from Peru. Diversity 18(8):458, doi:10.3390/d18080458，2026-07-30 发表 → 片中只说“今年才给它起名”，不说“刚刚/本周”。
- 眼睛：Diagnosis (3) “bicolored iris, upper half red and lower half greenish bronze with brown reticulations”；Characterization (13) “sclera yellow or orange”（片中“眼白：黄色”，与 O. shunkusacha 比较段也写 yellow sclera）。
- 名字：Etymology “folia meaning leaf and spectrum meaning image, vision, apparition, or appearance … reddish eyes, long fingers and toes, and cryptic coloration … a ghostly image that inhabits the leaf litter”。
- 背部颗粒/肚子：Diagnosis (6) “dorsum covered by pointed granules homogenous in size”；(5) “belly … orange or brownish orange with brown reticulations or blotches”。W 形肩斑、四肢橙/红褐色来自 Characterization (13)；“distinctly long and slender fingers/toes … webbing absent”来自 (7)(11)。
- 体长：Holotype 为成年雌性 CORBIDI 28468，2022 年 7 月采；Measurements “SVL 32.4”；Variation “three adult males (SVL = 23–26 mm) are smaller than four adult females (SVL = 30–33 mm)”。片中说“选作代表的那只雌蛙”（正模），不说“最大”。一元硬币直径 25 mm 为常识比较。
- 野外：Methods “rapid herpetological inventories … San Martín and Huánuco … from 2018 to 2025 … slow night walks (19:00 to 03:00 h) along streams and within the forest using headlamps … by hand”。（foliaspectrum 段落写的是 “between 19:00 and 12:00 h”，疑似笔误，片中采用 Methods 的 19:00–03:00。）
- 洞：“All specimens collected were captured near holes formed by raised roots and quickly hid in them when they felt threatened.” → 片中“每一只都在树根下的洞旁，一有危险就钻进去”。
- 分布：“only known from the type locality, Canan [Canaan] … at an elevation of 2100 m, San Martín department, northeastern Peru”；正模坐标 6.8926° S, 77.4476° W, 2118 m；Peruvian Yungas。地图定位点即此坐标；海拔计显示“约 2100 米”。
- 生境：“montane forest patches of low canopy (less than 6 m) with slender trees, tree ferns, and Chusquea bamboo … on poor sandy soils in a matrix of cattle ranching pastures … The forest floor showed signs of frequent cattle trampling.” 论文没给种群数量、没做受威胁评估 → 片中只说“四周全是养牛的牧场”+画面牛蹄印，不说“濒危”。
- 4 新种 & 属内种数：Introduction “currently comprises 27 recognized species”；Discussion “increasing the number of species in the genus to 31”。片中“蛙家族”= Oreobates 属（画面标“Oreobates 属”）。四个新种颜色：azulensis 古铜/褐背、浅黄褐肚；chirimoto 浅褐、黄肚；nigrumcompletum 深褐近黑；按各自 Characterization。
- 直接发育：Introduction “Terrarana … direct development, in which embryos develop into miniature versions of adults, bypassing a free-living larval stage”。论文没观察 foliaspectrum 本身的繁殖 → 片中说“这类蛙”，不说“它被观察到”。
- 声囊裂：四种雄蛙都没有 vocal slits；措辞容易说过头，本片未讲。
