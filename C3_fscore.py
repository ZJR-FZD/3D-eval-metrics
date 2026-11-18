"""
C3_fscore.py — F-Score@τ（阈值化精确率/召回率调和平均）【客观·几何保真】

【测什么】在给定距离阈值 τ 下，生成点云有多少比例"贴合"真值表面（precision），
  真值有多少比例被生成覆盖（recall），再取调和平均。比 CD 更抗离群点。

【根据什么算】点到对方点云的最近距离是否 < τ。常用 τ=0.01（归一化单位球）。

【公式】
  Precision = |{g∈Gen : min_{r∈Ref}||g-r|| < τ}| / |Gen|
  Recall    = |{r∈Ref : min_{g∈Gen}||r-g|| < τ}| / |Ref|
  F1        = 2·P·R / (P+R)          （越高越好，理想=1）

【出处】SAM3D benchmark 的 F-score@0.01、具身 3D 生成综述、sketch-to-3D 综述
  （被列为"对离群点不敏感"的稳健指标）。

【输入/输出】两组点云 + 阈值 τ → F1∈[0,1]（越高越好）。
"""
from common import (sample_sphere, jitter, translation, normalize_pointcloud,
                    nearest_distance, score_line)


def precision_recall(gen, ref, tau):
    p = sum(nearest_distance(g, ref) < tau for g in gen) / len(gen)
    r = sum(nearest_distance(x, gen) < tau for x in ref) / len(ref)
    return p, r


def f_score(gen, ref, tau=0.01):
    p, r = precision_recall(gen, ref, tau)
    return 2 * p * r / (p + r) if (p + r) else 0.0


if __name__ == "__main__":
    tau = 0.05  # 演示放宽阈值，否则 512 点采样太稀
    ref = normalize_pointcloud(sample_sphere(512, seed=1))
    candidates = {
        "完美复制": ref,
        "轻微噪声 σ=0.02": jitter(ref, 0.02, seed=2),
        "平移错位 +0.3": translation(ref, [0.3, 0, 0]),
    }
    print("=" * 64)
    print(f"A3 · F-Score@τ（τ={tau}，阈值内 P/R 调和平均，越高越好）")
    print("=" * 64)
    for name, pts in candidates.items():
        pts = normalize_pointcloud(pts)
        p, r = precision_recall(pts, ref, tau)
        f = 2 * p * r / (p + r) if (p + r) else 0.0
        score_line(name, f, "↑", f"(P={p:.3f}, R={r:.3f})")
    print("\n对比 A1/A2：F-Score 是「阈值内比例」，离群点不会无限拉低分数，更稳健。")
