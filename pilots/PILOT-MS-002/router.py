#!/usr/bin/env python3
"""MS-002 — ROUTER do Skill Pack. Deterministico e auditavel. ZERO modelo.
O router NAO e fonte de verdade semantica: ele so decide O QUE CARREGAR."""
import json, pathlib, re, unicodedata, sys

def _norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " " + re.sub(r"[^a-z0-9]+", " ", s).strip() + " "

class Router:
    MAX_TOP = 3

    def __init__(self, pack_dir):
        self.pack = pathlib.Path(pack_dir)
        self.cfg = json.loads((self.pack / "router" / "ROUTER.json").read_text(encoding="utf-8"))
        self.modules = self.cfg["modules"]

    # ---------------------------------------------------------------- score
    def score(self, task):
        t = _norm(task)
        out = {}
        for mid, m in self.modules.items():
            hits = [k for k in m["triggers"] if f" {_norm(k).strip()} " in t]
            if hits:
                out[mid] = {"score": len(hits), "matched": sorted(hits)}
        return out

    # --------------------------------------------------------------- select
    def route(self, task, deep=False, want_optional=None):
        """Devolve o MENOR conjunto suficiente de modulos + fechamento de REQUIRES."""
        want_optional = set(want_optional or [])
        sc = self.score(task)
        flags = []
        if not sc:
            return {"task": task, "selected": [], "scores": {},
                    "load": ["core/CORE.md", "router/ROUTER.json"],
                    "flags": ["NO_MODULE_MATCH"], "fallback": True,
                    "note": self.cfg["fallback"]["flag"]}
        ranked = sorted(sc.items(), key=lambda kv: (-kv[1]["score"], kv[0]))
        top = ranked[0][1]["score"]
        chosen = [m for m, v in ranked if v["score"] == top]
        if len(chosen) > self.MAX_TOP:
            chosen = chosen[:self.MAX_TOP]; flags.append("AMBIGUOUS_ROUTE")
        # modulos com score menor entram so se empatarem no topo -> nao entram
        sel, seen = [], set()
        def add(mid, why):
            if mid in seen or mid not in self.modules: return
            seen.add(mid); sel.append({"module": mid, "reason": why})
            for d in self.modules[mid]["dependencies"]:
                if d["type"] == "REQUIRES":
                    add(d["module"], f'REQUIRES de {mid}')
                elif d["type"] == "OPTIONAL" and d["module"] in want_optional:
                    add(d["module"], f'OPTIONAL de {mid} pedido pela tarefa')
        for m in chosen: add(m, f'trigger: {", ".join(sc[m]["matched"])}')
        load = ["core/CORE.md", "router/ROUTER.json"]
        for s in sel:
            m = self.modules[s["module"]]
            load.append(f'modules/{s["module"]}/MODULE.json')
            load.append(f'modules/{s["module"]}/{m["resources"]["contract"]}')
            if deep:
                for r in m["resources"]["workflows"] + m["resources"]["anti_patterns"]:
                    load.append(f'modules/{s["module"]}/{r}')
        return {"task": task, "selected": [s["module"] for s in sel], "reasons": sel,
                "scores": {k: v["score"] for k, v in sc.items()},
                "not_selected": sorted(set(self.modules) - seen),
                "load": load, "flags": flags, "fallback": False, "deep": deep}

    # ------------------------------------------------------------- medicao
    def measure(self, load):
        tot = 0; per = {}
        for rel in load:
            p = self.pack / rel
            n = p.stat().st_size if p.exists() else 0
            per[rel] = n; tot += n
        return {"bytes": tot, "tokens_est": round(tot / 4), "per_file": per}

    def monolithic(self):
        files = [str(p.relative_to(self.pack)) for p in sorted(self.pack.rglob("*"))
                 if p.is_file() and p.suffix in (".md", ".json")]
        return self.measure(files)

if __name__ == "__main__":
    r = Router(pathlib.Path(__file__).resolve().parent / "skillpack"
               if (pathlib.Path(__file__).resolve().parent / "skillpack").exists()
               else pathlib.Path(__file__).resolve().parent)
    task = " ".join(sys.argv[1:]) or "criar estrategia de conteudo para instagram"
    res = r.route(task)
    print(json.dumps({**res, "measurement": r.measure(res["load"])}, ensure_ascii=False, indent=1))
