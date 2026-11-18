"""
A1_execution_rate.py — Error Rate / Execution Rate（执行错误率 / 执行成功率）【客观·可执行】

【测什么】生成的 Python(bpy) / CadQuery 脚本能不能在软件里跑通、产出东西。
  对"纯文本→代码→3D"这条链，这是第一道生死线——代码跑不起来，后面所有指标都是 0。

【根据什么算】在 headless Blender / CAD 引擎里执行每份脚本，记录是否抛出
  语法错误(Syntax)、API 误用(API)、运行时崩溃(Runtime)。

【公式】Error Rate E = N_fail / N_total          （越低越好）
        Execution Rate = 1 − E                   （越高越好）
  CodeGen-3D 进一步把失败拆成三类做诊断。

【出处】CodeGen-3D 的三大核心贡献之一；3DCodeBench 的 Executability 同类。

【输入/输出】一批脚本的执行结果(成功/失败+失败类型) → 错误率 + 分类统计。
"""
from collections import Counter


def error_rate(results):
    """results: list of dict(success=bool, err_type=str|None)"""
    n = len(results)
    fails = [r for r in results if not r["success"]]
    return {
        "error_rate": len(fails) / n,
        "execution_rate": 1 - len(fails) / n,
        "n_fail": len(fails),
        "n_total": n,
        "by_type": dict(Counter(r["err_type"] for r in fails)),
    }


if __name__ == "__main__":
    # 模拟 CodeGen-3D 的错误分类：语法/API/运行时
    models = {
        "通用 LLM A": [{"success": i % 5 != 0, "err_type": None if i % 5 == 0 else ["Syntax", "API", "Runtime"][i % 3]} for i in range(100)],
        "领域专用 LLM": [{"success": i % 25 != 0, "err_type": None if i % 25 == 0 else "API"} for i in range(100)],
        "迭代自修正 agent": [{"success": i % 33 != 0, "err_type": None if i % 33 == 0 else "Runtime"} for i in range(100)],
    }
    print("=" * 64)
    print("C1 · Error Rate / Execution Rate（代码可执行性，错误率越低越好）")
    print("=" * 64)
    for name, results in models.items():
        r = error_rate(results)
        print(f"  {name:<20}: 错误率={r['error_rate']:.0%}  执行率={r['execution_rate']:.0%}  失败类型={r['by_type']}")
    print("\n真实口径：CodeGen-3D 中专用/迭代系统 3–4% 失败率，通用 LLM 21–92%——差距巨大。")
