"""
D2_physics.py — Stability Rate / Collision-Free（物理合理性与仿真就绪）【客观·物理】

【测什么】生成的 3D 物体/装配体放到物理仿真里：
  - Stability Rate：受重力后是否保持直立不倒
  - Collision-Free Ratio / Penetration Volume：装配体部件间是否穿插

【根据什么算】需要物理引擎（MuJoCo/Isaac/UE）实际仿真；本演示用"几何代理量"说明算法：
  稳定性 ≈ 质心投影是否落在支撑面内 + 底面是否平整；碰撞 ≈ 包围盒/AABB 是否重叠。

【公式】Stability Rate = 稳定物体数 / 总数
        Collision-Free Ratio = 无部件穿插的装配体数 / 总数（越高越好）

【出处】具身 3D 生成综述（Stab. Rate、CF Ratio、Penet. Vol.）；MUSE 装配检查。

【注意】综述强调"模拟器依赖"：MuJoCo 里稳的在 Isaac 里可能有伪影，多数工作只测一个引擎。

【输入/输出】物体的质心/支撑面/AABB → 稳定性与碰撞判定。
"""
from common import mean


def is_stable(points, ground_z=0.0, tol=0.1):
    """几何代理：最低点贴近地面 + 质心 xy 落在最低点构成的支撑凸包近似内"""
    zmin = min(p[2] for p in points)
    on_ground = abs(zmin - ground_z) < tol
    c = mean(points)
    base_pts = [p for p in points if p[2] < zmin + tol]
    if not base_pts:
        return False
    cx, cy = min(p[0] for p in base_pts), max(p[0] for p in base_pts)
    dx, dy = min(p[1] for p in base_pts), max(p[1] for p in base_pts)
    inside = dx - tol <= c[0] <= cx + tol and dy - tol <= c[1] <= dy + tol
    return on_ground and inside


def aabb_overlap(A, B):
    """两个点云的轴对齐包围盒是否重叠（碰撞代理）"""
    def aabb(P):
        return [(min(p[k] for p in P), max(p[k] for p in P)) for k in range(3)]
    aa, bb = aabb(A), aabb(B)
    return all(aa[k][0] <= bb[k][1] and bb[k][0] <= aa[k][1] for k in range(3))


if __name__ == "__main__":
    print("=" * 64)
    print("E2 · 物理合理性（Stability / Collision-Free，越高越好；几何代理演示）")
    print("=" * 64)
    # 稳定：底座宽、质心低
    stable = [[x, y, 0] for x in (-1, 1) for y in (-1, 1)] + [[0, 0, 0.2]]
    # 不稳：细杆、质心高
    unstable = [[0, 0, 0], [0, 0, 2], [0.05, 0, 1]]
    print(f"  宽底座物体稳定? {is_stable(stable)}   （期望 True）")
    print(f"  细高杆物体稳定? {is_stable(unstable)}  （期望 False）")
    box1 = [[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    box2 = [[x + 0.5, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    box3 = [[x + 5, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    print(f"  部件1 vs 部件2 碰撞? {aabb_overlap(box1, box2)}  （期望 True 重叠）")
    print(f"  部件1 vs 部件3 碰撞? {aabb_overlap(box1, box3)}  （期望 False）")
    print("\n真实评估要在物理引擎里跑：Stability Rate、Penetration Volume、Collision-Free Ratio。")
