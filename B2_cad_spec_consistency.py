"""
B2_cad_spec_consistency.py — CAD 规格一致性（.FCStd 特征名 + 尺寸 vs instruction）

【归哪个维度】② 语义对齐 —— 参照物是 instruction 文本（不是 GT！）。
  对照 D1 的 CLIP：D1 是渲染图 vs 文本算模糊余弦；本脚本是 .FCStd 特征树 vs 文本
  做结构化精确匹配。两者参照物同为文本 → 同归 ②，只是「手段」不同（模糊 vs 精确）。
  这正是「维度相同、手段可换」的例证。

【根据什么算】解析 .FCStd 文件（本质是 zip，核心是里面的 Document.xml）：
  - 特征名：Document.xml 里 <Object name="Pad" type="PartDesign::Pad"/> 的 name/type
  - 尺寸值：ObjectData 里各特征的属性（Length/Width/Depth/Radius...）
  真实 FreeCAD 里这些就是特征树和参数面板里的内容。

【公式】分两部分再加权：
  - 特征名 F1 = 2·P·R/(P+R)，P/R 按 instruction 点与 .FCStd 实际特征名集合算
  - 尺寸命中率 = |{维度在容差内}| / |instruction 要求的尺寸数|
  - 综合一致性 = w1·特征名F1 + w2·尺寸命中率（默认 0.5/0.5）

【输入】instruction 规格 dict + .FCStd 文件路径；【输出】特征名 F1、尺寸命中率、综合
"""
import io
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET


def make_fake_fcstd(path, features, dims):
    """
    造一个最小的 .FCStd（zip + Document.xml）用于演示。
    features: [(name, type), ...]；dims: {(feat, prop): value, ...}
    """
    # 特征树
    obj_lines = "".join(
        f'    <Object name="{n}" type="{t}"/>\n' for n, t in features
    )
    # 特征参数（ObjectData）
    data_lines = ""
    for (feat, prop), val in dims.items():
        data_lines += (
            f'    <Object name="{feat}">\n'
            f'      <Property name="{prop}" type="App::PropertyLength" value="{val}"/>\n'
            f'    </Object>\n'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Document>\n'
        '<Objects>\n' + obj_lines + '</Objects>\n'
        '<ObjectData>\n' + data_lines + '</ObjectData>\n'
        '</Document>\n'
    )
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Document.xml", xml)
        z.writestr("GuiDocument.xml", "<Document/>")  # FCStd 惯例附带


def parse_fcstd(path):
    """从 .FCStd 解析出 (特征名集合, 尺寸字典)，这就是本指标真正看的文件内容"""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("Document.xml"))
    names = set()
    for obj in root.findall("./Objects/Object"):
        names.add(obj.get("name"))
    dims = {}
    for obj in root.findall("./ObjectData/Object"):
        feat = obj.get("name")
        for prop in obj.findall("Property"):
            dims[(feat, prop.get("name"))] = float(prop.get("value"))
    return names, dims


def feature_f1(req_names, got_names):
    """特征名精确匹配的 P / R / F1"""
    hit = len(req_names & got_names)
    p = hit / len(got_names) if got_names else 0.0
    r = hit / len(req_names) if req_names else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f1, hit


def dim_hit_rate(req_dims, got_dims, tol=0.01):
    """尺寸在相对容差 tol 内算命中"""
    if not req_dims:
        return 1.0, 0
    hit = sum(
        1 for k, v in req_dims.items()
        if k in got_dims and abs(got_dims[k] - v) / max(abs(v), 1e-9) <= tol
    )
    return hit / len(req_dims), hit


def spec_consistency(instruction_spec, fcstd_path, w_feat=0.5, w_dim=0.5, tol=0.01):
    req_names = set(instruction_spec["features"])
    req_dims = instruction_spec["dims"]
    got_names, got_dims = parse_fcstd(fcstd_path)
    p, r, f1, n_hit = feature_f1(req_names, got_names)
    dhr, d_hit = dim_hit_rate(req_dims, got_dims, tol)
    total = w_feat * f1 + w_dim * dhr
    return dict(p=p, r=r, f1=f1, feat_hit=n_hit, dhr=dhr, dim_hit=d_hit, total=total)


def demo():
    # instruction 文本里点名要的特征与尺寸
    instruction = {
        "features": ["Pad", "Pocket", "Fillet"],
        "dims": {("Pad", "Length"): 50.0, ("Pad", "Width"): 30.0,
                 ("Pocket", "Depth"): 10.0},
    }

    tmpdir = tempfile.mkdtemp()
    good_f = os.path.join(tmpdir, "good.FCStd")
    bad_f = os.path.join(tmpdir, "bad.FCStd")

    # 好结果：特征全、尺寸在容差内
    make_fake_fcstd(good_f,
                    [("Pad", "PartDesign::Pad"), ("Pocket", "PartDesign::Pocket"),
                     ("Fillet", "PartDesign::Fillet")],
                    {("Pad", "Length"): 50.0, ("Pad", "Width"): 30.1,
                     ("Pocket", "Depth"): 10.0})
    # 坏结果：少一个特征、尺寸偏得多
    make_fake_fcstd(bad_f,
                    [("Pad", "PartDesign::Pad"), ("Pocket", "PartDesign::Pocket")],
                    {("Pad", "Length"): 55.0, ("Pad", "Width"): 30.0})

    for label, path in [("好结果", good_f), ("坏结果", bad_f)]:
        res = spec_consistency(instruction, path)
        print("=" * 62)
        print(f"{label}：真的从 {os.path.basename(path)} 解析 Document.xml")
        print(f"  解析到特征: {sorted(parse_fcstd(path)[0])}")
        print(f"  解析到尺寸: {parse_fcstd(path)[1]}")
        print(f"  特征名 P/R/F1 : {res['p']:.3f}/{res['r']:.3f}/{res['f1']:.3f} "
              f"(命中 {res['feat_hit']}/3)")
        print(f"  尺寸命中率     : {res['dhr']:.3f} (命中 {res['dim_hit']}/3)")
        print(f"  综合规格一致性 : {res['total']:.3f} (0.5·F1+0.5·命中率)")
    print("=" * 62)
    print("说明：参照物是 instruction 文本 → 归 ② 语义对齐；")
    print("      D1 用 CLIP 模糊余弦，本脚本用结构化精确匹配——同维度不同手段。")


if __name__ == "__main__":
    demo()
