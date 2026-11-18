"""
C9_uni3d.py — Uni3D 3D-to-3D 相似度【客观·语义（依赖 3D 骨干）】

【测什么】直接在"3D 空间"比对生成体和目标体的相似度，而不是先渲染成 2D 再比。
  优点：绕开渲染视角选择的偏差，抓住纯几何/结构的 3D 一致性。

【根据什么算】生成点云/网格与目标点云分别过 Uni3D（3D 自监督骨干）→ 特征余弦相似度。
  本演示用"点云几何统计量"当伪 3D 特征（真实需 Uni3D 权重）。

【公式】score = cosine(Uni3D_feat_gen, Uni3D_feat_gt)    （越高越好）

【出处】3DCodeBench 的 3D Geometric Alignment（与 Chamfer 并列用于几何对齐）。

【输入/输出】两个 3D 体的特征 → 相似度（越高越好）。
"""
import math
from common import (sample_sphere, sample_cube_surface, jitter, normalize_pointcloud,
                    mean, cosine, score_line)


def pseudo_3d_feature(points, n_bins=16):
    """用点云的空间占据直方图当伪 3D 特征（教学替代 Uni3D 嵌入）"""
    pts = normalize_pointcloud(points)
    feat = []
    for axis in range(3):
        hist = [0] * n_bins
        for p in pts:
            v = int((p[axis] + 1) / 2 * (n_bins - 1))
            hist[max(0, min(n_bins - 1, v))] += 1
        feat.extend(hist)
    n = math.sqrt(sum(x * x for x in feat)) or 1
    return [x / n for x in feat]


if __name__ == "__main__":
    gt = sample_sphere(600, seed=1)
    gt_feat = pseudo_3d_feature(gt)
    cases = {
        "同形状（加噪）": jitter(gt, 0.02, seed=2),
        "不同形状（立方体）": sample_cube_surface(600, seed=3),
    }
    print("=" * 64)
    print("D3 · Uni3D 3D-to-3D 相似度（越高越好；伪 3D 特征演示）")
    print("=" * 64)
    for name, gen in cases.items():
        score_line(name, cosine(pseudo_3d_feature(gen), gt_feat), "↑")
    print("\nUni3D vs Chamfer：CD 数点距离，Uni3D 比学到的语义特征——后者更接近「看起来像不像」。")
