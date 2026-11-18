"""
run_all.py — 一键运行所有指标脚本（按「维度顺序」运行）

顺序 = 文档 3D生成指标全景_主观客观分类.md 的框架：
    ① 代码可执行 → ② 语义对齐(跟文本，含 CAD 规格一致性)
    → ③ 跟GT比(数值几何含 CAD 几何相似度 + 特征相似度)
    → ④ 拓扑/物理/工程可用性 → S1/S2 主观 → 附录 分布多样性

脚本代号已与客观维度对齐：A=①可执行 · B=②语义 · C=③跟GT比 · D=④拓扑物理；
F=主观手段，X=附录(分布多样性)。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# 按维度顺序显式列出（每个二元组 = (脚本文件名, 所属维度)）
ORDERED = [
    # ① 代码可执行（第 0 关）
    ("A1_execution_rate.py",      "① 可执行"),
    ("A2_valid_shape_rate.py",    "① 可执行"),
    ("A3_pass_at_k.py",           "① 可执行"),
    # ② 语义对齐（跟 instruction 比）
    ("B1_clip_score.py",          "② 语义(跟文本)"),
    ("B2_cad_spec_consistency.py","② 语义(跟文本)"),
    # ③ 跟 GT 比 —— 数值几何距离
    ("C1_chamfer.py",             "③ 几何(数值)"),
    ("C2_emd.py",                 "③ 几何(数值)"),
    ("C3_fscore.py",              "③ 几何(数值)"),
    ("C4_voxel_iou.py",           "③ 几何(数值)"),
    ("C5_surface_iou.py",         "③ 几何(数值)"),
    ("C6_point2face.py",          "③ 几何(数值)"),
    ("C7_cad_geometry_similarity.py", "③ 几何(数值)"),
    # ③ 跟 GT 比 —— 特征相似度（本次从 ② 移入）
    ("C8_siglip_dino.py",         "③ 跟GT(特征)"),
    ("C9_uni3d.py",               "③ 跟GT(特征)"),
    # ④ 拓扑 / 物理 / 工程可用性
    ("D1_topology.py",            "④ 拓扑物理"),
    ("D2_physics.py",             "④ 拓扑物理"),
    ("D3_compactness.py",         "④ 拓扑物理"),
    # S1/S2 主观（手段的实现）
    ("F1_vlm_judge.py",           "S1/S2 主观"),
    ("F2_elo.py",                 "S1/S2 主观"),
    ("F3_rubric.py",              "S1/S2 主观"),
    ("F4_mos.py",                 "S1/S2 主观"),
    # 附录 分布 / 多样性
    ("X1_jsd.py",                 "附录 分布"),
    ("X2_coverage.py",            "附录 分布"),
    ("X3_mmd.py",                 "附录 分布"),
    ("X4_1nna.py",                "附录 分布"),
    ("X5_fid_fpd.py",             "附录 分布"),
]

def main():
    ok, fail = [], []
    for name, dim in ORDERED:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print(f"[缺失] {name}（{dim}）")
            fail.append(name)
            continue
        print(f"\n{'=' * 70}\n>>> [{dim}] 运行 {name}\n{'=' * 70}")
        r = subprocess.run([sys.executable, path], cwd=HERE,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0:
            print(r.stdout)
            ok.append(name)
        else:
            print("STDOUT:\n", r.stdout)
            print("STDERR:\n", r.stderr)
            fail.append(name)
    print(f"\n{'=' * 70}\n汇总: 成功 {len(ok)} / 失败 {len(fail)}")
    if fail:
        print("失败脚本:", ", ".join(fail))
    print("成功脚本:", ", ".join(ok))
    return 0 if not fail else 1

if __name__ == "__main__":
    sys.exit(main())
