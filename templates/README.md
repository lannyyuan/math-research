# templates

用于 `ROADMAP.md` 中的 C1 盲测压缩检验。

## corridor-template.md

新走廊文档模板。先做 Stage A(只记录,不命名机制),再分组。

## annotation-sheet.csv

盲标注表,每个标注者每个变换一行。字段:

| 字段 | 取值 |
|---|---|
| `label` | `M0` `M1` `M2` `M3` `M4` `M5` `PT1` `PT2` `OBS` `UNCLASSIFIABLE` |
| `confidence_1to5` | 1(很不确定)–5(很确定) |
| `needs_new_field` | `yes` / `no`:是否需要现有契约字段之外的东西 |
| `needs_lax_or_pac` | `lax` / `pac` / `none` |

**标注依据**:仅限 `mel-research/06-map-and-transformation-semantics.md` §4 的机制签名。
**标注者不得**阅读 `mel-research/12`、`16`(避免失去盲性)。
