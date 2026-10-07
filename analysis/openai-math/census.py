import os, re, sys, collections
root = sys.argv[1]
oai = os.path.join(root, "OAI")
imp = re.compile(r"^\s*(?:public\s+)?import\s+([A-Za-z0-9_.]+)", re.M)
files_by_area = collections.Counter(); loc_by_area = collections.Counter()
cross = collections.Counter(); intra = collections.Counter()
mathlib_by_area = collections.defaultdict(collections.Counter)
mathlib_files = collections.Counter()
nfiles = 0
topics = collections.defaultdict(set)
for dp, dn, fn in os.walk(oai):
    for f in fn:
        if not f.endswith(".lean"): continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, oai).split(os.sep)
        area = rel[0] if len(rel) > 1 else "(root)"
        if len(rel) > 2: topics[area].add(rel[1])
        try: txt = open(p, encoding="utf-8", errors="replace").read()
        except Exception: continue
        nfiles += 1; files_by_area[area] += 1; loc_by_area[area] += txt.count("\n")
        seen_m = set()
        for m in imp.findall(txt):
            if m.startswith("OAI."):
                parts = m.split(".")
                tgt = parts[1] if len(parts) > 2 else "(root)"
                (intra if tgt == area else cross)[(area, tgt)] += 1
            elif m.startswith("Mathlib"):
                seen_m.add(m)
        for m in seen_m:
            mathlib_by_area[area][m] += 1; mathlib_files[m] += 1
print("OAI lean files:", nfiles)
print("\n== files / LOC / topics by area ==")
for a, c in files_by_area.most_common():
    print(f"{a:22s} files={c:6d} loc={loc_by_area[a]:9d} topics={len(topics[a])}")
tot_c = sum(cross.values()); tot_i = sum(intra.values())
print(f"\nimport edges: intra-area={tot_i}  cross-area={tot_c}  (cross share {tot_c/(tot_i+tot_c):.1%})")
print("\n== top cross-area edges (src -> tgt: count) ==")
for (s, t), c in cross.most_common(25): print(f"{s:20s} -> {t:20s} {c}")
tgt_in = collections.Counter(); 
for (s, t), c in cross.items(): tgt_in[t] += c
print("\n== cross-area imports received, by target area ==")
for t, c in tgt_in.most_common(): print(f"{t:22s} {c}")
keys = ["ChainComplex","Homology","Dual","TensorProduct","Kernel","condExp","ConditionalExpectation","Markov","Kernel.Basic","Projection","Orthogonal","Quotient","Galois","Adjunction","Functor","Representation","Semigroup","Fourier","Lagrange","Convex","Hilbert","InnerProduct","Spectrum","Matrix","Module.Basic","Simplicial","Cohomology","GroupAction","MulAction","Equiv","Isometry","Basis"]
print("\n== Mathlib modules most imported (files) ==")
for m, c in mathlib_files.most_common(40): print(f"{c:6d} {m}")
print("\n== selected hub-like Mathlib modules: files importing, number of OAI areas ==")
for k in keys:
    ms = [m for m in mathlib_files if k in m]
    if not ms: continue
    files = sum(mathlib_files[m] for m in ms)
    areas = {a for a in mathlib_by_area if any(k in m for m in mathlib_by_area[a])}
    print(f"{k:24s} modules={len(ms):3d} file-imports={files:6d} areas={len(areas)}/{len(files_by_area)}")
