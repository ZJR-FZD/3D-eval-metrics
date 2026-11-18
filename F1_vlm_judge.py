"""
F1_vlm_judge.py — VLM-as-a-Judge 成对偏好 / Win Rate【主观·感知】

【测什么】把"真值视图 vs 生成视图 + 原始 prompt"交给 VLM（如 GPT-4o），让它二选一，
  判断哪个更符合描述、更好看。捕捉 CLIP 测不出的"人类对齐的感知质量"。

【根据什么算】输入给 VLM 的是**渲染图**（不是 .blend）：
  CodeGen-3D 取"GT 中 CLIP 分数最高的视图" vs "生成中 CLIP 分数最高的视图"，连同 prompt 一起给 GPT-4o。

【公式】VLM 偏好率 = 生成图被选中的 prompt 数 / 总 prompt 数
        或报 win/tie/loss 的成对胜率（pairwise preference）。越高越好。

【出处】CodeGen-3D 三大指标之一（GPT-4o 偏好，迭代 agent 33.3% win rate）；通用 VLM-as-judge。

【本演示】用可复现模拟的裁判选择代替真实 API；把 mock 换成 VLM 返回值即可跑真实分。

【输入/输出】一批 (prompt, 生成图分, 真值图分) → 偏好率 + win/tie/loss。
"""
def vlm_pairwise_preference(comparisons):
    """
    comparisons: list of dict(prompt, gen_score, gt_score)
    实际 gen_score/gt_score 来自 VLM 对图的判断，这里用数值模拟裁判倾向。
    """
    win = tie = loss = 0
    for c in comparisons:
        if c["gen_score"] > c["gt_score"]:
            win += 1
        elif c["gen_score"] < c["gt_score"]:
            loss += 1
        else:
            tie += 1
    n = len(comparisons)
    return {
        "win": win, "tie": tie, "loss": loss,
        "win_rate": win / n,
        "preference_rate": (win + 0.5 * tie) / n,
    }


if __name__ == "__main__":
    # 模拟：三个模型各 100 个 prompt 的 VLM 裁判打分（0-4 锚点）
    import random
    def make(seed, bias):
        rng = random.Random(seed)
        return [{"prompt": f"p{i}", "gen_score": rng.uniform(0, 4) + bias,
                 "gt_score": rng.uniform(0, 4)} for i in range(100)]
    models = {
        "弱模型": make(1, -0.6),
        "通用 LLM": make(2, 0.0),
        "迭代 agent": make(3, 0.5),
    }
    print("=" * 64)
    print("F1 · VLM-as-a-Judge 成对偏好 / Win Rate（越高越好）")
    print("=" * 64)
    for name, comps in models.items():
        r = vlm_pairwise_preference(comps)
        print(f"  {name:<12}: win={r['win']:>3} tie={r['tie']:>3} loss={r['loss']:>3}  "
              f"胜率={r['win_rate']:.1%}  偏好率={r['preference_rate']:.1%}")
    print("\n关键发现(CodeGen-3D)：CLIP 分数接近时，VLM 偏好率仍能清晰区分模型——主观指标是决胜局。")
    print("真实接入：把 gen_score/gt_score 换成 GPT-4o 对渲染图的 0-4 打分或二选一标签。")
