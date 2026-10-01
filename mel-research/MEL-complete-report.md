# Mathematical Expression Layer (MEL) — 完整研究报告

> **Learn from Linear Algebra's design, not from its dominance.**
> **Search for compression before coverage.**

本文件是**单一完整版**:第一部分为总报告,附录 01–17 为 prompt 所要求的各分项研究,附录 S 为计算验证输出。
文中以反引号标出的 `01`–`17` 指**本文件的对应附录**;`final-…` 指第一部分。
证据标签:`[T]` 定理/标准事实 · `[S]` 结构对应 · `[A]` 类比 · `[H]` 本研究假设;`(web)` 本次检索核实 · `(bg)` 背景知识未复核。

## 目录

- **第一部分 总报告**(结论、发现、Q1–Q12、下一步)
- 附录 01 — 为什么线性代数是一个好的 Expression Layer
- 附录 02 — LA 专有特征 vs 可泛化特征
- 附录 03 — 与既有框架的比较
- 附录 04 — MEL 核心候选:最小核应该是什么
- 附录 05 — MEL 类型系统
- 附录 06 — Map 与 Transformation 语义
- 附录 07 — 规范型与中间类型化形式
- 附录 08 — 走廊 A:局部线性化(Calculus ↔ Geometry → LA)
- 附录 09 — 走廊 B:离散 / 随机 / 动力(Graph → Probability → Dynamics → LA)
- 附录 10 — 走廊 C:拓扑 / 代数(Graph → Topology → Abstract Algebra → LA)
- 附录 11 — 走廊 D:解析 / 变分 / 有限维(Calculus → Functional Analysis → Optimization → Finite LA)
- 附录 12 — 分解与压缩检验(Factorization & Compression Test)
- 附录 13 — 复合模型
- 附录 14 — 非空洞性与失败模式
- 附录 15 — Agent-native 语言分析
- 附录 16 — MEL v0.1 候选
- 附录 17 — 红队评审
- 附录 S — 计算验证输出(`experiments/sanity_checks.py`)

---

## 第一部分 总报告

> **Learn from Linear Algebra's design, not from its dominance.**
> **Search for compression before coverage.**

本报告综合 `01`–`17`。语言:中文,技术术语保留英文。
证据标签:`[T]` 定理/标准事实 · `[S]` 结构对应 · `[A]` 类比 · `[H]` 本研究假设;`(web)` 本次检索核实 · `(bg)` 背景知识未复核。

---

### 0. 一页结论

**判定**:**Outcome C 为主、带一个小而真实的 Outcome B 残余。**

| | 判断 | 置信度 |
|---|---|---|
| **A 强**:存在小而可复用的类型化表达内核 | **不支持** | — |
| **B 中**:有小核,但变换族异质 | **部分支持**:有"按通道"的小复合演算,但缺陷通道的复合律各不相同,`lax` 缺陷的复合未解 | 低–中 |
| **C 工程**:有用的产物是类型化 IR/规约,不是新数学 | **主要判定** | 中 |
| **D 负**:既有范畴/类型论框架已完全覆盖 | **未被排除**(RT1、RT3 未决);对**语义核**基本成立 | — |

**一句话**:LA 之所以强,不是因为"线性",而是因为 $\mathbf{FinVect}_k$ 里一切"缺陷"恰好为零;MEL 要做的不是复制 LA,而是**把缺陷显式化、可声明、可复合**——这是一套**规约纪律**,其数学骨架几乎全是既有范畴论/MMT/契约理论。

**必须同时记住的三条限制**:
1. 压缩检验的判决实验**没有做**;现有证据由我自己分组、自己评价,且四走廊都终止于 LA。
2. 红队与被审对象同源。
3. 没有形式化、没有实现、没有 LLM 实验。

**建议下一步:C(先测更多走廊,盲测、含非 LA 终点)**,而不是自动进入 MEL v0.1 设计。

---

### 1. 方法与证据

* 阅读 prompt;约 12 次网页检索核实关键先例(MMT/MitM、institutions、MLIR、OpenMath/OMDoc、Mathlib 设计、Spivak 数据迁移、Markov 范畴、FEEC、抽象解释、Lawvere 度量范畴、自动形式化);其余先例凭背景知识并标 `(bg)`。
* **计算验证**:`experiments/sanity_checks.py`(numpy/scipy/sympy)重算了报告里引用的具体例子,全部通过,输出存于 `experiments/sanity_checks.out.txt`:
  * $\mathrm{RP}^2$:$H_*(\mathbb Z)=\mathbb Z,\mathbb Z/2,0$;$\dim H_*(\mathbb Q)=(1,0,0)$,$\dim H_*(\mathbb F_2)=(1,1,1)$;UCT 预测一致;
  * 随机游走归一化丢失行尺度;无向情形仅差一个全局标量;聚合缺陷 0.100;$\pi$-加权压缩保持聚合平稳律;
  * 同一矩阵在相似/合同下的不变量不同;有限元 $\mathrm{cond}(K)$ 基相关(32.2 → 2725.9)而广义特征值不变;
  * 误差复合界在 4 个步长上全部成立;下游 $L\sim1/h$ 把 $10^{-6}$ 放大到 $10^{-2}$;
  * 核对单调,但在 20/2000 随机情形中下游毁掉了上游保留的 observable。
* 没有做:机器形式化、检查器实现、LLM 实验、穷尽文献检索。

---

### 2. 核心发现

#### F1 — LA 的强来自八个性质的合取,且"缺陷消失"
P1 闭/自内含 · P2 加性/双积 · P3 阿贝尔 + **半单** · P4 刚性幺半闭 · P5 骨架化 + 小规范群 · P6 有限呈现/可判定 · P7 驯服分类 · P8 汇点位置(`01` §2)。
**[H] 缺陷消失论题**:在 $\mathbf{FinVect}_k$ 里,正合缺陷(Tor/Ext)、度量缺陷、信息缺陷、选择缺陷、假设缺陷几乎全为零;LA 的"优雅"是这一点的另一种说法。MEL 要面向缺陷**不为零**的世界。

#### F2 — 矩阵不是类型,(矩阵, 规范作用)才是类型
`Hom: PAQ⁻¹`、`Endo: PAP⁻¹`、`Bil: PᵀAP`、`Perm: ΠAΠᵀ`。对 Gram/Hessian 求特征值是**类型错误**,除非声明度量。这是"一切皆可矩阵化"为什么是 R0 的精确原因,并直接成为 MEL 坐标层的设计规则。

#### F3 — 可泛化的是方法论,不可泛化的是"运气"
* **可泛化(需弱化)**:呈现 + 规范群、泛性质定型、对偶(带自反性假设)、不变量绑定到声明的等价、迹、富足(grade)。
* **LA 专有**:每个子空间有补(半单)、双积、加性复合、统一可判定算法、完备规范型。
* 25 行分类见 `02`;`UNKNOWN` 两项被有意保留。

#### F4 — 最小核:Structure、Object、Transformation + 分级 Claim
Law、Observable、Equivalence、Approximation、Choice、Constraint、Information loss **全部可导出**;Cost 与 Witness 是附属元数据。唯一不可省的**索引**是 claim 的分级模式 `exact / graded / lax`(`04`)。

#### F5 — 基本实体是 Transformation(带缺陷声明的结构化对应),Map 只是特例
态射 = 全 + 单值 + 精确的对应。契约字段恰好对应对应偏离同构的方式:不全 → `requires`;不单值 → `choice`;不单射 → `loses`;不精确 → `graded`/`lax`(`06`)。**离散化、优化、模型选择、近似、性质桥都不是态射。**

#### F6 — 压缩:31 个变换 → 6 个机制 + 2 个模式 + 1 个契约成分
M0 视图 · **M1 呈现+规范** · **M2 泛构造** · **M3 对偶** · **M4 带分级的收缩** · **M5 假设下的重述**;PT1 生成元–半群、PT2 规范固定/分解;OBS 为契约成分;"离散化"被否决为原语(`12`)。
**但**:(i)分组是自评的;(ii)M0–M3 本身就是范畴论词汇,压缩可能与 MEL 无关;(iii)图-only 的走廊 C 会掩盖 `lax`——结论对实例选择敏感。

#### F7 — 复合:按通道的小演算 + 一个已知难角落
类型、假设(wp)、`exact`、`graded`(仿射幺半群 $(L,\varepsilon)$,结合律已证并数值验证)、信息(**按 observable**)、选择(群胚粘合)均有规则,并能**拒绝**五类具体非法复合;**`lax` 缺陷的复合(谱序列领域)没有演算**(`13`)。

#### F8 — 与既有框架:MEL ≈ MMT(结构层)+ 富足范畴/对应(变换层)+ 契约(复合层)
没有任何一块是新数学。可能的增量只在**打包**:缺陷账本、按 observable 复合、坐标类型带规范作用、证据状态一等化(`03`)。

#### F9 — 非空洞性是证据体系,不是语言性质
R0–R3 梯度 + 六道闸门;五个平凡化均有对应闸门,但**语言无法判定 claim 真假**(`14`)。

---

### 3. 逐题回答

**Q1 — 是什么使 LA 成为强表达层?**
架构上:闭 + 加性 + 阿贝尔半单 + 刚性幺半闭(P1–P4);骨架化使抽象/坐标二分干净(P5);有限呈现与可判定使自动化是统一算法(P6);驯服轨道使规范型存在(P7)。其中 P3、P6、P7 是"缺陷为零"的运气。(`01`)

**Q2 — 哪些性质真正可泛化?**
呈现 + 规范群;泛性质 + 弱化的正合性;对偶(自反性作假设);迹;"不变量是声明等价下的轨道函数";用 grade 记录误差。不可泛化:半单裂开、双积、加性、统一可判定、完备规范型。(`02`)

**Q3 — 最小 MEL 核?**
$\{\textsf{Structure},\textsf{Object},\textsf{Transformation}\}$ + 复合 + 分级 Claim($\textsf{exact}/\textsf{graded}/\textsf{lax}$)。语法骨架见 `04` §3.3,完整候选见 `16`。额外不可避免的只有 `lax` 缺陷对象与坐标类型的规范作用。

**Q4 — 正确的基本实体?**
**Structured Object(类型层)与 Transformation(操作层)。** Map 是特例;Interface 是契约的视图(即旧 MI);Bridge 是复合路径;Theory morphism 是类型层的 Transformation。(`06` §6)

**Q5 — Branch/Domain 属于语义核还是元数据?**
**元数据。** 命名空间 `ns` 与标签 `tags` 用于组织与路由,不参与类型相等。证据:走廊 A 中"微积分的导数"与"几何的切映射"去标签后是同一变换。(`05` §3.4、`08`)

**Q6 — 四个走廊能否不加临时字段地表达?**
**能,但需两项结构性扩展和一项参数扩展**:`lax` 模式(走廊 C 的 Tor)、带规范作用的坐标类型(A、D 的合同 vs 相似)、Γ 需包含序/germ/$(\varepsilon,\delta)$。四走廊都是我选的。(`12` §9)

**Q7 — 重复的跨越机制是否出现?多少个?**
**出现。** 较强证据:M1、M2、M3、M5;较弱:M4;模式:PT1、PT2;契约成分:OBS;否决:"离散化"。**盲测前诚实的区间是"5(±1)"**,不强行给数。(`12`)

**Q8 — 是否有复合演算的证据?**
**有部分证据。** 五个通道有可证或可检验的规则,并有五个被拒绝的具体复合;`lax` 缺陷复合、多值对应、规范群胚相容性未解。(`13`)

**Q9 — 什么防止 MEL 变成"任意函数 + 元数据"?**
闸门 G1(可证伪、非常值)、G2(自然性/一致性)、G3(杠杆见证)、G4(变异测试)、G5(非自由目标 + 封闭词汇)、G6(非退化域与分级),加证据状态。**局限**:Rice 型——语言不能判定 claim 真假,只能迫使证据外显。(`14`)

**Q10 — 最近的现有框架?MEL 是否只是其上的应用层?**
**MMT/Math-in-the-Middle(结构层)+ 富足(Lawvere/quantale)范畴与对应(变换层)+ assume–guarantee/wp(复合层)的并集;抽象解释与 L-reduction 是复合律的先例。** 是的,MEL 很可能只是其上的应用层;是否值得独立,取决于 RT3 的编码实验。(`03`)

**Q11 — 更自然的描述?**
**组合,以"规约语言/类型化 IR"为主**:
* *规约语言(specification language)*:契约字段 + 证据状态——主要价值;
* *类型化 IR / 互通 schema*:Structure 层(应直接落在 MMT);
* *小互操作演算*:按通道的复合规则(部分);
* *agent-native 协议*:降为**工程要求**(RT6);
* *新数学语言*:**不是**。

**Q12 — 项目下一步?** 见 §6。

---

### 4. 类比分级(MLIR 等)

| 说法 | 分级 | 说明 |
|---|---|---|
| "MEL 像多方言编译 IR" | `[A]` | 价值是工程性的;数学没有"最底层" |
| 方言 ↔ 理论族;operation/type/attribute ↔ 项/Structure/refinement | `[S]` | 对应可精确表述 |
| 复合 ↔ pass pipeline | `[S]` | 但 MEL 复合需**按 observable、按假设**检查 |
| lowering 保持语义 | `[A]` 且**失效** | 数学 lowering 常有损、带选择、带假设 |
| "归一化 = 规范固定" | `[S]` | 轨道截面;精确 |
| "聚合 ≡ Galerkin 压缩" | `[S]` | $\hat\pi\hat P=\hat\pi$ 已验证;同机制的断言不是已证定理 |
| 仿射误差幺半群结合 | `[T]` | 一行代数 |
| Kemeny–Snell 可 lump 条件、UCT、Céa、PF、Lax 等价 | `[T] (bg)` | 标准定理 |
| "缺陷账本统一一切" | `[H]` | 整齐过头,是警告信号(RT13) |

---

### 5. 风险与局限(汇总)

* **选择偏差**:四走廊都终止于 LA;图-only 的走廊 C 会隐藏 `lax`(`10`);E1/E2 控制与三个探针也是我选的。
* **同源评审**:RT11。
* **压缩可能与 MEL 无关**:M0–M3 就是范畴论词汇(`12` §6)。
* **`lax` 复合**与多值对应未解。
* **证据不均**:`(bg)` 占比大。
* **无实现/无形式化/无 LLM 实验。**
* 红队 10 项中:RT1、RT2 对语义核基本成立;RT3、RT5、RT10 未决;RT7 分裂;RT4、RT6 靠工程缓解(`17`)。

---

### 6. 项目下一步(Q12)

**选择:C — 先测更多走廊(盲测、含非 LA 终点)。** 不选 A。

**理由**:压缩是整个项目自设的存在判据(prompt §3、§16)。它是**信息价值最高、成本最低**的实验:不需要写软件,若失败则 MEL 抽象应被收缩为"规约文档"(Outcome D)或放弃;若成功,再进入 B/E/A 才有意义。

**步骤与判据(预注册)**

| 步 | 内容 | 成功判据 | 失败判据 |
|---|---|---|---|
| **C1(主)** | ≥6 条留出走廊,≥3 条终点非 LA;独立标注者只看 `06` §4 签名分类 | 覆盖 ≥70%;$\kappa\ge0.6$;新需求仅为**参数**而非字段 | >30% 需新机制;$\kappa<0.6$;按缺陷类型合并后独立机制 <3 |
| **B1(随后)** | 用 MMT + 自定义基础编码 `16` §10.2–10.5(RT3) | `graded/lax` 只需**写新理论**则合并入 MMT;需**改内核**则有残余 | — |
| **E1(随后)** | 用 Lean 4 形式化契约范畴片段与 5 个例子(RT1/RT2) | 成为现成库的 1–2 页实例 ⇒ 降为规约文档 | — |
| **A(最后)** | 仅当 C1 成功且 B1/E1 显示有残余 | — | — |

不选其余:
* **D 回到 Bridge Atlas**:无压缩即无理论,违背暂停理由。
* **F 放弃**:证据不足以放弃;`11` 的"成本不是规范不变量"、`10` 的"图-only 掩盖 `lax`"、`08` 的"类型 = 规范作用"都是**有价值、可独立使用**的发现。

---

### 7. 若只保留一个想法

> **LA 的方法论 = 呈现/语义分离 + 规范群 + 泛性质 + 缺陷为零。**
> **MEL = 在缺陷不为零的地方,把缺陷写进契约并让它们沿复合传播。**




---

## 附录 01 — 为什么线性代数是一个好的 Expression Layer

> 对应 Task 1 / Q1。把 LA 当作一种**语言/表示架构**来分析,而不是教科书摘要。
>
> **证据标签**(全套文档通用)
> `[T]` 已知定理/标准事实 · `[S]` 结构对应(可精确表述的对应,但非定理) · `[A]` 类比 · `[H]` 本研究的假设/论题
> 来源标签:`(web)` 本次检索核实过 · `(bg)` 凭背景知识、未在本次会话复核

---

### 0. 一句话结论

LA 之所以是强表达层,**不是因为"线性"本身,而是因为范畴 $\mathbf{FinVect}_k$ 同时满足八个彼此独立的性质(P1–P8)**,其中几乎每一条在别处都会失效。这八条合在一起的效果可以概括为一个论题:

> **[H] 缺陷消失论题**:在 $\mathbf{FinVect}_k$ 里,几乎所有"让数学表达变麻烦的缺陷"都恰好为零——不正合性(Tor/Ext)、不可裂、不可交换、信息损失的歧义、不可规范化的选择、对偶不自反、函数空间失控、不可判定。LA 的"优雅"是缺陷消失的另一种说法。
> MEL 要服务的是**缺陷不消失**的世界;因此它的任务不是"复制 LA",而是**把 LA 里隐形的缺陷变成显式、可声明、可复合的对象**。

这条论题贯穿全套文档。它**不是已知定理**,而是把已知的同调代数、数值分析、信息论、规范理论里的"缺陷"概念放在同一个账本里的一种组织方式。

---

### 1. 把 LA 当作语言来拆解:Task 1 的十个问题

| # | 问题 | 回答 |
|---|---|---|
| 1 | 原始对象类型? | 域 $k$ 上的(有限维)向量空间 $V$。等价地,在骨架范畴 $\mathbf{Mat}_k$ 里对象就是自然数 $n$。 |
| 2 | 原始态射? | 线性映射 $T:V\to W$。语言层面它既是抽象算子,也是(选定基后的)矩阵——这两层的分离是 LA 的核心(见 §3)。 |
| 3 | 基本 vs 派生? | **基本**:对象、态射、复合、恒等、零对象、$\oplus$、$\otimes$、幺元 $k$(标量是 $\mathrm{End}(k)$,**不是**额外原语)。**派生**:核、像、余核、商、对偶 $V^*=\mathrm{Hom}(V,k)$、内部 Hom、迹($=\mathrm{ev}\circ(\mathrm{id}\otimes f)\circ\mathrm{coev}$)、行列式($=\Lambda^{\mathrm{top}}$)、特征值(限制到一维子对象)。 |
| 4 | 什么使复合成立? | 范畴结构 + **复合双线性**:$(g_1+g_2)\circ f=g_1\circ f+g_2\circ f$。后者使 $\mathrm{End}(V)$ 成为环,从而有多项式演算、函数演算、谱。 |
| 5 | 什么使局部推理成立? | 线性映射**由生成元上的值唯一决定**(有限数据);直和分解 $V=\bigoplus V_i$ 使问题分块、叠加原理成立。 |
| 6 | 什么使规范化成立? | (a) 对象只被一个数 $\dim$ 分类;(b) 规范群 $GL_n$ 的轨道结构驯服;(c) 单个自同态 $\Leftrightarrow$ $k[x]$-模,PID 结构定理给出 Jordan/有理标准型;SVD 来自 $O(m)\times O(n)$ 的轨道。 |
| 7 | 什么使"保信息的换表示"成立? | 基变换是**同构**,且同构群 $GL(V)$ 作用在一切坐标形式上;不变量是该作用的轨道函数。 |
| 8 | 什么分离抽象与坐标? | 等价 $\mathbf{FinVect}_k\simeq\mathbf{Mat}_k$ + **选基 = 选择这个等价的一个"见证"**;基的全部任意性被封装在 $GL$ 里。 |
| 9 | 什么使自动化容易? | 态射有限呈现、等式可判定、存在统一算法(消元、SVD),复杂度多项式。 |
| 10 | 哪些是线性的人为产物? | 见 §2 的 P3、P5–P7 与 `02-la-specific-vs-generalizable.md`。 |

---

### 2. $\mathbf{FinVect}_k$ 的八个性质

