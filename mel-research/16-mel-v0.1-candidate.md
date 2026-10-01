# 16 — MEL v0.1 候选

> 对应 §24。**"当且仅当证据支持才提出候选。"**
>
> **证据判断**:证据支持一个**小而有限**的候选(四走廊 + 两个控制 + 三个探针),但:(i)压缩检验的判决实验**未做**(`12` §8);(ii)核的大部分是既有范畴/类型论内容(`03`)。
> 因此本文把 v0.1 定位为 **"待证伪的规约假设"**,**不是**"可以开始实现的规范"。
> 标签见 `01-…`。

---

## 1. 最小语义实体

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

## 2. 语法(紧凑 EBNF)

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

## 3. 类型系统(摘要,详见 `05`)

* 类型 = ⟨理论引用;参数;精化;变性⟩。
* **判定**:理论包含、参数合一、规范桥、变性。**证明义务**:精化蕴含、claim 真值。
* 坐标类型 `Coord[action, shape]` 携带规范作用。
* `ns`/`tags` **不入类型相等**。

## 4. 变换契约

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

## 5. 复合

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

## 6. 信息损失的表示

`loses` 取三种形式之一(不得省略不写):
```
loses  ~   : x ~ x′ ⇔ φ(x,x′)           -- 核对(显式关系)
loses  orbit(G)                            -- 丢失的是规范轨道坐标(如行尺度)
loses  obs{q₁,…}                           -- 丢失的 observable 集合
loses  none                                -- 声称无损;触发"是否同构?"的检查
```
`loses` 与 `recovers` **成对**:损失只有相对 observable 才有意义(`10` §6)。

## 7. 近似

| Γ | 复合 | 例 |
|---|---|---|
| `Bool` | 平凡 | 精确 |
| `Aff(L,ε)` | $(L_2L_1,\ \varepsilon_2+L_2\varepsilon_1)$ | Céa;数值误差 |
| `Order` | 单调下游 | 弱对偶;Jensen |
| `Germ@p` | 下游在像点可微 | 局部余项 |
| `PAC(ε,δ)` | $(\varepsilon_2+L_2\varepsilon_1,\ \delta_1+\delta_2)$ | 蒙特卡洛 |

近似**不得隐藏误差语义**:graded claim 必须写出 Γ 与(若作上游)`stable L`。

## 8. 等价

| 等价 | 定义 | 用途 |
|---|---|---|
| $\approx_q$(对象,对 observable $q$) | $q(x)=q(x')$,即 $\ker q$ | "对某目的等价" |
| $f\approx_q g$(变换) | $q\circ f=q\circ g$(在域上) | 观测等价 |
| 规范等价 | 存在 $\beta\in$ 规范群胚,$\beta\circ\mathrm{pres}_1=\mathrm{pres}_2$ | 换表示 |

## 9. 坐标层

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

## 10. 五个示例

### 10.1 导数 / 切映射
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

### 10.2 图 → Markov 核
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

### 10.3 拓扑 → 链复形 → 同调 → 系数变换
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

### 10.4 条件期望
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

### 10.5 连续 → 有限维逼近
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

## 11. 一致性检查清单(给检查器)

1. 每个 `tr` 至少一个 `claim` 或 `recovers`(否则标 `OpaqueFunction`)。
2. 每个 `claim` 有 `witness`(缺失 ⟹ `asserted`)。
3. 每个 `recovers q` 满足 G1、G6。
4. 每个 `graded` 有 Γ;若作上游则有 `stable`。
5. 每个 `choice` 有规范群;凡声称"规范不变"的 observable 在群轨道上抽样通过。
6. 每个 `coord` 声明规范作用。
7. 契约自带至少一个变异适配器(G4)。
8. `ns/tags` 不参与类型检查。

## 12. 非目标

* 不是通用数学语言;不覆盖数论、逻辑、信息论(按 prompt 保持范围)。
* 不是证明系统;不替代 Lean/Mathlib。
* 不追求规范型。
* 不把成本放进语义。

## 13. 未解

* `lax` 缺陷的复合(`13` §2.6)。
* 多值对应与规范群胚的相容性。
* 与 MMT 的精确关系(`17` RT3)。
* LLM 稳定性(`15`)。
* Γ 是否已过度设计(`17` RT14)。
