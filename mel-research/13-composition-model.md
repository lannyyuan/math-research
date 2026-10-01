# 13 — 复合模型

> 对应 §13、Q8。问题:**什么时候两个变换可以复合?复合后契约是什么?**
> 标签见 `01-…`;数值例子来自 `experiments/sanity_checks.py`(S1–S5)。

## 0. 结论

> 复合不是一个运算,而是**对契约各"缺陷通道"分别复合**。通道之间的复合律**异质**,但**前五个通道有可证或可检验的规则**;**`lax` 缺陷对象的复合没有简单演算**,这是本研究最诚实的缺口。
>
> | 通道 | 复合律 | 状态 |
> |---|---|---|
> | 类型 | 理论包含 + 参数合一,或显式规范桥 | 可检验 |
> | 假设 | $\mathrm{requires}(T_2\circ T_1)=\mathrm{req}(T_1)\wedge\mathrm{wp}_{T_1}(\mathrm{req}(T_2))$ | 可证(单值、全于 req 域) |
> | `exact` | 交换方块的粘贴 | 平凡 |
> | `graded` | 仿射误差幺半群 $(L,\varepsilon)$ | **可证**,已数值验证 |
> | 信息 | 核对单调;**按 observable 复合** | 可证,有限情形已验证 |
> | 选择 | 群胚粘合;observable 须规范不变 | 可检验 |
> | `lax` | 2-胞腔粘贴;缺陷对象 = 扩张(谱序列) | **未解** |

## 1. 复合有定义的条件

设 $T_1:S\Rightarrow S'$,$T_2:S''\Rightarrow S'''$。$T_2\circ T_1$ **有定义**当且仅当:

| 编号 | 条件 | 判定者 |
|---|---|---|
| C1 类型 | $S'\le S''$(理论包含路径存在、参数合一),**或**存在显式规范桥 $\beta\in\mathrm{Gauge}(S')(\mathrm{pres}_1\to\mathrm{pres}_2)$ | 类型检查器 |
| C2 假设 | $\mathrm{guarantees}(T_1)\models\mathrm{requires}(T_2)$ | 证明义务 |
| C3 变性 | 协/反变一致 | 类型检查器 |
| C4 claim | 按模式复合(§2) | 规则 |
| C5 观测 | 对每个要保留的 observable $q$,**可恢复性沿链保持**(§3) | 规则 |
| C6 选择 | 选择集并;跨阶段共享的规范须由 $\beta$ 粘合 | 规则 |
| C7 见证 | 复合见证状态 = 各成分的**最小者**(`formal > checked > cited > asserted`) | 规则 |
| C8 成本 | 若声明:按所声明的成本代数复合(**不入语义核**) | 附属 |

> **组合的新奇之处是 C5:复合是"按目的"检查的,不是整体检查的。**(先例见 §7:数据处理不等式、抽象解释。)

## 2. 逐模式复合律

### 2.1 `exact`
交换方块粘贴。$\mathrm{exact}\circ\mathrm{exact}=\mathrm{exact}$。

### 2.2 `graded`:仿射误差幺半群 `[T]`
每个阶段:理想映射 $f_s$,实现 $\hat f_s$,
$$d(\hat f_s(x),f_s(x))\le\varepsilon_s,\qquad f_s\ \text{是}\ L_s\text{-Lipschitz}.$$
则
$$d(\hat f_2\hat f_1x,\ f_2f_1x)\le d(\hat f_2\hat f_1x,\ f_2\hat f_1x)+d(f_2\hat f_1x,\ f_2f_1x)\le\varepsilon_2+L_2\varepsilon_1.$$
即阶段契约 $(L,\varepsilon)$ 按
$$(L_2,\varepsilon_2)\ast(L_1,\varepsilon_1)=(L_2L_1,\ \varepsilon_2+L_2\varepsilon_1)$$
复合——这是仿射映射 $t\mapsto Lt+\varepsilon$ 的复合,**结合、有幺元 $(1,0)$**(`S4` 随机三元组验证)。
**稳定常数 $L_2$ 必须由下游声明**;缺失则 grade 取 $\top$,并标记 `UNSTABLE`。

