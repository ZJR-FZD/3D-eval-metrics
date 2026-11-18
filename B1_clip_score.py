"""
B1_clip_score.py — CLIP Score（图文语义对齐）【客观·语义（依赖 CLIP 模型）】

【测什么】渲染图与输入文本 prompt 在 CLIP 嵌入空间里的余弦相似度，衡量"生成的东西像不像 prompt 说的"。

【根据什么算】把 6 个视角的渲染图 + prompt 分别过 CLIP 编码器，算余弦相似度。
  本演示用确定性伪特征向量模拟 CLIP 输出（真实需 open_clip / transformers）。

【公式（CodeGen-3D 原文）】
  S_CLIP_avg = (1/6) Σ_{i=1..6} CLIP(I_i, P)     整体一致性
  S_CLIP_max = max_{i=1..6} CLIP(I_i, P)         防止关键特征只在一个视角出现被过度惩罚
  通常再乘 100 缩放。越高越好。

【CLIP 家族】CLIP-T（文→形）、CLIP-I（图→形）、CLIP-S（条件一致），都是余弦相似度。

【出处】CodeGen-3D 三大指标之一；sketch-to-3D 综述列为语义对齐主指标。

【输入/输出】图像特征 + 文本特征 → avg/max 相似度（越高越好）。
"""
import math
from common import cosine, score_line


def clip_score_avg(views_feat, text_feat):
    return sum(cosine(v, text_feat) for v in views_feat) / len(views_feat)


def clip_score_max(views_feat, text_feat):
    return max(cosine(v, text_feat) for v in views_feat)


def pseudo_feature(seed, base=None, shift=0.0):
    """确定性伪特征向量（模拟 CLIP 嵌入）；base 加偏移=模拟"更像/不像 prompt" """
    import random
    rng = random.Random(seed)
    f = [rng.uniform(-1, 1) for _ in range(64)]
    if base is not None:
        f = [b + shift + 0.1 * rng.gauss(0, 1) for b in base]
    return f


if __name__ == "__main__":
    text_feat = pseudo_feature(0)  # prompt "一个红色的椅子" 的 CLIP 文本特征
    scenarios = {
        "高对齐（6视图都像）": [pseudo_feature(10+i, text_feat, shift=0.0) for i in range(6)],
        "单视角命中（1个视图像）": [pseudo_feature(20+i, text_feat, shift=-0.8 if i else 0.0) for i in range(6)],
        "低对齐（都不像）": [pseudo_feature(30+i) for i in range(6)],
    }
    print("=" * 64)
    print("D1 · CLIP Score（图文余弦相似度，avg/max，越高越好）")
    print("=" * 64)
    for name, views in scenarios.items():
        avg, mx = clip_score_avg(views, text_feat), clip_score_max(views, text_feat)
        score_line(name + " [avg]", avg, "↑")
        score_line(name + " [max]", mx, "↑")
    print("\nCodeGen-3D 发现：CLIP 分数常「挤在一起」分不出模型好坏 → 才需要 VLM 裁判(见 F1)补位。")
