# 06 — Map 与 Transformation 语义

> 对应 Task 12 / Q4。**不要把一切都叫 morphism,除非数学上有根据。**
> 标签见 `01-…`。

## 0. 结论

> **基本实体应是 Transformation(带类型、带契约的结构化对应),而不是 Map。**
> Map(态射)是 Transformation 的特例:"全 + 单值 + 精确"。其余常见的跨域变换(近似、优化、选择、商、离散化、不变量提取、性质桥)**不是**态射,要么是对应,要么是"对应 + 声明的缺陷",要么根本是定理(claim)。
> prompt 的契约字段 `requires/preserves/forgets/introduces/choice/law/cost` 可以收缩为 **`requires, choice, claims(模式), loses, recovers`** 五项 + 附属的 `witness`/`cost`。

---

## 1. 十种"常被称作 morphism 的东西"

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

## 2. 统一概念:带缺陷声明的结构化对应

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

## 3. 契约字段审问

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

## 4. "模式(kind)"不是原语,是 claim 的模式识别

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

## 5. 旧 7 元组 MI 的归位

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

## 6. 回答 Q4:基本实体是什么

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

## 7. 未解

* **变换之间的态射**(2-胞腔):两个变换"观测等价"(`q∘f = q∘g`)是否需要一阶实体?目前作为派生等价处理,但 `lax` 模式已隐含 2-胞腔,**层级是否要升到 double category** 是开放问题(留给 `E`/`B` 方向,见 `final-mel-research-report.md` §6)。
* "对应"的复合需要拉回存在性;在非阿贝尔/非局部呈现范畴里是否成立未检验。