**实测(S4)**:噪声 $\varepsilon_1=10^{-6}$ 的采样后接中心差分求导($L_2\approx1/h$,截断 $\varepsilon_2=h^2/6$):$h=10^{-1},10^{-2},10^{-3},10^{-4}$ 的实测最大误差 $1.60\times10^{-3},1.13\times10^{-4},9.97\times10^{-4},9.76\times10^{-3}$,**均不超过**复合界 $1.68\times10^{-3},1.17\times10^{-4},1.00\times10^{-3},1.00\times10^{-2}$;最后一档表明放大约 $10^{4}$ 倍。

### 2.3 序型 grade(不等式)
$e_1\le e_2$ 且下游 $g$ 单调 ⟹ $g(e_1)\le g(e_2)$。例:弱对偶间隙 $d^*\le p^*$;Jensen。

### 2.4 概率 grade $(\varepsilon,\delta)$
阶段 1 为 $(\varepsilon_1,\delta_1)$,阶段 2 为 $L_2$-Lipschitz 且 $(\varepsilon_2,\delta_2)$ ⟹ 复合为 $(\varepsilon_2+L_2\varepsilon_1,\ \delta_1+\delta_2)$(union bound)。**不需要阶段间独立,但要求阶段 2 的 $(\varepsilon_2,\delta_2)$ 保证对*任意输入*成立**(包括阶段 1 的随机输出);若阶段 2 只对固定输入有保证,该规则不适用。界较松。

### 2.5 germ/局部 grade
局部余项 $o(\lVert h\rVert)$ 在复合下封闭当且仅当下游在像点可微(链式法则带余项)。**与 Lipschitz 不是一回事**:此时误差不按 $L\varepsilon$ 传播,而是被 jet 本身携带。

### 2.6 `lax`:**未解**
两个 `lax` 方块的粘贴是 2-胞腔的纵横复合,**逻辑上**没问题;但**缺陷对象**(如 $\mathrm{Tor}$)的复合是扩张问题,一般需要**谱序列**(Grothendieck、Künneth、UCT 的迭代)。本研究**没有**给出一般演算。在 MEL 里,**对多步 `lax` 复合,契约只能声明"缺陷 = 未定,需下游检查"**。

## 3. 信息损失与按 observable 的复合

**事实 `[T]`(集合论)**:$\ker(g\circ f)\supseteq\ker f$——**信息不会回来**。
对 observable $q$,令 $q$ 经 $f$ 可恢复 ⟺ $\exists\tilde q_f:\ q=\tilde q_f\circ f$。则

> $q$ 经 $g\circ f$ 可恢复 ⟺ $q$ 经 $f$ 可恢复,**且** $\tilde q_f$ 在 $\mathrm{im}f$ 上对 $g$ 的纤维为常值。

即复合是否保留 $q$,取决于**中间类型上的 $\tilde q_f$ 是否仍为 $g$ 的 `recovers`**。
实测(S5):2000 个随机有限情形中,**核对单调性无一例外**成立;但有 **20 例**中 $f$ 保留了 $q$、$g$ 把它毁掉——故**必须逐 observable 检查**。

## 4. 假设沿复合向后传播(wp)

$$\mathrm{requires}(T_2\circ T_1)=\mathrm{requires}(T_1)\ \wedge\ \mathrm{wp}_{T_1}(\mathrm{requires}(T_2)).$$
这是 Dijkstra weakest precondition(`(bg)`)的搬用 `[S]`。
例:`PF ∘ RW` 要求"源图强连通且非周期",**这是对源图的假设,不是对 $P$ 的**。

## 5. 命题:契约范畴(片段)

> **命题(草证)** 取:对象 = 类型(带 $\le$ 与规范桥);态射 = 契约 $(\mathrm{req},\,(L,\varepsilon),\,\rho)$,其中 $\rho$ 是声明的损失关系。按 §1–§4 的规则复合。则在**单值、全于 req 域**的变换片段上,复合**结合、有幺元**。

