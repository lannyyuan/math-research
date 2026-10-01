# math-research

对一个假设性的 **Mathematical Expression Layer(MEL)** 的独立研究:一种紧凑的、带类型的、可复合的语言,用于表达跨数学领域的结构与变换。

核心问题不是"一切数学能否塞进线性代数",而是:

> **为什么线性代数是如此强的表达层?它的设计方法论,在去掉线性性之后还剩什么可以迁移?**

## 当前状态(2026-10)

| 项 | 状态 |
|---|---|
| 研究报告 | **完成**(单一完整版 + 17 个分项附录) |
| 主要判定 | **Outcome C 为主**(类型化 IR / 规约语言),带一个小的 Outcome B 残余 |
| 关键证据缺口 | 压缩检验的**盲测判决实验尚未执行**;红队与被审对象同源;无形式化、无实现、无 LLM 实验 |
| 下一步 | **C:盲测留出走廊**(见 [`ROADMAP.md`](ROADMAP.md)) |
| MEL v0.1 | 仅为**待证伪的规约假设**,**不建议开始实现** |

一句话结论:LA 的强来自 FinVect 中一切"缺陷"(Tor/Ext、近似误差、信息损失、选择、假设)几乎为零;MEL 要做的是在缺陷不为零的地方把它们**显式声明并让它们沿复合传播**。其数学骨架几乎全是既有的范畴论 / MMT / 契约理论,可能的增量在于**规约纪律**,而非新数学。

## 从哪里开始读

| 你想… | 读 |
|---|---|
| 15 分钟了解结论 | [`mel-research/MEL-complete-report.md`](mel-research/MEL-complete-report.md) 第一部分 |
| 看单一完整版(含全部附录) | [`mel-research/MEL-complete-report.md`](mel-research/MEL-complete-report.md) |
| 按主题查分项 | [`mel-research/README.md`](mel-research/README.md)(附录索引) |
| 看候选语法与五个示例 | [`mel-research/16-mel-v0.1-candidate.md`](mel-research/16-mel-v0.1-candidate.md) |
| 看最强的反对意见 | [`mel-research/17-red-team-review.md`](mel-research/17-red-team-review.md) |
| 知道接下来要做什么 | [`ROADMAP.md`](ROADMAP.md) |
| 查术语 | [`GLOSSARY.md`](GLOSSARY.md) |
| 参与/复核 | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

## 仓库结构

```
.
├── README.md                    本文件
├── ROADMAP.md                   下一步与预注册实验协议
├── GLOSSARY.md                  术语表(中英对照)
├── CONTRIBUTING.md              证据标签、写作与复核规范
├── requirements.txt             计算验证依赖
├── tools/
│   └── build_complete_report.py 重新生成单一完整版
├── templates/
│   ├── README.md
│   ├── corridor-template.md     新走廊文档模板
│   └── annotation-sheet.csv     盲标注表(压缩检验用)
└── mel-research/
    ├── README.md                附录索引
    ├── MEL-complete-report.md   单一完整版(由脚本生成,勿手改)
    ├── final-mel-research-report.md   总报告(单独版)
    ├── 01 … 17-*.md             分项研究
    └── experiments/
        ├── README.md
        ├── sanity_checks.py     重算报告中引用的具体例子
        └── sanity_checks.out.txt
```

## 复现计算验证

```bash
pip install -r requirements.txt
python3 mel-research/experiments/sanity_checks.py
```

脚本重算报告中引用的具体例子(RP² 的 Tor 缺陷、随机游走的信息损失与聚合、矩阵规范作用、有限元条件数的基相关性、误差复合、观测量流),全部以断言形式给出。**它们是对具体有限实例的检查,不是证明。**

## 证据约定

全套文档使用统一标签,详见 [`CONTRIBUTING.md`](CONTRIBUTING.md):

* `[T]` 定理/标准事实 · `[S]` 结构对应 · `[A]` 类比 · `[H]` 本研究假设
* `(web)` 本次检索核实 · `(bg)` 凭背景知识、未复核

**请不要把 `(bg)` 与 `[H]` 当作已核实的结论。**

## 研究纪律(摘自原 prompt)

* 先找压缩,再谈覆盖;
* 向 LA 学设计,不学它的统治地位;
* 不为显得新颖而造词;不把一切都叫 morphism;不拿四个走廊推出普适性;
* 不拿 LLM 的"理解"当数学验证。

## 许可

**尚未选择许可证。** 在所有者决定之前,默认保留全部权利。
