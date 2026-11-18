"""
C4_voxel_iou.py — Voxel IoU（体素交并比）【客观·几何保真】

【测什么】生成体与真值体在粗粒度体素栅格上的体积重叠度。全局、粗糙，但对细节不敏感。

【根据什么算】把两组点云分别离散到 res³ 占据栅格（常用 32³ 或 64³），数交集/并集体素数。

【公式】IoU = |A∩B| / |A∪B|        （越高越好，完全相同=1）

【出处】CADBench（Volumetric IoU）、SAM3D benchmark（64³ 网格）、ModelNet/ShapeNet 重建通用。

【输入/输出】两组点云 + 分辨率 → IoU∈[0,1]（越高越好）。
"""
from common import (sample_sphere, sample_cube_surface, jitter, translation,
                    normalize_pointcloud, voxel_iou, score_line)

if __name__ == "__main__":
    print("=" * 64)
    print("C4 · Voxel IoU（体素占据交并比，越高越好）")
    print("=" * 64)
    pairs = [
        ("球体 vs 自身", sample_sphere(800, seed=1), sample_sphere(800, seed=1)),
        ("球体 vs 加噪", sample_sphere(800, seed=1), jitter(sample_sphere(800, seed=1), 0.03, seed=2)),
        ("球体 vs 立方体（形状不同）", sample_sphere(800, seed=1), sample_cube_surface(800, seed=3)),
    ]
    for name, a, b in pairs:
        a = normalize_pointcloud(a)
        b = normalize_pointcloud(b)
        for res in (16, 32):
            score_line(f"{name} [res={res}]", voxel_iou(a, b, res), "↑")
    print("\n注意：res 越大越精细但也越稀疏；球体 vs 立方体 IoU 明显低，说明 IoU 抓的是粗体积。")
    print("局限：漏掉薄壁/小结构——所以 CADBench 还要配 SIoU 和 CD。")
