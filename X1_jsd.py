"""
X1_jsd.py — Jensen-Shannon Divergence（JS 散度）【客观·多样性】

【测什么】一批生成形状 vs 一批真值形状的"边缘点分布"差异，反映生成多样性/模式覆盖。
  做法：把所有生成点云合并成一个大点集 → 体素直方图 → 归一化成概率分布；真值同理。

【根据什么算】两组归一化 3D 直方图（occupancy probability）之间的 JS 散度。

【公式】JSD(P,Q) = ½·KL(P‖M) + ½·KL(Q‖M),  M=(P+Q)/2
  对称、有界 [0,1]（以 2 为底），完全同分布=0（越低越好）。

【出处】PointFlow、Go with the Flows、PAD、场景生成（NeurIPS 2022 等）。

【注意】Yang et al. 指出：JSD/COV/MMD 可能给"只输出平均形状"的模型打高分，
  因为它贴近 M；所以后来引入 1-NNA（见 B4）来纠正。

【输入/输出】两组"点云集合"→ 直方图 → JSD∈[0,1]（越低越好）。
"""
from common import sample_sphere, sample_cube_surface, jitter, voxelize, jsd, score_line


def pointsets_to_hist(pointsets, res=16, bounds=(-1.0, 1.0)):
    """把一组点云合并 → 占据计数直方图 → 归一化为概率分布"""
    size = res ** 3
    counts = [0] * size
    for pts in pointsets:
        for cell in voxelize(pts, res, bounds):
            i, j, k = cell
            counts[(i * res + j) * res + k] += 1
    total = sum(counts) or 1
    return [c / total for c in counts]


if __name__ == "__main__":
    # 真值集合：多个球面（不同位置）；三种生成集合
    ref_sets = [sample_sphere(300, seed=10 + i) for i in range(8)]
    scenarios = {
        "同分布生成（真值加噪）": [jitter(s, 0.02, seed=100 + i) for i, s in enumerate(ref_sets)],
        "模式坍缩（8 个都生成同一个球）": [sample_sphere(300, seed=1) for _ in range(8)],
        "错误分布（全生成立方体）": [sample_cube_surface(300, seed=200 + i) for i in range(8)],
    }
    print("=" * 64)
    print("B1 · Jensen-Shannon Divergence（边缘点分布差异，越低越好）")
    print("=" * 64)
    p_ref = pointsets_to_hist(ref_sets)
    for name, gen in scenarios.items():
        p_gen = pointsets_to_hist(gen)
        score_line(name, jsd(p_ref, p_gen), "↓")
    print("\n注意 JSD 的坑：模式坍缩（全生成一样的球）JSD 反而可能低——这正是 1-NNA 要解决的问题。")