| ID | 性质(精确表述) | 它"买到"什么 | 失去后的典型后果 |
|---|---|---|---|
| **P1** | **自内含/闭**:$\mathrm{Hom}(V,W)$ 仍是向量空间,复合双线性 `[T]` | "映射也是数据":可加、可数乘、可微、可构成环 | $C^\infty(M,N)$ 是无穷维 Fréchet 流形;$\mathbf{Meas}$ 不是笛卡尔闭的(Aumann),所以才需要 quasi-Borel 空间 `(bg)` |
| **P2** | **加性/双积**:$V\oplus W$ 同时是积与余积 `[T]` | 矩阵 = 和与和之间的映射,分块演算 | $\mathbf{Set}$、$\mathbf{Grp}$、$\mathbf{Top}$ 里积≠余积,没有"分块矩阵" |
| **P3** | **阿贝尔 + 半单**:核/余核/像存在,**且一切短正合列裂开** `[T]` | 子对象 ↔ 商对象可互换(取补),$\mathrm{Tor}=\mathrm{Ext}=0$,无挠 | $R$-模有挠、不可裂扩张;同调系数变换产生 Tor(§4) |
| **P4** | **刚性对称幺半闭**(有限维):$\otimes$、对偶、迹、维数内蕴 `[T]` | 张量指标演算 = 图演算;$\dim V=\mathrm{tr}(\mathrm{id}_V)$ | 无穷维里 $V\ne V^{**}$;对偶要换成拓扑对偶,自反性变成**假设** |
| **P5** | **骨架化 + 小规范群**:同构类 ↔ $\mathbb N$;$\mathbf{FinVect}\simeq\mathbf{Mat}$ | 坐标化永远存在;选择的任意性 = $GL_n$ | 只有**自由**模有基;流形需要图册+转移函数(上闭链);三角剖分不唯一 |
| **P6** | **有限呈现 + 可判定** | 等式、秩、解空间可机械计算;统一算法 | 群的字问题不可判定;一般拓扑空间的同胚问题不可判定 `(bg)` |
| **P7** | **驯服的分类**:单个算子的轨道有标准型 `[T]` | 规范型作为"完备不变量 + 截面" | 两个不交换算子的同时相似分类是 **wild** 的 `(bg)`;一般模范畴无有限分类 |
| **P8** | **汇点位置**:大量函子以 Vect 为目标 | 许多结构"降落"到 LA 才可计算 | (这不是 LA 的内部设计,见 §5) |

注意 P3 才是 LA"毫不费力"的深层原因:**在域上,每个对象既射影又内射**,所以所有"不正合/不可裂"的现象都被消灭了。

---

### 3. 关键观察 1:矩阵不是类型,(矩阵, 规范作用)才是类型

"一切皆可矩阵化"之所以空洞(R0),恰因**矩阵的类型信息不在形状里,而在规范作用里**:

| 抽象对象 | 坐标形式 | 规范变换 | 完备/典型不变量 |
|---|---|---|---|
| $\mathrm{Hom}(V,W)$ | $A\in\mathbb{M}_{m\times n}$ | $A\mapsto PAQ^{-1}$ | 秩(完备) |
| $\mathrm{End}(V)$ | $A\in\mathbb{M}_{n\times n}$ | $A\mapsto PAP^{-1}$ | 谱、Jordan 型 |
| $\mathrm{Bil}(V)$ | Gram/Hessian $G$ | $G\mapsto P^{\!\top}GP$(**合同**) | 惯性指数(Sylvester) |
| 图的邻接 | $A$ | $A\mapsto \Pi A\Pi^{\!\top}$($\Pi$ 置换) | 图同构不变量(谱是其中之一) |

`[T]` 本仓库 `experiments/sanity_checks.py`(S3)实际算了一遍:同一个随机矩阵,在相似下特征值不变,在合同下**不**不变,只有惯性 $(3,3)$ 不变。把双线性型当自同态去算"特征值"是**无意义的**——除非声明了度量(把规范群缩到 $O(n)$,合同与相似才重合)。这是真实的数学错误来源(例:"Hessian 的特征值"需要黎曼度量)。

**对 MEL 的含义**:坐标层的类型必须携带**规范作用**,而不只是 `Mat[m,n]`。这直接支撑 `16-mel-v0.1-candidate.md` 里 `coord` 的设计。

---

### 4. 关键观察 2:缺陷账本

> **[H]** 下表是"缺陷消失论题"的展开。右两栏是已有理论——说明这里没有新数学,只有新的**组织方式**。

| 缺陷类型 | 在 $\mathbf{FinVect}_k$ 中 | 在别处的形态 | 已有理论(`(bg)` 除非另注) |
|---|---|---|---|
| **正合缺陷** | 全部消失($\mathrm{Tor}=\mathrm{Ext}=0$) | 系数变换 $\mathbb Z\to\mathbb F_2$ 产生 $\mathrm{Tor}$;$\mathrm{RP}^2$ 中 $H_2(\,;\mathbb F_2)\neq H_2(\,;\mathbb Z)\otimes\mathbb F_2$ | 导出函子、谱序列 |
| **度量/序缺陷** | 无(精确算术) | 离散化误差、弱对偶间隙 | 数值分析、Lawvere 度量范畴 |
| **信息缺陷** | 同构保信息;非同构有核 | 量化、聚合、商、遗忘 | 信息论(数据处理不等式)、抽象解释 |
| **选择缺陷** | 基的选择被 $GL$ 吸收 | 法向量取向、归一化、网格、系数环 | 规范理论、torsor、descent |
| **假设缺陷** | 少(域上几乎无条件) | Perron–Frobenius 需不可约;Lax–Milgram 需强制性 | Hoare 前置条件、weakest precondition |

实测例子(均在 `experiments/sanity_checks.py` 中重算):

* $\mathrm{RP}^2$ 六顶点三角剖分:$H_*(\,;\mathbb Q)=(1,0,0)$,$H_*(\,;\mathbb F_2)=(1,1,1)$,Smith 标准型给出 $H_1(\mathbb Z)\cong\mathbb Z/2$;万有系数定理的预测与直接计算一致。
* 随机游走归一化 $P=D^{-1}W$:对有向图遗忘行尺度 $W\sim\Lambda W$;对无向图可由 $(P,\pi)$ 恢复 $W$,**仅差一个全局标量**。

---

### 5. 关键观察 3:LA 同时是"语言"与"汇点",必须分开

项目早期把 LA 当 IR 失败,原因之一是混淆了这两种角色:

* **语言角色**(P1–P7):LA 内部的组织方式——本研究要学的东西。
* **汇点角色**(P8):许多函子的目标是 LA。这是**位置**而非设计。

经检视,通往 LA 的函子大致来自四种**线性化机制** `[S]`:

| 机制 | 例 | 方向 | 保持 | 丢失 |
|---|---|---|---|---|
| **Free**(左伴随) | $X\mapsto k[X]$;$X\mapsto C_*(X)$;分布单子 | 协变 | 余极限、泛性质 | 线性结构对 $X$ 本无意义时是**空洞**的(R0 陷阱) |
| **函数代数/Koopman**(对偶) | $T\mapsto T^*$ 作用于 $\mathrm{Fun}(X)$;$L^2$ | 反变 | 复合(反序) | 非线性被推入无穷维 |
| **Jet/切空间**(局部) | $f\mapsto df_p$ | 协变,局部 | 复合(链式法则) | 一阶以上信息 |
| **表示**(群作用) | $G\to GL(V)$ | 协变 | 群结构 | 取决于 $V$ 的选择 |

结论:**LA 的"汇点地位"来自这四种机制的存在,而不是 LA 自己的设计优越。** 这条区分与项目的第一原则一致:*Learn from LA's design, not from its dominance.*

---

### 6. LA Expression Design Principles

> **LA Expression Design Principles**(精炼版;分类见 `02-…`)

| ID | 原则 | 在 LA 中的体现 |
|---|---|---|
| **DP1 闭性** | 构造的结果与输入同类 | $\mathrm{Hom}(V,W)$ 仍是向量空间 |
| **DP2 声明式保持律** | 结构 = 态射必须保持的东西 | 线性律定义了范畴本身 |
| **DP3 少生成、多派生** | 少数生成构造 + 泛性质 | $\oplus,\otimes,\mathrm{Hom}$,子/商/核 |
| **DP4 泛性质定型** | 构造由泛性质唯一确定到同构 | 选择只出现在**显式的基**里 |
| **DP5 呈现/语义分离 + 规范群** | 坐标是语义的呈现,换呈现 = 群作用 | $[T]_{\mathcal B,\mathcal C}$ 与 $GL$ |
| **DP6 不变量即 observable** | 可观测量 = 规范群的轨道函数 | 秩、迹、谱、惯性 |
| **DP7 分解式局部推理** | 沿直和/张量分解问题 | 分块、叠加 |
| **DP8 缺陷显式或为零** | 构造之间的相互作用由正合性刻画 | 域上缺陷恒为零 |
| **DP9 可计算的呈现** | 有限呈现 + 可判定等式 | Gauss 消元、SVD |
| **DP10 线性化汇点** | 许多函子降落于此 | 导数、自由、表示、Koopman |

其中 **DP8 与 DP9 是"运气"成分**(来自域上的半单性与有限维),DP1–DP7 是**方法论成分**,是本研究认为可迁移的部分。

---

### 7. 对 Q1 的回答

> LA 是强表达层,因为它在**架构上**同时具备:(i)闭、加性、阿贝尔半单、刚性幺半闭的范畴结构(P1–P4);(ii)骨架化 + 小规范群,使"抽象/坐标"二分干净(P5);(iii)有限呈现与可判定等式,使自动化成为统一算法(P6);(iv)驯服的轨道分类,使规范型存在(P7)。
> 这些性质中,**P3、P6、P7 是"缺陷为零"的运气**,不应被要求迁移;**P5(呈现 + 规范群)、P4 中的"不变量/迹"、P1 的"态射是数据"、泛性质定型(DP4)** 是可以带到非线性世界、只需弱化的方法论。

### 8. 证据状态与局限

* P1–P7 是标准范畴代数事实,`(bg)`;**未做**机器形式化。
* "缺陷消失论题"是本研究的**组织性假设**。它与导出函子、数值分析等并不冲突,但"各种缺陷能否纳入同一个代数"是开放问题(见 `17-red-team-review.md` RT1/RT7)。
* §3 的 `PAQ⁻¹ / PAP⁻¹ / PᵀAP` 分类是教科书内容;新的只是把它提升为"类型必须携带规范作用"的设计规则。


---

## 附录 02 — LA 专有特征 vs 可泛化特征

> 对应 Task 2 / Q2。标签:`LA-SPECIFIC` / `GENERALIZABLE` / `GENERALIZABLE-WITH-WEAKENING (GWW)` / `UNKNOWN`。
> 证据标签见 `01-…`。若无特别说明,理由为 `(bg)` 的标准数学。

分类时区分**两件事**:(a) 该特征的**具体数学内容**;(b) 该特征在语言设计中扮演的**角色**。很多特征(如"线性律")内容是 LA 专有的,但角色可泛化。

---

### 1. 主表

| # | 特征 | 标签 | 理由 | 弱化形式 / 替代 |
|---|---|---|---|---|
| 1 | 标量线性律 $T(ax+by)=aTx+bTy$ | **内容 LA-SPECIFIC;角色 GENERALIZABLE** | 角色 = "由理论声明的保持律",对任何代数理论(群、环、格、Lie 代数…)的同态都成立 | 保持律作为**可声明的 `preserves` 字段** |
| 2 | 带类型的映射 | GENERALIZABLE | 范畴的定义本身 | — |
| 3 | 复合与恒等 | GENERALIZABLE | 同上 | — |
| 4 | 复合双线性(加性) | LA-SPECIFIC → GWW | 来自 Ab-富足;使 $\mathrm{End}(V)$ 成环 | 对其他幺半范畴富足:半环上的矩阵(Boolean、tropical、$\mathbb R_{\ge0}$) |
| 5 | Hom 作为同类对象(闭性) | GWW | 自闭;笛卡尔闭/幺半闭是推广 | $\mathbf{Meas}$ 不闭 → quasi-Borel;光滑映射空间需 diffeological/convenient 设定 `(bg)` |
| 6 | 子对象 | GENERALIZABLE | 单态射/嵌入 | — |
| 7 | 每个子空间有补(裂开) | **LA-SPECIFIC** | 半单性;模、群、拓扑中通常失败 | 替代:短正合列 + $\mathrm{Ext}$ 作为缺陷 |
| 8 | 商 $V/U$ | GWW | 余等化子/余核 | 群商要求正规;拓扑商可能非 Hausdorff |
| 9 | 核/像/正合性 | GWW | 阿贝尔范畴;非阿贝尔处退为 Mal'cev/同余 | 正合范畴;导出函子刻画缺陷 |
| 10 | 直和 = 双积 | **LA-SPECIFIC** | 积≠余积 在多数范畴 | 分别使用积、余积;半加性范畴 |
| 11 | 对偶 $V^*$ | GWW | 反变函子;自反性只在有限维成立 | Pontryagin、Stone、Gelfand、Legendre–Fenchel;**自反性作为假设** |
| 12 | 张量积 | GWW | 幺半结构;**不唯一**(图有 Cartesian/tensor/strong 等多种积) | 多范畴(operad)刻画"多输入映射" |
| 13 | 迹/维数 | GWW | 迹幺半范畴(Joyal–Street–Verity)`(bg)` | Euler 示性数、Lefschetz 数 |
| 14 | 行列式 | LA-SPECIFIC(基本) | 依赖 $\Lambda^{\mathrm{top}}$ 与一维性 | Fredholm 行列式、K 理论 det;弱化后意义变化 |
| 15 | 谱 | GWW | Banach 代数/交换代数的 Spec | 谱 ≠ 特征值集合;需声明空间与范数 |
| 16 | 不变量 = 规范作用的轨道函数 | GENERALIZABLE | 对任何群(oid)作用成立 | 把"等价"从 $GL$ 换成声明的等价 |
| 17 | 规范型(Jordan、SVD) | **强度 LA-SPECIFIC;角色 GWW** | 来自 PID 结构定理 + 驯服轨道;一般分类 wild | **intermediate typed form**(见 `07-…`) |
| 18 | 基变换/坐标 | GWW | 只有自由模有基 | 呈现(generators + relations)、图册 + 上闭链 |
| 19 | 抽象/坐标分离 | **GENERALIZABLE**(作为方法论) | 语义对象 vs 其呈现 + 规范群 | 但"坐标处可判定"是 LA-SPECIFIC |
| 20 | 叠加原理(全局) | LA-SPECIFIC → GWW | 全局叠加依赖线性 | 局部线性化、层的局部性、沿 $\oplus/\otimes$ 分解 |
| 21 | 可判定性与统一算法 | **LA-SPECIFIC**(强);GWW(部分) | 消元 = 域上算术 | Gröbner、Smith/Hermite(PID)、受限的可判定片段 |
| 22 | 内积/正交投影 | GWW | 需要额外双线性结构 | 投影 = 幂等元;Hilbert 复形;条件期望(见 `09-…`、`11-…`) |
| 23 | 线性化(导数/Jet) | GENERALIZABLE(作为模式) | "用更简单的类型化目标作逼近,并声明误差" | 角色在 MEL 中 = `graded` claim |
| 24 | 汇点位置 | **UNKNOWN** | 位置是否可以被"设计"而不是"碰巧"? | 开放:是否存在 LA 以外同时给出 闭性+规范+规范型 的汇点? |
| 25 | 缺陷能否统一为一个代数 | **UNKNOWN** | 不同缺陷的复合律异质(见 `13-…`) | 开放 |

(行 24、25 是**有意保留的 UNKNOWN**——这是诚实的状态,不是遗漏。)

---

### 2. 统计与读法

| 标签 | 行数 | 备注 |
|---|---|---|
| GENERALIZABLE(含"角色可泛化") | 2, 3, 6, 16, 19, 23, 以及 1 的角色 | 共 7 |
| GWW | 4, 5, 8, 9, 11, 12, 13, 15, 17(角色), 18, 20, 21(部分), 22 | 共 13 |
| LA-SPECIFIC(强度/内容) | 7, 10, 14, 17(强度), 21(强) | 共 5 |
| UNKNOWN | 24, 25 | 共 2 |

> **读法**:这是人工分类,不是可复现测量;同一行常有"内容/角色"两层,所以计数会重叠。重要的不是数字,而是**哪些被判为 LA-SPECIFIC**——它们都对应 `01-…` 的 P3/P6/P7(半单、可判定、驯服分类),即**"缺陷为零"的运气**。

---

### 3. 最关键的三条泛化(带降级)

1. **呈现 + 规范群(行 18、19、16)**:把"基"换成"呈现",把"$GL$"换成"该呈现的同构群(oid)",把"矩阵"换成"携带规范作用的坐标形式"。——它在**全部四个走廊的最后一步**重复出现(`12-…`),是本研究最强的可迁移原则。
2. **泛性质定型(DP4)+ 弱化的正合性(行 8、9、13)**:构造由泛性质确定,若不正合则把**缺陷**写进契约(`lax` 模式)。
3. **不变量绑定到声明的等价(行 16、23)**:observable 不是"随便一个性质",而是"对某个声明的等价不变的映射"。

### 4. 不应指望迁移的东西

* 全局叠加原理、复合的加性、子对象的补、双积、统一可判定算法、完备的规范型。
* 这些在非线性里不是"弱一点还能用",而是**根本机制不同**。MEL 不应包含任何依赖它们的默认假设;所有这类依赖必须作为 `requires` 显式声明。

### 5. 对核心设计的约束

| 由此得到的设计规则 | 落实在 |
|---|---|
| 保持律必须是**声明字段**,不是隐含的"线性" | `04`、`16` 的 `claims` |
| 复合不默认双线性/加性 | `13` 复合规则 |
| 不假设规范型存在;提供 "intermediate typed form" | `07` |
| 对偶、投影、迹的自反性/幂等性/可迹性都以假设形式出现 | `05` 的 refinement、`16` 的 `requires` |
| "坐标层"可判定、"抽象层"不一定 | `16` 的 coordinate layer |


---

## 附录 03 — 与既有框架的比较

> 对应 Task 20 / Q10。**不要因术语不同而声称新颖。**
> 来源标签:`(web)` 本次会话检索核实;`(bg)` 背景知识、未复核。URL 仅列出本次检索实际返回的页面。

### 0. 结论先行

* **MEL 的类型/结构层**基本就是 **MMT 的理论 + view(理论态射)**,外加 Mathlib 式的"打包层级"经验。
* **MEL 的变换层**的数学骨架是**富足(quantale/Lawvere)范畴 / double category / 对应(relation, span)**。
* **复合律**与 **assume–guarantee 契约、weakest precondition、近似保持归约(L-reduction)、抽象解释的 Galois 连接** 同构或近似同构。
* 因此对 Q10:**MEL 更像应用于上述框架之上的一层规约纪律,而不是新的数学理论**(与 Outcome B/C 一致,见 `final-…`)。
* 真正"不在已有框架里被打包"的只有**组合方式**:(i)每个变换必须携带**缺陷账本**(假设/选择/信息/度量/正合);(ii)复合**按 observable 检查**;(iii)坐标层类型携带**规范作用**;(iv)证据状态(witness)是一等字段。每一块单独看都有先例,**打包本身是否有价值是经验问题**。

---

### 1. 框架逐项

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

### 2. "它已经解决什么" 与 "MEL 可能增加什么" 的诚实对照

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

### 3. 对 Q10 的回答

> **最近的现有框架是"MMT/Math-in-the-Middle(结构层)+ 富足范畴/对应(变换层)+ assume–guarantee 契约(复合层)"的并集。**
> MEL 确实可以只是这些之上的一层应用规约。**是否值得作为独立产物**取决于一个经验问题:缺陷账本 + 按 observable 复合检查 是否能在 MMT 里**自然**表达而不扩展其基础(这是 `17` RT3 的判决实验)。

### 4. 未做的事

* 未穷尽检索 2024–2026 的 LLM + 形式数学中间表示文献。本次检索命中过自动形式化综述与"relaxed natural formal language"一类工作(`arXiv:2505.23486`、`arXiv:2606.24443`,仅搜索命中,**未阅读**),不据此下任何结论。
* 未核对 MMT 当前的 view/metadata 机制能否直接承载 grade/lax 结构。

### 5. 来源(本次检索返回)

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


---

## 附录 04 — MEL 核心候选:最小核应该是什么

> 对应 Task 3 / Q3 / Q4(部分)。纪律:**对每个候选原语问"能否由其余导出?"**,不机械罗列。
> 标签见 `01-…`。

### 0. 结论

> **最小语义核 = {Structure, Object, Transformation} + 复合规则 + 一个"分级等式"(graded claim)。**
> Law、Observable、Equivalence、Approximation、Choice、Constraint、Information-loss 全部可导出;Cost、Witness 是附属元数据,不进语义核。
> 语法上为了**可检视性**,把 `Claim` 提升为一等语法类别(语义上可由"复合间的等式/不等式"导出),把 `choice`、`recovers`、`loses` 做成命名字段(语法糖,不是原语)。

