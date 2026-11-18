"""
X5_fid_fpd.py — FID / FPD（Fréchet Inception Distance / Fréchet Pointcloud Distance）【客观·分布质量】

【测什么】两组样本在"特征空间"里拟合出的高斯分布之间的距离，同时衡量质量与多样性。
  图像叫 FID（Inception 特征），点云叫 FPD（DGCNN/PointNet 特征）。

【根据什么算】对真值集合和生成集合各提特征，算均值 μ 和协方差 Σ，比两个高斯的 Fréchet 距离。

【公式】d² = ||μ1−μ2||² + Tr(Σ1 + Σ2 − 2·(Σ1Σ2)^(1/2))    （越低越好，同分布=0）

【本演示的简化】纯标准库难做矩阵平方根，这里用"对角协方差近似"：
  Tr(Σ1+Σ2−2√(Σ1Σ2)) ≈ Σ_i (σ1_i² + σ2_i² − 2σ1_iσ2_i) = Σ_i (σ1_i−σ2_i)²
  教学上完全够说明"分布均值差 + 方差差"两块；精确版请用 numpy/scipy.linalg.sqrtm。

【出处】具身 3D 生成综述（FID 多视图渲染）、点云生成（FPD，DGCNN 特征）。

【输入/输出】两组特征向量集合 → Fréchet 距离（越低越好）。
"""
import math
from common import score_line


def feature_stats(X):
    """算特征集合的逐维均值 μ 与逐维标准差 σ（对角协方差近似）"""
    n, d = len(X), len(X[0])
    mu = [sum(x[k] for x in X) / n for k in range(d)]
    sigma = [math.sqrt(sum((x[k] - mu[k]) ** 2 for x in X) / n) for k in range(d)]
    return mu, sigma


def frechet_distance_diag(X, Y):
    """对角协方差近似的 Fréchet 距离平方"""
    mu1, s1 = feature_stats(X)
    mu2, s2 = feature_stats(Y)
    mean_term = sum((a - b) ** 2 for a, b in zip(mu1, mu2))
    cov_term = sum((a - b) ** 2 for a, b in zip(s1, s2))
    return mean_term + cov_term


if __name__ == "__main__":
    # 演示：把"特征"抽象成 8 维向量（真实场景是 Inception/DGCNN 提的 2048/1024 维）
    def make_feats(seed, mu_shift=0.0, var=1.0):
        import random
        rng = random.Random(seed)
        return [[rng.gauss(k * 0.1 + mu_shift, var) for k in range(8)] for _ in range(64)]

    ref = make_feats(0)
    scenarios = {
        "同分布生成": make_feats(1),
        "均值偏移 +1": make_feats(2, mu_shift=1.0),
        "方差膨胀 ×3": make_feats(3, var=3.0),
    }
    print("=" * 64)
    print("B5 · FID/FPD（Fréchet 特征分布距离，越低越好；对角近似）")
    print("=" * 64)
    for name, gen in scenarios.items():
        score_line(name, frechet_distance_diag(ref, gen), "↓")
    print("\nFID 同时抓「均值偏移」（质量差）和「方差差」（多样性差），这是它比单指标强的地方。")
    print("注意：FID 依赖特征提取网络，跨论文比较必须同一 backbone、同一预处理。")
