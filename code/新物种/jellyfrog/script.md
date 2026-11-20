# 《这只飞蛙的宝宝，住在果冻里？》台本 / 内部分镜

- 时长 74.5 s（2235 帧 @30fps，ffprobe -count_packets 核对 2235 帧）；大重音只在 0.0 s（飞蛙滑入 + 果冻晃）和 BIG2 = 12.5 s（“一种新的飞蛙！”）。
- 旁白 edge-tts zh-CN-YunjianNeural −5%，每句字幕起点 +0.1 s 开口（hook +0.45 s，避开 0 秒重击；big2 +0.15 s），不加速。
- 画风：照 ghostfrog/howler 的 2D 扁平无描边（深色只用在瞳孔、嘴线、眉线）；新角色在 jchars.py（亮绿身体、淡粉色腿、尖吻、带吸盘的蹼足——按 UC Davis 新闻稿照片描述）。
- BGM：“苏拉威西雨夜甘美兰”（pelog 味 E F G B C，120 BPM，10% swing）：Vibraphone 骨干旋律（balungan）+ Celeste 八分（peking）+ Kalimba 十六分交错（bonang imbal）+ 合成大锣/小锣/kenong 的“锣点结构”、bongo/conga 当 kendang、Fretless 低音，主旋律 Pan Flute / Shakuhachi 当 suling；全程雨声底 + 水滴，湖边蛙群合唱、果冻“啵啵”晃动声、泡泡声。music.py 全读 cues.py。
- 字幕停留检查：cues.check() 无不达标项（每句 ≥ max(1.5 s, 字数/4) 且 ≥ 旁白+0.1 s）。
- 防闪烁：popcheck lint 0 处；滑翔↔坐姿用 0.35 s 叠化替换；成片 luma 检测 10 处，全部落在换场 0.3 s 叠化结束点或 BIG2 白闪内（亮/暗背景换场），无实体闪现。

