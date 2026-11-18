"""
C7_cad_geometry_similarity.py — CAD 几何相似度（实体数 / 体积 / 表面积相对误差）

【归哪个维度】③ 跟 GT 比（几何与外观保真）—— 参照物是隐藏的 Ground Truth。
  注意：这里比的是 CAD 实体的「宏观标量属性」（几个实体、多大体积、多大表面积），
  与 C1-C6 的「逐点/逐面微观距离」互补：C1-C6 量形状细节，本脚本量整体量纲。
  两者都是跟 GT 比，只是粒度不同——所以同归 ③。

【根据什么算】从两个 CAD 模型（生成 vs GT）的 B-rep 读三组标量：
  - 实体数量 N（solid 个数）
  - 体积 V
  - 表面积 A
  真实读法（三种内核）：
    FreeCAD:  solids = shape.Solids; N=len(solids); V=shape.Volume; A=shape.Area
    OpenCascade: BRepGProp.VolumeProperties_s / SurfaceProperties_s; TopExp_Explorer 数 Solid
    trimesh (网格近似): mesh.volume / mesh.area / len(mesh.split())

【公式】每组属性相对误差 e = |x_gen - x_gt| / x_gt
  相似度 = 1 - mean(e_N, e_V, e_A)，越接近 1 越像；三项误差分别报告。

【输入】gen / gt 各自的 (N, V, A)；【输出】三项相对误差 + 综合相似度
"""
from common import score_line


def rel_error(x_gen, x_gt):
    """单个属性的相对误差；GT 为 0 时用绝对差兜底"""
    if x_gt == 0:
        return abs(x_gen - x_gt)
    return abs(x_gen - x_gt) / x_gt


def cad_geometry_similarity(gen, gt):
    """
    gen, gt: dict，键为 'solids' / 'volume' / 'area'
    返回 (e_solids, e_volume, e_area, similarity)
    """
    keys = ("solids", "volume", "area")
    errs = {k: rel_error(gen[k], gt[k]) for k in keys}
    sim = 1.0 - sum(errs.values()) / len(keys)
    return errs["solids"], errs["volume"], errs["area"], sim


def demo():
    # 隐藏的 GT：一个 3 实体装配体
    gt = {"solids": 3, "volume": 125000.0, "area": 15000.0}  # mm^3 / mm^2

    # 案例 1：生成得很接近（体积/面积各偏 1%，实体数一致）
    good = {"solids": 3, "volume": 126250.0, "area": 15150.0}
    # 案例 2：生成得不对（少一个实体，体积偏 20%，面积偏 15%）
    bad = {"solids": 2, "volume": 150000.0, "area": 17250.0}

    print("=" * 62)
    print("案例 1：接近 GT 的生成结果")
    en, ev, ea, sim = cad_geometry_similarity(good, gt)
    score_line("实体数相对误差", en, "↓")
    score_line("体积相对误差", ev, "↓")
    score_line("表面积相对误差", ea, "↓")
    score_line("几何相似度 = 1-平均误差", sim, "↑")

    print("=" * 62)
    print("案例 2：明显偏离 GT 的生成结果")
    en, ev, ea, sim = cad_geometry_similarity(bad, gt)
    score_line("实体数相对误差", en, "↓")
    score_line("体积相对误差", ev, "↓")
    score_line("表面积相对误差", ea, "↓")
    score_line("几何相似度 = 1-平均误差", sim, "↑")
    print("=" * 62)
    print("说明：三项误差是宏观量纲，量形状细节请用 C1-C6；两者同归 ③ 跟GT比。")


if __name__ == "__main__":
    demo()
