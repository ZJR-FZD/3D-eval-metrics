"""
A3_pass_at_k.py — Pass@k（采样 k 次至少成功一次的概率）【客观·可执行】

【测什么】允许模型对同一个 prompt 采样 k 次，至少有一次成功的概率。
  代码生成（HumanEval）沿用过来的指标，衡量"给足机会时的能力上限"。

【根据什么算】n 次独立采样中有 c 次成功，估计从 n 次里取 k 次至少含一个成功的概率。

【公式（无偏估计）】pass@k = 1 − C(n−c, k) / C(n, k)
  当 n=k 时退化为 1−(失败率)^k。越高越好。

【出处】代码生成通用（HumanEval / MBPP）；适用于"多次重试/多候选"的 3D 代码生成设定。

【输入/输出】总采样数 n + 成功数 c + k → pass@k∈[0,1]（越高越好）。
"""
from math import comb


def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


if __name__ == "__main__":
    print("=" * 64)
    print("C3 · Pass@k（采样 k 次至少一次成功，越高越好）")
    print("=" * 64)
    n = 100  # 每个 prompt 采样 100 次
    for name, c in [("弱模型 (c=20)", 20), ("中模型 (c=60)", 60), ("强模型 (c=95)", 95)]:
        vals = "  ".join(f"pass@{k}={pass_at_k(n, c, k):.3f}" for k in (1, 5, 10, 20))
        print(f"  {name:<18}: {vals}")
    print("\n解读：弱模型 pass@1 低但 pass@20 高 → 会做但不稳，靠重试能救回来。")
    print("这正是 3DCodeBench 发现「multi-turn refinement 很有效」的量化体现。")
