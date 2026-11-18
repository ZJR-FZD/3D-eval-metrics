"""
C2_emd.py — Earth Mover's Distance（推土机距离 / 最优传输）【客观·几何保真】

【测什么】两组点云之间的全局最优匹配代价。相比 Chamfer（各自独立找最近邻），
  EMD 强制「一一配对」，约束更强，能捕捉整体结构错位，不易被离群点骗过。

【根据什么算】两组等数量的点 + 一组一一映射 φ；求使总距离最小的那个双射。

【手段】精确 EMD = 解线性分配问题（匈牙利算法 O(n³)）。
  本演示用「求解器风格」的贪心+ stabilized 近似（纯标准库），规模小结果接近精确；
  真实评估请用 geomloss / POT（sinkhorn）或 scipy.optimize.linear_sum_assignment。

【公式】EMD(P,Q) = min_{φ:P→Q 双射}  Σ_{p∈P} ||p − φ(p)||₂   （越低越好）

【出处】CADBench、PAD、Go with the Flows、点云生成通用（CD 的互补指标）。

【输入/输出】两组等大点云 → 一个标量代价（越低越好）。
"""
from common import sample_sphere, jitter, translation, normalize_pointcloud, dist, score_line


def emd_greedy(P, Q):
    """
    贪心最优传输近似：对每个 p，在尚未匹配的 q 中选最近的配对。
    规模小时接近精确解；精确解需匈牙利算法。返回平均匹配代价。
    """
    remaining = list(Q)
    total = 0.0
    for p in P:
        best_i = min(range(len(remaining)), key=lambda i: dist(p, remaining[i]))
        total += dist(p, remaining.pop(best_i))
    return total / len(P)


if __name__ == "__main__":
    gt = normalize_pointcloud(sample_sphere(256, seed=1))
    candidates = {
        "完美复制": gt,
        "轻微噪声 σ=0.02": jitter(gt, 0.02, seed=2),
        "平移错位 +0.3": translation(gt, [0.3, 0, 0]),
    }
    print("=" * 64)
    print("A2 · Earth Mover's Distance（一一配对最优传输，越低越好）")
    print("=" * 64)
    for name, pts in candidates.items():
        pts = normalize_pointcloud(pts)
        score_line(name, emd_greedy(gt, pts), "↓")
    print("\n对比 A1：EMD 强制一一配对，比 CD 更吃「整体结构」，对离群点更鲁棒。")
    print("注意：EMD 要求两组点数相等；实现为近似，精确解用 Hungarian/Sinkhorn。")