与 prompt 里提出的 $\{$Object, Structure, Map, Law, Observable$\}$ + 复合相比:

* **Map → Transformation**:Map 只覆盖"全函数 + 单值 + 精确"的特例(见 `06`)。
* **Law 与 Observable 被降为派生**。
* 额外需要且不可省的只有**一个索引**:claim 的**分级模式** Γ(否则近似会被隐藏)。

---

### 1. 原语审问表

| 候选 | 能否由其余导出? | 导出方式 | 决定 |
|---|---|---|---|
| **Structure** | 否 | 类型层:理论引用 + 参数 + 精化 | **原语** |
| **Object** | 否(但与 Structure 是同一实体的类型/项两层) | 项层:Structure 的居民 | **原语** |
| **Transformation** | 否 | 带声明缺陷的结构化**对应**(见 `06`) | **原语** |
| Map(态射) | **是** | Transformation 中"全 + 单值 + 精确"的特例 | 派生(特例) |
| Constraint / Assumption | **是** | Structure 的 refinement 谓词;或 Transformation 的 `requires` | 派生 |
| Law | **是**(语义) | 两个复合之间的等式/不等式 = `Claim` | 派生;语法保留 `Claim` |
| Observable | **是** | 以"值型 Structure"为目标、且对某声明的等价不变的 Transformation | 派生 |
| Equivalence(for purpose) | **是** | $\ker q=\{(x,x')\mid q(x)=q(x')\}$;对变换 = 观测等价 | 派生 |
| Approximation | **是** | `graded` 模式的 Claim | 派生 |
| Choice | **是** | 参数 Object,其类型是"选择群胚"(torsor) | 派生;**因四走廊全出现,做语法糖** |
| Information loss | **是** | 变换的核对 $\ker T$,相对某 observable | 派生(声明字段 `loses`) |
| **Composition** | 否 | 范畴运算 | **原语(规则,非实体)** |
| **Grade Γ** | 否 | Claim 的索引:quantale / 富足基(见下) | **参数,非实体** |
| Witness | 否(影响信任,不影响语义) | 证据状态 | 附属元数据 |
| Cost | 否(但与规范**不**相容,见 `08–11`) | 坐标层的标注 | 附属 |
| Variance | **是** | 类型的一部分(协/反变) | 类型字段 |
| Gauge | **是** | 呈现类型的自同构群胚 | 类型字段 |

---

### 2. 三个候选核的比较

| 核 | 内容 | 表达力(四走廊) | 问题 |
|---|---|---|---|
| **Core-5**(prompt 的猜测) | Object, Structure, Map, Law, Observable + 复合 | 走廊 A 的 $d f_p$ ✓;B 的归一化(带选择)✗;C 的系数变换缺陷 ✗;D 的 Galerkin 误差 ✗ | Map 排斥非态射;Law 无分级则隐藏误差 |
| **Core-3+**(推荐) | Structure, Object, Transformation + 复合 + graded Claim | 四走廊 ✓,**但**需三项扩展:`lax` 模式、坐标类型带规范作用、局部性(germ)qualifier(见 §5) | 对应(correspondence)过宽 → 必须配 `14` 的非空洞闸门 |
| **Core-max** | 把 prompt 列的 10 个候选全作原语 | ✓ | 冗余;每个字段都可由别的导出;违反"尽量小" |

---

### 3. 推荐核的形式候选

#### 3.1 语义层

* **Structure** $S$:理论 $\mathsf{Th}$(签名 + 公理,`(bg)` Lawvere/MMT 式)、参数 $\vec p$、精化 $\varphi$。
* **Object** $x:S$:$S$ 的居民。
* **Transformation** $T:S\Rightarrow S'$:结构化对应 $R_T\subseteq S\times S'$ + 构造 $c$ + 契约 $\mathcal C_T$。
* **Claim**:两个复合表达式 $e_1,e_2$ 之间在**模式** $m\in\{\textsf{exact},\textsf{graded},\textsf{lax}\}$ 下的陈述:

| 模式 | 数学含义 | 例 |
|---|---|---|
| `exact` | 等式(恒等型) | $\partial\partial=0$;链式法则 |
| `graded[Γ]` | 取值于 Γ 的"近似相等" $e_1\approx_{v}e_2$;Γ 对 Bool、$([0,\infty],+)$、序间隙可取为交换 quantale(Lawvere),**germ 与 $(\varepsilon,\delta)$ 不是现成的 quantale,需另行定义其复合**(见 `13` §2.4–2.5) | Céa 引理;离散化误差;弱对偶间隙 |
| `lax` | 典范**比较映射** $\kappa:F(x)\to G(x)$,其(余)核/锥为**缺陷对象**,并给出缺陷为零的条件 | $H_n(C)\otimes k\to H_n(C\otimes k)$,缺陷 = $\mathrm{Tor}$;强解 $\subset$ 弱解 |

> `lax` 模式不是量化的度量,而是**对象值**的缺陷。这是四走廊压力测试里**唯一迫使核扩张**的发现(走廊 C 的 UCT;走廊 D 的强/弱解;控制走廊 E2 的弱对偶)。

#### 3.2 派生定义(无需新原语)

```
Obs(q)       := tr q : S ⇒ V          -- V 为值型 Structure;附 claim "q 在 ≈ 下不变"
Equiv_q      := ker q                  -- x ≈_q x′  ⇔  q x = q x′
Approx       := claim graded …
Choice(c:G)  := 参数 Object,类型 Torsor(G);G 为声明的规范群(oid)
Loss(T; q)   := q 是否经 T 恢复:  ∃ q̃ . q = q̃ ∘ T
Constraint   := Structure 的 where φ  |  Transformation 的 requires φ
```

#### 3.3 紧凑语法骨架(完整版见 `16`)

```
Structure     S ::= Th⟨params⟩ [where φ]
Object        o ::= x : S  |  (o,…,o)  |  T(o)
Transformation T ::= tr n : S ⇒ S′ {
                       requires φ
                       choice   (c : C [gauge G])*
                       claims   (mode  e ≈ e′  [Γ]  [under φ]  [witness w])*
                       loses    ρ
                       recovers q*
                     }
Composition   T₂ ∘ T₁   定义见 13
```

---

### 4. 为什么 Claim 在语义上可导出、语法上仍要保留

* 在依赖类型论里,`exact` claim = 恒等类型,`graded` = 值取 Γ 的相等度,`lax` = 一个带比较映射的 2-胞腔;**语义上无需新原语**。
* 但一个面向 agent/审阅者的契约语言必须让**契约可被检视而不必运行证明**。因此保留 `Claim` 作为一等语法类别,并带 `witness`(证据状态)。
* 这与 RT2("MEL 就是依赖类型论")的回应一致:语义被依赖类型论覆盖,**渐进(gradual)的、可含非形式见证的前端**才是 MEL 的存在理由。

### 5. 对四个走廊的覆盖与压力点

| 走廊 | 核是否够用 | 需要的扩展(未在 prompt 的候选里) |
|---|---|---|
| A 局部线性化 | ✓ | **局部性**(germ at $p$)作为 `requires` 的限定;坐标类型的**规范作用**(Hom: $PAQ^{-1}$;Bil: $P^{\!\top}GP$) |
| B 离散/随机/动力 | ✓ | Cone/正性是 LA 之外的**额外结构**(Perron–Frobenius 是锥定理);假设向后传播(wp) |
| C 拓扑/代数 | ✓ | **`lax` 模式**(Tor 缺陷);系数环必须显式 |
| D 解析/变分/有限 | ✓ | `graded`(Céa);混合 exact(结构)+ graded(状态);成本与规范**不**相容 |

结论:**无需新增"字段"**,但需要 `lax` 模式与"带规范作用的坐标类型"两项**结构性**扩展——这比"字段不够"更诚实地说明了核的边界。

### 6. 候选原语的"原语纪律"检验

按 prompt §17,候选原语须满足:重复出现、稳定类型、有意义的复合律、非平凡保持语义、解释/计算价值。

| 实体 | 重复出现 | 稳定类型 | 复合律 | 非平凡保持 | 价值 | 结论 |
|---|---|---|---|---|---|---|
| Structure | ✓ | ✓ | (view 的复合) | ✓ | ✓ | 原语 |
| Object | ✓ | ✓ | — | — | ✓ | 原语 |
| Transformation | ✓ | ✓(S⇒S′) | ✓(见 `13`) | ✓ | ✓ | 原语 |
| Choice | 4/4 走廊 | ✓ | 群胚粘合 | ✓ | ✓ | **语法糖**(可导出,但太常见) |
| Observable | 4/4 | ✓ | 按 observable 的复合检查 | ✓ | ✓ | **派生**(契约成分) |
| Cost | 2/4 | ✗(与规范不相容) | 弱 | ✗ | 中 | **附属** |

### 7. 对 Q3 的回答

> **最小可信核**:$\{\textsf{Structure},\textsf{Object},\textsf{Transformation}\}$ + 复合 + 分级 Claim($\textsf{exact}/\textsf{graded}/\textsf{lax}$)。
> 形式语法见 §3.3 与 `16`。
> 关于"是否还有不可避免的概念":**有两个**——(i)`lax` 缺陷对象,(ii)坐标类型的规范作用;二者都已在上面入核或入类型系统。**没有发现需要独立原语的 Constraint、Law、Observable、Equivalence、Approximation。**

### 8. 局限

* "可导出"是在**语义层**成立的;在**可用性**层(agent 能否稳定产出、人能否检视)它们仍需命名字段,这是工程判断而非数学定理。
* 核是否"够小"取决于走廊选择(见 `12` 的选择偏差讨论)。


---

## 附录 05 — MEL 类型系统

> 对应 Task 4。目标:避免纯名义类型(`Graph`、`Probability`、`Topology`),也避免完全结构化到不可读;结果必须能被 LLM agent 稳定使用。
> 标签见 `01-…`。

### 0. 结论

> **推荐"混合方案":以理论引用为索引的结构类型 + 名义句柄 + 精化谓词 + 带规范作用的坐标类型。**
> 类型检查器**只判定句法/结构相容性**(理论包含路径存在、参数可合一、规范可桥接);一切语义性命题(精化蕴含、claim 成立)作为**证明义务**输出,并带**见证状态**。
> **分支名(Graph/Probability/…)是命名空间与路由元数据,不进入类型。**(回答 Q5)

---

### 1. 设计要求

| ID | 要求 | 来源 |
|---|---|---|
| T1 | 类型描述"是什么结构",而不是"来自哪门学科" | prompt §8 |
| T2 | 类型足以**拒绝非法复合**(见 §6) | prompt §24 |
| T3 | 不能冗长到无法书写/阅读 | prompt Task 4 |
| T4 | 对 LLM 友好:封闭词汇、稳定标识、字段少 | prompt §19 |
| T5 | 精化/假设可表达,但**不要求类型检查器能判定它们** | Rice 式限制 |
| T6 | 坐标形式的类型携带**规范作用**(`01` §3) | 本研究 |

---

### 2. 方案对比

| 方案 | 精度 | 冗长度 | LLM 友好 | 主要失败模式 | 判断 |
|---|---|---|---|---|---|
| **名义类型** | 低 | 低 | 高 | `Graph`/`WeightedGraph`/`Multigraph` 的边界随意;学科标签伪装成类型 | 只作**句柄**,不作定义 |
| **结构类型**(载体+操作+关系…) | 高 | **极高** | 低 | 组合爆炸;同一结构有多种等价呈现 | 作为定义,但需名义别名折叠 |
| **依赖类型** | 最高 | 高 | 中 | 需完整证明;数值/引用类见证无处安放 | 作为**后端**(Lean),不作前端 |
| **Typeclass/trait**(Lean/Mathlib) | 高 | 中 | 中高 | 实例解析的"菱形"冲突;打包 vs 非打包的取舍 `(web: Mathlib 设计文档)` | **采用**:理论包含图 ≈ 类层级 |
| **精化类型** | 中高 | 低 | **高** | 精化蕴含不可判定 | **采用**,但蕴含只作证明义务 |
| **Traits/capabilities** | 中 | 低 | 高 | 能力无公理,易空洞 | 作**标签**(`finite-dim`、`reflexive`) |
| **代数层级** | 高 | 中 | 中 | 层级维护成本(Mathlib 经验:仅在"有真实数学要做"或显著简化时才引入新类)`(web)` | 采用其**准入准则** |
| **范畴型类型**(对象 ∈ 某范畴) | 中高 | 低 | 中高 | 范畴选择本身是隐含假设 | **采用**:类型 = (范畴/理论, 对象数据) |
| **混合**(推荐) | 高 | 中 | 高 | 需维护**理论库与包含图** | **推荐** |

---

### 3. 推荐类型

#### 3.1 三层

```
L1 理论层      Th        ∈ TheoryLib            -- MMT 式理论;含包含图 (Hilb ⊂ Normed ⊂ Metric ⊂ Top …)
L2 实例层      S = Th⟨params⟩ [where φ] [var]   -- 参数、精化、变性(协/反变)
L3 坐标层      Coord[A, shape]                  -- 坐标形式;A = 规范作用(见 §3.3)
```

#### 3.2 类型的完整形式

$$S ::= \mathsf{Th}\langle\vec p\rangle\ [\textbf{where}\ \varphi]\ [\textbf{var}\ \pm]$$

* `Th`:对**理论库**的引用(可有别名,如 `Stoch ≜ MarkovKernel_fin`)。
* `params`:依赖类型**仅用于参数**(维数 $n$、环/域 $R,k$、容差 $\varepsilon$),保持轻量。
* `where φ`:精化谓词(行和为 1、强制性 $\alpha>0$、有限维…)。
* `var`:协变/反变(对偶、拉回需要)。

#### 3.3 坐标类型携带规范作用

```
Coord[Hom ,(m,n),k]      规范: A ↦ P A Q⁻¹        不变量: rank
Coord[Endo,(n),k]        规范: A ↦ P A P⁻¹        不变量: spectrum, Jordan
Coord[Bil ,(n),k]        规范: A ↦ Pᵀ A P         不变量: inertia (对称, ℝ)
Coord[Perm,(n)]          规范: A ↦ Π A Πᵀ         不变量: 图同构不变量
```

规则:**一个 observable 若声称在某 `Coord[A,…]` 上"规范不变",必须在 A 的轨道上不变**(可数值检验:见 `experiments/sanity_checks.py` S3)。

#### 3.4 命名空间/元数据

```
ns:   geometry.smooth | probability.finite | …     -- 命名空间(组织、检索、路由)
tags: {finite-dim, reflexive, positive-cone, …}     -- 能力标签(无公理,只作提示)
```

`ns` 与 `tags` **不参与类型相等**。把 `Graph → Probability` 重写为 `WeightedGraph → MarkovKernel`,学科词就只剩在命名空间里。

---

### 4. 类型检查器判定什么

| 判定内容 | 谁负责 | 结果 |
|---|---|---|
| 理论包含路径存在(如 $V_h\subset H^1$ 但 $\not\subset H^2$) | 类型检查器 | 通过/拒绝 |
| 参数合一(维数、环、范数一致) | 类型检查器 | 通过/拒绝 |
| 规范桥接存在(`Coord` 的规范作用相容) | 类型检查器 | 通过/需要显式 $\beta$ |
| 变性一致(协/反变) | 类型检查器 | 通过/拒绝 |
| 精化蕴含(如 stochastic ⇒ 对下游可用) | **证明义务** | `proved/checked/cited/asserted` |
| claim 的真假 | **证明义务** | 同上 |
| 非空洞闸门(`14`) | 契约校验器 | 通过/退回 |

---

### 5. 类型规则(非形式)

```
(T-Obj)    x : Th⟨p⟩ where φ         要求 φ[x] 作为证明义务
(T-Sub)    S ≤ S′                    当存在理论包含路径 Th ⊑ Th′ 且 参数合一
(T-Tr)     tr n : S⇒S′               契约良构(各字段按 14 的闸门)
(T-Comp)   T₁:S⇒S′, T₂:S″⇒S‴, S′ ≤ S″ (或经规范桥 β),
           guarantees(T₁) ⊨ requires(T₂)    ⟹  T₂∘T₁ : S ⇒ S‴      (见 13)
(T-Dual)   var 翻转: (f:S⇒S′)* : S′* ⇒ S*,  需要自反性假设方可 ** = id
(T-Coord)  coord(T,B,C) : Coord[A,(m,n),k]   其中 A 由 T 的类型决定
```

---

### 6. 接受 / 拒绝的例子

**拒绝 1 — 对 $V_h$ 取拉普拉斯。**
`Δ : H² ⇒ L²`,而 P1 有限元空间 $V_h\subset H^1$ 但 $V_h\not\subset H^2$ ⟹ `(T-Sub)` 失败(**结构类型即可捕捉**)。

**拒绝 2 — 对 Gram/Hessian 求"特征值"。**
`eig : Coord[Endo,…] ⇒ Spec`,输入类型是 `Coord[Bil,…]` ⟹ 类型不匹配。要通过必须显式提供度量(即规范群缩为 $O(n)$ 的声明)。

**拒绝 3 — 对非随机矩阵取平稳分布。**
`stationary : Stoch(n) ⇒ Dist(n)` 需要 `where P·1=1`,而上游只给出 `Mat(ℝ≥0)` ⟹ 产生精化义务,若无见证则**拒绝**。

**拒绝 4 — 协变用在反变位置。**
测度 $\mu P$ 与函数 $Pf$ 作用方向相反(`B8`);混用 ⟹ 变性检查失败。

**接受 — 同调系数变换。**
`⊗k : Module_ℤ ⇒ Vect_k` 类型相容,**但契约携带 `lax` claim**(Tor 缺陷),下游若要 `H_n(C⊗k) = H_n(C)⊗k` 必须带 `under Tor₁(H_{n-1},k)=0`。类型检查通过,**语义义务不被抹去**。

---

### 7. LLM 友好性规则

1. **封闭词汇**:模式 `exact|graded|lax`;规范作用 `Hom|Endo|Bil|Perm|…`;见证状态 `formal|checked|cited|asserted`。
2. **字段数少而固定**(见 `16`):`from/to`、`requires`、`choice`、`claims`、`loses`、`recovers`、`coord`。
3. **稳定标识**:每个理论、变换有稳定 ID,别名显式。
4. **默认值必须标记**(`default:ℝ`),不允许沉默默认。
5. **不让 agent 构造新理论而不声明**:新理论 = 新库条目,需带"这个理论有什么真实定理要做"的说明(借 Mathlib 准入准则)。

### 8. 开放问题

* 子类型/universe 层级是否必要,还是用"理论包含图 + 参数"足够?
* 实例解析的菱形(同一结构经两条路径)如何处理——Mathlib 有经验,但对跨域变换是否足够未知。
* 精化蕴含的自动化范围:委托 SMT/CAS/Lean 的边界在哪。
* 本文给出的是**设计**,没有实现与 LLM 稳定性实验;LLM 能否稳定产出该类型(RT6 的判决实验)尚未做。


---

## 附录 06 — Map 与 Transformation 语义

> 对应 Task 12 / Q4。**不要把一切都叫 morphism,除非数学上有根据。**
> 标签见 `01-…`。

### 0. 结论

> **基本实体应是 Transformation(带类型、带契约的结构化对应),而不是 Map。**
> Map(态射)是 Transformation 的特例:"全 + 单值 + 精确"。其余常见的跨域变换(近似、优化、选择、商、离散化、不变量提取、性质桥)**不是**态射,要么是对应,要么是"对应 + 声明的缺陷",要么根本是定理(claim)。
> prompt 的契约字段 `requires/preserves/forgets/introduces/choice/law/cost` 可以收缩为 **`requires, choice, claims(模式), loses, recovers`** 五项 + 附属的 `witness`/`cost`。

---

### 1. 十种"常被称作 morphism 的东西"

| 名称 | 实际是什么 | 是态射? | 在 MEL 里 |
|---|---|---|---|
| 真函子(切函子 $T$、$H_n$、自由向量空间) | 保持复合的映射 | ✓ | Transformation,`exact` + `natural[…]` |
| 表示 $G\to GL(V)$ | 以 $G$ 为单对象范畴的函子 | ✓ | 同上 |
| 商 $X\to X/{\sim}$ | 泛构造(余等化子)+ 典范态射 | 构造 ✓,商对象本身 ✗ | M2 |
| 完备化 | 反射子(左伴随) | ✓(函子) | M2 |
| 自由/遗忘 | 伴随对 | ✓ 但**成对** | M2(伴随) |
| **离散化** | **一族不同机制**:Galerkin 投影、采样/配置、谱截断 | ✗(不是一种东西) | M4 + 选择;**不设原语** |
| **优化 argmin** | 多值、可能不存在的**关系** | ✗ | 对应(非单值) |
| **模型选择** | **选择**(非规范)+ 准则 | ✗ | `choice` |
| **近似** | 带分级的关系 $x\approx_\varepsilon y$ | ✗ | `graded` claim |
| **不变量提取** | 对声明的等价为常值的映射 | ✓(映到值结构) | Transformation 目标为值结构 |
| **性质桥** "$P(x)\Leftrightarrow Q(E(x))$" | **定理**,不是变换 | ✗ | `claim` |

