"""
F2_elo.py — Elo Rating（人类两两对比偏好排名）【主观·人类偏好】

【测什么】让人类在两个模型的输出间二选一，用 Elo 积分系统维护一个全局排名。
  3DCodeBench 的 3DCodeArena 就是公众投票 → Elo 排名，用来验证自动指标是否符合人的直觉。

【根据什么算】每场比赛：胜者 +K(1−E)，负者 +K(0−E)，其中 E 是期望胜率。

【公式】E_a = 1 / (1 + 10^((R_b − R_a)/400))
        R_a' = R_a + K·(S_a − E_a)     S_a∈{1胜,0.5平,0负}，K 为更新步长。

【出处】3DCodeBench 的 3DCodeArena（Elo 人类偏好平台）。

【输入/输出】初始分 + 一系列对局结果 → 更新后的 Elo 排名。
"""
def expected_score(ra, rb):
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


def update_elo(ra, rb, sa, k=32):
    ea = expected_score(ra, rb)
    return ra + k * (sa - ea), rb + k * ((1 - sa) - (1 - ea))


if __name__ == "__main__":
    players = {"GPT-5.5": 1500.0, "Gemini-3.1": 1500.0, "开源模型X": 1500.0}
    # 模拟一轮 3DCodeArena 投票：强者互有胜负，都碾压开源
    matches = [
        ("GPT-5.5", "Gemini-3.1", 1.0),
        ("GPT-5.5", "Gemini-3.1", 0.0),
        ("GPT-5.5", "开源模型X", 1.0),
        ("Gemini-3.1", "开源模型X", 1.0),
        ("GPT-5.5", "开源模型X", 1.0),
        ("开源模型X", "Gemini-3.1", 0.0),
    ]
    print("=" * 64)
    print("F2 · Elo Rating（人类偏好排名，分越高越好）")
    print("=" * 64)
    for a, b, sa in matches:
        players[a], players[b] = update_elo(players[a], players[b], sa)
    for name, score in sorted(players.items(), key=lambda x: -x[1]):
        print(f"  {name:<14}: {score:.1f}")
    print("\nElo 的价值：把主观的两两偏好聚合成可比较的单一排名，3DCodeArena 用它对齐自动指标。")
