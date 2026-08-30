#!/usr/bin/env python3
"""Constroi as fixtures SINTETICAS e DESCARTAVEIS do PILOT-MS-000A.

NENHUMA fixture e mutacao de artefato historico. Nada em _mirror/, cts/, compiler-*,
runners ou pilotos e lido, copiado ou tocado. Todo conteudo abaixo e inventado aqui.
"""
from __future__ import annotations
import hashlib, pathlib, shutil, json, os

F = pathlib.Path(__file__).parent / "fixtures"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def seal_yaml(version, members, producer_path, producer_sha, extra=""):
    s = f"artifact_id: SYNTHETIC-SEAL\nversion: '{version}'\n"
    s += f"producer:\n  toolchain_path: {producer_path}\n  toolchain_sha256: '{producer_sha}'\n" if producer_path else "producer: toolchain textual v1.0\n"
    s += extra
    s += "members:\n"
    for rel, h in members:
        s += f"  - path: {rel}\n    sha256: '{h}'\n"
    return s

def write_members(d, files):
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for rel, content in files:
        p = d / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8"); os.chmod(p, 0o644)
        out.append((rel, sha(p)))
    return out

def toolchain(d, body):
    p = d / "TOOLCHAIN.txt"; p.write_text(body, encoding="utf-8"); os.chmod(p, 0o644)
    return sha(p)

if F.exists(): shutil.rmtree(F)
F.mkdir(parents=True)
REG = F / "EXTERNAL-SEAL-REGISTRY.txt"          # fora de todo conjunto selado
reg_lines = []

BODY = [("alpha.txt", "conteudo sintetico alpha\n"),
        ("beta/gamma.txt", "conteudo sintetico gamma\n")]

# ---------------------------------------------------------------- HAPPY
d = F / "HAPPY"; mem = write_members(d, BODY)
tc = toolchain(d, "toolchain sintetico v1\n")
mem = [m for m in mem if m[0] != "TOOLCHAIN.txt"] + [("TOOLCHAIN.txt", tc)]
(d / "SEAL-RECORD.yaml").write_text(seal_yaml("1.0", mem, "TOOLCHAIN.txt", tc), encoding="utf-8")
reg_lines.append(f"HAPPY/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")

# ---------------------------------------------------------------- C1 shared mutable dir
d = F / "C1"; mem = write_members(d, BODY)
tc = toolchain(d, "toolchain sintetico v1\n"); mem = mem + [("TOOLCHAIN.txt", tc)]
(d / "SEAL-RECORD.yaml").write_text(seal_yaml("1.0", mem, "TOOLCHAIN.txt", tc), encoding="utf-8")
(d / "SEAL-RECORD-v2.yaml").write_text(seal_yaml("2.0", mem, "TOOLCHAIN.txt", tc), encoding="utf-8")
reg_lines += [f"C1/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}",
              f"C1/SEAL-RECORD-v2.yaml {sha(d/'SEAL-RECORD-v2.yaml')}"]

# ------------------------------------------- C2 nao valida no lugar (selo copiado de A)
dA = F / "C2_SET_A"; memA = write_members(dA, [("alpha.txt", "conteudo do conjunto A\n")])
tcA = toolchain(dA, "toolchain sintetico v1\n"); memA = memA + [("TOOLCHAIN.txt", tcA)]
(dA / "SEAL-RECORD.yaml").write_text(seal_yaml("1.0", memA, "TOOLCHAIN.txt", tcA), encoding="utf-8")
d = F / "C2"; write_members(d, [("alpha.txt", "conteudo do conjunto B, DIFERENTE de A\n")])
tcB = toolchain(d, "toolchain sintetico v1\n")
shutil.copyfile(dA / "SEAL-RECORD.yaml", d / "SEAL-RECORD.yaml")   # byte-identico ao de A
reg_lines += [f"C2_SET_A/SEAL-RECORD.yaml {sha(dA/'SEAL-RECORD.yaml')}",
              f"C2/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}"]

# ---------------------------------------------------------------- C3 auto-referencia
d = F / "C3"; mem = write_members(d, BODY)
tc = toolchain(d, "toolchain sintetico v1\n"); mem = mem + [("TOOLCHAIN.txt", tc)]
tmp = seal_yaml("1.0", mem, "TOOLCHAIN.txt", tc)
(d / "SEAL-RECORD.yaml").write_text(tmp, encoding="utf-8")
selfh = sha(d / "SEAL-RECORD.yaml")
mem_self = mem + [("SEAL-RECORD.yaml", selfh)]                     # lista a si mesmo
(d / "SEAL-RECORD.yaml").write_text(seal_yaml("1.0", mem_self, "TOOLCHAIN.txt", tc), encoding="utf-8")
reg_lines.append(f"C3/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")

# ---------------------------------------------------------------- C4 produtor divergente
d = F / "C4"; mem = write_members(d, BODY)
tc = toolchain(d, "toolchain sintetico v1\n"); mem = mem + [("TOOLCHAIN.txt", tc)]
fake = "0" * 64                                                     # hash de toolchain que nao e o real
(d / "SEAL-RECORD.yaml").write_text(seal_yaml("1.0", mem, "TOOLCHAIN.txt", fake), encoding="utf-8")
reg_lines.append(f"C4/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")

# ---------------------------------------------------- CTRL-INVALID selo ilegivel
d = F / "CTRL-INVALID"; write_members(d, BODY)
(d / "SEAL-RECORD.yaml").write_text("::: isto nao e YAML valido :::\n  - [a, b\n", encoding="utf-8")
reg_lines.append(f"CTRL-INVALID/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")

REG.write_text("\n".join(reg_lines) + "\n", encoding="utf-8"); os.chmod(REG, 0o644)

# ---------------------------------------------------------------- C5 colisao de id
d = F / "C5"; d.mkdir(parents=True)
for nome, ph in [("pkg-A.json", "a" * 64), ("pkg-B.json", "b" * 64)]:
    (d / nome).write_text(json.dumps({
        "source_package_hash": ph,
        "items": [{"local_id": "EV-0001"}, {"local_id": "EV-0002"}],
        "cross_refs": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- C6 local_id nu
d = F / "C6"; d.mkdir(parents=True)
(d / "pkg-A.json").write_text(json.dumps({
    "source_package_hash": "c" * 64,
    "items": [{"local_id": "EV-0001"}],
    "cross_refs": [{"local_id": "EV-0001"}]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(d / "pkg-B.json").write_text(json.dumps({
    "source_package_hash": "d" * 64,
    "items": [{"local_id": "EV-0009"}],
    "cross_refs": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for p in F.rglob("*"):
    if p.is_file(): os.chmod(p, 0o644)
print("fixtures construidas em", F)
for p in sorted(F.rglob("*")):
    if p.is_file(): print(f"  {p.relative_to(F)}")
