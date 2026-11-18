"""
F4_mos.py — MOS（Mean Opinion Score，平均意见分）【主观·人类感知】

【测什么】最经典的主观评估：让一组人类评审对生成结果按等级(如 1-5)打分，取平均。
  VLM 裁判普及前的黄金标准，现在仍用来校准 VLM 裁判是否"与人类一致"。

【根据什么算】每个样本收集多个人类评分 → 求均值(MOS) + 标准差/置信区间。

【公式】MOS = (1/N) Σ score_i；置信区间 ≈ 1.96·σ/√N（95%）。

【出处】传统感知质量评估通用；MUSE 用它验证 rubric VLM judge "aligns well with human annotations"。

【输入/输出】人类评分列表 → MOS ± 置信区间。
"""
import math


def mos(scores):
    n = len(scores)
    m = sum(scores) / n
    sigma = math.sqrt(sum((s - m) ** 2 for s in scores) / n) if n > 1 else 0.0
    ci = 1.96 * sigma / math.sqrt(n) if n else 0.0
    return m, sigma, ci


if __name__ == "__main__":
    models = {
        "弱模型": [2, 3, 2, 2, 3, 1, 2, 3, 2, 2],
        "通用 LLM": [3, 4, 3, 3, 4, 3, 3, 4, 2, 3],
        "迭代 agent": [4, 5, 4, 4, 5, 4, 4, 5, 4, 4],
    }
    print("=" * 64)
    print("F4 · MOS 平均意见分（1-5，越高越好，±95%CI）")
    print("=" * 64)
    for name, scores in models.items():
        m, sigma, ci = mos(scores)
        print(f"  {name:<12}: MOS={m:.2f} ± {ci:.2f}  (σ={sigma:.2f}, n={len(scores)})")
    print("\nMOS 是校准 VLM 裁判的参照系：MUSE/CodeGen-3D 都论证过「VLM 打分与人类高度一致」。")
