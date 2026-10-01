# 09 — 走廊 B:离散 / 随机 / 动力(Graph → Probability → Dynamics → LA)

> 标签见 `01-…`;数值验证见 `experiments/sanity_checks.py` S2。

## 0. 结论

* 路径去标签后:$\mathsf{WeightedGraph}\Rightarrow\mathsf{Stoch}\Rightarrow\mathsf{Evolution}\Rightarrow\mathsf{LinOp}^{+}$。
* **归一化是规范固定**:$P=D^{-1}W$ 取 $W$ 在"正对角行缩放"轨道上的行和为 1 的切片;丢失的恰是行尺度。
* **LA 不够**:Perron–Frobenius 是**锥定理**(Krein–Rutman 一类),需要"正性/序结构",**不是向量空间结构**。目标类型必须是 $\mathsf{LinOp}$ 加上"保持的凸集/锥"这一精化。
* **聚合(lumping)与 Galerkin 是同一个机制(M4)**,这是走廊 B 与 D 之间最具体的复用证据(已数值验证)。

## 1. 路径

```
WeightedGraph(V,W)
  ⇒ Stoch(|V|)                    -- Markov 核 P  (choice: 归一化)
  ⇒ Evolution                     -- μ ↦ μPⁿ ,  e^{tQ}
  ⇒ LinOp restricted to Δ         -- 线性算子 + 保持单纯形(锥)
  ⇒ Obs                           -- π, 谱隙, 击中时
```

## 2. Stage A:原始变换

| ID | 变换 | 输入 | 输出 | 保持律 / 声明 | 复合行为 | 机制 |
|---|---|---|---|---|---|---|
| B1 | 邻接矩阵 | 带权图 | $\mathrm{Coord}[\mathrm{Perm}]$ | 规范群 $S_n$:$\Pi W\Pi^{\!\top}$ | 矩阵乘 | M1 |
| B2 | 归一化 $P=D^{-1}W$ | $W\ge0,\deg>0$ | $\mathsf{Stoch}(n)$ | 行和为 1;**仅对图同构自然** | — | PT2(规范固定) |
| B3 | *Stoch 对复合封闭* | — | — | $\mathsf{Stoch}\subset\mathrm{Mat}(\mathbb R_{\ge0})$ 的子范畴 | **元定律** | — |
| B4 | 作用于分布 $\mu\mapsto\mu P$ | $\mathsf{Stoch}$ | $\mathrm{Vect}$ + 单纯形 | $\mathbf{Kl}(\mathcal D)\to\mathrm{Vect}$ 忠实、非满 | 函子 | M2 |
| B5 | 迭代/半群 $P^n$、$e^{tQ}$ | $P$ / $Q$ | 幺半群作用 | 嵌入问题:并非每个 $P=e^Q$($\det P>0$ 必要)`(bg)` | 加法 | PT1 |
| B6 | 平稳律、谱隙、击中时 | $P$ | $\mathrm{Dist},\mathbb R$ | PF:不可约(+非周期)⇒ 唯一/收敛 `[T]` | — | OBS |
| B7 | 聚合/lumping | $P$, 划分 $\mathcal P$ | $\hat P$ on blocks | 强可 lump:$PV=V\hat P$(Kemeny–Snell)`[T]` | — | M4 |
| B8 | 前向 $\mu P$ vs 后向 $Pf$ | $P$ | 作用于测度 / 函数 | 伴随(Kolmogorov 前向/后向) | 反变 | M3 |

(7 个变换 + 1 条元定律。)

## 3. MEL 表达

