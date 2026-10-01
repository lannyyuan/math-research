# mel-research — 附录索引

> 单一完整版:[`MEL-complete-report.md`](MEL-complete-report.md)。总报告单独版:[`final-mel-research-report.md`](final-mel-research-report.md)。
> 证据标签与术语见仓库根目录的 [`CONTRIBUTING.md`](../CONTRIBUTING.md)、[`GLOSSARY.md`](../GLOSSARY.md)。

## 按问题查找

| 问题 | 文件 |
|---|---|
| Q1 LA 为什么强 | [`01`](01-why-linear-algebra-is-a-good-expression-layer.md) |
| Q2 哪些可泛化 | [`02`](02-la-specific-vs-generalizable.md) |
| Q3 最小核 / Q4 基本实体 | [`04`](04-mel-core-candidates.md)、[`06`](06-map-and-transformation-semantics.md) |
| Q5 分支作元数据 | [`05`](05-mel-type-system.md) §3.4、[`08`](08-corridor-a-local-linearization.md) |
| Q6 四走廊 | [`08`](08-corridor-a-local-linearization.md)–[`11`](11-corridor-d-analytic-variational.md) |
| Q7 重复机制 | [`12`](12-factorization-and-compression-test.md) |
| Q8 复合演算 | [`13`](13-composition-model.md) |
| Q9 非空洞性 | [`14`](14-non-vacuity-and-failure-modes.md) |
| Q10 现有框架 | [`03`](03-existing-frameworks-comparison.md) |
| Q11 定位 / agent-native | [`15`](15-agent-native-language-analysis.md)、总报告 |
| Q12 下一步 | 总报告 §6、[`../ROADMAP.md`](../ROADMAP.md) |

## 全部文件

| 文件 | 内容 |
|---|---|
| [`01-why-linear-algebra-is-a-good-expression-layer.md`](01-why-linear-algebra-is-a-good-expression-layer.md) | P1–P8;矩阵类型 = 规范作用;缺陷账本;DP1–DP10 |
| [`02-la-specific-vs-generalizable.md`](02-la-specific-vs-generalizable.md) | 25 行分类(LA-SPECIFIC / GENERALIZABLE / GWW / UNKNOWN) |
| [`03-existing-frameworks-comparison.md`](03-existing-frameworks-comparison.md) | 约 24 个既有框架逐项对照 |
| [`04-mel-core-candidates.md`](04-mel-core-candidates.md) | 原语审问;三个候选核;推荐核 |
| [`05-mel-type-system.md`](05-mel-type-system.md) | 混合类型系统;接受/拒绝例子 |
| [`06-map-and-transformation-semantics.md`](06-map-and-transformation-semantics.md) | 对应 + 缺陷分类;契约字段;MI 归位 |
| [`07-normal-and-intermediate-forms.md`](07-normal-and-intermediate-forms.md) | 规范型 vs ITF;MLIR 类比分级 |
| [`08-corridor-a-local-linearization.md`](08-corridor-a-local-linearization.md) | 走廊 A |
| [`09-corridor-b-stochastic-dynamic.md`](09-corridor-b-stochastic-dynamic.md) | 走廊 B |
| [`10-corridor-c-topological-algebraic.md`](10-corridor-c-topological-algebraic.md) | 走廊 C |
| [`11-corridor-d-analytic-variational.md`](11-corridor-d-analytic-variational.md) | 走廊 D |
| [`12-factorization-and-compression-test.md`](12-factorization-and-compression-test.md) | 压缩检验;控制;预注册判决实验 |
| [`13-composition-model.md`](13-composition-model.md) | 复合规则;契约范畴命题(草证);实例与拒绝 |
| [`14-non-vacuity-and-failure-modes.md`](14-non-vacuity-and-failure-modes.md) | R0–R3;G1–G6;失败模式 |
| [`15-agent-native-language-analysis.md`](15-agent-native-language-analysis.md) | 信任边界;conformance;LLM 假设 |
| [`16-mel-v0.1-candidate.md`](16-mel-v0.1-candidate.md) | 候选语法与五个示例(待证伪) |
| [`17-red-team-review.md`](17-red-team-review.md) | 10 项攻击 + 元攻击 |
| [`final-mel-research-report.md`](final-mel-research-report.md) | 综合与 Q1–Q12 |
| [`MEL-complete-report.md`](MEL-complete-report.md) | 单一完整版(由脚本生成) |
| [`experiments/`](experiments/) | 计算验证 |

## 阅读建议

* 想要结论:总报告 §0、§3。
* 想检验论证强度:先读 [`17`](17-red-team-review.md) 与 [`12`](12-factorization-and-compression-test.md) §6(有效性威胁)。
* 想动手:[`16`](16-mel-v0.1-candidate.md) §10 的五个示例 + [`experiments/sanity_checks.py`](experiments/sanity_checks.py)。
