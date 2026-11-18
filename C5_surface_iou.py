"""
C5_surface_iou.py — Surface IoU / SIoU（表面交并比）【客观·几何保真】

【测什么】阈值化的双向表面覆盖率。与体素 IoU 不同，它直接在表面点层面判断
  "生成表面点是否落在真值表面 τ 邻域内"，对薄壁/细节更敏感。

【根据什么算】双向：Gen→Ref 覆盖率 与 Ref→Gen 覆盖率，取平均。
  CADBench 里 τ 取"目标包围盒对角线的 1%"。

【公式】
  cov(Gen→Ref) = |{g∈Gen : min_r ||g−r|| < τ}| / |Gen|
  cov(Ref→Gen) = |{r∈Ref : min_g ||r−g|| < τ}| / |Gen|
  SIoU = mean(两个方向的覆盖率)     （越高越好）

【出处】CADBench（Surface IoU，与 IoU 相关仅 ρ=0.45，与 CD 相关 −0.85，互补性强）。

【输入/输出】两组表面点云 + 阈值 τ → SIoU∈[0,1]（越高越好）。
"""
from common import (sample_sphere, jitter, translation, normalize_pointcloud,
                    nearest_distance, score_line)


def surface_iou(gen, ref, tau):
    cov_gr = sum(nearest_distance(g, ref) < tau for g in gen) / len(gen)
    cov_rg = sum(nearest_distance(r, gen) < tau for r in ref) / len(ref)
    return (cov_gr + cov_rg) / 2, cov_gr, cov_rg


if __name__ == "__main__":
    tau = 0.05
    ref = normalize_pointcloud(sample_sphere(600, seed=1))
    candidates = {
        "完美复制": ref,
        "轻微噪声 σ=0.02": jitter(ref, 0.02, seed=2),
        "平移错位 +0.3": translation(ref, [0.3, 0, 0]),
    }
    print("=" * 64)
    print(f"A5 · Surface IoU（双向表面覆盖，τ={tau}，越高越好）")
    print("=" * 64)
    for name, pts in candidates.items():
        pts = normalize_pointcloud(pts)
        s, gr, rg = surface_iou(pts, ref, tau)
        score_line(name, s, "↑", f"(Gen→Ref={gr:.3f}, Ref→Gen={rg:.3f})")
    print("\n对比 C4：SIoU 直接量表面点覆盖，比体素 IoU 更能反映细节缺失。")
    print("SIoU 高但 IoU 低 → 可能是薄壁结构（CADBench 观察到的典型分歧）。")
