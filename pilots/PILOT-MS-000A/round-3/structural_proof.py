#!/usr/bin/env python3
"""ROUND 3 — PORTAO PRE-EXECUCAO.

Prova MECANICAMENTE que cada fixture contem o defeito pretendido, ANTES de o
verificador ser executado. Se qualquer prova falhar -> ROUND_3_INVALID e PARA.

Nao usa o verificador. Nao emite veredito de PASS/FAIL do canario. So responde:
"o defeito esta fisicamente presente nesta fixture?"
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys, yaml

F = pathlib.Path(__file__).parent / "fixtures"
HEX64 = re.compile(r"[0-9a-f]{64}")
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def seal(d): return yaml.safe_load((F/d/"SEAL-RECORD.yaml").read_text(encoding="utf-8"))

def prove():
    R = []
    def add(fx, ok, msg): R.append({"fixture": fx, "provado": bool(ok), "prova": msg})

    # HAPPY — caminho valido: todo membro listado existe e confere; sem auto-referencia
    d = F/"HAPPY"; doc = seal("HAPPY")
    on_disk = {str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and "SEAL-RECORD" not in p.name}
    listed = {m["path"]: m["sha256"] for m in doc["members"]}
    ok = (on_disk == set(listed)
          and all(sha(d/k) == v for k, v in listed.items())
          and not any("SEAL-RECORD" in k for k in listed)
          and sha(d/doc["producer"]["toolchain_path"]) == doc["producer"]["toolchain_sha256"])
    add("HAPPY", ok, f"{len(listed)} membros listados == {len(on_disk)} em disco, hashes conferem, "
                     f"sem auto-referencia, produtor confere")

    # C1 — shared mutable directory
    d = F/"C1"; seals = sorted(d.glob("*SEAL-RECORD*.yaml"))
    vs = {str(yaml.safe_load(s.read_text(encoding="utf-8"))["version"]) for s in seals}
    add("C1", len(seals) > 1 and len(vs) > 1,
        f"{len(seals)} selos no mesmo diretorio, versoes {sorted(vs)}")

    # C2 — nao valida in-place, mas valida no conjunto de origem
    a, b = F/"C2_SET_A", F/"C2"
    same = sha(a/"SEAL-RECORD.yaml") == sha(b/"SEAL-RECORD.yaml")
    doc = seal("C2")
    div_here = [m["path"] for m in doc["members"] if (b/m["path"]).is_file() and sha(b/m["path"]) != m["sha256"]]
    ok_there = all(sha(a/m["path"]) == m["sha256"] for m in doc["members"] if (a/m["path"]).is_file())
    add("C2", same and div_here and ok_there,
        f"selo byte-identico ao de C2_SET_A={same}; diverge em C2 nos membros {div_here}; "
        f"confere em C2_SET_A={ok_there}")

    # C3 — self-reference invalida
    doc = seal("C3"); d = F/"C3"
    selfref = [m for m in doc["members"] if "SEAL-RECORD" in m["path"]]
    impossible = bool(selfref) and selfref[0]["sha256"] != sha(d/"SEAL-RECORD.yaml")
    add("C3", bool(selfref) and impossible,
        f"members[] lista o proprio selo ({[m['path'] for m in selfref]}); hash declarado "
        f"{selfref[0]['sha256'][:16] if selfref else '-'}… != real {sha(d/'SEAL-RECORD.yaml')[:16]}… "
        f"-> insatisfazivel por construcao")

    # C4 — DOIS produtores validos e divergentes
    d = F/"C4"; doc = seal("C4")
    decl = doc["producer"]["toolchain_sha256"]
    real_a = sha(d/doc["producer"]["toolchain_path"])
    tb = F/"TOOLCHAINS"/"TOOLCHAIN-B.txt"; real_b = sha(tb)
    syntactic = bool(HEX64.fullmatch(decl))
    is_real_producer = (decl == real_b)          # o hash declarado E de um produtor REAL
    divergent = (decl != real_a)                 # e diverge do produtor efetivamente presente
    add("C4", syntactic and is_real_producer and divergent,
        f"declarado sintaticamente sha256 valido={syntactic}; declarado == sha256 REAL de "
        f"TOOLCHAIN-B={is_real_producer}; diverge do produtor presente TOOLCHAIN-A={divergent} "
        f"(A={real_a[:16]}… B={real_b[:16]}…) -> identidade divergente, NAO dado malformado")

    # C5 — colisao de local_id + identidade qualificada distinta
    d = F/"C5"; docs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))]
    ids = [i["local_id"] for doc in docs for i in doc["items"]]
    qual = {(doc["source_package_hash"], i["local_id"]) for doc in docs for i in doc["items"]}
    hashes = {doc["source_package_hash"] for doc in docs}
    add("C5", len(ids) != len(set(ids)) and len(qual) == len(ids) and len(hashes) == len(docs),
        f"local_ids={ids} (nus colidem); qualificadas distintas={len(qual)}=={len(ids)}; "
        f"{len(hashes)} package hashes distintos")

    # C6 — referencia cross-package por local_id nu
    d = F/"C6"; naked = []
    for p in sorted(d.glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        naked += [r for r in doc.get("cross_refs", []) if not r.get("source_package_hash")]
    add("C6", bool(naked), f"cross_refs sem source_package_hash: {naked}")

    # CTRL-INVALID — selo ilegivel
    try:
        yaml.safe_load((F/"CTRL-INVALID"/"SEAL-RECORD.yaml").read_text(encoding="utf-8"))
        add("CTRL-INVALID", False, "YAML parseou — a fixture NAO e ilegivel")
    except Exception as e:
        add("CTRL-INVALID", True, f"YAML ilegivel: {type(e).__name__}")
    return R

if __name__ == "__main__":
    R = prove()
    for r in R:
        print(f"  {'PROVADO ' if r['provado'] else '*** NAO '} {r['fixture']:<14} {r['prova']}")
    falhas = [r["fixture"] for r in R if not r["provado"]]
    print(f"\n  fixtures provadas: {len(R)-len(falhas)}/{len(R)}")
    if falhas:
        print(f"  ROUND_3_INVALID — sem prova estrutural: {falhas}"); sys.exit(2)
    print("  PORTAO PRE-EXECUCAO: PASS")
