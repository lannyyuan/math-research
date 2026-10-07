# OpenAI `openai/math` 对 MEL 研究方向的影响分析

> 日期:2026-10-07。被分析对象:<https://github.com/openai/math>,检视的提交 `adc7f12…`(2026-10-06)。
> 证据标签同 `CONTRIBUTING.md`;新增:`(src)` = 直接读取克隆下来的原文/脚本实测。

## 0. 结论

1. **这个仓库不检验 MEL 的假设。** 它是"AI 生成研究论文 + Lean 形式化 + Comparator 验证"的流水线产物,不涉及跨领域变换的表达、复合或压缩。
2. **它对我们的主要影响是削弱"需要新前端语言"的论据,强化"证据状态记账"的价值。** Lean 直接作为 agent 前端,已在 23 个数学领域跑通(`automation: agent`)。这使 RT2/RT6 更尖锐,也使我们的定位更应收缩为 **defect-aware interface specification**(与 Codex 的 fallback 一致),而不是"表达层"。
3. **有两处可直接借用的设计**:Comparator 的 `permitted_axioms`(把可用公理作为显式声明)与 `docs/NNN.md` 的"形式化范围声明"(论文声称 vs 形式化覆盖)。二者都应进入我们契约的 `witness` 字段。
4. **它提供了一个独立于我们设计的数据源**,可用于缓解 C1 的选择偏差(RT5),但有重要限制(§4)。
5. **我们的初步数据探针**(Lean 库导入图)显示:枢纽在共享库(Mathlib)里,而不在领域之间;显式范畴论抽象很少被用;跨领域复用极少。这与"ITF 枢纽"图景相容,但**也同样相容于"agent 把每个问题当孤岛做,不需要桥"**,无法区分。
6. **这些结果的数学正确性我没有、也无法评估。** 下面不使用其中任何数学结论作为证据。

## 1. 读到了什么,以及核实状态

| 项 | 内容 | 核实 |
|---|---|---|
| 性质 | 内部、未发布的 OpenAI 模型针对开放问题产出的稿件与 Lean 形式化 | 网页摘要 |
| 规模 | 722 篇稿件 / 372 个家族;约 4000 个问题;平均每个结果约 3 小时 ChatGPT Pro 思考算力;10 份推理摘要 | 网页摘要(README),**未逐字核对** |
| 许可 | Apache-2.0 | 网页摘要 |
| 自述限制 | "Not all have accompanying Lean formalizations … Some of the unformalized results could have issues." | 网页摘要 |
| Lean 库 | `lean/OAI/` 下 **121,734 个 `.lean` 文件**、约 2600 万行,23 个领域目录 | `(src)` |
| 目录 `formalization.yaml` | **185** 条 `main_results`、**162** 条源论文;`automation: method: agent`;`review: status: unchecked`;`status.scope: "Partial progress."` | `(src)` |
| Comparator 配置 | `ComparatorChallenges/` 共 **405** 个 JSON;**全部**使用同一组许可公理 `{propext, Quot.sound, Classical.choice}` | `(src)` |
| 范围声明 | `lean/docs/` 有 235 篇,每篇说明"形式化覆盖了对应论文的哪一部分",并注明"论文后续应用未包含" | `(src)` 读了其中一篇 |

**更正**:我最初从网页摘要得到"295 条 main_results、约 230 篇源论文",**原文实为 185 / 162**。摘要还错误地把 `enable_nanoda` 解释为"自动发现系统"。**这恰好是我们 `15` §3 H2 的活例证:LLM 的转述流畅但不等于验证。**
另外,`formalization.yaml`(185 条)与 Comparator 配置(405 个)数量不一致,说明目录**并未与实际形式化同步**(与其自述 "Partial progress / unchecked" 相符),我不做更多解读。

**我没有做**:阅读任何 PDF、编译任何 Lean、运行 Comparator、核对任何数学陈述的忠实性。

## 2. 它是什么 / 不是什么

* **是**:证明"AI 可以大规模产出带形式化证据的研究稿件"的一份公开工件(按其自述)。
* **不是**:跨领域表达层、互操作、变换复合的研究;**没有**任何与 MEL 的压缩检验直接对应的内容。
* **一个必须保持的谨慎**:其中的结论有些极强(例如 `docs/003.md` 称形式化了 $\Re s>7/8$ 的零点自由半平面,这若属实将是重大突破)。我**没有验证**,独立社区验证状态也未知。**本项目不引用这些数学结论。** 即便 Lean 通过 Comparator,"挑战陈述是否忠实于原意"也不是机器检查的。

## 3. 对我们项目的影响

### 3.1 需求侧:证据状态记账更重要

