"""
X4_1nna.py — 1-Nearest Neighbor Accuracy（1 近邻分类准确率）【客观·质量/分布拟合】

【测什么】把"真值样本"和"生成样本"混在一起，用留一法 1-NN 分类器判断每个样本属于哪一类。
  如果生成分布骗不过分类器（准确率很高）→ 说明真假可分、生成质量差；
  如果准确率≈50% → 真假难分、生成分布完美拟合真值（理想）。

【根据什么算】所有样本两两距离（这里用 CD），对每个样本找最近邻，看邻居标签是否同类。

【公式】1-NNA = 正确分类数 / 总样本数
  理想值 = 50%（不是越高越好！这是它和所有其他指标最大的不同）。
  论文里常报 |1-NNA − 50%|，越接近 0 越好。

【出处】PointFlow、Go with the Flows、PAD；Yang et al. 专门提出它来纠正
  JSD/COV/MMD"给模式坍缩打高分"的缺陷。

【输入/输出】真值集合 + 生成集合 → 准确率∈[0,1]（越接近 0.5 越好）。
"""
from common import sample_sphere, jitter, normalize_pointcloud, chamfer, score_line


def one_nn_accuracy(gen_set, ref_set):
    """留一法 1-NN：标签 0=ref, 1=gen，返回分类准确率"""
    samples = [(s, 0) for s in ref_set] + [(s, 1) for s in gen_set]
    correct = 0
    for i, (pts_i, label_i) in enumerate(samples):
        # 找最近邻（排除自己）
        best_j, best_d = -1, float("inf")
        for j, (pts_j, _) in enumerate(samples):
            if i == j:
                continue
            d = chamfer(pts_i, pts_j)
            if d < best_d:
                best_d, best_j = d, j
        if samples[best_j][1] == label_i:
            correct += 1
    return correct / len(samples)


if __name__ == "__main__":
    ref_set = [normalize_pointcloud(sample_sphere(200, seed=10 + i)) for i in range(8)]
    scenarios = {
        "完美拟合（真值复制）": [normalize_pointcloud(jitter(s, 0.005, seed=100+i)) for i, s in enumerate(ref_set)],
        "明显偏差（大噪声）": [normalize_pointcloud(jitter(s, 0.20, seed=100+i)) for i, s in enumerate(ref_set)],
        "模式坍缩（全生成一个样）": [normalize_pointcloud(sample_sphere(200, seed=1)) for _ in range(8)],
    }
    print("=" * 64)
    print("B4 · 1-NNA（真假 1-NN 分类准确率，理想≈50%）")
    print("=" * 64)
    for name, gen in scenarios.items():
        acc = one_nn_accuracy(gen, ref_set)
        score_line(name, acc, "→50%", f"(距理想值 {abs(acc-0.5):.3f})")
    print("\n这是唯一「越接近 50% 越好」的指标：分类器分不出真假 = 生成分布最像真值。")
