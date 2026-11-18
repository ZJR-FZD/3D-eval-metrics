"""
D3_compactness.py — Token Count / Operation Count（程序紧凑度）【客观·可编辑性代理】

【测什么】生成的 CAD/建模程序用了多少 token、多少个建模操作，作为"语义简洁度/可编辑性"的代理。
  更简洁的程序通常更容易被工程师修改和复用。

【根据什么算】Token Count = 分词后的 token 数；Operation Count = 程序里的 CAD 操作调用次数。

【公式】直接计数（越少越简洁）。CADBench 把它当独立一轴报告，不参与"对错"判断。

【出处】CADBench 的 Program Compactness 轴（Token Count + Operation Count）。

【输入/输出】一段代码字符串 → token 数 + 操作调用数。
"""
import re


def count_tokens(code):
    """简单分词近似：标识符/数字/符号各算一个 token"""
    return len(re.findall(r"[A-Za-z_]\w*|\d+\.?\d*|[^\s\w]", code))


def count_operations(code, op_names):
    """统计 CAD 操作函数调用次数"""
    total = 0
    detail = {}
    for op in op_names:
        n = len(re.findall(r"\b" + re.escape(op) + r"\s*\(", code))
        if n:
            detail[op] = n
            total += n
    return total, detail


if __name__ == "__main__":
    concise = """import cadquery as cq
result = cq.Workplane("XY").box(10, 20, 5).edges("|Z").fillet(1)"""
    verbose = """import cadquery as cq
base = cq.Workplane("XY").box(10, 20, 5)
edge_sel = base.edges("|Z")
result = edge_sel.fillet(1)
tmp = result
tmp = tmp.fillet(0.5)
result = tmp"""
    ops = ["box", "fillet", "extrude", "circle", "cut", "union", "chamfer"]
    print("=" * 64)
    print("E3 · Program Compactness（token / 操作数，越少越简洁）")
    print("=" * 64)
    for name, code in [("简洁版", concise), ("冗余版", verbose)]:
        tc = count_tokens(code)
        oc, detail = count_operations(code, ops)
        print(f"  {name}: token≈{tc}  操作数={oc}  明细={detail}")
    print("\n用途：在两个模型几何分接近时，紧凑度反映「谁的代码更好维护」——CADBench 的独立诊断轴。")