要点:**离散化不是一个原语**——它是 Galerkin(保结构的投影)、配置/有限差分(点评估)、谱截断三种**不同**机制的统称,只能算 CONVENIENCE LABEL(见 `11`、`12`)。

---

### 2. 统一概念:带缺陷声明的结构化对应

把 Transformation 视为 $X$ 与 $Y$ 之间的**结构化对应** $R\subseteq X\times Y$(`(bg)` 关系代数 / span / profunctor)。经典事实:

* **态射 = 全 + 单值(univalent)的对应。**
* **同构 = 全 + 单值 + 单射 + 满射。**
* 偏离这些性质的方式有且仅有"缺陷"的几种。把它们逐条对应到契约字段:

| 对应的性质 | 失败时叫什么 | 契约字段 | 例 |
|---|---|---|---|
| **全**(每个 $x$ 有像) | 假设缺陷 | `requires φ` | 归一化需 $\deg>0$;Lax–Milgram 需强制性 |
| **单值** | 选择缺陷 | `choice c : C [gauge G]` | 基、归一化、网格、系数环 |
| **单射** | 信息缺陷 | `loses ρ` | $W\sim\Lambda W$;1-jet 等价;聚合 |
| **满射/像的结构** | 保证(guarantee) | `claims` 中对像的 exact 陈述 | 像是随机矩阵;像在 $V_h$ |
| **精确** | 度量/正合缺陷 | `graded[Γ]` / `lax` | Céa;Tor |

> **[H]** 这就是"契约 = 缺陷账本"的数学内容:每个声明字段对应"对应偏离同构"的一种方式。**这不是新数学**(Schmidt–Ströhlein 关系代数;Freyd–Scedrov allegories `(bg)`),新的只是**强制声明**。

**危险**:对应比函数宽得多,"任意对应 + 元数据"是空洞的(RT4)。防护见 `14` 的闸门 G1–G6。

---

### 3. 契约字段审问

| prompt 字段 | 可导出? | 处理 |
|---|---|---|
| `requires` | 否(对应的"全"缺陷) | **保留** |
| `preserves` | 是:`exact` claim(交换方块) | 并入 `claims` |
| `forgets` | 是:核对 $\ker T$;但**相对 observable** 才有意义 | 保留为 `loses`(声明的上界),并与 `recovers` 配对 |
| `introduces` | 与 `choice` 重合 | 合并为 `choice` |
| `choice` | 保留(规范群) | **保留** |
| `law` | 是:`claims` | 并入 |
| `cost` | 与规范**不**相容(`08–11`);语义核之外 | **附属**,挂在坐标层 |
| (新)`recovers q` | 否(它声明"purpose") | **保留** |
| (新)`witness` | 否(证据状态) | **附属但强制** |

最终:`requires, choice, claims, loses, recovers` + `witness`(+ 可选 `cost`、`coord`)。

---

### 4. "模式(kind)"不是原语,是 claim 的模式识别

按 prompt 的原语纪律(`FAMILY / PATTERN / CONVENIENCE LABEL`),不把"functorial / retraction / quotient…"设为变换类型枚举。它们是**可检验的 claim 签名**:

| 机制 | 签名(可被第二个标注者独立检验) |
|---|---|
| **M0 视图/函子** | $S\Rightarrow S'$,对声明结构全部 `exact` 保持;`natural[class]` 声明;无 `choice` |
| **M1 呈现+规范** | $S\Rightarrow\mathsf{Coord}[A,\cdot]$;有 `choice`(基/图/排序)与规范群;claim:$[g\circ f]=[g][f]$;observable 为 $A$-不变 |
| **M2 泛构造** | 带**泛性质**陈述(伴随/余极限)的 `exact` claim;典范、无 `choice` |
| **M3 对偶/伴随** | 反变:$(g\circ f)^*=f^*\circ g^*$;自反性作为**带假设**的 claim |
| **M4 带分级的收缩** | 成对 $(R,P)$:`exact` $R\circ P=\mathrm{id}$;`graded` $P\circ R\approx_\Gamma\mathrm{id}$(在 $D$ 上) |
| **M5 假设下的重述** | $\mathrm{Problem}_1\Rightarrow\mathrm{Problem}_2$:`requires H` 下 `exact` $\mathrm{Sol}_1=\mathrm{Sol}_2$;否则 `lax` $\mathrm{Sol}_1\subseteq\mathrm{Sol}_2$ |

详见 `12` 的压缩检验。**这里只给签名,不给"存在多少个"的结论。**

---

### 5. 旧 7 元组 MI 的归位

$MI(op,A,q,E,L,\widetilde{op},W)$ 不是废弃,而是**降为契约的一个特例**:

| MI 分量 | 在 Transformation 中的位置 |
|---|---|
| $E$ | 变换本身(构造 `via`) |
| $A$ | `requires` |
| $op$ & $\widetilde{op}$ | 一个 `exact` claim:$E(op\,x)=\widetilde{op}(E\,x)$ |
| $q$ | `recovers q`(与 claim $q=\tilde q\circ E$) |
| $L$ | 目标 Structure $S'$ |
| $W$ | `witness` |

即 **MI = 带一条 `exact` 命名 claim 与一条 `recovers` 的 Transformation**。MI 里没有的:`choice`、`loses`、`graded`、`lax`。这些恰是四走廊压力测试里不得不添加的。

与 R0–R3 的对应:

* R0 可表示 → Transformation 存在但**无 claim**(被闸门 G1 拒绝为"bridge")
* R1 性质可恢复 → 有 `recovers q`
* R2 操作有对应 → 有 `exact` 对 op 的 claim(自然性)
* R3 真正杠杆 → 通过闸门 G3(`14`)

---

### 6. 回答 Q4:基本实体是什么

| 候选 | 判定 | 理由 |
|---|---|---|
| Object | 类型/项两层之一 | 与 Structure 同一实体的两层 |
| **Structured Object** | **类型层基本实体** | = Structure + 其居民 |
| Operation | 派生 | 自映射的 Transformation($S\Rightarrow S$) |
| **Map** | **特例** | "全 + 单值 + 精确"的 Transformation |
| **Transformation** | **操作层基本实体** | 带声明缺陷的结构化对应 |
| Relation | 派生 | 以 $\mathbf 2$ 为值的对应 |
| **Interface** | **契约的视图**,不是实体 | 即旧 MI |
| **Bridge** | **派生**:Transformation 的复合路径 | 不独立编目(这正是暂停 Bridge Atlas 的理由) |
| **Theory morphism** | 类型层的 Transformation | MMT 的 view;institution 意义下的态射 |

> **选择**:**Structured Object(类型层)与 Transformation(操作层)是两个基本实体**;Map、Interface、Bridge、Theory morphism 都不是原语。

### 7. 未解

* **变换之间的态射**(2-胞腔):两个变换"观测等价"(`q∘f = q∘g`)是否需要一阶实体?目前作为派生等价处理,但 `lax` 模式已隐含 2-胞腔,**层级是否要升到 double category** 是开放问题(留给 `E`/`B` 方向,见 `final-mel-research-report.md` §6)。
* "对应"的复合需要拉回存在性;在非阿贝尔/非局部呈现范畴里是否成立未检验。


---

## 附录 07 — 规范型与中间类型化形式

> 对应 Task / §14 与 §9–§10(中间形式、MLIR 类比)。
> 标签见 `01-…`。

### 0. 结论

> 1. **"规范型"对互操作不是必要的,且在 LA 之外往往根本不存在**;不应把它放进核。
> 2. 应当引入更弱的概念 **intermediate typed form(ITF,中间类型化形式)**:非规范、非唯一,但**类型稳定、保留的信息被声明、可复合**。
> 3. 互操作真正需要的不是"规范化",而是"**带见证的等价检验 / 声明的规范群胚内的同构**"。
> 4. 有实证迹象(来自背景知识,未系统计数)表明,若干结构确实是**多入口(fan-in)枢纽**:链复形、Markov 核/随机算子、带半群的 Hilbert 空间算子、优化问题、群作用。这支持"**多个类型化方言 + 可复用转换**"而非单一表示。
> 5. MLIR 类比有用但**仅为类比**;见 §6 的三级分级。

---

### 1. 三个必须区分的概念

| 概念 | 定义 | 要求 | 例子 |
|---|---|---|---|
| **规范型 / normal form** | 等价类的**唯一**代表(或完备不变量的可计算截面) | 等价可判定;重写系统合流且终止,或轨道有可计算截面 | RREF、Smith 标准型、Gröbner 约化基、β-范式 |
| **规范到规范群** | 唯一到一个声明的群(oid)作用 | 声明规范群 | 谱(到排列)、SVD(到符号/排序)、Jordan 型(到块排列) |
| **中间类型化形式(ITF)** | 若干结构共同"降落"到、再"升起"出的**类型**;**非唯一、非截面** | 稳定类型;声明保留/丢失的信息;可复合 | 链复形、Markov 核、切空间、Hilbert 算子、优化问题 |

关键:**"规范型"是一个关于等价类的陈述,"ITF"是一个关于枢纽类型的陈述**。把二者混淆是 LA 直觉最容易误导的地方(RT9)。

---

### 2. LA 里规范型为什么存在,以及为什么多数地方不存在

规范型存在 = **等价可判定** + **轨道驯服**:

* 单个自同态 $\Leftrightarrow$ $k[x]$-模;PID 上有限生成模的**结构定理** ⟹ 有理/Jordan 标准型。`[T]`
* 整数矩阵的 Smith 标准型 ⟹ 有限生成阿贝尔群结构定理 ⟹ **同调的挠部分**(走廊 C 实际用到:$\mathrm{RP}^2$ 的 $\partial_2$ 的不变因子 $\{1,\dots,1,2\}$ ⟹ $H_1(\mathbb Z)=\mathbb Z/2$,`experiments/sanity_checks.py` S1)。
* 两个不交换算子的同时相似分类是 **wild** 的;一般模范畴没有有限分类;流形同胚在维数 $\ge4$ 不可判定。`(bg)`

所以对 MEL:**规范型是 P6/P7 的运气,不是可要求的设计**。能做的是 PT2(**规范型计算**)——当且仅当目标理论恰好提供它(Smith、Jordan、SVD、Gröbner、LU),作为**可选的变换模式**。

#### 一个有用的重新理解

> **[S] 归一化 = 规范固定(gauge fixing)。** 走廊 B 的 $P=D^{-1}W$ 是 $W$ 在"正对角行缩放"群作用下的一个**轨道截面**(取行和为 1 的代表);它丢掉的信息恰好是轨道坐标(行尺度)。这给出一个统一说法:**很多"归一化/规范化"是选择轨道上的一个切片**——选择本身是 `choice`,丢弃的是 `loses`。

---

### 3. 回答 §14 的六个问题

| # | 问题 | 回答 |
|---|---|---|
| 1 | "规范型"在 LA 之外意味着什么? | 等价类的**可计算唯一代表**;常见于代数(Gröbner、Smith)、λ 演算(β-范式,Church–Rosser)。**很多领域不存在。** |
| 2 | 规范化对互操作是否必要? | **否。** 必要的是带见证的**等价检验**或规范群胚内的同构;规范型只是实现等价检验的一种**优化**(便于哈希/去重/缓存)。 |
| 3 | 链复形、Markov 核、切空间是规范型还是中间形式? | **中间形式**:没有等价类的截面语义;它们是类型上的枢纽。 |
| 4 | 两个不同结构能否降到同一中间类型? | **能**,且是常态(§4)。 |
| 5 | 等价表示能否经典范等价关系比较? | 能,经**规范群胚**:呈现间的同构 $\beta$;observable 对 $\beta$ 不变。 |
| 6 | "规范型"是否过强,应改用"中间类型化形式"? | **是。** 规范型是 ITF 的特例(当截面存在时)。 |

---

### 4. ITF 的扇入证据(hub census,`(bg)`,未系统计数)

> **[H]** 下表是基于数学常识的枚举,不是穷举实验。判决实验见 `17` RT8。

| 候选 ITF | 已知来源结构(多入口) | 已知去向(多出口) | 保留什么 |
|---|---|---|---|
| **链/上链复形** | 图、单纯/胞腔复形、拓扑空间(奇异链)、群(bar 分解)、Lie 代数(Chevalley–Eilenberg)、流形(de Rham 复形) | 同调/上同调、Euler 示性数、谱序列、Hodge | 边缘/上边缘结构;不保留几何 |
| **Markov 核 / 随机算子** | 带权图(随机游走)、动力系统(Ulam/传递算子)、PDE 有限体积(Fokker–Planck)、MCMC | 平稳律、混合时间、谱隙 | 转移结构;不保留原权重尺度 |
| **Hilbert 空间 + 算子/半群** | PDE、概率($L^2$ 条件期望)、量子、信号 | 谱理论、投影、半群 | 内积结构;不保留逐点信息 |
| **优化/变分问题** | 变分 PDE、最小二乘/MLE、图割松弛、正则化 | 对偶、KKT、迭代算法 | 极小化结构 |
| **群作用 / 表示** | 几何对称、组合、动力、代数 | 特征标、等变分解 | 对称结构 |
| **切空间 / jet** | 光滑映射、微分方程 | 线性化、稳定性 | 一阶信息 |

**准入准则**(一个类型要被称为 ITF):
1. 来自**至少两个不同理论谱系**的入口;
2. 通往**至少两个不同目标**的出口;
3. 类型稳定(有明确 Structure);
4. **声明保留与丢失的信息**(否则就是 R0 序列化);
5. 入口与出口变换在复合下行为良好(见 `13`)。

上表所列均满足 1–2;3–5 需逐个验证,**本研究只在四走廊与两个控制走廊里验证了其中几个**。

---

### 5. "多个类型化方言 + 可复用转换"

> **[S]** 在这个视角里,MEL 不是"一个通用表示",而是:
> (i)若干 ITF 作为**方言**(每个有自己的理论、规范群、observable);
> (ii)一小批**可复用的转换模式**(`12` 的 M0–M5、PT1–PT2)在方言之间搭桥。
>
> 如果 ITF 的数目随覆盖领域线性增长,则压缩失败(Outcome D);如果少数 ITF 吸收绝大多数转换,则压缩成立。**这是 `12` 的压缩检验要回答的问题,目前证据仅为四走廊 + 两个控制。**

---

### 6. MLIR 类比:三级分级(Task / §10)

> 仅将 MLIR 作为**类比**。分级:`[A]` 类比 / `[S]` 结构对应 / `[T]` 实际定理。

| MLIR 概念 `(web: Lattner 等 2020)` | MEL 对应物 | 分级 | 类比失效处 |
|---|---|---|---|
| dialect(共享骨架上的领域扩展) | 理论族 / 命名空间 | `[A]` | 编译器各方言底部共享**单一操作语义**;数学没有 |
| operation / type / attribute | 项 / Structure / refinement | `[S]` | — |
| verifier | 契约良构校验(闸门) | `[A]` | MLIR verifier 查良构而非语义真值,**MEL 同样**——这个限制是共同的 |
| progressive lowering | 变换链至坐标层/求解器 | `[A]` | 编译 lowering 多为**构造即保持语义**;数学 lowering 常**有损、带选择、带假设** |
| conversion/legalization pattern | M0–M5 模板 | `[A]` | — |
| pass pipeline | 复合变换 | `[S]` | MEL 的复合需**按 observable、按假设**检查 |
| 目标 = 机器码 | 目标 = ? | **失效** | 数学至少有 ≥3 类彼此不同的"后端":数值计算、形式证明(Lean)、搜索/判定(SAT/SMT/CAS) |
| 实际定理 | — | — | **本研究没有从 MLIR 类比推出任何定理** |

结论:类比的**价值**是工程性的(方言化组织、渐进降级的复合),**风险**是误以为数学有一个"最底层"。MEL 必须允许**多个后端**。

### 7. 局限

* ITF 表是知识性枚举,不是经过数据驱动的统计。
* 未检验"链复形"等 ITF 的复合在 `lax` 模式下的行为(谱序列)——这是已知难点(`13` §5)。


---

## 附录 08 — 走廊 A:局部线性化(Calculus ↔ Geometry → LA)

> 对应 Task / §15 Corridor A。关键问题:**哪些 MEL 原语真的被用到?**
> 标签见 `01-…`;计算验证见 `experiments/sanity_checks.py`。

### 0. 结论

* **去掉分支标签后,"微积分的导数"与"几何的切映射"是同一个 Transformation**;唯一差别在坐标化(`Calculus` 的图 = 恒等)。**分支词只在命名空间里**。
* 走廊 A 只需要:**M1(呈现+规范)、M2(jet 作为泛构造)、M3(拉回/反变)、`exact` 函子性、局部 `graded`(germ)**。**不需要 `lax`、`choice`(除图册)、`cost`。**
* 两个压力点:(i)**局部性**——claim 只在 germ 上成立;(ii)**坐标类型必须携带规范作用**:度量的拉回按**合同**变换,不是相似。

### 1. 去标签后的类型路径

```
PointedSmoothMap(M,N;f,p)
    ⇒ Jet¹                       -- 1-jet(= 芽模 m²)
    ⇒ Lin(T_pM, T_{f(p)}N)       -- 切映射 df_p
    ⇒ Coord[Hom,(m,n),ℝ]         -- Jacobian(选图)
    ⇒ ℕ                          -- rank   (observable)
```

### 2. Stage A:原始变换

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

### 3. MEL 表达

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

### 4. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| $D(g)\circ D(f)$ 在 $f(p)$ 处对齐 | ✓ `exact` | 链式法则;需 `requires` 基点对齐 $q=f(p)$,否则类型失败 |
| Jacobian 换图 | ✓ | $J\mapsto BJA^{-1}$;rank 不变 |
| 对 Hessian 取特征值 | **✗**(`05` §6) | `Coord[Bil]` ≠ `Coord[Endo]`;需先声明度量 |
| 局部 claim 接全局 claim | ✗ | germ 域不包含全局;`requires` 不满足 |

> 实测(S3):相似下特征值不变、合同下**不**不变,惯性不变——这是"类型 = 规范作用"的数值证据。

### 5. 非空洞性检验(闸门见 `14`)

对"光滑映射 → Jacobian 矩阵":

* **G1 可证伪**:rank 在域上非常值 ✓
* **G2 自然性**:链式法则(对复合封闭)✓
* **G3 杠杆**:秩定理 / 隐函数定理——矩阵秩可判定 immersion/submersion ✓
* **G4 变异测试**:把 $[df]$ 换成转置 ⟹ 复合顺序反,链式 claim 失败 ✓

### 6. 需要什么 / 不需要什么

| 需要 | 不需要 |
|---|---|
| M1、M2(jet 作为"芽模 $\mathfrak m^2$"的商)、M3、`exact`、germ-`graded`、坐标规范作用 | `lax`、`choice`(图册之外)、`cost`、PT2 |

**对 prompt 的回答("MEL 原语哪些被需要")**:Structure(光滑流形芽、Lin、Bil)、Transformation(`D`、`pullback`、`coord`)、Claim(`exact` + 局部 `graded`)。**没有 Law/Observable/Equivalence 作为独立原语的需要。**

### 7. 局限

* 走廊 A 对 MEL 是**最容易**的一个:几乎所有变换都是精确函子。它**不能**检验 `lax`/`choice`/成本。
* Jet 被并入 M2(商)后,"局部线性化"自身不单列;但"导数即最佳线性逼近"的**度量**含义(余项估计)仍需 `graded`。


---

## 附录 09 — 走廊 B:离散 / 随机 / 动力(Graph → Probability → Dynamics → LA)

> 标签见 `01-…`;数值验证见 `experiments/sanity_checks.py` S2。

### 0. 结论

* 路径去标签后:$\mathsf{WeightedGraph}\Rightarrow\mathsf{Stoch}\Rightarrow\mathsf{Evolution}\Rightarrow\mathsf{LinOp}^{+}$。
* **归一化是规范固定**:$P=D^{-1}W$ 取 $W$ 在"正对角行缩放"轨道上的行和为 1 的切片;丢失的恰是行尺度。
* **LA 不够**:Perron–Frobenius 是**锥定理**(Krein–Rutman 一类),需要"正性/序结构",**不是向量空间结构**。目标类型必须是 $\mathsf{LinOp}$ 加上"保持的凸集/锥"这一精化。
* **聚合(lumping)与 Galerkin 是同一个机制(M4)**,这是走廊 B 与 D 之间最具体的复用证据(已数值验证)。

