"""
D1_topology.py — Watertight / Manifold / Self-intersection（拓扑有效性）【客观·拓扑】

【测什么】生成的 3D 网格是不是"几何上合法"：封闭(watertight)、流形(manifold)、无自交。
  具身综述特别指出：CD 很低的网格仍可能有自交/非流形边——所以必须单独查拓扑。

【根据什么算】对三角网格的"边"统计：每条边应恰好被 2 个三角形共享（流形封闭条件）。
  开口边(只被1个面用)=非封闭；被>2个面用=非流形。

【公式】Watertight Rate = 封闭流形网格数 / 总网格数
  open_edges = 出现次数为 1 的边数；nonmanifold_edges = 出现次数>2 的边数。

【出处】具身 3D 综述（WT Ratio）、MUSE 几何有效性检查（watertight/manifold/自交）。

【输入/输出】三角面列表 → 开放边数/非流形边数/是否封闭（演示用 tetra/带洞网格）。
"""
from collections import Counter


def edge_manifold_check(faces):
    """
    faces: list of (a,b,c) 顶点索引三元组
    返回：open_edges（只被1面用）、nonmanifold_edges（被>2面用）、is_watertight
    """
    edge_count = Counter()
    for a, b, c in faces:
        for e in (tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((c, a)))):
            edge_count[e] += 1
    open_edges = [e for e, n in edge_count.items() if n == 1]
    nonmanifold = [e for e, n in edge_count.items() if n > 2]
    return {
        "n_edges": len(edge_count),
        "open_edges": len(open_edges),
        "nonmanifold_edges": len(nonmanifold),
        "is_watertight": len(open_edges) == 0 and len(nonmanifold) == 0,
    }


if __name__ == "__main__":
    # 闭合四面体：4 个面，每条边被 2 个面共享 → watertight
    tetra = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # 带洞：删掉一个面 → 3 条开放边
    tetra_with_hole = [(0, 1, 2), (0, 1, 3), (0, 2, 3)]
    print("=" * 64)
    print("E1 · 拓扑有效性（watertight / manifold，越高越好）")
    print("=" * 64)
    for name, faces in [("闭合四面体", tetra), ("缺一面(有洞)", tetra_with_hole)]:
        r = edge_manifold_check(faces)
        print(f"  {name:<16}: 边数={r['n_edges']} 开放边={r['open_edges']} "
              f"非流形边={r['nonmanifold_edges']} 封闭={r['is_watertight']}")
    print("\n工程提示：真实评估用 bpy / trimesh / OpenCascade，它们还会查自交、法向一致、体积符号。")
