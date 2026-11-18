"""
common.py — 3D 生成指标公共底座（纯 Python 标准库，无需 pip）

提供所有指标脚本共用的基础算子：
  - 点云距离：欧氏、chamfer、点到面
  - ICP / Procrustes 对齐（Kabsch 算法，纯标准库 SVD 替代）
  - 体素化、占据栅格
  - 信息论：熵、KL、JSD
  - 向量相似度：余弦
  - 演示数据：球面/立方体采样点云（带 seed 可复现）

设计原则：不依赖 numpy/scipy，全部手写，保证任何 Python 3 机器可跑。
"""
import math
import random

# ---------------- 基础向量运算 ----------------

def dist(a, b):
    """欧氏距离 L2"""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def scale(a, s):
    return [x * s for x in a]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def normalize(a):
    n = norm(a)
    return [x / n for x in a] if n else list(a)


def mean(points):
    """点云质心"""
    if not points:
        return [0.0, 0.0, 0.0]
    n = len(points)
    return [sum(p[i] for p in points) / n for i in range(len(points[0]))]


def cosine(a, b):
    """余弦相似度 [-1, 1]"""
    na, nb = norm(a), norm(b)
    return dot(a, b) / (na * nb) if na and nb else 0.0


# ---------------- 点云距离核心 ----------------

def nearest_distance(p, cloud):
    """点 p 到点云 cloud 的最近距离"""
    return min(dist(p, q) for q in cloud)


def chamfer_unidirectional(A, B):
    """单方向 Chamfer: mean_{a∈A} min_{b∈B} ||a-b||"""
    return sum(nearest_distance(a, B) for a in A) / len(A)


def chamfer(A, B):
    """双向对称 Chamfer Distance（越低越好）"""
    return chamfer_unidirectional(A, B) + chamfer_unidirectional(B, A)


def point_to_plane_distance(p, face_pts):
    """点到三角面片的近似距离：点到面质心的距离（演示用简化版）"""
    c = mean(face_pts)
    return dist(p, c)


# ---------------- 对齐（ICP / Kabsch 的纯标准库近似） ----------------

def center(points):
    """去中心化"""
    c = mean(points)
    return [sub(p, c) for p in points]


def icp_align(source, target, iterations=20):
    """
    迭代最近点对齐的简化版：只做质心对齐 + 均匀缩放对齐。
    完整 ICP 每步要算最优旋转（Kabsch/SVD），纯标准库实现代价高；
    这里提供质心+尺度归一，足够让演示数据的 CD/EMD 可比。
    真实评估请用 Open3D/PyTorch3D 的完整 ICP。
    """
    cs, ct = mean(source), mean(target)
    centered = [sub(p, cs) for p in source]
    t_centered = [sub(p, ct) for p in target]
    rs = max(norm(p) for p in centered) or 1.0
    rt = max(norm(p) for p in t_centered) or 1.0
    s = rt / rs
    return [add(scale(p, s), ct) for p in centered]  # 缩放后平移到目标质心


def normalize_pointcloud(points, target=1.0):
    """归一化到零质心、最大半径 target（评估标准预处理）"""
    c = mean(points)
    centered = [sub(p, c) for p in points]
    r = max(norm(p) for p in centered) or 1.0
    return [scale(p, target / r) for p in centered]


# ---------------- 体素化 / 占据栅格 ----------------

def voxelize(points, res=32, bounds=(-1.0, 1.0)):
    """
    把点云离散到 res^3 体素栅格，返回占据的体素集合 (i,j,k)。
    坐标先线性映射到 [0,res-1]。
    """
    lo, hi = bounds
    span = hi - lo
    occ = set()
    for p in points:
        idx = []
        for coord in p[:3]:
            v = int((coord - lo) / span * (res - 1))
            idx.append(max(0, min(res - 1, v)))
        occ.add(tuple(idx))
    return occ


def voxel_iou(A, B, res=32):
    """体素 IoU = |A∩B| / |A∪B|"""
    va, vb = voxelize(A, res), voxelize(B, res)
    inter = len(va & vb)
    union = len(va | vb)
    return inter / union if union else 0.0


# ---------------- 信息论（JSD 用） ----------------

def kl_divergence(p, q, eps=1e-12):
    """KL(P||Q)，输入为概率数组"""
    s = 0.0
    for pi, qi in zip(p, q):
        pi = max(pi, eps)
        qi = max(qi, eps)
        s += pi * math.log(pi / qi)
    return s


def jsd(p, q):
    """Jensen-Shannon 散度，对称，[0,1]（以 2 为底）"""
    m = [(a + b) / 2 for a, b in zip(p, q)]
    val = 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)
    return val / math.log(2)


def entropy(p, eps=1e-12):
    return -sum(pi * math.log(pi) for pi in p if pi > eps)


# ---------------- 演示数据（带 seed 可复现） ----------------

def sample_sphere(n, seed=0, radius=1.0, center=(0, 0, 0)):
    """球面均匀采样点云（可复现）"""
    rng = random.Random(seed)
    pts = []
    for _ in range(n):
        z = rng.uniform(-1, 1)
        theta = rng.uniform(0, 2 * math.pi)
        r_xy = math.sqrt(1 - z * z)
        pts.append([
            center[0] + radius * r_xy * math.cos(theta),
            center[1] + radius * r_xy * math.sin(theta),
            center[2] + radius * z,
        ])
    return pts


def sample_cube_surface(n, seed=0, size=1.0, center=(0, 0, 0)):
    """立方体表面采样点云"""
    rng = random.Random(seed)
    pts = []
    h = size / 2
    for _ in range(n):
        face = rng.randint(0, 5)
        u, v = rng.uniform(-h, h), rng.uniform(-h, h)
        if face == 0:   p = [u, v, h]
        elif face == 1: p = [u, v, -h]
        elif face == 2: p = [u, h, v]
        elif face == 3: p = [u, -h, v]
        elif face == 4: p = [h, u, v]
        else:           p = [-h, u, v]
        pts.append([p[0] + center[0], p[1] + center[1], p[2] + center[2]])
    return pts


def jitter(points, noise, seed=0):
    """给点云加高斯噪声，模拟生成误差"""
    rng = random.Random(seed)
    return [[c + rng.gauss(0, noise) for c in p] for p in points]


def translation(points, offset):
    return [add(p, offset) for p in points]


def score_line(name, value, direction="", note=""):
    """统一打印一行指标结果"""
    print(f"  {name:<28}: {value:.6f}  {direction}  {note}")


if __name__ == "__main__":
    A = sample_sphere(500, seed=1)
    B = jitter(A, 0.02, seed=2)
    print("common.py 自检")
    score_line("Chamfer(A,A)", chamfer(A, A), "(应=0)")
    score_line("Chamfer(A,B)", chamfer(A, B), "(加噪后>0)")
    score_line("Voxel IoU(A,A)", voxel_iou(A, A, 32), "(应=1)")
    score_line("JSD(A,A histogram)", jsd([0.5, 0.5], [0.5, 0.5]), "(应=0)")