### 1. 路径

```
WeightedGraph(V,W)
  ⇒ Stoch(|V|)                    -- Markov 核 P  (choice: 归一化)
  ⇒ Evolution                     -- μ ↦ μPⁿ ,  e^{tQ}
  ⇒ LinOp restricted to Δ         -- 线性算子 + 保持单纯形(锥)
  ⇒ Obs                           -- π, 谱隙, 击中时
```

### 2. Stage A:原始变换

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

### 3. MEL 表达

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

### 4. 数值验证(S2,实际计算过)

| 命题 | 结果 |
|---|---|
| 有向情形 $P(\Lambda W)=P(W)$ | ✓ 行尺度被丢失 |
| 无向情形 $(P,\pi)$ 恢复 $W$,仅差一个全局标量 | ✓ |
| $\mathrm{spec}(P)=\mathrm{spec}(D^{-1/2}WD^{-1/2})$(相似) | ✓ |
| 慢混合环上 $\lVert P^t-\mathbf 1\pi\rVert\lesssim|\lambda_2|^t$(误差远高于机器精度) | ✓ |
| 可 lump 链 $PV=V\hat P$ | ✓ |
| 不可 lump 链的朴素聚合有缺陷 | ✓ 缺陷 = 0.100 |
| π-加权压缩得到随机矩阵且保持 lumped 平稳律 | ✓ |

### 5. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| RW 后迭代 $P^n$ | ✓ `exact` | $\mathsf{Stoch}$ 对复合封闭 |
| RW 后对**顶点商图**再 RW | **✗**(除非可 lump) | 归一化对一般图态射**不自然**;商后再归一化 $\ne$ 归一化后聚合 |
| 对 `Mat(ℝ≥0)`(非随机)取平稳律 | ✗ | 缺 `where P·1=1`,产生精化义务 |
| 平稳律后恢复 $W$ | ✗ | 信息已丢失(行尺度 / 全局标量) |
| 谱 observable 经 RW 后恢复 | ✓ | `recovers` 声明含谱 |

### 6. 压力点

1. **选择即规范固定**:`choice norm : Slice(RowScaling)`。换归一化(lazy、对称化)= 换切片;**观测量对切片的依赖必须声明**(混合时间随 lazy 与否而变)。
2. **锥/正性是 LA 之外的结构**:B4 的目标若只写 `Vect`,就丢了 PF 所需的信息;必须写 `LinOp where preserves(Δ)`。
3. **假设向后传播**:PF 的"不可约"是对**源图**的假设;`requires` 沿复合向后传播(wp,见 `13`)。
4. **连续时间的存在性**:$P=e^{Q}$ 不总存在(`requires` 嵌入性)。
5. **M3**:前向/后向的变性必须在类型里。

### 7. 非空洞性检验

* "带权图 → $\mathbb R^V$ 上的算子 $W$"若不使用 Markov 结构,只达 **R0**。
* 通过 **G3**:PF + 谱隙给出混合时间界(有定理见证);
* **G2**:"把平稳律直接作为表示"(答案预计算)失败——因为不能经 $P^n$ 复合得到;
* **G4**:变异测试——把行归一化改成列归一化,`P·1=1` claim 失败。

### 8. 局限

* Markov 范畴(Fritz `(web)`)提供了本走廊更强的理论基础,本文只用到有限、离散的片段。
* "聚合 ≡ Galerkin"是**结构对应 `[S]`**,不是已证定理;但 $\hat\pi\hat P=\hat\pi$ 的恒等式已直接验证并可手证。


---

## 附录 10 — 走廊 C:拓扑 / 代数(Graph → Topology → Abstract Algebra → LA)

> 标签见 `01-…`;数值验证见 `experiments/sanity_checks.py` S1。

### 0. 结论

* 走廊 C 是**唯一强制 `lax` 模式**的走廊:系数变换产生 **Tor 缺陷**。
* **只用图(1 维)做这条走廊会完全掩盖 `lax`**——图的 $H_1$ 无挠,系数变换的缺陷恒为 0。这是一个具体的**选择偏差**例子(见 `12`)。必须补一个 2 维例子($\mathrm{RP}^2$)才能暴露。
* "Graph → Topology"一步**极有损**:同伦型只保留 $(\beta_0,\beta_1)$;与"邻接谱"保留的信息**互不可比**——这是"信息损失相对 purpose"最清楚的例子。

### 1. 路径

```
Graph(V,E)
  ⇒ Cell₁                         -- 1 维胞腔复形(重解释;M0)
  ⇒ Chain[R]                      -- 链复形(choice: 取向;系数环 R)
  ⇒ Module_R                      -- H_n = ker∂_n / im∂_{n+1}
  ⇒ Vect_k                        -- ⊗_R k  (系数变换;lax)
```

补充 2 维例子:$\mathrm{RP}^2$(六顶点三角剖分:$V-E+F=6-15+10=1$)。

### 2. Stage A:原始变换

| ID | 变换 | 输入 | 输出 | 保持律 / 声明 | 复合行为 | 机制 |
|---|---|---|---|---|---|---|
| C1 | 图 → 1 维胞腔复形 | 图 | 复形 | 几何实现;忠实函子 | 函子 | M0 |
| C2 | 边的取向 | 边集 | $\{\pm1\}^E$ | 规范:符号翻转 | 群作用 | M1 |
| C3 | 链群 $C_n=R[\text{cells}_n]$ | 复形 | $\mathrm{Chain}[R]$ | 左伴随(自由) | 伴随复合 | M2 |
| C4 | 边缘算子(关联矩阵) | 复形 | $\mathrm{Coord}[\mathrm{Hom}]$ | $\partial\partial=0$ | 矩阵乘 | M1 |
| C5 | 同调 $H_n=\ker\partial_n/\mathrm{im}\,\partial_{n+1}$ | 链复形 | $\mathrm{Module}_R$ | 泛构造(余核) | 函子 | M2 |
| C6 | 系数变换 $\otimes_Rk$ | $\mathrm{Module}_R$ | $\mathrm{Vect}_k$ | 扩张标量 ⊣ 限制标量;**正合缺陷 Tor** | 函子(右正合) | M2 + `lax` |
| C7 | 不变量 $\beta_n,\chi$、挠系数 | 同调 | $\mathbb N,\mathbb Z$ | $\chi=\sum(-1)^n\beta_n$,**与系数无关** | — | OBS |
| C8 | *函子性*:胞腔映射 ⟹ 链映射 ⟹ 同调映射 | — | — | — | **元定律** | — |
| C9 | Smith 标准型(over $\mathbb Z$) | 整数矩阵 | 对角 | 提取挠 | — | PT2 |

(8 个变换 + 1 条元定律。)

### 3. 实际计算(S1)

| 量 | 结果 |
|---|---|
| $H_*(\mathrm{RP}^2;\mathbb Z)$ | $\mathbb Z,\ \mathbb Z/2,\ 0$(Smith 不变因子 $\{1,\dots,1,2\}$) |
| $\dim H_*(\,;\mathbb Q)$ | $(1,0,0)$ |
| $\dim H_*(\,;\mathbb F_2)$ | $(1,1,1)$ |
| $\chi$ | 两种系数下均为 1 ✓ |
| UCT 预测 | $\dim H_n(\,;\mathbb F_2)=\dim(H_n(\mathbb Z)\otimes\mathbb F_2)+\dim\mathrm{Tor}(H_{n-1}(\mathbb Z),\mathbb F_2)$ → $(1,1,1)$ ✓ |
| 图控制(9 边 7 点) | $\partial_1$ 的秩与取向、系数无关;无挠;$\beta_1=E-V+1=3$ |

**缺陷的精确位置**:度 2、$k=\mathbb F_2$:
$H_2(C;\mathbb Z)\otimes\mathbb F_2=0$,但 $H_2(C\otimes\mathbb F_2)=\mathbb F_2$,差 $=\mathrm{Tor}_1(\mathbb Z/2,\mathbb F_2)=\mathbb F_2$。

### 4. MEL 表达

```
tr Cells : SimplicialComplex(K) ⇒ Chain[R]
  choice    取向 o : Torsor({±1}^{cells})              gauge  符号
  claims    exact ∂∘∂ = 0
            exact natural[SimplicialMap]
  recovers  β_n(k), χ                                  (对取向不变)

tr H_n : Chain[R] ⇒ Module_R         -- 泛构造(余核)

tr BaseChange[k] : Module_R ⇒ Vect_k
  requires  R → k 环同态
  claims
    lax   κ : H_n(C)⊗_R k  ↪  H_n(C⊗_R k)   defect = Tor₁^R(H_{n-1}(C), k)
          under  Tor₁^R(H_{n-1}(C),k) = 0    (例: k=ℚ;或 H_{n-1} 自由)
    exact χ(C⊗k) = χ(C)
  loses     挠结构(⊗k 后 ℤ/2 ⊗ ℚ = 0)
```

### 5. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| `Cells` → $H_n$ → `⊗k` 与 `Cells` → `⊗k` → $H_n$ | **仅在 `lax` 缺陷为 0 时相等** | UCT;$\mathrm{RP}^2$、$\mathbb F_2$、度 2 为反例 |
| 取向翻转前后 rank | ✓ 不变 | 规范不变 |
| 对**图**用 `lax` | 平凡(缺陷恒 0) | 1 维复形的 $H_1$ 是自由群的子群,无挠 |
| 图 → 同伦型 → 邻接谱 | ✗ | 同伦型已丢失谱信息 |

### 6. 信息损失相对 purpose

同一源对象,两种降级保留**互不可比**的信息:

| 降级 | 保留 | 丢失 |
|---|---|---|
| 图 → 同伦型/同调 | $(\beta_0,\beta_1)$(连通分支数 + 环秩) | 几乎全部组合信息:同 $\beta_1$ 的连通图同伦等价 |
| 图 → 邻接谱 | 谱不变量 | 同谱非同构图(cospectral)不可区分 |

> 这正是契约里 `recovers q` + `loses ρ` 要**成对声明**的原因:损失只有相对 observable 才有意义。

### 7. 压力点

1. **`lax` 模式**:缺陷是**对象**(Tor),不是度量;必须进核。
2. **系数环显式**:$\mathbb Z/\mathbb Q/\mathbb F_2$ 会改变 Betti 数。**绝不可隐含。**
3. **自然性作用域**:对"图同态"还是"胞腔映射"自然?(边收缩需约定 ⟹ 声明 `natural[class]`)
4. **规范群随环变**:在 $\mathbb Z$ 上是 $GL_n(\mathbb Z)$(Smith 标准型 = 规范固定),在域上是 $GL_n(k)$。

### 8. 非空洞性检验

* **G4 变异测试**:翻转某个三角形边缘算子里的**一项**符号 ⟹ $\partial_1\partial_2$ 的某列变为 $2(c-a)\ne0$,`exact ∂∂=0` 失败 ✓(注意:对纯图此测试**无效**——1 维没有 $\partial_2$,`∂∂=0` 空真。又一次说明图-only 的走廊太弱。)
* **G3 杠杆**:在 $\mathbb F_2$ 上用高斯消元计算 $\beta_1$(多项式时间),并读回"环秩/可定向性"(挠与否)。

### 9. 局限

* 未涉及上同调环结构、谱序列的复合;`lax` 缺陷如何**跨多步复合**没有简单演算(见 `13` §5)。
* 只测了一个带挠的例子($\mathrm{RP}^2$)。


---

## 附录 11 — 走廊 D:解析 / 变分 / 有限维(Calculus → Functional Analysis → Optimization → Finite LA)

> 标签见 `01-…`;数值验证见 `experiments/sanity_checks.py` S3、S4。
> 模型问题:$-u''=f$ 于 $(0,1)$,$u(0)=u(1)=0$;一般形式:求 $u\in V$(Hilbert)使 $a(u,v)=\ell(v)\ \forall v\in V$,$a$ 有界($M$)、强制($\alpha$)。

### 0. 结论

* "连续 → 离散"**不是一个原语**:至少是三种不同机制——**Galerkin 投影(保结构)**、**点评估/配置(有限差分)**、**谱截断**。只能算 CONVENIENCE LABEL。
* 走廊 D 的核心是 **M4(带分级的收缩)**:精确保持结构、近似状态。这与 FEEC(Arnold–Falk–Winther `(web)`)的"子复形 + 有界上链投射"一致:**结构精确,状态graded**。
* **成本不是规范不变量**:同一个离散问题,换基后 $\mathrm{cond}(K)$ 从 32.2 变到 2725.9(S3)。因此"抽象/坐标分离"对**语义**成立,对**数值成本/稳定性**不成立;成本必须挂在坐标层。
* 弱形式、变分形式、线性系统、极小化之间的等价是 **M5(假设下的重述)**。

### 1. 路径

```
StrongProblem(A,f)
  ⇒ WeakProblem(V,a,ℓ)           -- 对 V* 测试;lax(强⊂弱)
  ⇒ Variational(V,J)             -- 对称强制 ⇒ 极小化 ½a(v,v)−ℓ(v)
  ⇒ Subspace V_h ⊂ V             -- choice
  ⇒ Coord[Bil](K,b)              -- 选基;合同规范
  ⇒ LinSys / Minimize(½xᵀKx−bᵀx)
  ⇒ u_h = Σ xᵢφᵢ                 -- 重构
```

### 2. Stage A:原始变换

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

### 3. 实际计算(S3、S4)

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

### 4. MEL 表达

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

### 5. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| Galerkin → 装配 → 求解 → 重构 | ✓,误差 = Céa + 求解误差 | 求解误差系数含 $\mathrm{cond}(K)$,**基相关** |
| 对 $u_h$ 取点式拉普拉斯 $\Delta$ | **✗** 类型错误 | $V_h\subset H^1$,$\not\subset H^2$;`Δ: H²⇒L²` |
| 离散化后无声明稳定常数的求导 | **✗**(或 grade=$\top$) | 有限差分求导的 $L\sim1/h$:$10^{-6}\to10^{-2}$ |
| 有限元(Galerkin) vs 有限差分(采样)混用 | ✗ | 采样不是收缩;一致性+稳定性 ⟹ 收敛(Lax 等价)是另一种契约 |
| 混合:结构精确 + 状态近似(FEEC) | ✓ | 对 $d$ 交换精确;范数下 graded |

> 复合检查没有任何"总是通过"的先验:**稳定常数 $L$ 必须由下游声明**,否则 `T-Comp` 退为 grade $\top$ 并标记 `UNSTABLE`。

### 6. "连续 → 离散"不是单一原语

| 机制 | 对象 | 精确保持什么 | 误差性质 |
|---|---|---|---|
| **Galerkin / Ritz 投影** | $V\to V_h$ 子空间 | 变分结构、对称性、(FEEC 下)复形 | 最佳逼近 × $M/\alpha$ |
| **点评估/配置/有限差分** | $V\to\mathbb R^n$ 采样 | 无(需一致性+稳定性) | 截断误差 × $1/h$ 放大 |
| **谱截断** | 基展开的前 $n$ 项 | 谱结构 | 尾项 |

结论:把"discretization"设为原语会把三个不同的契约抹成一个;在 MEL 里,它只能是**标签**。

### 7. 非空洞性检验

* **零编码**:$V\to\mathbb R^n$ 任取 $n$ 个数 ⟹ **G1** 失败(无可恢复的 observable)。
* **答案预计算**:把 $u$ 的节点值写进 $b$ ⟹ **G2** 失败(装配必须不依赖 $u$)。
* **G4**:使 $K$ 不对称 ⟹ "能量范数最佳逼近" claim 失败(可数值检验)。
* **G3**:Céa 引理 + Lax–Milgram ⟹ 有界、可预测的误差;线性系统有多项式算法。

### 8. 压力点

1. **混合 claim**:精确(结构)+ graded(状态)必须在同一契约里并存。
2. **成本与规范不相容**:成本不能进语义核。
3. **`lax`**:强解 ⊂ 弱解。
4. **稳定常数是一等声明**,否则无法复合。
5. **假设链**:强制性 → Lax–Milgram → Céa → 误差界;`requires` 沿链传播。

### 9. 局限

* 只数值验证了 1D P1 有限元;高维、非线性、非协调元均未测。
* FEEC 的"有界上链投射"只引用,未重做。


---

## 附录 12 — 分解与压缩检验(Factorization & Compression Test)

> 对应 §16、§17、Q6、Q7。**先压缩,再覆盖。**
> 纪律(§17):Stage A 记录原始变换 → Stage B 只按"输入型 / 输出型 / 保持律 / 复合行为"分组 → Stage C 才提候选原语,并要求 5 条准入标准,否则只叫 `FAMILY/PATTERN/CONVENIENCE LABEL`。
> 标签见 `01-…`。

### 0. 结论(诚实版)

> **[H]** 四个走廊的 **31 个原始变换**(外加 3 条元定律)被分成 **9 组**;其中 **6 组满足准入标准**(M0–M5),**2 组只是模式**(PT1、PT2),**1 组是契约成分而非变换**(OBS)。
> 压缩比约 **31 → 6(+2)**,落在 prompt 设想的"5–8"区间内。
>
> **但该结果证据强度很弱**,因为:(i)分组由本研究自己完成、事后分配;(ii)四个走廊都终止于 LA(见 §6);(iii)M0–M3 本身是经典范畴构造,**压缩可能只是"范畴论词汇很少"**,不是 MEL 的功劳。
> 在七个控制变换(§5)与三个对抗探针(§7)上,新机制需求为 0、新**参数**需求为 1(概率分级 $(\varepsilon,\delta)$)——仍不足以推出普适性。
> **判决实验(见 §8)尚未做。**

---

### 1. Stage A:原始变换(31 + 3)

走廊 A:A1 A2 A4 A5 A6 A7 A8(7)+ 元定律 A3
走廊 B:B1 B2 B4 B5 B6 B7 B8(7)+ 元定律 B3
走廊 C:C1 C2 C3 C4 C5 C6 C7 C9(8)+ 元定律 C8
走廊 D:D1–D9(9)

总计 7+7+8+9 = **31** 个变换;3 条元定律(链式法则、Stoch 封闭、同调函子性)——它们是"复合如何成立"的陈述,不是变换。详表见 `08`–`11`。

### 2. Stage B:分组(只看输入型 / 输出型 / 保持律 / 复合行为)

| 组 | 成员 | 数 | 输入型 → 输出型 | 保持律 | 复合行为 |
|---|---|---|---|---|---|
| **M0 视图/函子** | C1 | 1 | 结构 → 另一理论下的结构 | 对声明结构 exact | 函子 |
| **M1 呈现+规范** | A1 A6 B1 C2 C4 D6 D8 | 7 | 抽象 → `Coord[A,shape]` | $[g\circ f]=[g][f]$;规范不变量 | 矩阵乘 |
| **M2 泛构造**(自由/商/jet/基变换) | A2 A4 B4 C3 C5 C6 | 6 | 结构 → 泛对象 | 泛性质(伴随/余极限) | 伴随复合 |
| **M3 对偶/伴随** | A5 B8 D3 | 3 | 反变 | $(g\circ f)^*=f^*\circ g^*$ | 反序复合 |
| **M4 带分级的收缩** | B7 D4 D5 | 3 | $S\rightleftarrows S'$ | $R\circ P=\mathrm{id}$ 精确;$P\circ R\approx\mathrm{id}$ graded | Galois 连接可复合 |
| **M5 假设下的重述** | D1 D2 D9 | 3 | 问题 → 问题 | 在 $H$ 下 $\mathrm{Sol}_1=\mathrm{Sol}_2$ | 假设累积 |
| **PT1 生成元–半群** | A8 B5 | 2 | $Q\leftrightarrow e^{tQ}$ | 半群律 | 加法/乘法 |
| **PT2 规范型/规范固定/分解** | B2 C9 D7 | 3 | 对象 → 轨道代表 | 轨道不变 | — |
| **OBS 观测** | A7 B6 C7 | 3 | → 值结构 | 对规范/等价不变 | — |

**核对**:1+7+6+3+3+3+2+3+3 = **31** ✓;无未分配项。

> ⚠️ **零残余本身是弱证据**:分类若足够弹性,总能零残余。因此 §3 给出**可由第二标注者独立检验**的签名(见 `06` §4)。

### 3. Stage C:候选原语的准入检验

准入标准:**(a)重复出现 (b)稳定类型 (c)有意义的复合律 (d)非平凡保持语义 (e)解释/计算价值。**

