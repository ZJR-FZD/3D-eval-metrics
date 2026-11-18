"""
F3_rubric.py — Rubric 打分（逐条锚点评分，VLM 裁判）【主观·设计意图/需求满足】

【测什么】按一份"评分细则(rubric)"逐条打分，每条有锚点(如 0/1/2/3/4 各代表什么)和权重，
  最后加权求和。用来评估"功能/可制造/可装配"或"需求逐条满足"这类无法用单一几何指标判断的东西。

【根据什么算】每条 rubric + 渲染图/代码 → VLM 按锚点给 0-4 分；乘以 importance 权重求和。
  本演示用可复现模拟分数；真实接 VLM 时把 grades 换成模型返回即可。

【公式】score = 100 × Σ(grade_i × weight_i) / (4 × Σweight_i)     归一化到 0-100
  （BlenderWorld 用类似的 rubric=100×Σ(score·w)/Σw，这里除以 4 把 0-4 锚点归一）

【出处】MUSE（功能/可制造/可装配三桶 rubric）、BlenderWorld（2651 条 rubric）、
        Frontier3DBench（judge_spec 逐条 check + vlm_spec 0-4 锚点）。

【输入/输出】rubric 条目(描述+权重) + 各条等级 → 加权分。
"""
def rubric_score(items, grades, max_grade=4):
    """items: list of dict(criterion, weight); grades: 对应 0..max_grade 的列表"""
    total_w = sum(it["weight"] for it in items)
    weighted = sum(g * it["weight"] for g, it in zip(grades, items))
    return 100.0 * weighted / (max_grade * total_w), weighted / total_w


if __name__ == "__main__":
    # 模拟 MUSE 一个"可制造性"rubric
    rubrics = [
        {"criterion": "壁厚≥2mm 可注塑", "weight": 3},
        {"criterion": "无倒扣可脱模", "weight": 2},
        {"criterion": "圆角过渡无应力集中", "weight": 1},
        {"criterion": "装配间隙≤0.2mm", "weight": 2},
    ]
    models = {
        "优秀设计": [4, 4, 3, 4],
        "一般设计": [3, 2, 2, 1],
        "不可用设计": [1, 0, 2, 0],
    }
    print("=" * 64)
    print("F3 · Rubric 加权打分（0-4 锚点 × 权重，越高越好）")
    print("=" * 64)
    for name, grades in models.items():
        score100, avg = rubric_score(rubrics, grades)
        print(f"  {name:<12}: 归一化分={score100:5.1f}  加权原始均分={avg:.2f}/4")
    print("\nRubric 是「把主观判断结构化」的核心手段：MUSE/BlenderWorld/Frontier 都靠它。")
    print("真实接入：把 grades 换成 VLM 按 vlm_spec.json 锚点返回的等级即可。")
