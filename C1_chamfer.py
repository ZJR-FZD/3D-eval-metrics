"""
C1_chamfer.py — Chamfer Distance（倒角距离）【客观·几何保真】

【测什么】生成点云与真值点云之间的局部几何偏差，text-to-3D 最基础的指标。

【根据什么算】两组三维点（生成 points vs GT points），逐点找对方最近邻求距离。
  不看颜色、不看材质、不看 .blend 的任何元数据——纯粹比较表面采样点的空间位置。

【手段/预处理】先把两组点云归一化到零质心单位球（或 ICP 对齐），再算双向最近邻。

【公式】
  CD(A,B) = mean_{a∈A} min_{b∈B} ||a-b||₂  +  mean_{b∈B} min_{a∈A} ||b-a||₂
  双向对称；越低越好，完全相同则 =0。

【出处】3DCodeBench（3D Geometric Alignment）、CADBench、CAD-Recode、几乎所有点云生成论文。

【输入/输出】输入两段点云 list[[x,y,z],...]；输出一个标量距离（越低越好）。
"""
from common import (sample_sphere, jitter, translation, normalize_pointcloud,
                    chamfer_unidirectional, chamfer, score_line)

if __name__ == "__main__":
    # 演示构造：真值球 vs 三个候选（自身 / 加噪 / 平移错位）
    gt = normalize_pointcloud(sample_sphere(512, seed=1))
    candidates = {
        "完美复制": gt,
        "轻微噪声 σ=0.02": jitter(gt, 0.02, seed=2),
        "平移错位 +0.3": translation(gt, [0.3, 0, 0]),
    }
    print("=" * 64)
    print("A1 · Chamfer Distance（双向倒角距离，越低越好）")
    print("=" * 64)
    for name, pts in candidates.items():
        pts = normalize_pointcloud(pts)  # 标准预处理：先对齐尺度
        c = chamfer(gt, pts)
        one_way = chamfer_unidirectional(gt, pts)
        score_line(name, c, "↓", f"(GT→候选单向={one_way:.6f})")
    print("\n解读：完美复制=0；噪声越大/错位越远 CD 越大。")
    print("局限：CD 只看最近点，对离群点敏感、不反映拓扑，也不衡量多样性。")