*证明草图。*
* **类型**:$\le$ 是预序,传递 ⟹ 复合的类型条件一致;恒等变换满足 $S\le S$。
* **假设**:$\mathrm{wp}_{T_2\circ T_1}=\mathrm{wp}_{T_1}\circ\mathrm{wp}_{T_2}$ 且 $\mathrm{wp}_{T_1}$ 对 $\wedge$ 分配 ⟹ 两种括号给出同一 requires。
* **grade**:仿射映射复合的结合律(§2.2),幺元 $(1,0)$。
* **损失**:$\rho(T_2\circ T_1)=\rho(T_1)\vee T_1^{-1}(\rho(T_2))$;原像与复合可交换 ⟹ 结合。
* **见证**:取最小是结合的。
□

> **范围声明**:这只证明了**片段**的结合性。多值对应、`lax`、概率 grade 的依赖结构、规范群胚的上闭链条件**均未纳入**。**没有机器形式化。**

## 6. 实例

### 6.1 成功的复合

| # | 复合 | 结果 |
|---|---|---|
| S-1 | 走廊 D:Galerkin → 装配 → 求解 → 重构 | 总误差 = Céa 项 + 求解项;求解项系数含 $\mathrm{cond}(K)$(**基相关**:$32.2$ vs $2725.9$,S3) |
| S-2 | 走廊 B:RW → $P^n$ → 平稳律 | exact;假设向后传播:源图强连通且非周期 |
| S-3 | 走廊 A:$D(g)\circ D(f)$ 与换图 | exact;规范桥 $J\mapsto BJA^{-1}$ |
| S-4 | 走廊 C:Cells → $H_n$ → $\otimes\mathbb Q$ | `lax` 缺陷 = 0($\mathbb Q$ 平坦) |

### 6.2 **被拒绝**的复合(检查器必须拒绝)

| # | 复合 | 拒绝原因 | 证据 |
|---|---|---|---|
| R-1 | Galerkin → 点式 $\Delta$ | 类型:$V_h\not\subset H^2$ | 结构类型 |
| R-2 | 噪声采样 → 无声明 $L$ 的求导 | grade $\top$ | S4:放大 $10^4$ |
| R-3 | RW → 顶点商图再 RW | 归一化对商不自然;除非强可 lump | S2:缺陷 0.100 |
| R-4 | $H_n(\,;\mathbb Z)\otimes\mathbb F_2$ 当作 $H_n(\,;\mathbb F_2)$ | `lax` 缺陷 $\ne0$ | S1:$\mathrm{RP}^2$,度 2,缺陷 $\mathbb F_2$ |
| R-5 | $f$ 保留 $q$ 但 $g$ 毁掉它却声称整体保留 | observable 流断 | S5:20/2000 |

> 注意:**这些"被拒绝"的例子是我知道答案的反例**(RT10)。检查器是否能**自动**拒绝它们未被实现测试。

## 7. 先例对照

| 本模型的部分 | 既有先例 |
|---|---|
| C2 + §4 | Hoare 逻辑、Dijkstra wp、assume–guarantee 契约(Benveniste 等)`(bg)` |
| §2.2 | 数值分析的误差传播;**近似保持归约(L-reduction)的复合常数相乘** `(bg)`;Lawvere 度量范畴的非扩张复合 `(web)` |
| §3 | 数据处理不等式;抽象解释中**Galois 连接可复合** `(web)` |
| C1 + 规范桥 | 群胚/descent;表示论中的 intertwiner |
| 整个契约的"成本 + 近似 + 保答案" | **Karp/Cook 归约**:保答案 + 多项式成本 `(bg)` |

## 8. 对 Q8 的回答

> **有"部分的"复合演算的证据**:对 `exact`、`graded`(含序、概率)、假设、信息(按 observable)、选择五个通道,有可证或可数值验证的规则,并能**拒绝**具体的非法复合。
> **缺口**:`lax` 缺陷的复合(同调代数的谱序列领域),多值对应,规范群胚的相容性。
> 因此:**不是一个统一演算,而是"一个小的、按通道的演算 + 一个已知困难的角落"**——与 Outcome B 一致。