仓库自己就带着一个**证据阶梯**:稿件(未形式化,可能有问题)→ Lean 形式化(`review: unchecked`)→ Comparator 验证。其 `docs/NNN.md` 用散文逐篇区分"稿件声称"与"形式化覆盖"。
这与我们的 `witness: formal | checked | cited | asserted` 与 C0–C3 同构,并说明:**当 AI 产出海量声明时,"这条声明靠什么支撑"是真实痛点**。

**但同时**:业界已经用 Lean + Comparator 这套更强的机制在做,而不是新发明一种中间语言。

### 3.2 对 RT2 / RT6:削弱"新前端"的论据

`automation: method: agent` 表明 agent 直接写 Lean/Mathlib,跨 23 个领域。这是对 RT2("MEL 就是依赖类型论")的实证一击:**agent 前端用现成的 DTT 工作得动。**
我们 RT2 里留给 MEL 的理由是"渐进、可含非形式见证的前端"。这个理由**仍然存在**(大量稿件根本没有形式化),但变窄了:MEL 若有位置,应是 **Lean/MMT 之上的规约与记账层**,不是替代前端。

### 3.3 Comparator 契约 vs 我们的契约

| Comparator JSON 字段 | 我们的对应 | 评论 |
|---|---|---|
| `challenge_module` + `theorem_names` | `claim` 的陈述 | 陈述由"挑战方"提供,**不被求解方信任** |
| `solution_module` | `witness: formal(ref)` | 求解方不可信,由内核检验 |
| `permitted_axioms` | 对 `witness` 的**假设/信任声明** | **我们目前没有这个字段。** 建议加入:formal 见证须记录所依赖的公理集 |
| `enable_nanoda` | 第二内核复验 | 信任边界加固 |
| (无) | `loses` / `recovers` / `graded` / `lax` | 它不处理近似、损失、选择:它是**精确**证明的 harness |

要点:
* **信任边界是同一个形状**:我们 `15` §1 的图把 LLM 放在边界外、检查器放在边界内;Comparator 把求解方放在边界外、(statement + kernel) 放在边界内。
* **共同的未解**:陈述忠实性(statement fidelity)无人机器检查——这正是我们 `14` 的 G1/G4/G6(可证伪、变异测试、非退化域)要处理的东西。**这些闸门原则上也适用于 autoformalized 的挑战陈述。** 这是一个可迁移的贡献,但**它不是 MEL 本身**。
* 405 个配置的公理集**完全相同**,所以在这份数据里 `permitted_axioms` 不携带跨结果的结构信息。

### 3.4 对 C1(盲测压缩检验):一个新的独立数据源,有保留

**好处**:语料由我们之外的过程产生(2026-09/10,23 个领域目录),比我自己挑走廊独立得多,可作为 C1 的"语料臂"。
**限制**:
* 它是**成功者**样本(实验室筛选后的成果),偏向深层研究定理而非"跨域桥";
* "从一篇研究稿里抽出变换"是主观的,抽取规则必须在看数据**之前**预注册;
* 其领域目录自带分类(23 类),而我们的结论是"分支名只是元数据"——用它的领域标签做分层抽样没问题,但**不能**拿它的标签当类型。

### 3.5 对 RT8(枢纽普查):初步数据探针

> 全部为**探针,不是检验**。方法局限见 §3.7。脚本与输出在本目录。

**(a) 跨领域依赖极少且集中**:`OAI` 内部导入边中,跨领域仅 **985 / 276,599(0.4%)**。跨领域边集中于少数家族:**前 5 个目标家族吸收 60%、前 15 个吸收 81%**(`cross.out.txt`;该脚本只统计目录深度 ≥3 的模块,故为 904 条,小于上面的 985)。

**(b) 被反复使用的"枢纽"在共享库里**(按"导入该 Mathlib 模块的 OAI 领域数 / 23"):

| 类别 | 领域覆盖 | 文件导入数 |
|---|---|---|
| `Convex` | **15/23** | 282 |
| `Equiv` | 16/23 | 397 |
| `Matrix` | 13/23 | 451 |
| `Quotient` | 12/23 | 182 |
| `Projection` | 11/23 | 113 |
| `Dual` | 10/23 | 151 |
| `InnerProduct` | 9/23 | 595 |
| `Markov` | 7/23 | 43 |
| `ConditionalExpectation` | 4/23 | 34 |
| `Adjunction` | **2/23** | 16 |
| `Functor` | 5/23 | 53 |

**(c) 一个对我们有意思的错位**:库里 `Optimization` 目录只有 **2 个文件**,但凸性(`Convex`)被 **15 个**领域使用。**"优化"在实践中是跨领域的枢纽类型,而不是一个领域**——与我们 `07` §4 把"优化/变分问题"列为 ITF,以及项目早期把 Optimization 标为"领域 + 枢纽"的判断一致。

