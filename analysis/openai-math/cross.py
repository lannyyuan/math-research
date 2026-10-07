import os, re, sys, collections
root = sys.argv[1]; oai = os.path.join(root, "OAI")
imp = re.compile(r"^\s*(?:public\s+)?import\s+(OAI\.[A-Za-z0-9_.]+)", re.M)
tg = collections.Counter(); srcfam = collections.Counter(); n=0
for dp, dn, fn in os.walk(oai):
    for f in fn:
        if not f.endswith(".lean"): continue
        rel = os.path.relpath(os.path.join(dp, f), oai).split(os.sep)
        if len(rel) < 3: continue
        area = rel[0]; fam = "/".join(rel[:2])
        txt = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
        for m in imp.findall(txt):
            p = m.split(".")
            if len(p) > 2 and p[1] != area:
                tg[".".join(p[:3])] += 1; srcfam[fam] += 1; n += 1
print("cross-area edges:", n, " distinct target families:", len(tg), " distinct source families:", len(srcfam))
print("\ntop target families (area.family):")
for k, c in tg.most_common(15): print(f"{c:5d} {k}")
print("\ntop source families:")
for k, c in srcfam.most_common(10): print(f"{c:5d} {k}")
tot = sum(tg.values()); top5 = sum(c for _, c in tg.most_common(5))
print(f"\ntop-5 target families absorb {top5/tot:.0%} of cross-area edges; top-15 absorb {sum(c for _,c in tg.most_common(15))/tot:.0%}")
