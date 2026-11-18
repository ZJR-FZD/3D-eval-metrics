# 3D 生成任务评估指标 · 代码库（一个指标一个脚本）

纯 Python 标准库实现，无 numpy/PIL/scipy 依赖，任何有 Python 3 的机器可直接跑。
聚焦榜单上**纯文本输入**任务用到的指标，并补齐 Chamfer/EMD/F-score 这类经典几何指标。

## 怎么运行

```bash
cd D:/3D-datasets/_3D生成指标代码
python run_all.py        # 一键跑全部 26 个脚本（按维度顺序，已验证 26/26 通过）
python C1_chamfer.py     # 单独跑某一个
python common.py         # 公共库自检
```

每个脚本开头 docstring 说明：**测什么 / 根据什么算 / 公式 / 出处 / 输入输出**；末尾直接跑一遍给结果。
`run_all.py` 按文档维度顺序运行：① 可执行 → ② 语义 → ③ 跟GT比 → ④ 拓扑物理 → S1/S2 主观 → 附录。

## 分类总览（详细版见 `3D生成指标全景_主观客观分类.md`）

> **先分清「维度」和「手段」**：维度 = 评什么；手段 = 怎么收集判断（Elo / VLM judge / MOS / Rubric）。
> **Elo 是排名手段，不是维度**。
> **脚本代号已与客观维度对齐**：`A`=①可执行 · `B`=②语义(跟文本) · `C`=③跟GT比 · `D`=④拓扑物理；
> `F`=主观手段，`X`=附录(分布多样性，需一批样本，这批榜单不用)。
> 客观维度按**参照物**分：① 可执行(无) → ② 语义(跟文本) → ③ 几何/外观(跟GT) → ④ 拓扑物理(自检)。

### 客观维度（程序可直接算）

| 维度 | 脚本 | 指标 | 核心手段 | 方向 |
|---|---|---|---|---|
| **① 代码可执行** | `A1_execution_rate.py` | Error/Execution Rate | 脚本执行成功占比 | ↓错误 |
| | `A2_valid_shape_rate.py` | Valid Shape Rate | 有效实体占比（两种口径） | ↑ |
| | `A3_pass_at_k.py` | Pass@k | k 次采样至少一次成功 | ↑ |
| **② 语义对齐（跟文本）** | `B1_clip_score.py` | CLIP Score / CLIP-T | 图文余弦（avg/max） | ↑ |
| | `B2_cad_spec_consistency.py` | CAD 规格一致性 | 解析 .FCStd 特征名+尺寸 vs 文本精确匹配 | ↑ |
| **③ 跟GT比·数值几何** | `C1_chamfer.py` | Chamfer Distance | 双向最近邻距离 | ↓ |
| | `C2_emd.py` | Earth Mover's Distance | 一一配对最优传输（贪心近似） | ↓ |
| | `C3_fscore.py` | F-Score@τ | 阈值内 P/R 调和平均 | ↑ |
| | `C4_voxel_iou.py` | Voxel IoU | 体素占据交并比 | ↑ |
| | `C5_surface_iou.py` | Surface IoU | 双向表面覆盖 | ↑ |
| | `C6_point2face.py` | Point-to-Face RMSE | 点到面距离 RMSE | ↓ |
| | `C7_cad_geometry_similarity.py` | CAD 几何相似度 | 实体数/体积/表面积相对误差 vs GT | ↑ |
| **③ 跟GT比·特征相似度** | `C8_siglip_dino.py` | SigLIP-2 / DINOv3 | 渲染图 vs GT 图特征余弦 | ↑ |
| | `C9_uni3d.py` | Uni3D | 生成体 vs 目标体 3D 特征余弦 | ↑ |
| **④ 拓扑/物理/工程可用性** | `D1_topology.py` | Watertight/Manifold | 边流形检查 | ↑ |
| | `D2_physics.py` | Stability/Collision-Free | 物理/几何代理判定 | ↑ |
| | `D3_compactness.py` | Token/Operation Count | 程序紧凑度计数 | ↓简洁 |
| | （未单列） | 可制造DFM/可装配DFA/功能DOF | CAD几何规则+仿真，程序可算 | 合格↑ |
| **附录 分布/多样性** | `X1_jsd.py` | Jensen-Shannon 散度 | 直方图分布 KL 组合 | ↓ |
| | `X2_coverage.py` | Coverage | 真值被生成匹配比例（防坍缩） | ↑ |
| | `X3_mmd.py` | Min Matching Distance | 最近邻平均距离 | ↓ |
| | `X4_1nna.py` | 1-NN Accuracy | 真假 1-NN 分类 | →50% |
| | `X5_fid_fpd.py` | FID / FPD | Fréchet 特征分布距离（对角近似） | ↓ |

