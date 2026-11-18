"""
X3_mmd.py — Minimum Matching Distance（最小匹配距离）【客观·质量】

【测什么】每个真值形状到"最近生成形状"的平均距离，反映生成样本的整体质量。
  与 COV 互补：COV 看覆盖广度，MMD 看最近邻有多近。

【根据什么算】对每个真值，按 CD/EMD 找生成集合中的最近邻，取距离均值。

【公式】MMD = (1/|Ref|) Σ_{X∈Ref} min_{Y∈Gen} D(X,Y)     （越低越好）

【出处】PointFlow、Go with the Flows、PAD（与 COV/JSD/1-NNA 标配四件套）。

【注意】MMD 只取最近的一个，可能被"少数几个高质量样本"拉低而掩盖整体质量，
  所以对高频细节不敏感（Go with the Flows 的观察）。

【输入/输出】生成集合 + 真值集合 → 平均最近邻距离（越低越好）。
"""
from common import sample_sphere, jitter, normalize_pointcloud, chamfer, score_line


def mmd(gen_set, ref_set):
    total = 0.0
    for r in ref_set:
        total += min(chamfer(r, g) for g in gen_set)
    return total / len(ref_set)


if __name__ == "__main__":
    ref_set = [normalize_pointcloud(sample_sphere(200, seed=10 + i)) for i in range(6)]
    scenarios = {
        "高质量生成": [normalize_pointcloud(jitter(s, 0.02, seed=100+i)) for i, s in enumerate(ref_set)],
        "低质量生成（大噪声）": [normalize_pointcloud(jitter(s, 0.15, seed=100+i)) for i, s in enumerate(ref_set)],
    }
    print("=" * 64)
    print("B3 · Minimum Matching Distance（最近邻平均距离，越低越好）")
    print("=" * 64)
    for name, gen in scenarios.items():
        score_line(name, mmd(gen, ref_set), "↓")
    print("\n与 COV 对照：MMD 低说明「最近的那批」质量好，但不保证覆盖全部模式。")
