#!/usr/bin/env python3
"""PACKAGE_IDENTITY verifier — E6 e I4 do ARCHITECTURE FREEZE.

Identidade cross-package e propriedade do ENVELOPE, nao do hashing do conjunto.
MECHANICAL / OFFLINE.

Regras:
  NAKED_LOCAL_ID          referencia cross-package sem source_package_hash
  GLOBAL_ID_COLLISION     local_id nu colide entre pacotes distintos
  QUALIFIED_ID_NOT_DISTINCT  identidade qualificada nao permanece distinta
"""
from __future__ import annotations
import json, pathlib, sys, collections

def verify(packages_dir):
    d = pathlib.Path(packages_dir)
    if not d.is_dir():
        return {"verdict": "INVALID", "codes": ["PACKAGES_DIR_MISSING"], "detail": {}}
    pkgs = sorted(d.glob("*.json"))
    if len(pkgs) < 1:
        return {"verdict": "INVALID", "codes": ["NO_PACKAGES"], "detail": {}}

    codes, detail = [], {}
    loaded = []
    for p in pkgs:
        try:
            loaded.append((p.name, json.loads(p.read_text(encoding="utf-8"))))
        except Exception as e:
            return {"verdict": "INVALID", "codes": ["PACKAGE_UNPARSEABLE"],
                    "detail": {"erro": f"{p.name}: {type(e).__name__}"}}

    # --- identidade NUA: local_id sozinho
    naked = collections.Counter()
    qualified = collections.Counter()
    for name, doc in loaded:
        ph = doc.get("source_package_hash")
        if not ph:
            return {"verdict": "INVALID", "codes": ["PACKAGE_WITHOUT_HASH"],
                    "detail": {"erro": name}}
        for it in doc.get("items", []):
            naked[it["local_id"]] += 1
            qualified[(ph, it["local_id"])] += 1
    detail["packages"] = [n for n, _ in loaded]
    detail["local_ids_total"] = sum(naked.values())
    collided = sorted(k for k, v in naked.items() if v > 1)
    detail["naked_collisions"] = collided
    detail["qualified_distinct"] = len(qualified)
    if collided:
        codes.append("GLOBAL_ID_COLLISION")
    # a identidade qualificada TEM de permanecer distinta
    if len(qualified) != sum(naked.values()):
        codes.append("QUALIFIED_ID_NOT_DISTINCT")

    # --- referencias cross-package: tem de ser qualificadas
    naked_refs = []
    for name, doc in loaded:
        for r in doc.get("cross_refs", []):
            if not isinstance(r, dict) or not r.get("source_package_hash"):
                naked_refs.append({"pacote": name, "ref": r})
    detail["naked_refs"] = naked_refs
    if naked_refs:
        codes.append("NAKED_LOCAL_ID")

    codes = sorted(set(codes))
    return {"verdict": "FAIL" if codes else "PASS", "codes": codes, "detail": detail}

if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1]), ensure_ascii=False, indent=2))