| # | key | 时间 | 字幕 | 专属场景 |
|---|---|---|---|---|
| 1 | hook | 00.00–04.50 | 树枝上挂着一团果冻， 里面的小东西在扭！ | 特写→近景：夜雨中的水面上方，一团透明果冻挂在树枝上，里面十几只小蝌蚪在扭；0 秒一只亮绿飞蛙张开四个脚蹼从右上角滑翔进画面、落在树枝上（滑翔姿态 0.35 s 叠化成坐姿），果冻被震得大幅晃动 + 光圈；超大字“果冻？”“在扭！” |
| 2 | lake | 04.50–09.50 | 印尼一座高山的小湖边， 趴着成千上万只绿蛙 | 大全：黄昏的高山小湖（远山+雾），湖边 40 只小绿蛙依次蹦出、声囊轮流鼓起，音符往上飘；右上计数框“×0→1000+” |
| 3 | q | 09.50–12.50 | 这团果冻， 到底是谁的？ | 近景：聚光灯下的果冻团，放大镜来回扫、镜中蝌蚪放大；发光大“?”，右下身份卡“妈妈：？？？”滑入；滚奏+riser |
| 4 | big2 | 12.50–17.00 | 一种新的飞蛙！ 它把宝宝养在果冻里 | BIG2 重击+白闪：绿色放射光、彩点爆散，飞蛙跳起（惊→得意脸），大字“新物种！”，红圈印章“2026 命名”，学名牌 Rhacophorus kurniatiae，左侧果冻团冒出爱心 |
| 5 | glide | 17.00–21.50 | 飞蛙的大脚蹼一张开， 就能在树间滑翔 | 全景：月夜两棵树之间，飞蛙从左树枝起跳，俯视滑翔姿态沿虚线弧线滑到右树，四个蹼张开发光+风线；下方卡片“脚蹼 ≈ 降落伞”图示；落地叠化成坐姿 |
| 6 | cheek | 21.50–25.00 | 它小到能趴在 人的脸颊上 | 近景：桃色背景，卡通小朋友正脸（惊讶→微笑），小蛙一跳落到脸颊上，金色虚线圈 + “示意”小牌 |
| 7 | jelly | 25.00–30.00 | 卵产在果冻似的胶团里， 挂在水边的植物上 | 中景：夜里池塘，树枝伸到水面上，蛙妈妈坐在枝上，枝下长出一团果冻胶团（弹簧放大，内有卵），水面倒影；虚线箭头指向下方水面+涟漪；细雨 |
| 8 | grow | 30.00–33.50 | 卵和蝌蚪， 都在胶团里长大 | 显微镜视野（圆形取景框）：胶团里 卵→卷曲胚胎→蝌蚪 在胶里游动；底部三格进度条（卵/胚/蝌蚪图标）随发育点亮 |
| 9 | foam | 33.50–37.00 | 可它的亲戚们， 做的是泡沫巢 | 左右并排：左半青色=新种的透明果冻团（树枝下），右半暖褐=亲戚的白色泡沫巢（叶下，泡泡渐涨），中间金色 VS；下方两只蛙（新种亮绿 vs 亲戚暗绿） |
| 10 | card | 37.00–42.00 | 泡沫巢：用一团泡泡裹住卵， 让卵一直湿湿的 | “一句话学会”知识卡：泡沫巢＝用一团泡泡裹住卵，让卵一直湿湿的 + 泡沫巢图示 + 水滴（此句不出底部字幕） |
| 11 | first | 42.00–48.00 | 在苏拉威西的飞蛙里， 胶团下蛋以前没记录过 | 深蓝底：顶部苏拉威西岛剪影；4 张灰绿色“亲戚”卡依次弹出，卡底是空的虚线“?”胶团槽；随后新种卡大号弹起（亮绿蛙+果冻团），金色“首次”星章 |
| 12 | three | 48.00–54.00 | 长得像亲戚？就量 28 处特征， 再比 DNA 和叫声 | 实验室网格底：两只蛙左右滑入、中间“≈”（长得像，狐疑脸互看）；随后三块面板依次弹出：尺子+计数 0→28、DNA 条码逐条出现、叫声波形+喇叭 |
| 13 | map | 54.00–58.50 | 它只住在苏拉威西岛 一座大山的高山湖边 | 地图：婆罗洲+苏拉威西 K 形岛（标“苏拉威西”）→ 推近东南半岛，红色定位点+脉冲圈，长出三座山，标签“梅孔加山”；右侧海拔计 0→“1800+ 米” |
| 14 | years | 58.50–64.00 | 科学家 2009–2013 年上山调查， 今年才发表论文 | 暖橙山坡：背包科学家上山、帐篷；翻页日历 2009→2010→…→2013，然后快速翻到 2026（绿色），一份 ZOOTAXA 论文落下 + 绿色对勾 |
| 15 | name | 64.00–69.50 | 它的名字，纪念一位已故的 印尼两栖爬行动物学家 | 淡紫底：横线笔记卡写着 Hellen Kurniati + 白色悼念小花；“Kurniati”飞起变小写 kurniati，金色“ae”弹出拼成 kurniatiae，上方出现 Rhacophorus；小蛙在卡前 |
| 16 | end | 69.50–74.50 | 如果你是小蝌蚪， 想住果冻还是泡泡？ | 回扣开头：同一根树枝和果冻团（蝌蚪在扭），飞蛙坐在枝上；两个选择气泡“果冻”（果冻图标）/“泡泡”（泡沫图标）轻轻跳动；文献小字；末 0.6 s 渐黑 |

## 旁白全文
- hook：树枝上挂着一团果冻，里面的小东西在扭！
- lake：印尼一座高山的小湖边，趴着成千上万只绿青蛙。
- q：这团果冻，到底是谁的？
- big2：一种新的飞蛙！它把宝宝养在果冻里。
- glide：飞蛙的大脚蹼一张开，就能在树和树之间滑翔。
- cheek：它小小的，能趴在人的脸颊上。
- jelly：它把卵产在果冻一样的胶团里，挂在水边的植物上。
- grow：卵和蝌蚪，都在胶团里慢慢长大。
- foam：可它的亲戚们，做的却是一团泡沫巢。
- card：这叫泡沫巢：用泡泡裹住卵，让卵一直湿湿的。
- first：科学家说，在苏拉威西的飞蛙里，胶团下蛋以前从没记录过。
- three：它和亲戚长得像，科学家就量了二十八处特征，还比了DNA和叫声。
- map：它只住在苏拉威西岛，一座大山的高山湖边。
- years：科学家二零零九到二零一三年上山调查，今年才发表论文。
- name：它的名字，纪念一位已故的印尼两栖爬行动物学家。
- end：如果你是小蝌蚪，想住果冻，还是泡泡？

