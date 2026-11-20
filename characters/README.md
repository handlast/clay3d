# characters
- `macaque_poses.py`：`monkey2()` Q 版阿萨姆猕猴（转头、歪头、挤压、工牌，表情 happy/angry/wow/look/worry）、`POSE` 手臂姿势、`to_local()`、`armlerp()`
- 原始简版 `monkey()` 在 `engine/clay_proto.py`
- `clownfish.py`：`clownfish()` Q 版小丑鱼（大头圆身、三道白环、白眼球+黑瞳+高光，表情 look/happy/wow/angry/worry/fierce，tail/flap/pitch/squash，helmet 安全帽，body/fin/bands 可换成别的鱼如雀鲷）。返回 face/face_r 供脸部超采样
- `bumblebee.py`：`bumblebee()` Q 版熊蜂（东方熊蜂 Bombus impatiens；role=male 黄脸长触角+工牌 / queen 金冠 / worker；表情 look/happy/wow/worry/proud/sleepy/shy/angry；lie 孵卵趴姿、wing 扇翅、arms 抬手、lod 远景小蜂）。返回 face/face_r/thorax/abdomen/badge/hand_l/hand_r（动物打工人 No.04）
