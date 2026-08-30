"""MS-001 — SOURCE PACKAGE. Member set literal do contrato aceito (MS-000B),
com L0 = RAW-CAPTION.json. Selo reusa o contrato e o verificador de MS-000A."""
import json, hashlib, pathlib, yaml, collections

REQUIRED_MEMBERS = [
 ("SOURCE-PROFILE",          "SOURCE-PROFILE.json"),
 ("L0",                      "L0/RAW-CAPTION.json"),
 ("ARTIFACTS",               "ARTIFACTS/ARTIFACT-INDEX.json"),
 ("SOURCE_ANCHORS",          "SOURCE-ANCHORS.jsonl"),
 ("EVIDENCE",                "EVIDENCE.jsonl"),
 ("CLAIMS",                  "CLAIMS.jsonl"),
 ("SOURCE_LOCAL_CANDIDATES", "SOURCE-LOCAL-CANDIDATES.json"),
 ("COMPILE-TRACE",           "COMPILE-TRACE.jsonl"),
 ("LOCAL-COHERENCE-REPORT",  "LOCAL-COHERENCE-REPORT.json"),
 ("DECLARATION-SPACE-INDEX", "DECLARATION-SPACE-INDEX.json"),
 ("SEAL-RECORD",             "SEAL-RECORD.yaml"),
]
TOOLCHAIN_PATH = "TOOLCHAIN.json"


def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
def sha_text(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def sha_file(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def wjson(p, o): pathlib.Path(p).write_text(json.dumps(o, sort_keys=True, ensure_ascii=False, indent=1), encoding="utf-8")
def wjsonl(p, L): pathlib.Path(p).write_text("".join(canon(x) + "\n" for x in L), encoding="utf-8")


def member_manifest(d):
    """EXCLUI o SEAL-RECORD: condicao 7 de SEALED, nenhum membro se auto-referencia."""
    d = pathlib.Path(d)
    return sorted([{"path": p, "sha256": sha_file(d / p)}
                   for n, p in REQUIRED_MEMBERS if n != "SEAL-RECORD" and (d / p).is_file()]
                  + ([{"path": TOOLCHAIN_PATH, "sha256": sha_file(d / TOOLCHAIN_PATH)}]
                     if (d / TOOLCHAIN_PATH).is_file() else []),
                  key=lambda x: x["path"])


def source_package_hash(manifest): return sha_text(canon(manifest))


def completeness_gate(d):
    d = pathlib.Path(d)
    missing = [n for n, p in REQUIRED_MEMBERS if not (d / p).is_file()]
    empty = [n for n, p in REQUIRED_MEMBERS if (d / p).is_file() and (d / p).stat().st_size == 0]
    if not (d / TOOLCHAIN_PATH).is_file(): missing.append("TOOLCHAIN")
    return {"verdict": "PASS" if not missing and not empty else "FAIL",
            "codes": (["REQUIRED_MEMBER_MISSING"] if missing else []) +
                     (["REQUIRED_MEMBER_EMPTY"] if empty else []),
            "missing": missing, "empty": empty, "required_total": len(REQUIRED_MEMBERS)}


def seal(d, source_id, content_hash, registry_path):
    d = pathlib.Path(d)
    man = member_manifest(d)
    sph = source_package_hash(man)
    # forma LITERAL do contrato aceito (MS-000B): producer.{toolchain_path,toolchain_sha256}
    rec = {"artifact_id": f"MS001A-SEAL-{source_id}", "artifact_status": "SEALED",
           "seal_contract_version": "SEALED/7-conditions/freeze-6d0eb7dd",
           "source_id": source_id, "source_content_hash": content_hash,
           "member_manifest_hash": sph, "source_package_hash": sph,
           "producer": {"toolchain_path": TOOLCHAIN_PATH,
                        "toolchain_sha256": sha_file(d / TOOLCHAIN_PATH)},
           "members_count": len(man), "members": man,
           "nota": "SEAL-RECORD nao se auto-referencia (condicao 7). Sem mtime (condicao 6)."}
    (d / "SEAL-RECORD.yaml").write_text(
        yaml.safe_dump(rec, sort_keys=True, allow_unicode=True, default_flow_style=False),
        encoding="utf-8")
    srh = sha_file(d / "SEAL-RECORD.yaml")
    with open(registry_path, "a", encoding="utf-8") as f:
        f.write(f"{srh}  {d.name}/SEAL-RECORD.yaml  source_package_hash={sph}\n")
    return {"source_package_hash": sph, "seal_record_hash": srh, "members": len(man)}