## 科学口径与出处
**已核对原文摘要**（Mapress 文章页 https://www.mapress.com/zt/article/view/zootaxa.5900.4.3 ，全文 PDF 需订阅，未读）：
- Trilaksono W, Racho A, Engilis A, Hitch AT, Herlambang AEN (2026) Montane endemism and cryptic diversity in Sulawesi: A new species of flying frog with derived breeding traits. Zootaxa 5900(4):349–370, doi:10.11646/zootaxa.5900.4.3。Mapress 页写 Published 2026-11-11（Vol. 5900 No. 4: 11 Nov. 2026）；DOI 元数据有处写 2026-11-10 → 片中只说“今年才发表论文”。
- 摘要原话：新种“distinguished by morphological, genetic, acoustic, and reproductive characters”；“endemic to a high-elevation lake in the Mekongga Mountains, Southeast Sulawesi”；与 *R. boeadii* “phylogenetically allied … with minimal genetic divergence”；“egg deposition in an irregular gel matrix, lacking both foam structure and oviposition substrate specificity”；“**represents an oviposition strategy previously undocumented among Sulawesi Rhacophorus**”；“may reflect ecological adaptation to ephemeral aquatic habitats”。
  → 片中“在苏拉威西的飞蛙里，胶团下蛋以前没记录过”按论文口径（限定苏拉威西），**没用**新闻稿里通讯作者的口头说法（“It’s the first time we have seen Rhacophorus with gelatinous matrix”“different reproductive strategy from all other Asian flying frogs”），那是作者采访原话、范围更大，不放进片子。
  → “它和亲戚长得很像”来自摘要 cryptic diversity / minimal genetic divergence + 新闻稿 Engilis “looks very similar to other Rhacophorus”。片中没说“基因很不一样”（新闻稿 Engilis 说 genetics distinctive，与摘要“minimal genetic divergence”口径不一致，故不用）。

**只核对了 UC Davis 新闻稿**（https://www.ucdavis.edu/news/new-asian-flying-frog-species-identified-indonesia ，2026-11-17；Sci.News 2026-11-17 转述一致）：
- 2009–2013 年在梅孔加山从近海平面到最高峰做生物调查；
- “At more than 6,100 feet above sea level … thousands of frogs near a small seasonal mountain lake known as Danau Coca-Cola” → 片中旁白只说“高山湖边”，海拔计显示“1800+ 米”（6100 ft ≈ 1859 m，取“超过 1800 米”这一稳妥下限；Discover Wildlife 标题写“2,000m-high lake”，与新闻稿不完全一致，所以不写具体数字）；
- “The bright green frog can fit on a person’s cheek” → 片中“小到能趴在人的脸颊上”，画面标“示意”；论文体长（SVL）未读到，片中不给毫米数；
- 28 项形态特征 + 基因 + 叫声录音（“measured 28 physical characteristics and analyzed genetic information and audio recordings”）；尖吻、叫声不同；
- 卵产在挂在水面上方或水边植物上的果冻状胶团里，“The eggs and tadpoles develop inside the gel”；近缘种做泡沫巢（frothy, protective coverings … to keep them moist）→ 知识卡；
- 飞蛙之名：“large, webbed feet help them glide between trees”（属的特征）→ 片中说“飞蛙的大脚蹼一张开，就能在树间滑翔”，说的是“飞蛙”这类蛙，没说观察到这一种滑翔；
- 名字纪念已故两栖爬行学家 Hellen Kurniati（茂物动物学博物馆长期职员）。片中不画她的肖像，只用笔记卡+白花。
- 新闻稿说“this region … is now under consideration to become a national park”，片中未用；论文是否做了受威胁评估未知，片中不说“濒危”。

## 偏离/取舍
- 中文名“果冻蛙”是按产卵方式起的叫法，不是正式中文名。
- 只讲到“苏拉威西的飞蛙里首次记录”，不说“全世界飞蛙首次”。
- 梅孔加山（Mekongga）出现在地图标签，没进旁白（控制时长）。
