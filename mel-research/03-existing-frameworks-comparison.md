# 03 — 与既有框架的比较

> 对应 Task 20 / Q10。**不要因术语不同而声称新颖。**
> 来源标签:`(web)` 本次会话检索核实;`(bg)` 背景知识、未复核。URL 仅列出本次检索实际返回的页面。

## 0. 结论先行

* **MEL 的类型/结构层**基本就是 **MMT 的理论 + view(理论态射)**,外加 Mathlib 式的"打包层级"经验。
* **MEL 的变换层**的数学骨架是**富足(quantale/Lawvere)范畴 / double category / 对应(relation, span)**。
* **复合律**与 **assume–guarantee 契约、weakest precondition、近似保持归约(L-reduction)、抽象解释的 Galois 连接** 同构或近似同构。
* 因此对 Q10:**MEL 更像应用于上述框架之上的一层规约纪律,而不是新的数学理论**(与 Outcome B/C 一致,见 `final-…`)。
* 真正"不在已有框架里被打包"的只有**组合方式**:(i)每个变换必须携带**缺陷账本**(假设/选择/信息/度量/正合);(ii)复合**按 observable 检查**;(iii)坐标层类型携带**规范作用**;(iv)证据状态(witness)是一等字段。每一块单独看都有先例,**打包本身是否有价值是经验问题**。

---

## 1. 框架逐项

| 框架 | 它已经解决什么 | 与 MEL 的关系 | MEL 可能增加什么(假设) | 判断 |
|---|---|---|---|---|
| **范畴论(函子、自然变换、泛性质)** `(bg)` | 类型化映射与复合;结构保持;构造由泛性质定义 | MEL 变换核 = 范畴态射的推广 | 对**非态射**变换(近似、选择、优化)的统一记账 | **基底**,非竞争者 |
| **代数理论 / Lawvere 理论** `(bg)` | "结构 = 操作 + 方程",同态 = 保持 | `Structure` 的数学内容就是理论;保持律 = 同态条件 | — | **直接复用** |
| **Operad / 多范畴** `(bg)` | 多输入映射、复合的结合性 | 张量/多输入变换(如 $a(u,v)$)自然落此 | — | **复用**,必要时 |
| **Institutions(Goguen–Burstall)** `(web)` | 与具体逻辑无关的"满足条件":跨签名变换下满足关系协变;Hets 用 institution 态射/比较态射异质地集成逻辑与证明器 | **最像** MEL 的 `preserves`:"理论态射下的满足条件" = 保持律 | 近似/有损/带选择的态射;purpose(observable) | **高度相关**:任何 MEL 的 `Structure`-层态射应当是 institution 意义下的理论态射 |
| **类型论 / 依赖类型论** `(bg)` | 类型即命题;证明项即见证;精化类型 | MEL 可在其中**表达**(RT2) | 对**非形式化/数值/引用**见证的渐进(gradual)层 | **后端**:MEL 的 witness 可落到 Lean |
| **Mathlib 打包层级经验** `(web)` | 打包 vs 非打包;"仅当有真实数学要做,或显著简化,才引入新类" | 直接约束 `05` 的类型设计 | — | **复用设计准则** |
| **范畴逻辑 / fibration** `(bg)` | 逻辑作为(纤维化)范畴 | 为"claim = 命题"提供语义 | — | 背景 |
| **表示论** `(bg)` | "结构 → $\mathrm{Vect}$"的函子,作为线性化 | LA 汇点地位的数学本质(见 `01` §5) | — | **已解释** LA 的 hub 角色 |
| **抽象解释(Cousot)** `(web)` | $\langle\alpha,\gamma\rangle$ Galois 连接:具体域 ↔ 抽象域;soundness = $\alpha(x)\sqsubseteq y\Leftrightarrow x\subseteq\gamma(y)$;Galois 连接**可复合** | **正是** M4(retraction-with-grade)的形状;purpose 相对性也有先例(抽象域由"关心的性质"决定) | 度量近似(Galois 连接多为序) | **高度相关**,不应重新命名 |
| **精化/模拟关系(Milner 等)** `(bg)` | 观测等价、模拟、双模拟 | MEL 的"purpose 相对等价"(=核对) = 观测等价 | — | **复用** |
| **MLIR / 方言** `(web)` | 方言 + 渐进降级(progressive lowering);共享的 operation/type/attribute 骨架 | **类比** `[A]`(分级见 `07` §6 与 `final-mel-research-report.md` §4) | 数学无单一"机器语义";降级常有损/带选择 | 类比,非数学内容 |
| **定理证明器 IR(Dedukti、Lean Expr、Metamath…)** `(bg)` | 小而可验证的内核 | MEL 的 Claim 若形式化,就是这些内核里的命题 | — | **后端** |
| **OpenMath / OMDoc** `(web)` | OpenMath:符号 + Content Dictionary 定义语义,交换格式;OMDoc 在其上加语句层、理论层,理论 ↔ CD | **内容语义 + 呈现分离已有先例** → RT6 的"agent-native 内部、人类可读投影"并不新 | 变换契约 | 先例强 |
| **MMT / Math-in-the-Middle** `(web)` | MMT:基础无关的模块系统(理论、view);MitM:先在中间本体里形式化概念,再对各系统**对齐**,用于 CAS 间互操作;LATIN:逻辑图谱与集成 | **目的最近**:经"中间结构"互操作 | 有损/近似/带选择的**降级**;purpose;规范 | **最近邻**;MEL 的 `Structure` 层应**直接在 MMT 里写**(RT3) |
| **Spivak 函子式数据迁移(Δ, Σ, Π)** `(web)` | 模式态射诱导**三个伴随函子**:一小族有泛性质的"数据迁移变换" | **现成的"小而可复用变换词汇"的例子**——支持压缩假设 | 面向数学对象、带误差/选择 | **强先例**(压缩可能性的正面证据) |
| **Fong–Spivak 应用范畴论 / decorated cospans / backprop as functor** `(web: Seven Sketches; bg: 其余)` | 可复合系统;带结构的复合;学习算法作为函子 | 近似/带成本算法的**可复合性**已有范畴化 | — | 相关 |
| **Markov 范畴(Fritz)** `(web)` | 以 Markov 核为态射的综合概率论;条件独立、充分统计量;统一离散、测度、Gaussian | **走廊 B** 的 `Stoch` 就是它的实例 | — | **走廊 B 的数学基础,应引用而非重造** |
| **Hilbert 复形 + 有界上链投射(AFW, FEEC)** `(web)` | 子复形 + 有界上链投射 ⇒ 稳定离散化;同调结构精确保持,状态近似 | **走廊 C+D 交汇**:精确保持结构 + 度量近似 | — | **应引用**;它是"混合 exact/graded 契约"的现成范例 |
| **Lawvere 度量空间/量子ale 富足范畴** `(web)` | $[0,\infty]$-富足 ↔ 广义度量;富足函子 ↔ 短映射;复合非扩张 | **grade 代数 Γ 的数学基础** | — | **复用** |
| **复杂性归约(Cook–Karp, L-reduction)** `(bg)` | 保答案 + 多项式成本;**近似保持归约的复合有乘法常数** | 一个已成熟的"带成本与误差的变换复合演算" | — | **最重要的被忽视先例**(见 `13`) |
| **Assume–guarantee 契约 / Hoare / wp** `(bg)` | 前置/后置条件;组合规则;**weakest precondition 向后传播假设** | `requires`/复合假设传播 = wp | — | **直接复用** |
| **Univalent 基础 / Structure Identity Principle** `(bg)` | 同构结构不可区分;transport | "呈现/规范"的形式化背景 | — | 背景 |
| **关系代数 / allegories** `(bg)` | 函数 = 全 + 单值关系;单射、满射的分类 | `06` 的"对应的缺陷分类"直接用此 | — | **复用** |

