"""
A2_valid_shape_rate.py — Valid Shape Rate / VSR（有效实体率）【客观·可执行/几何有效性】

【测什么】生成的 CAD 程序不仅能执行，还要能产出一个"合法的实体/实体几何"。
  比 Error Rate 更严：Error Rate 只管"代码跑没跑通"，VSR 还要管"结果是不是有效 solid"。

【根据什么算】执行 CAD 程序 → 尝试转成 B-Rep/solid → 判断是否有效。
  无效情形：语法错、CAD 操作失败、输出无法转成合法实体。

【公式】VSR = 有效实体数 / 总生成数        （越高越好，理想=1）

【出处】CADBench 的 Executability 轴核心指标（CADFit 0.895 IoU 配 1.000 VSR）。

【两种计分口径】来自 3DCodeBench：
  - conditional：只看跑通了的脚本（剥离 API 错误，测几何能力）
  - penalized  ：跑失败的记 0 分（把可靠性也算进去）

【输入/输出】一批生成结果(是否产出有效 solid) → VSR。
"""
def valid_shape_rate(results, mode="penalized"):
    """results: list of dict(executed=bool, valid_solid=bool, shape_score=float)"""
    if mode == "conditional":
        ok = [r for r in results if r["executed"]]
        if not ok:
            return 0.0
        return sum(r["valid_solid"] for r in ok) / len(ok)
    else:  # penalized：失败整个算无效
        return sum(r["executed"] and r["valid_solid"] for r in results) / len(results)


if __name__ == "__main__":
    # 模拟：100 个 CAD 程序，有的跑不通，有的跑通但不是合法实体
    results = []
    for i in range(100):
        executed = i % 10 != 0           # 10% 执行失败
        valid = executed and i % 7 != 0  # 其中一部分产出非法实体
        results.append({"executed": executed, "valid_solid": bool(valid), "shape_score": 0.8})
    print("=" * 64)
    print("C2 · Valid Shape Rate（有效实体率，越高越好）")
    print("=" * 64)
    print(f"  总样本: {len(results)}")
    print(f"  能执行: {sum(r['executed'] for r in results)}")
    print(f"  有效实体: {sum(r['executed'] and r['valid_solid'] for r in results)}")
    print(f"  VSR (penalized)  : {valid_shape_rate(results, 'penalized'):.2%}  ← 失败记0")
    print(f"  VSR (conditional): {valid_shape_rate(results, 'conditional'):.2%}  ← 只看跑通的")
    print("\n两种口径差距揭示：模型是「不会写 API」（执行失败）还是「几何推理差」（产出非法实体）。")