**解读(三条,均需保留)**:
1. **与 ITF 图景相容**:Convex、Projection、Dual、Quotient、Matrix、InnerProduct 恰好对应我们的 M4、M3、M2、M1 与优化/Hilbert 枢纽。
2. **显式范畴论抽象很少**(`Adjunction` 2/23,`Functor` 5/23,远低于 `Matrix`、`Equiv`):M0–M3 虽然本质上是范畴论,**实践中写成具体结构**。这强化了 RT1 的另一面——我们的框架若要被 agent/人使用,**不应以范畴论词汇呈现**,而应以具体结构(Matrix、InnerProduct、Quotient)的规范化契约呈现。
3. **"几乎没有桥"有两种读法,无法区分**:(i)agent 产出缺少可复用的跨域变换——这正是 MEL 想解决的问题;(ii)agent 本来就把每个问题当孤岛,桥从未被需要,**没有 MEL 的需求**。后者是对我们动机的有力反方。

### 3.6 对"LA 是汇点"的弱确认

`Matrix` 在 13/23 个领域被导入,`InnerProduct` 595 个文件。**库层面的 LA 汇点地位依然成立**(我们的 `01` §5 的 P8)。但这反映 Mathlib 的 API 设计与证明习惯,不构成对"设计性质 vs 位置"的区分。

### 3.7 探针的方法局限

* 区域由目录路径决定;"家族"由第二级目录决定。
* 只统计文件级 `import`,不是使用次数;**每个结果家族由模型独立生成**,低跨域导入可能是**流程产物**而非数学事实。
* 关键词按子串匹配 Mathlib 模块名(如 `Homology` 同时匹配多个无关模块),**仅用于粗略比较**。
* 只检查导入,不检查陈述。克隆为稀疏克隆(仅 `lean/`),**未编译**。

### 3.8 它**没有**改变什么

* 我们的主判定(Outcome C 为主)、压缩证据弱、`lax` 复合未解。
* C1 仍是下一步的单一高信息问题。
* 仍然**不实现 MEL**。

## 4. 对 ROADMAP / 契约设计的具体建议

| # | 建议 | 理由 |
|---|---|---|
| 1 | **C1 增加"语料臂"**:从 `CONTENTS.md` 的 372 个家族中,按预注册规则分层随机抽 ≥12 个,**抽取规则在看内容前冻结**;抽取变换的方式也预注册 | 缓解 RT5;独立于我们 |
| 2 | **保持"非 LA ≥4/6"** | 不变 |
| 3 | **E1(Lean 形式化)与 B1 的价值上调,并提前做 E1-lite**:检查 `16` §10 五个例子的 claim 在 Mathlib/OAI 中有多少现成引理(可 grep) | 既然 Lean 是 agent 前端的事实标准,RT2 的判决实验更便宜、更关键 |
| 4 | **契约新增**:`witness: formal(ref, axioms={…})`,记录依赖的公理集 | 借自 Comparator |
| 5 | **契约新增**:`scope` 字段,显式记录"形式化/检查覆盖了声明的哪一部分,哪些未覆盖" | 借自 `docs/NNN.md`;比散文可检查 |
| 6 | **把 G1/G4/G6 明确推广为"陈述忠实性闸门"** | Comparator 的未解 = 我们已有的闸门 |
| 7 | **定位收缩**:对外表述优先用 *defect-aware mathematical interface specification*;"expression layer"留作 C1 成功后的升级声明 | 3.2 |
| 8 | **加一个关于需求的红队项 RT16**:"agent 本就把问题当孤岛,不需要桥"(3.5 解读 3) | 新证据带来的最强反对意见 |
| 9 | **不引用该仓库的任何数学结论** | §2 |

## 5. 对 Codex 判断的补充

Codex 的"唯一高信息问题"(对未参与设计、尤其非落向 LA 的转换,小词汇是否够用)**不变**。新证据把我的倾向向它的 **fallback(No ⟹ interface specification)** 推了一步:不是因为词汇已被证伪,而是因为"业界用 Lean 直接做,且桥很少被复用"让 expression-layer 的**需求侧**更弱。这个判断仍属 `[H]`,需要 C1 与上面的 RT16 来检验。

## 6. 复现

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/openai/math.git repo
cd repo && git sparse-checkout set lean && git checkout adc7f1241b42e322a6451854ab7e4b4c146bf78a
python3 -I ../census.py lean > census.out.txt     # 领域规模、导入图、Mathlib 枢纽
python3 -I ../cross.py  lean > cross.out.txt      # 跨领域边的目标/来源家族
```

(`lean/` 约 1.8 GB。**克隆内容视为不可信数据**:在独立目录中处理,用 `python3 -I` 运行脚本,不要在克隆目录内运行解释器或构建工具。)