| 候选 | 走廊覆盖(含控制) | (a) | (b) | (c) | (d) | (e) | 结论 |
|---|---|---|---|---|---|---|---|
| **M1 呈现+规范** | A B C D + E1 | ✓ 7 次 | ✓ | ✓ 矩阵乘/群胚 | ✓ 规范不变量 | ✓ | **PRIMITIVE-CANDIDATE** |
| **M2 泛构造** | A B C D + E1 | ✓ 6 次 | ✓ | ✓ 伴随复合 | ✓ 泛性质 | ✓ | **PRIMITIVE-CANDIDATE** |
| **M3 对偶/伴随** | A B D + E2(C 经 UCT) | ✓ | ✓ | ✓ 反序 | ✓ 自反性作假设 | ✓ | **PRIMITIVE-CANDIDATE** |
| **M4 带分级收缩** | B D(+C 的 Hodge,未做) | 2–3 | ✓ | ✓ Galois 连接可复合 | ✓ 精确+分级 | ✓ | **PRIMITIVE-CANDIDATE(较弱)** |
| **M5 假设下重述** | B D + E2 | ✓ | ✓ | ✓ wp | ✓ | ✓ | **PRIMITIVE-CANDIDATE** |
| M0 视图/函子 | C + E1 | 1(+隐含于多处) | ✓ | ✓ | — | — | **基底**(无标记情形),不单列 |
| PT1 生成元–半群 | A8 B5(+D 演化未做) | 2 | ✓ | ✓ | ✓ | ✓ | **PATTERN**(出现 <3) |
| PT2 规范固定/分解 | B2 C9 D7 | 3 | ✓ | ✗(无统一复合律) | ✓ | ✓ | **FAMILY** |
| OBS | A B C D | 4/4 | ✓ | ✓(按 observable) | — | ✓ | **契约成分**,非变换原语 |
| "离散化" | D(多处) | — | ✗(三种机制) | ✗ | — | — | **CONVENIENCE LABEL** |

### 4. 机制 × 缺陷对照

> **[H]** 提示:这张表**太整齐**,整齐本身是警告信号(RT5)。

| 机制 | 主要缺陷 | 复合律 |
|---|---|---|
| M0 | 无(精确、规范) | 范畴复合 |
| M1 | **选择**(规范群胚) | 群胚粘合,observable 须不变 |
| M2 | 信息(商)/ 无(自由);基变换时 **正合缺陷** | 伴随复合;缺陷复合 = 谱序列(难) |
| M3 | **自反性**缺陷($V\ne V^{**}$) | 反序;自反性须作假设 |
| M4 | **度量 + 信息** | 仿射误差幺半群;Galois 连接复合 |
| M5 | **假设** | wp 向后传播;不满足时退化为 `lax` |

### 5. 控制走廊(终点不是 LA)

> 目的:检验"重复机制"是不是只是**终点都是 LA**造成的假象。选取不引入新学科的控制(Abstract Algebra 内、Optimization 内)。

**E1:Graph ⇒ 1-复形 ⇒ $\pi_1$(自由群 $F_{\beta_1}$)⇒ 阿贝尔化 $\mathbb Z^{\beta_1}=H_1$**

| ID | 变换 | 机制 |
|---|---|---|
| E1.1 | 图 → 几何实现 | M0 |
| E1.2 | 基点与生成树的选择(规范群 $\mathrm{Aut}(F_n)$,基点改变 = 共轭) | M1 |
| E1.3 | $\pi_1(|G|)\cong F_{\beta_1}$(van Kampen) | M2 |
| E1.4 | 阿贝尔化(左伴随) | M2 |
| E1.5 | $\operatorname{rank}=\beta_1$ | OBS |

观察:**$GL_n(\mathbb Z)$ 是 $\mathrm{Aut}(F_n)$ 的线性化(经 $\mathrm{Aut}(F_n)\to GL_n(\mathbb Z)$ 满射)`[T](bg)`**——LA 在这里是"群结构的阿贝尔一阶近似",而不是出发点。**[H]** 这与 `01` §5 的"线性化机制"一致。

**E2:凸优化原问题 ⇒ Lagrange 对偶(Legendre–Fenchel)**

| ID | 变换 | 机制 |
|---|---|---|
| E2.1 | 约束问题 → 无约束 Lagrange 鞍点问题 | M5 |
| E2.2 | 对偶函数/共轭 $f\mapsto f^*$ | M3 |
| *E2.3* | *弱对偶 $d^*\le p^*$(**恒成立**)* | `lax`/序 claim |
| *E2.4* | *强对偶(Slater 条件下相等)* | M5 的 `under` |
| *E2.5* | *Fenchel–Moreau:闭凸正常函数 $f^{**}=f$* | M3 的自反性假设 |

共 **7 个变换 + 3 条 claim**:全部落入既有机制,**新机制数 = 0**。
副产物:**弱对偶是"序值缺陷"**——`graded` 的 Γ 不能只是度量,还要能是**序**(间隙 $\ge0$,在假设下为 0)。

### 6. 选择偏差与有效性威胁

| # | 威胁 | 现状 |
|---|---|---|
| 1 | 四个走廊都终止于 LA | 以 E1/E2 部分缓解;**不足** |
| 2 | 走廊由项目方挑选 | 未缓解 |
| 3 | 分组者即本研究者,事后分配 | **未缓解**;需盲测 |
| 4 | 零残余是弱证据 | 以签名(`06` §4)半缓解 |
| 5 | **图-only 的走廊 C 会掩盖 `lax`** | **已观察到**:只有加 2 维例子才暴露 |
| 6 | **M0–M3 就是范畴论词汇**,压缩可能无关 MEL | **承认**:MEL 的增量不在"机制数目",而在**让每个机制可检验的契约字段** |
| 7 | 已知答案的"回头解释" | 未缓解 |

### 7. 对抗探针(快速,非穷举)

| 探针 | 落入的机制 | 是否需要新东西 |
|---|---|---|
| **Fourier 变换** | M1(谱基 = 特殊规范)+ M3(群 $G\to\hat G$ 对偶) | 否 |
| **蒙特卡洛采样** | M4 的 graded 变体 | **是**:$(\varepsilon,\delta)$ 概率分级(Γ 的新**参数**,非新字段);复合用 union bound |
| **持续同调** | M2 + `graded` | 否:稳定性定理 $d_B\le\lVert f-g\rVert_\infty$ 即 $L=1$ 的 Lipschitz 声明 `(bg)` |

3/3 落入,1 个新参数。**这些探针也是我自己选的。**

### 8. 判决实验(预注册,未执行)

**目的**:检验压缩是否稳健。
**设计**:
1. **留出走廊 ≥6 条**,由独立过程抽取(例如从教科书"定理 ⇒ 联系"的索引随机抽 12 条,再由第三方挑 6 条),其中 **≥3 条终点不是 LA**。
2. **盲标注**:两位独立标注者(或两个不同 LLM + 一位人类审核),**只看 `06` §4 的签名**,把每个变换归入 M0–M5 / PT / OBS / "无法归类"。
3. **指标**:覆盖率、"无法归类"比例、标注者间一致性(Cohen's $\kappa$)。

**失败判据(任一成立即判压缩不成立)**:
* 留出集中 >30% 的变换需要新机制;
* $\kappa<0.6$;
* 按缺陷类型合并后,独立存活的机制 <3。

**成功判据**:覆盖 ≥70%,$\kappa\ge0.6$,且新增需求仅为参数而非字段。

### 9. 对 Q7、Q6 的回答

**Q7**:重复机制**确实出现**:**5 个有较强证据(M1、M2、M3、M5,较弱的 M4)**,**2 个只是模式(PT1、PT2)**,**1 个契约成分(OBS)**,**1 个应当被否决为原语(离散化)**。不强行给数;盲测之前,**"5(±1)"**是诚实的区间。
**Q6**:四走廊**无需新增字段**即可表达;**但需要两项结构性扩展**:`lax` 模式、带规范作用的坐标类型;以及一项**参数扩展**:Γ 需包含序、germ、$(\varepsilon,\delta)$。

### 10. 局限

* 本文件的分组与评价都是我完成的,**没有独立复核**。
* 未做任何自动化的"分解"——只是人工分类 + 数值验证个别例子。


---

## 附录 13 — 复合模型

> 对应 §13、Q8。问题:**什么时候两个变换可以复合?复合后契约是什么?**
> 标签见 `01-…`;数值例子来自 `experiments/sanity_checks.py`(S1–S5)。

### 0. 结论

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

### 1. 复合有定义的条件

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

### 2. 逐模式复合律

#### 2.1 `exact`
交换方块粘贴。$\mathrm{exact}\circ\mathrm{exact}=\mathrm{exact}$。

#### 2.2 `graded`:仿射误差幺半群 `[T]`
每个阶段:理想映射 $f_s$,实现 $\hat f_s$,
$$d(\hat f_s(x),f_s(x))\le\varepsilon_s,\qquad f_s\ \text{是}\ L_s\text{-Lipschitz}.$$
则
$$d(\hat f_2\hat f_1x,\ f_2f_1x)\le d(\hat f_2\hat f_1x,\ f_2\hat f_1x)+d(f_2\hat f_1x,\ f_2f_1x)\le\varepsilon_2+L_2\varepsilon_1.$$
即阶段契约 $(L,\varepsilon)$ 按
$$(L_2,\varepsilon_2)\ast(L_1,\varepsilon_1)=(L_2L_1,\ \varepsilon_2+L_2\varepsilon_1)$$
复合——这是仿射映射 $t\mapsto Lt+\varepsilon$ 的复合,**结合、有幺元 $(1,0)$**(`S4` 随机三元组验证)。
**稳定常数 $L_2$ 必须由下游声明**;缺失则 grade 取 $\top$,并标记 `UNSTABLE`。

**实测(S4)**:噪声 $\varepsilon_1=10^{-6}$ 的采样后接中心差分求导($L_2\approx1/h$,截断 $\varepsilon_2=h^2/6$):$h=10^{-1},10^{-2},10^{-3},10^{-4}$ 的实测最大误差 $1.60\times10^{-3},1.13\times10^{-4},9.97\times10^{-4},9.76\times10^{-3}$,**均不超过**复合界 $1.68\times10^{-3},1.17\times10^{-4},1.00\times10^{-3},1.00\times10^{-2}$;最后一档表明放大约 $10^{4}$ 倍。

#### 2.3 序型 grade(不等式)
$e_1\le e_2$ 且下游 $g$ 单调 ⟹ $g(e_1)\le g(e_2)$。例:弱对偶间隙 $d^*\le p^*$;Jensen。

#### 2.4 概率 grade $(\varepsilon,\delta)$
阶段 1 为 $(\varepsilon_1,\delta_1)$,阶段 2 为 $L_2$-Lipschitz 且 $(\varepsilon_2,\delta_2)$ ⟹ 复合为 $(\varepsilon_2+L_2\varepsilon_1,\ \delta_1+\delta_2)$(union bound)。**不需要阶段间独立,但要求阶段 2 的 $(\varepsilon_2,\delta_2)$ 保证对*任意输入*成立**(包括阶段 1 的随机输出);若阶段 2 只对固定输入有保证,该规则不适用。界较松。

#### 2.5 germ/局部 grade
局部余项 $o(\lVert h\rVert)$ 在复合下封闭当且仅当下游在像点可微(链式法则带余项)。**与 Lipschitz 不是一回事**:此时误差不按 $L\varepsilon$ 传播,而是被 jet 本身携带。

#### 2.6 `lax`:**未解**
两个 `lax` 方块的粘贴是 2-胞腔的纵横复合,**逻辑上**没问题;但**缺陷对象**(如 $\mathrm{Tor}$)的复合是扩张问题,一般需要**谱序列**(Grothendieck、Künneth、UCT 的迭代)。本研究**没有**给出一般演算。在 MEL 里,**对多步 `lax` 复合,契约只能声明"缺陷 = 未定,需下游检查"**。

### 3. 信息损失与按 observable 的复合

**事实 `[T]`(集合论)**:$\ker(g\circ f)\supseteq\ker f$——**信息不会回来**。
对 observable $q$,令 $q$ 经 $f$ 可恢复 ⟺ $\exists\tilde q_f:\ q=\tilde q_f\circ f$。则

> $q$ 经 $g\circ f$ 可恢复 ⟺ $q$ 经 $f$ 可恢复,**且** $\tilde q_f$ 在 $\mathrm{im}f$ 上对 $g$ 的纤维为常值。

即复合是否保留 $q$,取决于**中间类型上的 $\tilde q_f$ 是否仍为 $g$ 的 `recovers`**。
实测(S5):2000 个随机有限情形中,**核对单调性无一例外**成立;但有 **20 例**中 $f$ 保留了 $q$、$g$ 把它毁掉——故**必须逐 observable 检查**。

### 4. 假设沿复合向后传播(wp)

$$\mathrm{requires}(T_2\circ T_1)=\mathrm{requires}(T_1)\ \wedge\ \mathrm{wp}_{T_1}(\mathrm{requires}(T_2)).$$
这是 Dijkstra weakest precondition(`(bg)`)的搬用 `[S]`。
例:`PF ∘ RW` 要求"源图强连通且非周期",**这是对源图的假设,不是对 $P$ 的**。

### 5. 命题:契约范畴(片段)

> **命题(草证)** 取:对象 = 类型(带 $\le$ 与规范桥);态射 = 契约 $(\mathrm{req},\,(L,\varepsilon),\,\rho)$,其中 $\rho$ 是声明的损失关系。按 §1–§4 的规则复合。则在**单值、全于 req 域**的变换片段上,复合**结合、有幺元**。

*证明草图。*
* **类型**:$\le$ 是预序,传递 ⟹ 复合的类型条件一致;恒等变换满足 $S\le S$。
* **假设**:$\mathrm{wp}_{T_2\circ T_1}=\mathrm{wp}_{T_1}\circ\mathrm{wp}_{T_2}$ 且 $\mathrm{wp}_{T_1}$ 对 $\wedge$ 分配 ⟹ 两种括号给出同一 requires。
* **grade**:仿射映射复合的结合律(§2.2),幺元 $(1,0)$。
* **损失**:$\rho(T_2\circ T_1)=\rho(T_1)\vee T_1^{-1}(\rho(T_2))$;原像与复合可交换 ⟹ 结合。
* **见证**:取最小是结合的。
□

> **范围声明**:这只证明了**片段**的结合性。多值对应、`lax`、概率 grade 的依赖结构、规范群胚的上闭链条件**均未纳入**。**没有机器形式化。**

### 6. 实例

#### 6.1 成功的复合

| # | 复合 | 结果 |
|---|---|---|
| S-1 | 走廊 D:Galerkin → 装配 → 求解 → 重构 | 总误差 = Céa 项 + 求解项;求解项系数含 $\mathrm{cond}(K)$(**基相关**:$32.2$ vs $2725.9$,S3) |
| S-2 | 走廊 B:RW → $P^n$ → 平稳律 | exact;假设向后传播:源图强连通且非周期 |
| S-3 | 走廊 A:$D(g)\circ D(f)$ 与换图 | exact;规范桥 $J\mapsto BJA^{-1}$ |
| S-4 | 走廊 C:Cells → $H_n$ → $\otimes\mathbb Q$ | `lax` 缺陷 = 0($\mathbb Q$ 平坦) |

#### 6.2 **被拒绝**的复合(检查器必须拒绝)

| # | 复合 | 拒绝原因 | 证据 |
|---|---|---|---|
| R-1 | Galerkin → 点式 $\Delta$ | 类型:$V_h\not\subset H^2$ | 结构类型 |
| R-2 | 噪声采样 → 无声明 $L$ 的求导 | grade $\top$ | S4:放大 $10^4$ |
| R-3 | RW → 顶点商图再 RW | 归一化对商不自然;除非强可 lump | S2:缺陷 0.100 |
| R-4 | $H_n(\,;\mathbb Z)\otimes\mathbb F_2$ 当作 $H_n(\,;\mathbb F_2)$ | `lax` 缺陷 $\ne0$ | S1:$\mathrm{RP}^2$,度 2,缺陷 $\mathbb F_2$ |
| R-5 | $f$ 保留 $q$ 但 $g$ 毁掉它却声称整体保留 | observable 流断 | S5:20/2000 |

> 注意:**这些"被拒绝"的例子是我知道答案的反例**(RT10)。检查器是否能**自动**拒绝它们未被实现测试。

### 7. 先例对照

| 本模型的部分 | 既有先例 |
|---|---|
| C2 + §4 | Hoare 逻辑、Dijkstra wp、assume–guarantee 契约(Benveniste 等)`(bg)` |
| §2.2 | 数值分析的误差传播;**近似保持归约(L-reduction)的复合常数相乘** `(bg)`;Lawvere 度量范畴的非扩张复合 `(web)` |
| §3 | 数据处理不等式;抽象解释中**Galois 连接可复合** `(web)` |
| C1 + 规范桥 | 群胚/descent;表示论中的 intertwiner |
| 整个契约的"成本 + 近似 + 保答案" | **Karp/Cook 归约**:保答案 + 多项式成本 `(bg)` |

### 8. 对 Q8 的回答

> **有"部分的"复合演算的证据**:对 `exact`、`graded`(含序、概率)、假设、信息(按 observable)、选择五个通道,有可证或可数值验证的规则,并能**拒绝**具体的非法复合。
> **缺口**:`lax` 缺陷的复合(同调代数的谱序列领域),多值对应,规范群胚的相容性。
> 因此:**不是一个统一演算,而是"一个小的、按通道的演算 + 一个已知困难的角落"**——与 Outcome B 一致。


---

## 附录 14 — 非空洞性与失败模式

> 对应 §18、Q9。**这可能是整项研究最重要的部分**:MEL 很容易变得"普适但无意义"。
> 标签见 `01-…`。

### 0. 结论

> 1. 语言**无法在语义上强制**非空洞性——任意函数是否保持任意结构是不可判定的(Rice 型限制)。MEL 能做的是:**(i)句法闸门**拒绝明显空洞的契约;**(ii)把"证据状态"变成一等字段**;**(iii)要求可执行的证伪器(变异测试)**。
> 2. 空洞性不是二值的,而是**梯度**:R0 → R3。
> 3. 五个 prompt 里的平凡化(恒等、零编码、自由向量空间、答案预计算、任意宽的 StructuredMap)**全部可被闸门 G1–G6 的某一条拦住**,但**每条闸门都有残余风险**(§3)。

### 1. 空洞性梯度

| 级别 | 含义 | 要求 | 地位 |
|---|---|---|---|
| **R0** 可表示 | 存在某种编码 | 无 | **不构成 bridge**(拒绝) |
| **R1** 可恢复 | 某个**声明的 observable** 可由目标表示恢复:$q=\tilde q\circ E$ | `recovers q`,通过 G1、G5、G6 | 可作 `lowering` |
| **R2** 操作可对应 | 源操作有目标对应物,且对声明片段**自然**:$E(\mathrm{op}\,x)=\widetilde{\mathrm{op}}(E\,x)$ | R1 + G2 + G4 | 可作 `bridge` |
| **R3** 真杠杆 | 目标侧有**具名**定理/算法给出源侧 observable 的可计算性/可判定性/复杂度优势 | R2 + G3 | 推荐 agent 路由 |

> 对应 prompt 的 R0–R3:R0 = 序列化;R1 = 性质恢复;R2 = 操作对应;R3 = 数学/计算杠杆。

### 2. 六道闸门

| 闸门 | 内容 | 可检验形式 |
|---|---|---|
| **G1 可证伪** | 每条 claim 有可反驳实例;所涉 observable 在域上**非常值**;claim 不是由类型本身蕴含的 | 域内存在 $x,x'$ 使 $q(x)\ne q(x')$ |
| **G2 自然性/一致性** | 适配器在声明域上**统一**定义,不看被查询的答案;claim 对**操作及其复合**成立,而不是单个实例 | 对 op、op∘op 抽样验证;不得读 $q(x)$ |
| **G3 杠杆见证** | 至少点名一个目标理论中的定理/算法,用于计算或证明源 observable,并说明所得(可判定性/复杂度/可用定理) | 文字 + 引用 |
| **G4 变异测试** | 契约自带至少一个**变异适配器**(故意做错),且 claim 检查在其上**失败** | 可执行测试 |
| **G5 非自由目标 + 封闭词汇** | 目标 Structure 至少含一条非平凡公理;claim 只用 `exact/graded/lax` | 句法检查 |
| **G6 非退化域与分级** | 域含 ≥2 个 $q$-可区分点;分级容差 < $q$ 的值域直径 | 数值/符号 |

### 3. 逐个攻击