```
tr RW[norm ∈ {row, lazy}] : WGraph(V,W) ⇒ Stoch(|V|)
  requires  W ≥ 0 ;  ∀v. deg(v) > 0
  choice    norm : Slice(RowScaling)      gauge diag(ℝ>0)^|V|
  claims
    exact    P = D⁻¹W                                   (norm=row)
    exact    natural[Iso]  RW(σ·G) = σ·RW(G)·σᵀ
    -- 注意:不声明对"顶点收缩/商"自然
  loses     W ~ ΛW (Λ 对角>0)                -- 有向;若 W 对称:W ~ cW(每连通分量)
  recovers  走一步转移概率;  (不可约+非周期下)平稳律、谱隙

tr Lump[𝒫] : Stoch(n) ⇒ Stoch(|𝒫|)
  requires  𝒫 强可 lump                       -- 否则退化为下行
  claims    exact  P·V = V·P̂
  -- 不可 lump 时:
  tr Compress[𝒫,π] : Stoch(n) ⇒ Stoch(|𝒫|)   -- π-加权 Galerkin 压缩
  claims    exact  π̂ P̂ = π̂        (lumped 平稳律被保持)
            graded ‖P·V − V·P̂‖ ≤ ε            Γ=metric
```

## 4. 数值验证(S2,实际计算过)

| 命题 | 结果 |
|---|---|
| 有向情形 $P(\Lambda W)=P(W)$ | ✓ 行尺度被丢失 |
| 无向情形 $(P,\pi)$ 恢复 $W$,仅差一个全局标量 | ✓ |
| $\mathrm{spec}(P)=\mathrm{spec}(D^{-1/2}WD^{-1/2})$(相似) | ✓ |
| 慢混合环上 $\lVert P^t-\mathbf 1\pi\rVert\lesssim|\lambda_2|^t$(误差远高于机器精度) | ✓ |
| 可 lump 链 $PV=V\hat P$ | ✓ |
| 不可 lump 链的朴素聚合有缺陷 | ✓ 缺陷 = 0.100 |
| π-加权压缩得到随机矩阵且保持 lumped 平稳律 | ✓ |

## 5. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| RW 后迭代 $P^n$ | ✓ `exact` | $\mathsf{Stoch}$ 对复合封闭 |
| RW 后对**顶点商图**再 RW | **✗**(除非可 lump) | 归一化对一般图态射**不自然**;商后再归一化 $\ne$ 归一化后聚合 |
| 对 `Mat(ℝ≥0)`(非随机)取平稳律 | ✗ | 缺 `where P·1=1`,产生精化义务 |
| 平稳律后恢复 $W$ | ✗ | 信息已丢失(行尺度 / 全局标量) |
| 谱 observable 经 RW 后恢复 | ✓ | `recovers` 声明含谱 |

## 6. 压力点

1. **选择即规范固定**:`choice norm : Slice(RowScaling)`。换归一化(lazy、对称化)= 换切片;**观测量对切片的依赖必须声明**(混合时间随 lazy 与否而变)。
2. **锥/正性是 LA 之外的结构**:B4 的目标若只写 `Vect`,就丢了 PF 所需的信息;必须写 `LinOp where preserves(Δ)`。
3. **假设向后传播**:PF 的"不可约"是对**源图**的假设;`requires` 沿复合向后传播(wp,见 `13`)。
4. **连续时间的存在性**:$P=e^{Q}$ 不总存在(`requires` 嵌入性)。
5. **M3**:前向/后向的变性必须在类型里。

## 7. 非空洞性检验

* "带权图 → $\mathbb R^V$ 上的算子 $W$"若不使用 Markov 结构,只达 **R0**。
* 通过 **G3**:PF + 谱隙给出混合时间界(有定理见证);
* **G2**:"把平稳律直接作为表示"(答案预计算)失败——因为不能经 $P^n$ 复合得到;
* **G4**:变异测试——把行归一化改成列归一化,`P·1=1` claim 失败。

## 8. 局限

* Markov 范畴(Fritz `(web)`)提供了本走廊更强的理论基础,本文只用到有限、离散的片段。
* "聚合 ≡ Galerkin"是**结构对应 `[S]`**,不是已证定理;但 $\hat\pi\hat P=\hat\pi$ 的恒等式已直接验证并可手证。
