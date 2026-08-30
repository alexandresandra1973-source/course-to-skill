#!/usr/bin/env python3
"""SEAL_INTEGRITY verifier — as sete condicoes de SEALED congeladas na secao 13 do
ARCHITECTURE FREEZE (6d0eb7ddabe4d7c7b46d7e1934783e8f0e1603b9e3ac9241cbff1a24cfbc780b).

MECHANICAL / OFFLINE. Zero chamadas de modelo. Nao usa mtime, relogio nem rede.

Estados: PASS | FAIL (com codigos) | INVALID (nao avaliavel).
FAIL != INVALID: o primeiro e defeito no objeto, o segundo e impossibilidade de avaliar.
"""
from __future__ import annotations
import hashlib, pathlib, sys, json

try:
    import yaml
except ImportError:                                     # pragma: no cover
    print("PyYAML ausente", file=sys.stderr); raise

SEAL_GLOB = "*SEAL-RECORD*.yaml"

def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(seal_dir, external_registry=None, toolchain_dir=None):
    """Devolve {'verdict': PASS|FAIL|INVALID, 'codes': [...], 'detail': {...}}"""
    d = pathlib.Path(seal_dir)
    codes, detail = [], {}

    if not d.is_dir():
        return {"verdict": "INVALID", "codes": ["SEAL_DIR_MISSING"], "detail": {}}

    seals = sorted(d.glob(SEAL_GLOB))
    detail["seal_records_found"] = [s.name for s in seals]
    if not seals:
        return {"verdict": "INVALID", "codes": ["SEAL_RECORD_MISSING"], "detail": detail}

    # --- condicao 4: nenhuma outra versao selada escreve o mesmo diretorio
    parsed = []
    for s in seals:
        try:
            parsed.append((s, yaml.safe_load(s.read_text(encoding="utf-8"))))
        except Exception as e:
            return {"verdict": "INVALID", "codes": ["SEAL_RECORD_UNPARSEABLE"],
                    "detail": {**detail, "erro": f"{s.name}: {type(e).__name__}"}}
    for s, doc in parsed:
        if not isinstance(doc, dict):
            return {"verdict": "INVALID", "codes": ["SEAL_RECORD_UNPARSEABLE"],
                    "detail": {**detail, "erro": f"{s.name}: raiz nao e mapeamento"}}
    versions = {str((doc or {}).get("version")) for _, doc in parsed}
    detail["versions_declared"] = sorted(versions)
    if len(parsed) > 1 and len(versions) > 1:
        codes.append("SHARED_MUTABLE_DIRECTORY")

    seal, doc = parsed[0]
    members = doc.get("members")
    if not isinstance(members, list) or not members:
        return {"verdict": "INVALID", "codes": ["SEAL_RECORD_UNPARSEABLE"],
                "detail": {**detail, "erro": "members[] ausente ou vazio"}}

    listed = {}
    for m in members:
        if not isinstance(m, dict) or "path" not in m or "sha256" not in m:
            return {"verdict": "INVALID", "codes": ["SEAL_RECORD_UNPARSEABLE"],
                    "detail": {**detail, "erro": "membro sem path/sha256"}}
        listed[m["path"]] = m["sha256"]
    detail["members_listed"] = len(listed)

    # --- condicao 7: nenhum membro se auto-referencia
    seal_names = {s.name for s in seals}
    self_refs = [p for p in listed if pathlib.Path(p).name in seal_names]
    if self_refs:
        codes.append("SEAL_SELF_REFERENCE"); detail["self_refs"] = self_refs

    # --- condicao 6: o selo nao pode depender de mtime
    if any(k in doc for k in ("mtime", "mtime_utc", "modified_at")) or \
       any(isinstance(m, dict) and any(k in m for k in ("mtime", "mtime_utc")) for m in members):
        codes.append("MTIME_DEPENDENCY")

    # --- condicao 1 + 3: conjunto completo e hashes conferem NO LUGAR
    on_disk = {str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()
               and p.name not in seal_names}
    extra   = sorted(on_disk - set(listed))          # membro presente e nao listado
    missing = sorted(set(listed) - on_disk)          # listado e ausente
    detail["extra_on_disk"], detail["missing_on_disk"] = extra, missing
    if extra or missing:
        codes.append("MEMBER_SET_MISMATCH")

    mismatched = []
    for rel, want in listed.items():
        f = d / rel
        if not f.is_file():
            continue                                  # ja contabilizado em MEMBER_SET_MISMATCH
        if sha256(f) != want:
            mismatched.append(rel)
    detail["hash_mismatched"] = mismatched
    if mismatched:
        codes.append("MEMBER_HASH_MISMATCH")
        codes.append("DOES_NOT_VALIDATE_IN_PLACE")    # o selo nao confere no diretorio em que vive

    # --- condicao 5: produtor e referencia com hash proprio, nao campo de texto
    prod = doc.get("producer")
    if not isinstance(prod, dict) or "toolchain_sha256" not in prod or "toolchain_path" not in prod:
        codes.append("PRODUCER_IDENTITY_MISMATCH"); detail["producer"] = "ausente ou apenas texto"
    else:
        base = pathlib.Path(toolchain_dir) if toolchain_dir else d
        tp = base / prod["toolchain_path"]
        if not tp.is_file():
            codes.append("PRODUCER_IDENTITY_MISMATCH"); detail["producer"] = "toolchain nao resolve"
        else:
            real = sha256(tp)
            detail["producer_declared"], detail["producer_real"] = prod["toolchain_sha256"], real
            if real != prod["toolchain_sha256"]:
                codes.append("PRODUCER_IDENTITY_MISMATCH")

    # --- condicao 2: hash do selo registrado FORA do conjunto
    seal_hash = sha256(seal)
    detail["seal_sha256"] = seal_hash
    if external_registry is None:
        codes.append("SEAL_HASH_NOT_REGISTERED_EXTERNALLY")
    else:
        reg = pathlib.Path(external_registry)
        try:
            inside = reg.resolve().is_relative_to(d.resolve())
        except AttributeError:                        # pragma: no cover
            inside = str(reg.resolve()).startswith(str(d.resolve()))
        if inside or not reg.is_file() or seal_hash not in reg.read_text(encoding="utf-8"):
            codes.append("SEAL_HASH_NOT_REGISTERED_EXTERNALLY")

    codes = sorted(set(codes))
    return {"verdict": "FAIL" if codes else "PASS", "codes": codes, "detail": detail}

if __name__ == "__main__":
    a = sys.argv[1:]
    print(json.dumps(verify(a[0], a[1] if len(a) > 1 else None,
                            a[2] if len(a) > 2 else None), ensure_ascii=False, indent=2))