| 平凡化 | 为什么会骗过朴素 MI | 拦住它的闸门 | 残余风险 | 测试 |
|---|---|---|---|---|
| **恒等**:$E(x)=x,\ \widetilde{op}=op$ | 7 元组里所有等式都成立 | **G3**:无任何"目标理论里的新东西"可点名;**G5**:目标 Structure 与源同谱系 | "新东西"的认定带主观成分 | 要求写出:使用了目标侧哪个定理 |
| **零编码**:$E(x)=0$ | 若 $\widetilde{op}=0$,等式恒成立 | **G1**:observable 常值 ⟹ 无可证伪实例;**G6** | 低 | 域内取两个不同 $q$ 值,检查读出 |
| **自由向量空间** $X\to k[X]$ | 忠实、函子、真有定理 | **G3**:自由化本身不是杠杆;须用到线性结构的**解释**(混合/叠加)与具名定理;**R0 不计入证据** | 难以机械判定"线性结构被用了" | 看是否调用了目标侧定理(如 PF、谱隙) |
| **答案预计算**:适配器算出答案并存入表示 | $q=\tilde q\circ E$ 成立;`recovers` 满足 | **G2**:适配器须不看答案;claim 对**复合**成立——预存的答案不随 op 复合更新;**G4** 变异 | **单次 observable、无复合**时 G2 失效 ⟹ 需**成本声明**(适配器代价 ≤ 直接算 $q$) | 对 $\mathrm{op}^n$ 复验;成本比较 |
| **任意宽的 StructuredMap** | 任意函数都能配上元数据 | **G1+G5+G4**:必须有可证伪、非常值、有变异测试;只有类型而无 claim 的,标为 `OpaqueFunction`,**不得**作为 MEL-valid bridge | **Rice**:语言不能判定 claim 真假 ⟹ 只能靠证据状态 | 对抗式:红队写"能通过闸门的空洞契约",统计通过率 |
| **平凡分级**:$\varepsilon=\infty$ 或 $\varepsilon>\mathrm{diam}(q)$ | claim 恒真 | **G6** | 低 | 数值 |
| **空洞假设**:`requires` 不可满足或域为单点 | 蕴含恒成立 | **G6** | 低 | SAT/CAS 抽样 |
| **规范自封**:把一切都声明为"规范选择",从而 observable 都"不变" | 不变性被空洞满足 | **规范群必须显式给出**,且不变性声明须在群的轨道上**检验**(`05` §3.3) | 轨道检验的覆盖度 | 数值抽样规范群元素 |
| **见证自引**:`witness: asserted` | 契约形式完整 | 证据状态进入复合(C7:取最小);`asserted` 不能支撑 R3 | 仍可被人误读 | 导出报告按证据状态着色 |
| **自由理论塌缩**:无公理的 Structure | "一切都是 Structure" | **G5**,以及 Mathlib 式准入:新理论须说明"有什么真实定理要做"`(web)` | 理论库治理 | 库条目审查 |

### 4. 正例与反例的闸门演示

| 候选 bridge | G1 | G2 | G3 | G4 | 级别 | 说明 |
|---|---|---|---|---|---|---|
| 图 → $\mathbb R^V$(仅序列化) | ✗ | — | ✗ | ✗ | **R0** | 无 claim |
| 缓存最短路答案到适配器 | ✓ | **✗** | ✗ | ✗ | R1 以下 | 预计算 |
| 编码 $E(x)=0$ | **✗** | — | — | — | 拒绝 | 常值 |
| 邻接谱判二部性:连通图是二部图 ⟺ $-\lambda_{\max}$ 是特征值 `(bg)` | ✓ | ✓ | ✓(Perron–Frobenius) | ✓(扰动一条边) | **R3** | 有定理见证 |
| $\mathbb F_2$ 上高斯消元求 $\beta_1$ 并读出环秩/挠 | ✓ | ✓ | ✓(多项式算法) | ✓(翻转取向符号 ⟹ $\partial\partial\ne0$,**需 2 维**) | **R3** | 对纯图的 `∂∂=0` 空真 |
| 图 → Markov 核(只写算子,不用 Markov 结构) | ✓ | ✓ | **✗** | ✓ | **R2** | 无杠杆 |
| 图 → Markov 核 + PF + 谱隙混合时间 | ✓ | ✓ | ✓ | ✓(列归一化变异) | **R3** | |
| Galerkin:$V\to V_h\to(K,b)$ | ✓ | ✓ | ✓(Céa + 多项式求解) | ✓(破坏对称性) | **R3** | |

### 5. 失败模式清单(不限于 prompt)

1. **R0 当成证据**:"所有东西都能矩阵化"——已被 R0–R3 梯度和 G3 否定。
2. **坐标污染**:在抽象层写指标;或把坐标依赖量(`cond K`、Gram 的特征值)当语义 observable。
3. **隐含系数/度量**:$\mathbb Z/\mathbb Q/\mathbb F_2$、范数、测度默认。
4. **选择掩盖**:把非规范归一化当成规范(RW 的 `norm`)。
5. **假设丢失**:PF 不可约、Lax–Milgram 强制性在复合中被遗忘。
6. **稳定性缺失**:graded 复合缺 $L$。
7. **自反性默认**:$V=V^{**}$ 被默认(无穷维错)。
8. **过度整齐**:缺陷账本本身可能是"事后看起来整齐"(`17` RT5)。
9. **LLM 流畅造假**:字段填满但语义错误(`15`)。

### 6. 非空洞性的能力边界

* **能做**:拒绝明显空洞的契约;迫使证据状态外显;提供可执行证伪器。
* **不能做**:判定 claim 的真假(Rice);判定"杠杆"的主观部分(G3);防止有意构造的、通过闸门的空洞契约(只能靠对抗测试降低概率)。
* **因此**:非空洞性是**证据体系**,不是**语言性质**。这一点必须在文档里写明,不应让读者以为"MEL 类型检查通过 = 数学上有意义"。


---

## 附录 15 — Agent-native 语言分析

> 对应 §19、Q11(部分)与 RT6。**不要把 LLM"理解"当作语义精确性的证明。**
> 标签见 `01-…`。

### 0. 结论

> 1. "Agent-native 内部、人类可读投影"在**数学上不是新东西**:OpenMath/MathML 的"内容语义 + 呈现投影"早有此分离 `(web)`。它是**工程原则**,不是数学性质。
> 2. 对 agent 真正有价值的是几项**可检验的设计约束**:封闭词汇、强制字段、可机器检查的证据状态、稳定标识、类型导向的路径搜索。
> 3. **字段填满 ≠ 语义正确**。LLM 能流畅地填出所有字段并且错。因此 MEL 必须把验证外包给**可执行/可形式化的检查器**,而不是 LLM 的一致意见。
> 4. 本研究**没有**做任何 LLM 翻译可靠性实验;下面所有 LLM 相关的陈述都是**设计与待测假设**。

### 1. 架构与信任边界

```
人类数学语言
     ↕   (不可信:LLM 翻译)
LLM / 数学 agent
     ↕   (不可信:LLM 产出 MEL)
MEL        ── 类型检查器(可信:句法/结构) ──┐
     ↕                                       │ 证明义务
Lean / CAS / 数值求解器 / 搜索 / 证明系统   ←──┘  (可信:各自的内核/实现)
```

* **只有**类型检查器与后端检查器在信任边界内。
* LLM 两端(NL→MEL、MEL→NL)都**不可信**,必须被"检查器 + 变异测试 + 往返测试"包住。

### 2. 哪些必须显式、哪些可推断

| 字段 | 可推断? | 规则 |
|---|---|---|
| 理论引用与参数(维数、域/环、度量、测度) | **绝不可隐含**(尤其**系数环**、**范数**、**测度**) | 须显式;可用标记过的默认 `default:ℝ` |
| 规范/选择(基、取向、归一化、网格) | **绝不可隐含** | 写明群(oid) |
| `requires` | 部分可推断(从上游 `guarantees`) | 推断出的须标 `inferred` 并作为证明义务 |
| `recovers q`(purpose) | **绝不可隐含** | 缺失 ⟹ 只能视为 R0 |
| 分级模式与 Γ | **绝不可隐含** | 缺失 ⟹ 默认 `exact`,**并警告** |
| 变性(协/反变) | 可由构造推断,但须在类型里显式 | |
| 等价记号("相等"指严格/同构/近似) | **绝不可隐含** | |
| 量词顺序($\forall\varepsilon\exists\delta$) | **绝不可隐含** | |
| 恒等规范桥、平凡规范 | 可推断 | 标 `default` |
| `witness` | **绝不可隐含** | 缺失 ⟹ `asserted` |
| 成本 | 可省略 | 仅 R3 在 G2 不足时必填 |

### 3. LLM 能否可靠翻译?(假设与实验,**未做**)

| 假设 | 检验方式 | 判据 |
|---|---|---|
| H1 NL → MEL 翻译的**字段完整率**高 | 在 50 条固定陈述上统计 | 完整率 |
| H2 完整 ≠ 正确 | 对每个产出跑**执行检查**(数值/CAS/Lean) | 通过率远低于完整率则 H2 成立 |
| H3 两个不同 LLM 产出**语义等价**的 MEL | 见 §4 的三级等价 | 一致率 |
| H4 往返(MEL→NL→MEL)稳定 | 往返后契约等价 | 稳定率 |
| H5 MEL 比"直接写 Lean"或"自然语言"更稳 | A/B 对照 | 错误率 |

