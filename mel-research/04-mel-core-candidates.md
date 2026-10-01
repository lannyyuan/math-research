# 04 — MEL 核心候选:最小核应该是什么

> 对应 Task 3 / Q3 / Q4(部分)。纪律:**对每个候选原语问"能否由其余导出?"**,不机械罗列。
> 标签见 `01-…`。

## 0. 结论

> **最小语义核 = {Structure, Object, Transformation} + 复合规则 + 一个"分级等式"(graded claim)。**
> Law、Observable、Equivalence、Approximation、Choice、Constraint、Information-loss 全部可导出;Cost、Witness 是附属元数据,不进语义核。
> 语法上为了**可检视性**,把 `Claim` 提升为一等语法类别(语义上可由"复合间的等式/不等式"导出),把 `choice`、`recovers`、`loses` 做成命名字段(语法糖,不是原语)。

与 prompt 里提出的 $\{$Object, Structure, Map, Law, Observable$\}$ + 复合相比:

* **Map → Transformation**:Map 只覆盖"全函数 + 单值 + 精确"的特例(见 `06`)。
* **Law 与 Observable 被降为派生**。
* 额外需要且不可省的只有**一个索引**:claim 的**分级模式** Γ(否则近似会被隐藏)。

---

## 1. 原语审问表

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

## 2. 三个候选核的比较

| 核 | 内容 | 表达力(四走廊) | 问题 |
|---|---|---|---|
| **Core-5**(prompt 的猜测) | Object, Structure, Map, Law, Observable + 复合 | 走廊 A 的 $d f_p$ ✓;B 的归一化(带选择)✗;C 的系数变换缺陷 ✗;D 的 Galerkin 误差 ✗ | Map 排斥非态射;Law 无分级则隐藏误差 |
| **Core-3+**(推荐) | Structure, Object, Transformation + 复合 + graded Claim | 四走廊 ✓,**但**需三项扩展:`lax` 模式、坐标类型带规范作用、局部性(germ)qualifier(见 §5) | 对应(correspondence)过宽 → 必须配 `14` 的非空洞闸门 |
| **Core-max** | 把 prompt 列的 10 个候选全作原语 | ✓ | 冗余;每个字段都可由别的导出;违反"尽量小" |

---

## 3. 推荐核的形式候选

### 3.1 语义层

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

### 3.2 派生定义(无需新原语)

```
Obs(q)       := tr q : S ⇒ V          -- V 为值型 Structure;附 claim "q 在 ≈ 下不变"
Equiv_q      := ker q                  -- x ≈_q x′  ⇔  q x = q x′
Approx       := claim graded …
Choice(c:G)  := 参数 Object,类型 Torsor(G);G 为声明的规范群(oid)
Loss(T; q)   := q 是否经 T 恢复:  ∃ q̃ . q = q̃ ∘ T
Constraint   := Structure 的 where φ  |  Transformation 的 requires φ
```

### 3.3 紧凑语法骨架(完整版见 `16`)

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

## 4. 为什么 Claim 在语义上可导出、语法上仍要保留

* 在依赖类型论里,`exact` claim = 恒等类型,`graded` = 值取 Γ 的相等度,`lax` = 一个带比较映射的 2-胞腔;**语义上无需新原语**。
* 但一个面向 agent/审阅者的契约语言必须让**契约可被检视而不必运行证明**。因此保留 `Claim` 作为一等语法类别,并带 `witness`(证据状态)。
* 这与 RT2("MEL 就是依赖类型论")的回应一致:语义被依赖类型论覆盖,**渐进(gradual)的、可含非形式见证的前端**才是 MEL 的存在理由。

## 5. 对四个走廊的覆盖与压力点

| 走廊 | 核是否够用 | 需要的扩展(未在 prompt 的候选里) |
|---|---|---|
| A 局部线性化 | ✓ | **局部性**(germ at $p$)作为 `requires` 的限定;坐标类型的**规范作用**(Hom: $PAQ^{-1}$;Bil: $P^{\!\top}GP$) |
| B 离散/随机/动力 | ✓ | Cone/正性是 LA 之外的**额外结构**(Perron–Frobenius 是锥定理);假设向后传播(wp) |
| C 拓扑/代数 | ✓ | **`lax` 模式**(Tor 缺陷);系数环必须显式 |
| D 解析/变分/有限 | ✓ | `graded`(Céa);混合 exact(结构)+ graded(状态);成本与规范**不**相容 |

结论:**无需新增"字段"**,但需要 `lax` 模式与"带规范作用的坐标类型"两项**结构性**扩展——这比"字段不够"更诚实地说明了核的边界。

## 6. 候选原语的"原语纪律"检验

按 prompt §17,候选原语须满足:重复出现、稳定类型、有意义的复合律、非平凡保持语义、解释/计算价值。

| 实体 | 重复出现 | 稳定类型 | 复合律 | 非平凡保持 | 价值 | 结论 |
|---|---|---|---|---|---|---|
| Structure | ✓ | ✓ | (view 的复合) | ✓ | ✓ | 原语 |
| Object | ✓ | ✓ | — | — | ✓ | 原语 |
| Transformation | ✓ | ✓(S⇒S′) | ✓(见 `13`) | ✓ | ✓ | 原语 |
| Choice | 4/4 走廊 | ✓ | 群胚粘合 | ✓ | ✓ | **语法糖**(可导出,但太常见) |
| Observable | 4/4 | ✓ | 按 observable 的复合检查 | ✓ | ✓ | **派生**(契约成分) |
| Cost | 2/4 | ✗(与规范不相容) | 弱 | ✗ | 中 | **附属** |

## 7. 对 Q3 的回答

> **最小可信核**:$\{\textsf{Structure},\textsf{Object},\textsf{Transformation}\}$ + 复合 + 分级 Claim($\textsf{exact}/\textsf{graded}/\textsf{lax}$)。
> 形式语法见 §3.3 与 `16`。
> 关于"是否还有不可避免的概念":**有两个**——(i)`lax` 缺陷对象,(ii)坐标类型的规范作用;二者都已在上面入核或入类型系统。**没有发现需要独立原语的 Constraint、Law、Observable、Equivalence、Approximation。**

## 8. 局限

* "可导出"是在**语义层**成立的;在**可用性**层(agent 能否稳定产出、人能否检视)它们仍需命名字段,这是工程判断而非数学定理。
* 核是否"够小"取决于走廊选择(见 `12` 的选择偏差讨论)。
