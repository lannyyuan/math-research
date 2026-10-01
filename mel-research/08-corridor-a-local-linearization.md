# 08 — 走廊 A:局部线性化(Calculus ↔ Geometry → LA)

> 对应 Task / §15 Corridor A。关键问题:**哪些 MEL 原语真的被用到?**
> 标签见 `01-…`;计算验证见 `experiments/sanity_checks.py`。

## 0. 结论

* **去掉分支标签后,"微积分的导数"与"几何的切映射"是同一个 Transformation**;唯一差别在坐标化(`Calculus` 的图 = 恒等)。**分支词只在命名空间里**。
* 走廊 A 只需要:**M1(呈现+规范)、M2(jet 作为泛构造)、M3(拉回/反变)、`exact` 函子性、局部 `graded`(germ)**。**不需要 `lax`、`choice`(除图册)、`cost`。**
* 两个压力点:(i)**局部性**——claim 只在 germ 上成立;(ii)**坐标类型必须携带规范作用**:度量的拉回按**合同**变换,不是相似。

## 1. 去标签后的类型路径

```
PointedSmoothMap(M,N;f,p)
    ⇒ Jet¹                       -- 1-jet(= 芽模 m²)
    ⇒ Lin(T_pM, T_{f(p)}N)       -- 切映射 df_p
    ⇒ Coord[Hom,(m,n),ℝ]         -- Jacobian(选图)
    ⇒ ℕ                          -- rank   (observable)
```

## 2. Stage A:原始变换

| ID | 变换 | 输入 | 输出 | 保持律 / 声明 | 复合行为 | 机制 |
|---|---|---|---|---|---|---|
| A1 | 选图 $\varphi:U\to\mathbb R^n$ | 流形芽 | 坐标 | 转移函数满足上闭链 $J_{\chi\psi}J_{\psi\varphi}=J_{\chi\varphi}$ | 群胚复合 | M1 |
| A2 | 导数 $df_p$ | $(f,p)$ | $\mathrm{Lin}(T_pM,T_{f(p)}N)$ | $f(p+h)=f(p)+df_p h+o(\lVert h\rVert)$ | 函子(链式法则) | M2 |
| A3 | *链式法则* $T(g\circ f)=Tg\circ Tf$ | — | — | — | **元定律**,非变换 | — |
| A4 | 切空间 $T_pM$ | $(M,p)$ | $\mathrm{Vect}$ | 曲线类 / 导子 / $(\mathfrak m/\mathfrak m^2)^*$ 三种构造**典范同构** | — | M2 |
| A5 | 拉回 $f^*$(形式/度量) | $g$ on $N$ | $f^*g$ on $M$ | $(g\circ f)^*=f^*\circ g^*$ | 反变 | M3 |
| A6 | Jacobian $[df]_{\varphi\psi}$ | $df_p$ + 图 | $\mathrm{Mat}$ | $[dg\circ df]=[dg][df]$;规范 $PAQ^{-1}$ | 矩阵乘法 | M1 |
| A7 | 不变量 rank、惯性指数、$\operatorname{sign}\det J$ | Lin / Coord | $\mathbb N,\mathbb Z$ | 对规范不变 | — | OBS |
| A8 | 平衡点线性化 $A=DF(x^*)$ → $e^{tA}$ | 向量场 | $\mathrm{End}$ + 半群 | Hartman–Grobman(双曲)`(bg)` | 半群复合 | PT1 |

(7 个变换 + 1 条元定律。)

## 3. MEL 表达

```
tr D : (f: Smooth(M→N), p: M) ⇒ Lin(T_pM, T_{f p}N)
  requires  f 在 p 处 C¹
  claims
    exact   D(g∘f, p) = D(g, f p) ∘ D(f, p)               [witness: cited 链式法则]
    graded  f(p+h) − f(p) − D(f,p)·h = o(‖h‖)   Γ=germ@p  [witness: 定义]
  loses     f ~₁ g  ⇔  f(p)=g(p) ∧ D(f,p)=D(g,p)          -- 1-jet 等价(核对)
  recovers  rank, ker, im 的 D                            -- 以 Lin 的 observable
  coord     图 φ@p, ψ@f(p) ⇒ Jac : Coord[Hom,(m,n),ℝ]       -- 规范 (GL_n × GL_m)

tr pullback : (f, g: Bil(T N)) ⇒ Bil(T M)            var −
  claims  exact (g∘f)^* = f^* ∘ g^*
  coord   Coord[Bil,(n)]                              -- 规范 Pᵀ G P(合同)
```

## 4. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| $D(g)\circ D(f)$ 在 $f(p)$ 处对齐 | ✓ `exact` | 链式法则;需 `requires` 基点对齐 $q=f(p)$,否则类型失败 |
| Jacobian 换图 | ✓ | $J\mapsto BJA^{-1}$;rank 不变 |
| 对 Hessian 取特征值 | **✗**(`05` §6) | `Coord[Bil]` ≠ `Coord[Endo]`;需先声明度量 |
| 局部 claim 接全局 claim | ✗ | germ 域不包含全局;`requires` 不满足 |

> 实测(S3):相似下特征值不变、合同下**不**不变,惯性不变——这是"类型 = 规范作用"的数值证据。

## 5. 非空洞性检验(闸门见 `14`)

对"光滑映射 → Jacobian 矩阵":

* **G1 可证伪**:rank 在域上非常值 ✓
* **G2 自然性**:链式法则(对复合封闭)✓
* **G3 杠杆**:秩定理 / 隐函数定理——矩阵秩可判定 immersion/submersion ✓
* **G4 变异测试**:把 $[df]$ 换成转置 ⟹ 复合顺序反,链式 claim 失败 ✓

## 6. 需要什么 / 不需要什么

| 需要 | 不需要 |
|---|---|
| M1、M2(jet 作为"芽模 $\mathfrak m^2$"的商)、M3、`exact`、germ-`graded`、坐标规范作用 | `lax`、`choice`(图册之外)、`cost`、PT2 |

**对 prompt 的回答("MEL 原语哪些被需要")**:Structure(光滑流形芽、Lin、Bil)、Transformation(`D`、`pullback`、`coord`)、Claim(`exact` + 局部 `graded`)。**没有 Law/Observable/Equivalence 作为独立原语的需要。**

## 7. 局限

* 走廊 A 对 MEL 是**最容易**的一个:几乎所有变换都是精确函子。它**不能**检验 `lax`/`choice`/成本。
* Jet 被并入 M2(商)后,"局部线性化"自身不单列;但"导数即最佳线性逼近"的**度量**含义(余项估计)仍需 `graded`。