> **归类说明**：`C8`/`C9`（SigLIP/DINO、Uni3D）参照物是 **GT 图/目标体，不是 instruction** → 归 ③ 特征相似度；
> 真正跟文本比的是 `B1`（CLIP）和 `B2`（CAD 规格一致性）。代号已按维度重排，见上方映射。
>
> **CAD 特有指标**：`B2` CAD 规格一致性参照物是 instruction → 归 ②（看 .FCStd 特征树+尺寸，结构化精确匹配，与 B1 的模糊余弦是同维度两手段）；
> `C7` CAD 几何相似度参照物是 GT → 归 ③（实体数/体积/表面积相对误差，宏观量纲，与 C1–C6 的微观距离互补）。
> **"设计可用性"拆两半**：可制造/可装配/功能是几何+物理检查（程序可算，属 ④，CAD 里叫 DFM/DFA）；
> 只有"好不好看"的审美是主观，已并入 S2。

### 主观维度 + 采集手段（依赖人 / VLM 判断）

**主观维度（评什么，共 2 个）**：
- **S1 感知语义一致性** = ② 的主观版（参照物同为文本，只换裁判）
- **S2 感知视觉质量** = 真实感 + 审美（原 S1/S3 合并）

**采集手段（怎么判，不单列为维度）**：MOS 绝对打分 · Rubric 结构化打分 · Pairwise/Elo 两两对比 · VLM/Human 裁判来源。
同一手段可服务多个维度，同一维度可换手段测——故下列脚本是**手段的实现**，不是独立维度。
**唯一干净的主客观对子 = ②语义 ↔ S1**（同参照物=文本，只换裁判）；S2 比 ③几何保真宽（含材质/光影/审美），**不是** ③ 的主观版。

| 脚本 | 手段 | 服务的主观维度 | 方向 |
|---|---|---|---|
| `F1_vlm_judge.py` | 成对偏好 win rate（VLM 裁判看渲染图） | S2 为主，兼 S1 | ↑ |
| `F2_elo.py` | Elo 排名（两两投票积分更新） | 综合 S1–S2 偏好 | ↑ |
| `F3_rubric.py` | Rubric 加权打分（0-4 锚点 × 权重） | S2（含审美）为主 | ↑ |
| `F4_mos.py` | MOS 平均意见分（人类打分均值±CI） | S1/S2 通用 | ↑ |

## 三类脚本的真实程度（诚实说明）

1. **端到端真算的**（自带演示数据、算法完整）：A 全部、B 全部、C1/C2/C3、E1/E2/E3。
2. **算法完整但特征是模拟的**（真实需预训练模型）：D1（CLIP）、D2（SigLIP/DINO）、D3（Uni3D）、B5（FID backbone）——余弦/Fréchet 计算是真的，把伪特征换成模型输出即可。
3. **VLM/人类 judgment 用可复现模拟**（真实需 API/人）：F 全部——聚合公式是真的，把模拟分换成真实返回即可。

## 与榜单的对应

| 榜单（纯文本任务） | 用到的指标（本库对应脚本） |
|---|---|
| **CodeGen-3D** | Error Rate(C1) + 6视图 CLIP(D1) + GPT-4o 偏好(F1) |
| **3DCodeBench** | Executability(C1/C2) + SigLIP/DINO(D2, ③特征) + **Chamfer(A1)** + Uni3D(D3, ③特征) + Elo(F2) |
| **MUSE** | 代码执行(C1) + 几何有效性(E1) + rubric VLM(F3) |
| **CADBench / CAD Bench v2** | Volumetric IoU(A4) + CD(A1) + SIoU(A5) + VSR(C2) + Token/Op(E3) |
| **Frontier3DBench / BlenderWorld** | rubric(F3) + VLM judge(F1) + 数值探针(A/E 类) |

## 关键提醒

- **主客观必须组合**：CodeGen-3D/3DCodeBench/MUSE 都发现 CLIP/几何分接近时，VLM/人类偏好仍能拉开差距。
- **按参照物归类**：判据只有一条——比的一端是不是 instruction（②）还是 GT（③）。名字带"语义"的 DINO/Uni3D 因比的是 GT，归 ③。
- **1-NNA 特例**：越接近 50% 越好（真假难分），不是越高越好。
- **对齐预处理**：几何指标前通常要归一化到单位球或 ICP 对齐，否则平移/尺度差会污染结果。
- **模拟 ≠ 真实**：标注了"模拟"的脚本请勿把演示分数当真实模型表现引用。
