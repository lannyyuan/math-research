# 10 — 走廊 C:拓扑 / 代数(Graph → Topology → Abstract Algebra → LA)

> 标签见 `01-…`;数值验证见 `experiments/sanity_checks.py` S1。

## 0. 结论

* 走廊 C 是**唯一强制 `lax` 模式**的走廊:系数变换产生 **Tor 缺陷**。
* **只用图(1 维)做这条走廊会完全掩盖 `lax`**——图的 $H_1$ 无挠,系数变换的缺陷恒为 0。这是一个具体的**选择偏差**例子(见 `12`)。必须补一个 2 维例子($\mathrm{RP}^2$)才能暴露。
* "Graph → Topology"一步**极有损**:同伦型只保留 $(\beta_0,\beta_1)$;与"邻接谱"保留的信息**互不可比**——这是"信息损失相对 purpose"最清楚的例子。

## 1. 路径

```
Graph(V,E)
  ⇒ Cell₁                         -- 1 维胞腔复形(重解释;M0)
  ⇒ Chain[R]                      -- 链复形(choice: 取向;系数环 R)
  ⇒ Module_R                      -- H_n = ker∂_n / im∂_{n+1}
  ⇒ Vect_k                        -- ⊗_R k  (系数变换;lax)
```

补充 2 维例子:$\mathrm{RP}^2$(六顶点三角剖分:$V-E+F=6-15+10=1$)。

## 2. Stage A:原始变换

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

## 3. 实际计算(S1)

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

## 4. MEL 表达

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

## 5. 复合检查

| 复合 | 结果 | 理由 |
|---|---|---|
| `Cells` → $H_n$ → `⊗k` 与 `Cells` → `⊗k` → $H_n$ | **仅在 `lax` 缺陷为 0 时相等** | UCT;$\mathrm{RP}^2$、$\mathbb F_2$、度 2 为反例 |
| 取向翻转前后 rank | ✓ 不变 | 规范不变 |
| 对**图**用 `lax` | 平凡(缺陷恒 0) | 1 维复形的 $H_1$ 是自由群的子群,无挠 |
| 图 → 同伦型 → 邻接谱 | ✗ | 同伦型已丢失谱信息 |

## 6. 信息损失相对 purpose

同一源对象,两种降级保留**互不可比**的信息:

| 降级 | 保留 | 丢失 |
|---|---|---|
| 图 → 同伦型/同调 | $(\beta_0,\beta_1)$(连通分支数 + 环秩) | 几乎全部组合信息:同 $\beta_1$ 的连通图同伦等价 |
| 图 → 邻接谱 | 谱不变量 | 同谱非同构图(cospectral)不可区分 |

> 这正是契约里 `recovers q` + `loses ρ` 要**成对声明**的原因:损失只有相对 observable 才有意义。

## 7. 压力点

1. **`lax` 模式**:缺陷是**对象**(Tor),不是度量;必须进核。
2. **系数环显式**:$\mathbb Z/\mathbb Q/\mathbb F_2$ 会改变 Betti 数。**绝不可隐含。**
3. **自然性作用域**:对"图同态"还是"胞腔映射"自然?(边收缩需约定 ⟹ 声明 `natural[class]`)
4. **规范群随环变**:在 $\mathbb Z$ 上是 $GL_n(\mathbb Z)$(Smith 标准型 = 规范固定),在域上是 $GL_n(k)$。

## 8. 非空洞性检验

* **G4 变异测试**:翻转某个三角形边缘算子里的**一项**符号 ⟹ $\partial_1\partial_2$ 的某列变为 $2(c-a)\ne0$,`exact ∂∂=0` 失败 ✓(注意:对纯图此测试**无效**——1 维没有 $\partial_2$,`∂∂=0` 空真。又一次说明图-only 的走廊太弱。)
* **G3 杠杆**:在 $\mathbb F_2$ 上用高斯消元计算 $\beta_1$(多项式时间),并读回"环秩/可定向性"(挠与否)。

## 9. 局限

* 未涉及上同调环结构、谱序列的复合;`lax` 缺陷如何**跨多步复合**没有简单演算(见 `13` §5)。
* 只测了一个带挠的例子($\mathrm{RP}^2$)。
