"""
C8_siglip_dino.py — SigLIP-2 / DINOv3 感知保真度【客观·语义（依赖预训练模型）】

【测什么】3DCodeBench 用两个互补的 2D 视觉特征模型比对"生成物的渲染图 vs GT 图"：
  - SigLIP-2：语义对应关系（这东西是不是"椅子"）
  - DINOv3  ：结构形状细节（形状轮廓对不对）
  比单用 CLIP 更细：一个管语义、一个管结构。

【根据什么算】渲染图与 GT 图分别过 SigLIP-2 / DINOv3 → 特征余弦相似度。
  本演示用伪特征模拟（真实需 transformers 加载对应权重）。

【公式】score = cosine( feat_render, feat_gt )    （越高越好）

【出处】3DCodeBench 的 Perceptual Fidelity（感知保真）轴。

【输入/输出】两图特征 → 相似度（越高越好）。
"""
import random
from common import cosine, score_line


def pseudo_feat(seed, shift=0.0):
    rng = random.Random(seed)
    return [rng.uniform(-1, 1) * (1 - shift) for _ in range(96)]


if __name__ == "__main__":
    print("=" * 64)
    print("D2 · SigLIP-2 / DINOv3（语义 + 结构保真，越高越好）")
    print("=" * 64)
    gt_feat = pseudo_feat(0)
    cases = {
        "高保真（语义结构都对）": (pseudo_feat(0, 0.05), pseudo_feat(1, 0.05)),
        "语义对结构错": (pseudo_feat(0, 0.05), pseudo_feat(99, 0.5)),
        "都不对": (pseudo_feat(50, 0.8), pseudo_feat(60, 0.8)),
    }
    for name, (sig_feat, dino_feat) in cases.items():
        sig = cosine(sig_feat, gt_feat)   # SigLIP 语义
        dino = cosine(dino_feat, gt_feat) # DINO 结构
        score_line(name + " [SigLIP]", sig, "↑")
        score_line(name + " [DINOv3]", dino, "↑")
    print("\n双模型分工：SigLIP 抓「是不是对的物体」，DINO 抓「形状细节对不对」，互补。")
