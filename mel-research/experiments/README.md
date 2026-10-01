# experiments

## sanity_checks.py

重算报告中引用的具体例子。**对有限实例的检查,不是证明。** 随机数种子固定(`default_rng(0)`),结果可复现。

```bash
pip install -r ../../requirements.txt
python3 sanity_checks.py            # 期望输出 "All sanity checks passed."
```

已用 Python 3.11、numpy 2.4、scipy 1.17、sympy 1.14 测试。

| 块 | 检验内容 | 被哪些文档引用 |
|---|---|---|
| **S1** | $\mathrm{RP}^2$ 六顶点三角剖分:Smith 标准型得 $H_*(\mathbb Z)=\mathbb Z,\mathbb Z/2,0$;$\mathbb Q$ 与 $\mathbb F_2$ 下 Betti 数 $(1,0,0)$ vs $(1,1,1)$;Euler 示性数与系数无关;UCT 预测一致;图的取向无关性与无挠 | `10`、`13` |
| **S2** | 带权图 → Markov 核:归一化丢失行尺度;无向情形恢复 $W$ 仅差全局标量;谱相似;**慢混合环**上收敛速率受 $\lvert\lambda_2\rvert^t$ 控制;强可 lump 与不可 lump 的缺陷;$\pi$-加权压缩保持聚合平稳律 | `09`、`13` |
| **S3** | 矩阵类型 = 规范作用:相似下特征值不变、合同下不变惯性;有限元 $\mathrm{cond}(K)\sim h^{-2}$;换基后特征值变、广义特征值不变;能量不变;**条件数随基变化**;Galerkin 正交性与能量最佳逼近 | `01`、`08`、`11` |
| **S4** | 仿射误差幺半群 $(L,\varepsilon)$ 结合且有幺元;噪声采样 + 中心差分的实测误差不超过复合界,并出现 $10^4$ 倍放大 | `13`、`11` |
| **S5** | 核对单调;在 2000 个随机有限情形中统计下游毁掉上游保留 observable 的次数 | `13` |

## sanity_checks.out.txt

上述脚本的一次实际输出,作为报告引用的数字来源。修改脚本后应重新生成:

```bash
python3 sanity_checks.py > sanity_checks.out.txt 2>&1
```

## 局限

* 只覆盖 1D P1 有限元、小规模随机图、一个带挠的单纯复形。
* S5 的随机试验对"observable 被毁"的频率(约 1%)只是示例,不是对任何分布的估计。
* 没有对 `lax` 缺陷的多步复合做任何检验(无一般演算)。