---

## 2. "它已经解决什么" 与 "MEL 可能增加什么" 的诚实对照

| 想声称的 MEL 特色 | 已有先例 | 是否真的新 |
|---|---|---|
| 显式 purpose/observable | 观测等价、抽象域、abstraction-by-property | **不新**,但在跨域变换里很少被强制声明 |
| 显式信息损失 | 数据处理不等式、核对、抽象解释的不完备 | **不新** |
| 跨域 lowering | MitM 对齐、Hets、institution 态射 | **部分新**:先例多为**精确**翻译,而非有损/带选择 |
| 近似 | 数值分析、Lawvere 富足、L-reduction、Galois 连接 | **不新**;"把它写进复合律"在应用层少见 |
| 计算成本 | 复杂性理论 | **不新**;放入语义核**有争议**(RT7) |
| agent 路由 | 类型导向搜索(Hoogle 式) | 工程 |
| **坐标类型携带规范作用** | 张量/表示论教科书 | **作为类型系统规则:未见先例**(未做穷尽检索) |
| **缺陷账本作为统一契约** | 各缺陷有各自理论 | **组织方式新,数学不新** |

## 3. 对 Q10 的回答

> **最近的现有框架是"MMT/Math-in-the-Middle(结构层)+ 富足范畴/对应(变换层)+ assume–guarantee 契约(复合层)"的并集。**
> MEL 确实可以只是这些之上的一层应用规约。**是否值得作为独立产物**取决于一个经验问题:缺陷账本 + 按 observable 复合检查 是否能在 MMT 里**自然**表达而不扩展其基础(这是 `17` RT3 的判决实验)。

## 4. 未做的事

* 未穷尽检索 2024–2026 的 LLM + 形式数学中间表示文献。本次检索命中过自动形式化综述与"relaxed natural formal language"一类工作(`arXiv:2505.23486`、`arXiv:2606.24443`,仅搜索命中,**未阅读**),不据此下任何结论。
* 未核对 MMT 当前的 view/metadata 机制能否直接承载 grade/lax 结构。

## 5. 来源(本次检索返回)

* MMT / MKM:<https://arxiv.org/pdf/1005.5232> · <https://ar5iv.arxiv.org/html/1105.0548>
* OpenMath / OMDoc:<https://en.wikipedia.org/wiki/OpenMath> · <https://en.wikipedia.org/wiki/OMDoc>
* Institutions:<https://courses.grainger.illinois.edu/cs522/sp2016/InstitutionsAbstractModelTheory.pdf>
* MLIR:<https://arxiv.org/pdf/2002.11054>
* Mathlib 层级设计:<https://cs.brown.edu/courses/cs1951x/docs/algebra/hierarchy_design.html>
* Spivak 数据迁移:<https://arxiv.org/abs/1009.1166> · Seven Sketches:<https://arxiv.org/pdf/1803.05316>
* Markov 范畴:<https://arxiv.org/pdf/1908.07021>
* FEEC / Hilbert 复形:<https://arxiv.org/pdf/0906.4325>
* 抽象解释:<https://cs.nyu.edu/~pmc309/publications.www/CousotCousot-PLILP-92-LNCS-n631-p269--295-1992.pdf>
* Lawvere / 度量富足:<https://emis.univie.ac.at/journals/TAC/reprints/articles/1/tr1.pdf>