> 先验:我**没有**证据支持 H1–H5 中任何一个为真或假。H2 在一般文献经验上更可能成立(`(bg)` 自动形式化综述的普遍发现是"语法正确但语义偏离"常见;检索命中 <https://arxiv.org/html/2505.23486>,**未阅读**)。

### 4. "语义等价的 MEL"与"一致性"(conformance)

两个文档 $D_1,D_2$ 的等价**不能**靠 LLM 的"我觉得一样":

| 级别 | 定义 | 判定 |
|---|---|---|
| **E0 句法等价** | 经规范化(别名消解、字段排序、$\alpha$-重命名)后相同 | 机器 |
| **E1 契约等价** | 互相蕴含各 claim(含 requires、loses、recovers) | 证明义务(后端) |
| **E2 观测等价** | 在固定夹具集上,所有 claim 的检查结果一致、所有 observable 读出一致 | 可执行 |

**一致性(conformance)级别**:

| 级别 | 含义 |
|---|---|
| **C0** | 解析 + 类型检查通过 |
| **C1** | 契约自洽:各 claim 类型良构;`requires` 在夹具上可满足;通过闸门 G1、G5、G6 |
| **C2** | 可执行一致:适配器在夹具上运行,claim 数值/符号验证通过;变异测试(G4)按预期失败 |
| **C3** | 形式化:关键 claim 有 Lean 证明或被接受的引用 |

LLM 一致意见**至多**证明"不同模型倾向于产生同一文本",**不证明**数学正确。

### 5. 显式性的收益与成本

| 收益 | 成本 |
|---|---|
| 假设、选择、系数环不再被沉默 | 对人类冗长 |
| 复合检查可机器执行(C1–C8) | 需要维护理论库 |
| 路径搜索可类型导向(给定源类型与目标 observable,搜索可复合路径) | 路径爆炸取决于词汇表大小(见 `12`:词汇表小才可搜索) |
| 证据状态可汇总("这条路径 80% `cited`,20% `asserted`") | 证据状态的**准确性**仍依赖人/工具 |

> **类型导向路径搜索**是一个具体的 agent 用例:相当于"数学的 Hoogle"。它**是否可行**完全取决于压缩检验(`12`):若转换词汇表小,路径搜索可行;若随领域线性增长,不可行。

### 6. 对 RT6("agent-native 是产品修辞")的回应

* **承认**:"agent-native"本身不是数学概念,没有可证伪内容。
* **转化**:把它替换为**五项可检验设计要求**:
  1. 封闭词汇(模式、规范作用、证据状态);
  2. 强制字段(`recovers`、`witness`、`choice`);
  3. 稳定标识与别名显式;
  4. 验证外包给检查器;
  5. 路径搜索可行性(受压缩检验支配)。
* **剩余的开放问题**:是否这些要求相比"直接用 Lean + 少量约定"带来**可测的**改善——需 H5 的 A/B 实验。

### 7. 局限

* 没有实现、没有 LLM 实验。
* "agent 能容忍更多显式性"的前提本身未被验证。


---

## 附录 16 — MEL v0.1 候选

> 对应 §24。**"当且仅当证据支持才提出候选。"**
>
> **证据判断**:证据支持一个**小而有限**的候选(四走廊 + 两个控制 + 三个探针),但:(i)压缩检验的判决实验**未做**(`12` §8);(ii)核的大部分是既有范畴/类型论内容(`03`)。
> 因此本文把 v0.1 定位为 **"待证伪的规约假设"**,**不是**"可以开始实现的规范"。
> 标签见 `01-…`。

---

### 1. 最小语义实体

| 实体 | 内容 | 备注 |
|---|---|---|
| **Structure** $S$ | 理论引用 + 参数 + 精化 + 变性 | 类型层 |
| **Object** $x:S$ | $S$ 的居民 | 项层 |
| **Transformation** $T:S\Rightarrow S'$ | 结构化对应 + 构造 + 契约 | 操作层 |
| **Claim** | 复合表达式间的陈述,模式 $\in\{\textsf{exact},\textsf{graded},\textsf{lax}\}$ | 语义上可导出,语法上保留 |
| **复合规则** | `13` 的 C1–C8 | 规则,非实体 |
| **分级参数 Γ** | `Bool`、仿射 $(L,\varepsilon)$、序间隙、germ、$(\varepsilon,\delta)$ | 参数,非实体 |
| 元数据 | `ns`、`tags`、`witness`、可选 `cost` | 不入类型相等 |

**指称语义草图**:
* $[\![\mathsf{Th}]\!]=\mathbf{Mod}(\mathsf{Th})$;$[\![S]\!]$ 是被 $\varphi$ 切出的满子范畴。
* $[\![T:S\Rightarrow S']\!]=R_T\subseteq|S|\times|S'|$,由构造 $c$ 呈现,且在 `requires` 域上全。
* $[\![\textsf{exact}\ e_1\approx e_2]\!]$:两关系在域上相等;$[\![\textsf{graded}\,\Gamma]\!]$:Γ-值距离界;$[\![\textsf{lax}]\!]$:存在典范 $\kappa$,缺陷 = $\mathrm{cone}(\kappa)$。

### 2. 语法(紧凑 EBNF)

```
module  ::= (struct | tr)*
struct  ::= 'struct' ID params? ('where' φ)? ('var' ('+'|'-'))? ('ns:' path)? ('tags:' {tag,…})?
tr      ::= 'tr' ID params? ':' type '⇒' type '{' field* '}'
field   ::= 'requires' φ
          | 'choice'  ID ':' type ('gauge' G)?
          | 'claim'   mode expr '≈' expr ('Γ=' grade)? ('under' φ)? ('witness:' w)?
          | 'natural' '[' class ']'
          | 'stable'  'L=' num
          | 'loses'   rel
          | 'recovers' obs (',' obs)*
          | 'coord'   chart-decl '⇒' 'Coord' '[' action ',' shape ']'
          | 'cost'    expr                       -- 可选,附属
mode    ::= 'exact' | 'graded' | 'lax'
grade   ::= 'Bool' | 'Aff(L,ε)' | 'Order' | 'Germ@p' | 'PAC(ε,δ)'
action  ::= 'Hom' | 'Endo' | 'Bil' | 'Perm' | …   -- 规范作用
w       ::= 'formal(ref)' | 'checked(tool)' | 'cited(ref)' | 'asserted'
```

约定:`⇒` 表示变换(对应);`∘` 为复合;`*` 为对偶;`~` 为声明的等价。

### 3. 类型系统(摘要,详见 `05`)

* 类型 = ⟨理论引用;参数;精化;变性⟩。
* **判定**:理论包含、参数合一、规范桥、变性。**证明义务**:精化蕴含、claim 真值。
* 坐标类型 `Coord[action, shape]` 携带规范作用。
* `ns`/`tags` **不入类型相等**。

### 4. 变换契约

| 字段 | 必填? | 含义 | 空洞性守卫 |
|---|---|---|---|
| `from/to` | 必填 | 源/目标类型 | G5(目标非自由) |
| `requires` | 必填(可为 `true`) | 对应的"全"缺陷 | G6 |
| `choice` | 若构造非规范则必填 | 选择 + 规范群(oid) | 规范须显式,不变性须检验 |
| `claims` | **≥1,否则不是 bridge** | 带模式、Γ、`under`、`witness` | G1、G4 |
| `natural[class]` | 若声称函子性 | 对哪类源态射自然 | 范围须声明 |
| `stable L=` | 若可作下游 graded 复合的上游 | 稳定常数 | 缺失 ⟹ Γ=$\top$ |
| `loses` | 必填(可为 `none`,但被警告) | 核对 / 规范轨道坐标 / observable 集 | 与 `recovers` 成对 |
| `recovers` | R1 以上必填 | purpose | G1、G6 |
| `coord` | 若降到坐标层 | 图/基 ⇒ `Coord[…]` | 规范作用 |
| `witness` | **强制**(于每条 claim) | 证据状态 | 缺失 ⟹ `asserted` |
| `cost` | 可选 | 附属;挂坐标层 | 不入语义核 |

### 5. 复合

> $T_2\circ T_1$ 有定义 ⟺ C1–C8 全部满足(`13` §1)。

```
compose(T1, T2):
  1. 类型     S′ ≤ S″  或 存在规范桥 β            (类型检查器)
  2. 假设     guarantees(T1) ⊨ requires(T2)        (证明义务;传播 wp)
  3. claim    逐模式:exact 粘贴 | graded 用 (L,ε)*(L,ε) | lax 标记"缺陷未定"
  4. 观测     对每个 q∈recovers(T1):q̃ ∈ recovers(T2)?  否则从复合的 recovers 中剔除
  5. 选择     choices = choices(T1) ⊎ choices(T2),经 β 粘合
  6. 见证     min(witness)
```

### 6. 信息损失的表示

`loses` 取三种形式之一(不得省略不写):
```
loses  ~   : x ~ x′ ⇔ φ(x,x′)           -- 核对(显式关系)
loses  orbit(G)                            -- 丢失的是规范轨道坐标(如行尺度)
loses  obs{q₁,…}                           -- 丢失的 observable 集合
loses  none                                -- 声称无损;触发"是否同构?"的检查
```
`loses` 与 `recovers` **成对**:损失只有相对 observable 才有意义(`10` §6)。

### 7. 近似

| Γ | 复合 | 例 |
|---|---|---|
| `Bool` | 平凡 | 精确 |
| `Aff(L,ε)` | $(L_2L_1,\ \varepsilon_2+L_2\varepsilon_1)$ | Céa;数值误差 |
| `Order` | 单调下游 | 弱对偶;Jensen |
| `Germ@p` | 下游在像点可微 | 局部余项 |
| `PAC(ε,δ)` | $(\varepsilon_2+L_2\varepsilon_1,\ \delta_1+\delta_2)$ | 蒙特卡洛 |

近似**不得隐藏误差语义**:graded claim 必须写出 Γ 与(若作上游)`stable L`。

### 8. 等价

| 等价 | 定义 | 用途 |
|---|---|---|
| $\approx_q$(对象,对 observable $q$) | $q(x)=q(x')$,即 $\ker q$ | "对某目的等价" |
| $f\approx_q g$(变换) | $q\circ f=q\circ g$(在域上) | 观测等价 |
| 规范等价 | 存在 $\beta\in$ 规范群胚,$\beta\circ\mathrm{pres}_1=\mathrm{pres}_2$ | 换表示 |

### 9. 坐标层

* **抽象层不得出现下标。** 坐标进入的唯一入口是 `coord`。
* `coord(T,B,C):Coord[A,(m,n),k]`,满足 $[g\circ f]=[g][f]$。
* 规范作用表:

| action | 规范 | 完备/典型不变量 | 例 |
|---|---|---|---|
| `Hom` | $PAQ^{-1}$ | 秩 | Jacobian |
| `Endo` | $PAP^{-1}$ | 谱、Jordan | 转移矩阵 $P$ |
| `Bil` | $P^{\!\top}AP$ | 惯性 | 刚度矩阵 $K$、度量 |
| `Perm` | $\Pi A\Pi^{\!\top}$ | 同构不变量 | 邻接 |

* **成本**(`cond K`、稀疏模式)**只挂在坐标层**,不是规范不变量(`11` §3)。

---

### 10. 五个示例

#### 10.1 导数 / 切映射
```
tr D : (f: Smooth(M→N), p: M) ⇒ Lin(T_pM, T_{f p}N)
  requires  f 在 p 处 C¹
  claim exact  D(g∘f,p) = D(g,f p)∘D(f,p)                   witness: cited
  claim graded f(p+h)−f(p)−D(f,p)h = o(‖h‖)     Γ=Germ@p     witness: formal(def)
  natural[PointedSmoothMap]
  loses     ~ : f~g ⇔ f(p)=g(p) ∧ D(f,p)=D(g,p)             -- 1-jet
  recovers  rank, ker, im
  coord     图 φ@p, ψ@f p ⇒ Coord[Hom,(m,n),ℝ]              -- 规范 GL_n×GL_m
```

#### 10.2 图 → Markov 核
```
tr RW[norm ∈ {row,lazy}] : WGraph(V,W) ⇒ Stoch(|V|)
  requires  W ≥ 0 ; ∀v. deg(v)>0
  choice    norm : Slice(RowScaling)      gauge diag(ℝ>0)^|V|
  claim exact  P = D⁻¹W                      (norm=row)                witness: formal(def)
  natural[GraphIso]                                                    -- 对顶点商不自然
  loses     orbit(RowScaling)               -- 无向对称 W:仅差全局标量
  recovers  walk probabilities; (不可约+非周期)平稳律、谱隙
  coord     Coord[Perm,(|V|)]  -- 邻接;  [P]: Coord[Endo,(|V|),ℝ]
```

#### 10.3 拓扑 → 链复形 → 同调 → 系数变换
```
tr Cells : SimplicialComplex(K) ⇒ Chain[R]
  requires  K 有限
  choice    o : Torsor({±1}^{cells})          gauge 符号
  claim exact ∂∘∂ = 0 ;  natural[SimplicialMap]
  recovers  β_n(k), χ
tr H_n : Chain[R] ⇒ Module_R                        -- 泛构造(余核)
tr BaseChange[k] : Module_R ⇒ Vect_k
  requires  R→k 环同态
  claim lax   κ : H_n(C)⊗_R k ↪ H_n(C⊗_R k)   defect=Tor₁^R(H_{n−1}(C),k)
              under Tor₁^R(H_{n−1}(C),k)=0                              witness: cited(UCT)
  claim exact χ(C⊗k)=χ(C)
  loses     obs{挠}
```
> 验证(`experiments/sanity_checks.py` S1):$\mathrm{RP}^2$、$k=\mathbb F_2$、度 2 时缺陷 $=\mathbb F_2\ne0$。

#### 10.4 条件期望
```
tr CondExp[𝒢] : L²(Ω,ℱ,P) ⇒ L²(Ω,𝒢,P)
  requires  𝒢 ⊆ ℱ
  claim exact  E∘E=E ; E*=E ; E[1]=1 ; X≥0 ⇒ E[X]≥0
  claim exact  E[X] = argmin_{Y∈L²(𝒢)} ‖X−Y‖₂            -- 正交投影
  claim graded φ(E[X]) ≤ E[φ(X)]     Γ=Order  under φ 凸    -- Jensen
  stable    L=1
  loses     ~ : X~X′ ⇔ E[X]=E[X′]                         -- 与 L²(𝒢) 正交的部分
  recovers  𝒢-可测 observable;  E[X·Z] (Z 𝒢-可测)
```

#### 10.5 连续 → 有限维逼近
```
tr Galerkin[V_h,basis] : Variational(V,a,ℓ) ⇒ LinSys(n)
  requires  a 有界(M)、强制(α);ℓ∈V*;V_h⊂V 有限维
  choice    V_h : Subspace(V) ;  basis : Torsor(GL_n)  gauge K↦SᵀKS
  claim exact  a(u−u_h, v_h)=0  ∀v_h∈V_h
  claim exact  (a 对称) u_h = argmin_{v∈V_h}‖u−v‖_a
  claim graded ‖u−u_h‖_V ≤ (M/α)·inf_{v∈V_h}‖u−v‖_V   Γ=Aff(L=M/α, ε=0)
  claim exact  R_h∘P_h = id_{V_h}
  stable    L=1/α
  loses     V_h 之外的一切
  recovers  能量 a(u_h,u_h);误差界
  coord     K : Coord[Bil,(n),ℝ]      cost: cond(K)   -- 基相关,仅注记
```
> 验证(S3):Galerkin 正交性 $1.2\times10^{-15}$;$u_h$ 为能量范数最佳逼近;$\mathrm{cond}$ 随基变化 32.2 → 2725.9。

---

### 11. 一致性检查清单(给检查器)

1. 每个 `tr` 至少一个 `claim` 或 `recovers`(否则标 `OpaqueFunction`)。
2. 每个 `claim` 有 `witness`(缺失 ⟹ `asserted`)。
3. 每个 `recovers q` 满足 G1、G6。
4. 每个 `graded` 有 Γ;若作上游则有 `stable`。
5. 每个 `choice` 有规范群;凡声称"规范不变"的 observable 在群轨道上抽样通过。
6. 每个 `coord` 声明规范作用。
7. 契约自带至少一个变异适配器(G4)。
8. `ns/tags` 不参与类型检查。

### 12. 非目标

* 不是通用数学语言;不覆盖数论、逻辑、信息论(按 prompt 保持范围)。
* 不是证明系统;不替代 Lean/Mathlib。
* 不追求规范型。
* 不把成本放进语义。

### 13. 未解

* `lax` 缺陷的复合(`13` §2.6)。
* 多值对应与规范群胚的相容性。
* 与 MMT 的精确关系(`17` RT3)。
* LLM 稳定性(`15`)。
* Γ 是否已过度设计(`17` RT14)。


---

## 附录 17 — 红队评审

> 对应 §25。每项攻击格式:**Attack / Evidence for attack / Evidence against attack / Current verdict / What experiment would settle it**。
> **红队与被审对象出自同一作者**(本研究者),盲点必然相关;因此每项都附"判决实验",并在末尾追加元攻击。
> 标签见 `01-…`。

### 判决总览

| # | 攻击 | 判决 |
|---|---|---|
| RT1 | MEL = 范畴论 + 冗长元数据 | **对语义核基本成立**;契约纪律是剩余主张 |
| RT2 | MEL = 依赖类型论 | **对"可表达"成立**;MEL 的理由只能是渐进前端 |
| RT3 | MEL = OpenMath/MMT 换术语 | **对 Structure 层成立;Transformation 层未决** |
| RT4 | `StructuredMap` 太宽 | **对朴素形式成立**;靠闸门缓解,语言无法强制 |
| RT5 | 例子是挑选的 | **大体成立;未决** |
| RT6 | agent-native 是产品修辞 | **未测量前成立**;降为工程要求 |
| RT7 | 损失/目的/成本属应用层 | **分裂判决**:成本出核(同意);损失/目的留核(不同意) |
| RT8 | 通用 IR 不可能/不可取 | **通用语义 IR:同意;小规模枢纽集:可能,未决** |
| RT9 | LA 的规范型直觉不泛化 | **同意**;以 ITF 取代 |
| RT10 | 复合只在挑选的精确例子里成立 | **部分成立**;`lax` 复合未解 |

---

### RT1 — MEL 就是"带冗长元数据的范畴论"

* **Attack**:Structure = 理论,Transformation = (富足)对应,Claim = 交换方块/2-胞腔,grade = 富足基,复合 = 富足范畴的复合。没有任何东西超出 enriched/double category。
* **Evidence for**:`03`:每个组件都有名字很熟的先例(Lawvere 富足、关系代数、Galois 连接、assume–guarantee)。`06`:Transformation 就是"带缺陷声明的对应"。`12`:M0–M3 本就是经典范畴构造,压缩可能与 MEL 无关。
* **Evidence against**:范畴论**不强制声明**缺陷;MEL 的增量是**契约纪律**(必填的 `requires/choice/loses/recovers/witness`)、**按 observable 的复合检查**、**坐标类型携带规范作用**。这些是"规约"而不是"数学定理"。
* **Verdict**:**对语义核基本成立。** MEL 若有价值,价值在**规约纪律**,不在新数学。
* **Experiment**:把 `16` 的核在 Lean/Agda 里形式化。若它是**某个现成富足/double category 库的 1–2 页实例**,则攻击被证实,MEL 降为"规约文档";若需要实质性新构造(特别是 `lax` 复合),则有残余内容。

### RT2 — MEL 就是依赖类型论

* **Attack**:类型 = Structure,项 = Object,命题 = Claim,证明 = witness,精化 = 子类型。Lean/Mathlib 全部能写。
* **For**:`04` §4 自己承认 Claim 在语义上被依赖类型论覆盖。
* **Against**:(i)DTT 不**强制**声明损失/选择/目的;(ii)大量有价值的 witness 是**数值验证/文献引用**,无法放入内核;(iii)LLM 直接写完整证明代价高。MEL 作为**渐进(gradual)、证据状态外显**的前端有独立理由。
* **Verdict**:**表达力上成立;存在理由只能是"渐进前端"**——这是工程论证,不是数学论证。
* **Experiment**:把 `16` §10 的五个例子写成 Lean 4 + Mathlib;统计(a)多少条 claim 能直接用 Mathlib 现成引理证明,(b)多少需要定制开发,(c)多少只能 `sorry`/引用。若 (c) 占多数,说明渐进层有独立价值。

### RT3 — MEL 就是 OpenMath / MMT 换了术语

* **Attack**:MMT 有基础无关的理论、view、metadata;MitM 用中间本体做互操作;OpenMath 有内容字典。
* **For**:`03` `(web)`:MMT 的目的最近("经中间结构互操作");OpenMath/OMDoc 的"内容 + 呈现"分离早已存在。Structure 层**应当**直接在 MMT 写。
* **Against**:MitM 的 view 是**精确**理论态射;没有一等的 grade/`lax`/选择/按 observable 复合。**但**(我没有检验)MMT 的 metadata 与"基础无关"特性可能允许把这些作为**新基础**写进去。
* **Verdict**:**Structure 层被子集化;Transformation 层未决**。
* **Experiment**:用 MMT(+ 一个自定义基础)编码 `16` §10.2–10.5。若 `graded/lax` 需要**修改 MMT 内核或语义**,则 MEL 有残余;若仅需**写新理论**,则 MEL ⊂ MMT + 约定,应直接合并。

### RT4 — `StructuredMap` 太宽,什么也没说

* **Attack**:任意函数加元数据都是 StructuredMap;语言没有内容。
* **For**:`06`:对应比函数更宽;Rice 定理:语言无法判定 claim 真假;`14` 的"能力边界"。
* **Against**:闸门 G1–G6 拦住五个平凡化(`14` §3);`OpaqueFunction` 作为显式的"非 MEL-valid"类别;证据状态使"断言"与"已证"可区分。
* **Verdict**:**对朴素形式成立。** MEL 不应使用无约束的"StructuredMap"概念;非空洞性是**证据体系**,不是语言性质(`14` §6)。
* **Experiment**:**对抗式红队**:让若干 agent 在不知闸门细节的情况下,尝试写出"通过 G1–G6 但数学空洞"的契约;统计通过率及典型逃逸模式。

### RT5 — 每个例子都是因为"合适"才被选中的

* **Attack**:四个走廊都终止于 LA、都是项目方选的;分组由我完成、事后分配;零残余是弱证据。
* **For**:`12` §6 列了 7 个威胁,**多数未缓解**。尤其:**图-only 的走廊 C 会掩盖 `lax`**(`10`)——说明结论对实例选择敏感;"缺陷账本"过于整齐(`12` §4)。
* **Against**:加入了 E1/E2 控制与三个探针;**反例也被记录**(`lax` 与 `Γ=PAC` 是被迫扩张,而非事后套上去的)。
* **Verdict**:**大体成立,未决。**
* **Experiment**:`12` §8 的预注册盲测(≥6 条留出走廊,≥3 条终点非 LA,独立标注,$\kappa\ge0.6$,新机制 <30%)。

### RT6 — "Agent-native"是产品修辞,不是数学

* **Attack**:没有可证伪内容。
* **For**:`15`:无任何 LLM 实验;OpenMath 早有"内容 + 呈现"分离。
* **Against**:可转化为五项**可检验的设计要求**(封闭词汇、强制字段、证据状态外显、验证外包、路径搜索可行性)。
* **Verdict**:**在测量之前成立**;应从语言定位里降为"工程要求"。
* **Experiment**:`15` §3 的 H1–H5,尤其 H5 的 A/B(MEL vs 直接 Lean vs 自然语言)。

### RT7 — 损失 / 目的 / 成本属于应用,不属于数学语义

* **Attack**:这些是工程关切;数学语义只关心对象与态射。
* **For(成本)**:`11` §3 **实测**:$\mathrm{cond}(K)$ 随基变化 32.2 → 2725.9——成本不是规范不变量,不是语义。
* **Against(损失/目的)**:**复合的合法性取决于它们**(`13` §3:$q$ 能否经 $g\circ f$ 恢复由中间的 `recovers` 决定;`S5` 实测 20/2000 情形中 $g$ 毁掉了 $f$ 保留的 observable)。语义上,"对 $q$ 等价"= 观测等价,是**标准语义概念**(`03`)。
* **Verdict**:**分裂。** 成本:**同意**,出核,挂坐标层。损失/目的:**不同意**,留核——它们是复合律的参数。
* **Experiment**:构造一批路径,其中"若忽略 `recovers`,检查器会错误接受"的比例是多少?若很高,则 purpose 属语义;若很低,则可降级。

### RT8 — 通用中间表示不可能且不可取

* **Attack**:语义上没有统一底层;强行统一会破坏领域结构。
* **For**:项目早期结论 2.1;`07` §6:数学没有单一机器语义。
* **Against**:MEL **不声称**通用语义 IR;`07` §4 的 ITF 枚举显示**少数枢纽**吸收多数入口(链复形、Markov 核、Hilbert 算子、优化问题、群作用)。
* **Verdict**:**通用语义 IR:同意不可能。小规模枢纽集:有迹象,未决**——枢纽数是否随领域线性增长未测。
* **Experiment**:**枢纽普查**:取 100 个教科书级"跨域定理/构造"(随机抽样),统计有多大比例可经 ≤8 个 ITF 路由。

### RT9 — LA 的规范型直觉不泛化

* **Attack**:规范型来自半单性与驯服分类;别处不存在。
* **For**:`02`、`07` §2:wild 分类、不可判定性。
* **Against**:提出了弱化概念 ITF;规范型作为 PT2 **可选模式**保留(Smith、Jordan、SVD)。
* **Verdict**:**同意**;规范型已被移出核。
* **Experiment**:无需。

### RT10 — 复合只在特意挑选的精确例子里成立

* **Attack**:所有成功的复合都是精确或简单误差。
* **For**:`13` §2.6:`lax` 复合**未解**;**被拒绝的例子也是我知道答案的反例**;未实现检查器,没有自动化。
* **Against**:`13` §6.2 含 5 个**被拒绝**的复合,并有**数值证据**(S1、S2、S4、S5);graded 的仿射幺半群结合律已证。
* **Verdict**:**部分成立。**
* **Experiment**:**复合模糊测试**:从变换目录随机生成类型良好的路径,让专家独立标注"应接受/应拒绝",检查器的**假接受率**。

---

### 元攻击

#### RT11 — 单作者、同模型的盲点相关
正反两方均由同一研究者产出。**缓解**:所有判决实验都要求**独立**标注者;**未缓解**:本报告自身。

#### RT12 — 证据来源的不均匀
`(web)` 只覆盖约 12 次检索命中的页面;大量先例标 `(bg)`(背景知识,未复核)。**不应把 `(bg)` 当作已核实**。

#### RT13 — 过度整齐
"缺陷账本"、"机制 × 缺陷"表是事后组织,整齐本身是警告。若盲测中缺陷类型与机制不能独立标注,则该框架应当放弃。

#### RT14 — Γ 与 `lax` 是否过度设计?
`lax` 的唯一**强制**来源是走廊 C(Tor)与控制 E2(弱对偶),Γ 的概率版来自一个探针。**样本太少**,有可能是在为 3 个例子过拟合。**Experiment**:盲测里统计需要 `lax` / `PAC` 的变换比例;若 <5%,考虑降为扩展而非核。

#### RT15 — 本研究没有做什么
没有实现检查器;没有 LLM 实验;没有 Lean/MMT 形式化;未穷尽文献检索;控制走廊只有两条;样本全部是"已知答案"的教科书例子。


---

## 附录 S — 计算验证输出

`experiments/sanity_checks.py` 的实际运行输出(全部通过):

```text

== S1  Corridor C: RP^2 (6-vertex triangulation) - Tor defect under coefficient change ==
[OK]   every edge lies in exactly two triangles (closed surface)
[OK]   Euler characteristic V-E+F = 6-15+10 = 1
[OK]   boundary of boundary is zero (d1 @ d2 = 0)
       Betti numbers over Q  : [1, 0, 0]
       Betti numbers over F2 : [1, 1, 1]
       Smith normal form of d2 over Z: invariant factors > 1 = [2]  -> torsion of H_1(Z)
[OK]   H_*(RP^2;Z) = Z, Z/2, 0
[OK]   dim H_*(;Q) = (1,0,0) but dim H_*(;F2) = (1,1,1)
[OK]   Euler characteristic is coefficient-independent (= 1)
[OK]   universal coefficient theorem prediction [1, 1, 1] matches direct computation [1, 1, 1]
       Defect of the 'commuting square' H_n(C;Z)(x)k -> H_n(C(x)k) in degree 2 with k=F2: Tor(Z/2,F2)=F2 (dim 1)
[OK]   graph: boundary rank is orientation- and coefficient-independent (V-c)
[OK]   graph: no torsion (H_1 of a graph is free), so no Tor defect arises in 1-dim
       graph beta_1 = E - V + c = 9 - 7 + 1 = 3

== S2  Corridor B: weighted graph -> Markov kernel (loss, gauge, lumping) ==
[OK]   directed case: row-normalisation forgets W ~ Lambda*W (row scales are the lost information)
[OK]   undirected case: stationary law pi ~ degree
[OK]   undirected case: W is recovered from (P, pi) up to ONE global scalar
[OK]   spectrum of P equals spectrum of symmetric normalisation D^-1/2 W D^-1/2 (similarity by D^1/2)
       lazy ring n=24, t=20: max|P^t - 1 pi| = 8.37e-02,  |lambda_2|^t = 7.09e-01
       lazy ring n=24, t=60: max|P^t - 1 pi| = 3.10e-02,  |lambda_2|^t = 3.57e-01
       lazy ring n=24, t=120: max|P^t - 1 pi| = 1.06e-02,  |lambda_2|^t = 1.27e-01
[OK]   convergence rate of P^t is governed by |lambda_2| (spectral gap), non-vacuously (error is far above machine precision)
[OK]   lumpable chain: intertwining P V = V P^ holds exactly (Kemeny-Snell)
[OK]   non-lumpable chain: intertwining defect = 0.100 > 0 (naive aggregation is NOT a Markov kernel on blocks)
[OK]   pi-weighted compression gives a genuine stochastic matrix on blocks
[OK]   ...and its stationary law is the lumped stationary law  (same mechanism as Galerkin / conditional expectation)

== S3  Corridor A/D: a matrix is typed by its gauge action, not by its shape ==
[OK]   Endo (similarity P A P^-1): eigenvalues are gauge-invariant
[OK]   Bil (congruence P^T A P): eigenvalues are NOT gauge-invariant -> 'eigenvalues of a Gram/Hessian matrix' need a declared metric
[OK]   Bil: inertia (signature) (3, 3) is the congruence invariant (Sylvester)
       cond(K) for n=16,32,64,128 : 116, 441, 1712, 6744  (ratio ~4 per doubling => O(h^-2))
[OK]   stiffness-matrix conditioning grows like h^-2
[OK]   eigenvalues of the stiffness matrix alone change with the basis
[OK]   generalised eigenvalues of the pencil (K, M) are basis-invariant
       smallest generalised eigenvalue 9.9702  vs  pi^2 = 9.8696
[OK]   energy a(u_h,u_h) is gauge-invariant (x^T K x = x'^T K' x')
[OK]   conditioning is basis-dependent: cond(K)=32.2, cond(K')=2725.9 -> cost is NOT a gauge-invariant observable
[OK]   Galerkin orthogonality a(u-u_h, v_h) = 0 (max |.| = 1.2e-15)
[OK]   u_h is the energy-norm best approximation in V_h (all 500 perturbations are worse)

== S4  Composition of graded claims: affine error monoid and a rejected composition ==
[OK]   (L,eps) composition is associative with unit (1,0)  [monoid of affine error bounds]
[OK]   h=0.1: observed 1.60e-03 <= composed bound 1.68e-03
[OK]   h=0.01: observed 1.13e-04 <= composed bound 1.17e-04
[OK]   h=0.001: observed 9.97e-04 <= composed bound 1.00e-03
[OK]   h=0.0001: observed 9.76e-03 <= composed bound 1.00e-02
[OK]   stage 1 error 1e-6 is amplified to ~1e-2 by a downstream map with L ~ 1/h: composition needs a declared stability constant

== S5  Composition of loss: observable flow ==
[OK]   kernel pair of g.f contains kernel pair of f: information lost never returns (monotone)
       in 2000 random finite trials, g destroyed an observable that f still preserved 20 times -> composition must be checked per observable

All sanity checks passed.
```
