# 11 — 走廊 D:解析 / 变分 / 有限维(Calculus → Functional Analysis → Optimization → Finite LA)

> 标签见 `01-…`;数值验证见 `experiments/sanity_checks.py` S3、S4。
> 模型问题:$-u''=f$ 于 $(0,1)$,$u(0)=u(1)=0$;一般形式:求 $u\in V$(Hilbert)使 $a(u,v)=\ell(v)\ \forall v\in V$,$a$ 有界($M$)、强制($\alpha$)。

## 0. 结论

* "连续 → 离散"**不是一个原语**:至少是三种不同机制——**Galerkin 投影(保结构)**、**点评估/配置(有限差分)**、**谱截断**。只能算 CONVENIENCE LABEL。
* 走廊 D 的核心是 **M4(带分级的收缩)**:精确保持结构、近似状态。这与 FEEC(Arnold–Falk–Winther `(web)`)的"子复形 + 有界上链投射"一致:**结构精确,状态graded**。
* **成本不是规范不变量**:同一个离散问题,换基后 $\mathrm{cond}(K)$ 从 32.2 变到 2725.9(S3)。因此"抽象/坐标分离"对**语义**成立,对**数值成本/稳定性**不成立;成本必须挂在坐标层。
* 弱形式、变分形式、线性系统、极小化之间的等价是 **M5(假设下的重述)**。

## 1. 路径

```
StrongProblem(A,f)
  ⇒ WeakProblem(V,a,ℓ)           -- 对 V* 测试;lax(强⊂弱)
  ⇒ Variational(V,J)             -- 对称强制 ⇒ 极小化 ½a(v,v)−ℓ(v)
  ⇒ Subspace V_h ⊂ V             -- choice
  ⇒ Coord[Bil](K,b)              -- 选基;合同规范
  ⇒ LinSys / Minimize(½xᵀKx−bᵀx)
  ⇒ u_h = Σ xᵢφᵢ                 -- 重构
```

## 2. Stage A:原始变换

| ID | 变换 | 输入 | 输出 | 保持律 / 声明 | 机制 |
|---|---|---|---|---|---|
| D1 | 强 → 弱 | 强问题 | 弱问题 | 强解 ⊂ 弱解;**需正则性**才相等 | M5 |
| D2 | 弱 → 变分 | 弱问题 | 极小化 | **对称 + 强制** ⟹ 等价(Dirichlet 原理) | M5 |
| D3 | Riesz / 解算子 $A:V\to V^*$ | Hilbert | 对偶 | $V\cong V^*$ | M3 |
| D4 | 选子空间 $V_h\subset V$ | $V$ | 有限维 | 选择(网格/空间) | M4(选择部分) |
| D5 | Galerkin / Ritz 投影 | 变分问题, $V_h$ | $u_h$ | $a(u-u_h,v_h)=0$;对称时为**能量范数最佳逼近** | M4 |
| D6 | 选基 + 装配 | $V_h$ | $K_{ij}=a(\varphi_j,\varphi_i)$, $b_i=\ell(\varphi_i)$ | 规范:**合同** $K\mapsto S^{\!\top}KS$ | M1 |
| D7 | 求解 $Kx=b$ | $(K,b)$ | $x$ | Cholesky/CG;成本依赖 $\mathrm{cond}(K)$ | PT2 |
| D8 | 重构 $P_h:\mathbb R^n\to V_h\subset V$ | $x$ | $u_h$ | $R_hP_h=\mathrm{id}$ | M1(逆) |
| D9 | 线性系统 ⇔ 二次极小化 | $(K,b)$ | $\min\frac12x^{\!\top}Kx-b^{\!\top}x$ | $K$ SPD ⟹ 等价 | M5 |

(9 个变换。)

## 3. 实际计算(S3、S4)

