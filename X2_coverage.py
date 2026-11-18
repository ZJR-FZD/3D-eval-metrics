"""
X2_coverage.py — Coverage / COV（覆盖率，防模式坍缩）【客观·多样性】

【测什么】真值集合里有多少比例的形状，能被"至少一个生成形状"匹配上。
  COV 低 = 模式坍缩（generator 只会生成少数几种形状）。

【根据什么算】对每个真值形状，按 CD/EMD 找它在生成集合里的最近邻；
  统计"被至少一个真值当成最近邻"的生成形状占比。

【公式】COV = |{ argmin_{Y∈Gen} D(X,Y) : X∈Ref }| / |Ref|
  分子去重后是"被匹配到的生成样本数"。越高越好（理想接近1）。

【出处】PointFlow、Go with the Flows、PAD、场景生成（与 JSD 一起报）。

【输入/输出】生成集合 + 真值集合（每个是点云）+ 距离度量 → COV∈[0,1]（越高越好）。
"""
from common import sample_sphere, sample_cube_surface, jitter, normalize_pointcloud, chamfer, score_line


def coverage(gen_set, ref_set):
    """被匹配到的去重生成样本数 / 真值集合大小"""
    matched = set()
    for r in ref_set:
        best_i = min(range(len(gen_set)), key=lambda i: chamfer(r, gen_set[i]))
        matched.add(best_i)
    return len(matched) / len(ref_set)


if __name__ == "__main__":
    ref_set = [normalize_pointcloud(sample_sphere(200, seed=10 + i)) for i in range(8)]
    scenarios = {
        "多样化生成（8种）": [normalize_pointcloud(jitter(s, 0.02, seed=100+i)) for i, s in enumerate(ref_set)],
        "模式坍缩（8个都一个样）": [normalize_pointcloud(sample_sphere(200, seed=1)) for _ in range(8)],
    }
    print("=" * 64)
    print("B2 · Coverage（真值被生成覆盖的比例，越高越好）")
    print("=" * 64)
    for name, gen in scenarios.items():
        score_line(name, coverage(gen, ref_set), "↑")
    print("\n模式坍缩时 COV 会明显低（多个真值挤到同一个生成样本上）——这就是它存在的意义。")
