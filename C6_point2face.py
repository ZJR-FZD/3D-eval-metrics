"""
C6_point2face.py — P2F / Point-to-Face RMSE（点到面距离）【客观·几何保真】

【测什么】生成点云到真值三角网格面的距离 RMSE。是 mesh 重建时代最经典的指标之一，
  和 CD 的区别：CD 比"点到点"，P2F 比"点到面"，后者对采样密度差异更鲁棒。

【根据什么算】每个生成点 → 真值 mesh 上最近三角面 → 距离；取 RMSE。
  本演示简化为"点到真值采样点集最近距离的 RMSE"（点到面的高精度投影需三角形最近点算法）。

【公式】P2F = sqrt( (1/|G|) Σ_{g∈G} d(g, Ref_surface)² )     （越低越好）

【出处】早期 mesh 重建（MeshLab / 3D reconstruction survey）、部分 CAD 几何检查。

【输入/输出】生成点云 + 真值表面点/mesh → RMSE（越低越好）。
"""
import math
from common import (sample_sphere, jitter, translation, normalize_pointcloud,
                    nearest_distance, score_line)


def p2f_rmse(gen, ref_surface, use_sqrt=True):
    d2 = [nearest_distance(g, ref_surface) ** 2 for g in gen]
    mse = sum(d2) / len(d2)
    return math.sqrt(mse) if use_sqrt else mse


if __name__ == "__main__":
    ref = normalize_pointcloud(sample_sphere(700, seed=1))
    candidates = {
        "完美复制": ref,
        "轻微噪声 σ=0.02": jitter(ref, 0.02, seed=2),
        "平移错位 +0.3": translation(ref, [0.3, 0, 0]),
    }
    print("=" * 64)
    print("A6 · Point-to-Face RMSE（点到真值表面距离，越低越好）")
    print("=" * 64)
    for name, pts in candidates.items():
        pts = normalize_pointcloud(pts)
        score_line(name, p2f_rmse(pts, ref), "↓")
    print("\n与 A1 CD 对比：CD 是平均距离，P2F 是 RMSE（平方再开根），更惩罚大偏差的离群点。")
    print("工程提示：真实 mesh 上要算点到三角形的最近点投影，本演示用密采样点近似表面。")