| 量 | 结果 |
|---|---|
| $\mathrm{cond}(K)$($n=16,32,64,128$) | $116,441,1712,6744$ ⟹ $O(h^{-2})$ |
| 换基 $K'=S^{\!\top}KS$:$K$ 的特征值 | **改变**(无规范不变性) |
| 广义特征值 $(K,M)$ | **不变** ✓;最小者 9.970 vs $\pi^2=9.870$ |
| 能量 $x^{\!\top}Kx$ | 不变 ✓ |
| $\mathrm{cond}(K)$ vs $\mathrm{cond}(K')$ | 32.2 vs 2725.9 ⟹ **成本是基相关的** |
| Galerkin 正交性 | $\max|a(u-u_h,v_h)|=1.2\times10^{-15}$ ✓ |
| $u_h$ 是能量范数最佳逼近 | 500 个随机扰动全部更差 ✓ |
| 有限差分求导(噪声 $10^{-6}$)实测误差 vs 复合界 $\varepsilon_2+L_2\varepsilon_1$ | 全部 $\le$ 界;$h=10^{-4}$ 时误差 $\approx10^{-2}$(放大 $10^4$ 倍) |

## 4. MEL 表达

```
tr Galerkin[V_h, basis] : Variational(V,a,ℓ) ⇒ LinSys(n)
  requires  a 有界(M)、强制(α);ℓ ∈ V*;  V_h ⊂ V 有限维
  choice    V_h : Subspace(V)                  -- 网格/空间
            basis : Torsor(GL_n)               -- 规范: K ↦ SᵀKS(合同)
  claims
    exact   a(u − u_h, v_h) = 0   ∀ v_h ∈ V_h                 [witness: 定义]
    exact   (a 对称) u_h = argmin_{v∈V_h} ‖u−v‖_a             [witness: cited]
    graded  ‖u − u_h‖_V ≤ (M/α)·inf_{v∈V_h}‖u − v‖_V   Γ=Lipschitz-affine, L=M/α
                                                                 [witness: cited Céa]
    exact   R_h ∘ P_h = id_{V_h}                              -- 收缩的精确部分
  loses     V_h 之外的一切(核对 = V ⊖ V_h 的正交补)
  recovers  能量 a(u_h,u_h);‖·‖_V 误差界
  coord     K : Coord[Bil,(n)] ;   cost: cond(K) [基相关,仅注记]
  stable    L = 1/α                                         -- 声明稳定常数,方可下游复合

tr StrongToWeak : Strong(A,f) ⇒ Weak(V,a,ℓ)
  claims  lax  Sol_strong ↪ Sol_weak     defect = 非经典弱解
          under  椭圆正则性 (u ∈ H² ⟹ 弱解即强解)
```

## 5. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| Galerkin → 装配 → 求解 → 重构 | ✓,误差 = Céa + 求解误差 | 求解误差系数含 $\mathrm{cond}(K)$,**基相关** |
| 对 $u_h$ 取点式拉普拉斯 $\Delta$ | **✗** 类型错误 | $V_h\subset H^1$,$\not\subset H^2$;`Δ: H²⇒L²` |
| 离散化后无声明稳定常数的求导 | **✗**(或 grade=$\top$) | 有限差分求导的 $L\sim1/h$:$10^{-6}\to10^{-2}$ |
| 有限元(Galerkin) vs 有限差分(采样)混用 | ✗ | 采样不是收缩;一致性+稳定性 ⟹ 收敛(Lax 等价)是另一种契约 |
| 混合:结构精确 + 状态近似(FEEC) | ✓ | 对 $d$ 交换精确;范数下 graded |

> 复合检查没有任何"总是通过"的先验:**稳定常数 $L$ 必须由下游声明**,否则 `T-Comp` 退为 grade $\top$ 并标记 `UNSTABLE`。

## 6. "连续 → 离散"不是单一原语

| 机制 | 对象 | 精确保持什么 | 误差性质 |
|---|---|---|---|
| **Galerkin / Ritz 投影** | $V\to V_h$ 子空间 | 变分结构、对称性、(FEEC 下)复形 | 最佳逼近 × $M/\alpha$ |
| **点评估/配置/有限差分** | $V\to\mathbb R^n$ 采样 | 无(需一致性+稳定性) | 截断误差 × $1/h$ 放大 |
| **谱截断** | 基展开的前 $n$ 项 | 谱结构 | 尾项 |

结论:把"discretization"设为原语会把三个不同的契约抹成一个;在 MEL 里,它只能是**标签**。

## 7. 非空洞性检验

* **零编码**:$V\to\mathbb R^n$ 任取 $n$ 个数 ⟹ **G1** 失败(无可恢复的 observable)。
* **答案预计算**:把 $u$ 的节点值写进 $b$ ⟹ **G2** 失败(装配必须不依赖 $u$)。
* **G4**:使 $K$ 不对称 ⟹ "能量范数最佳逼近" claim 失败(可数值检验)。
* **G3**:Céa 引理 + Lax–Milgram ⟹ 有界、可预测的误差;线性系统有多项式算法。

## 8. 压力点

1. **混合 claim**:精确(结构)+ graded(状态)必须在同一契约里并存。
2. **成本与规范不相容**:成本不能进语义核。
3. **`lax`**:强解 ⊂ 弱解。
4. **稳定常数是一等声明**,否则无法复合。
5. **假设链**:强制性 → Lax–Milgram → Céa → 误差界;`requires` 沿链传播。

## 9. 局限

* 只数值验证了 1D P1 有限元;高维、非线性、非协调元均未测。
* FEEC 的"有界上链投射"只引用,未重做。
