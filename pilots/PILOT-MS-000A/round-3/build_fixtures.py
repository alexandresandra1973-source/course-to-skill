#!/usr/bin/env python3
"""ROUND 3 — fixtures SINTETICAS e DESCARTAVEIS do PILOT-MS-000A.

NENHUMA fixture e mutacao de artefato historico. Nada em _mirror/, cts/, compiler-*,
runners, pilotos ou Drive e lido, copiado ou tocado.

DIFERENCA DA ROUND 2 — apenas C4:
  a ROUND 2 plantava "0"*64, um placeholder. Aqui existem DOIS produtores REAIS,
  TOOLCHAIN-A.txt (o que esta de fato no conjunto selado) e TOOLCHAIN-B.txt (outro
  produtor real, fora do conjunto). O selo aponta para A e declara o sha256 de B.
  Ambos sao sha256 reais de arquivos existentes: o defeito e DIVERGENCIA DE
  IDENTIDADE, nao dado malformado.
"""
from __future__ import annotations
import hashlib, pathlib, shutil, json, os

F = pathlib.Path(__file__).parent / "fixtures"
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def seal_yaml(version, members, producer_path, producer_sha):
    s = f"artifact_id: SYNTHETIC-SEAL\nversion: '{version}'\n"
    s += f"producer:\n  toolchain_path: {producer_path}\n  toolchain_sha256: '{producer_sha}'\n"
    s += "members:\n"
    for rel, h in members:
        s += f"  - path: {rel}\n    sha256: '{h}'\n"
    return s

def write_members(d, files):
    d.mkdir(parents=True, exist_ok=True); out = []
    for rel, content in files:
        p = d / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8"); os.chmod(p, 0o644); out.append((rel, sha(p)))
    return out

def toolchain(d, name, body):
    p = d / name; p.write_text(body, encoding="utf-8"); os.chmod(p, 0o644); return sha(p)

if F.exists(): shutil.rmtree(F)
F.mkdir(parents=True)
REG = F / "EXTERNAL-SEAL-REGISTRY.txt"; reg = []
BODY = [("alpha.txt", "conteudo sintetico alpha\n"), ("beta/gamma.txt", "conteudo sintetico gamma\n")]

# --- produtor B: artefato REAL de um segundo produtor, fora de qualquer conjunto selado
TC = F / "TOOLCHAINS"; TC.mkdir()
shb = toolchain(TC, "TOOLCHAIN-B.txt", "toolchain sintetico B — produtor DIFERENTE, versao 2\n")

def standard(name, version="1.0", extra_seal=None, producer_sha_override=None):
    d = F / name; mem = write_members(d, BODY)
    sha_a = toolchain(d, "TOOLCHAIN-A.txt", "toolchain sintetico A — produtor real, versao 1\n")
    mem = mem + [("TOOLCHAIN-A.txt", sha_a)]
    decl = producer_sha_override or sha_a
    (d / "SEAL-RECORD.yaml").write_text(seal_yaml(version, mem, "TOOLCHAIN-A.txt", decl), encoding="utf-8")
    reg.append(f"{name}/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")
    return d, mem, sha_a

standard("HAPPY")

# --- C1: duas versoes seladas escrevendo o mesmo diretorio
d, mem, sha_a = standard("C1", "1.0")
(d / "SEAL-RECORD-v2.yaml").write_text(seal_yaml("2.0", mem, "TOOLCHAIN-A.txt", sha_a), encoding="utf-8")
reg.append(f"C1/SEAL-RECORD-v2.yaml {sha(d/'SEAL-RECORD-v2.yaml')}")

# --- C2: selo byte-identico ao de outro conjunto; nao valida no lugar
dA, _, _ = standard("C2_SET_A")
(dA / "alpha.txt").write_text("conteudo do conjunto A\n", encoding="utf-8")
memA = [("alpha.txt", sha(dA/"alpha.txt")), ("beta/gamma.txt", sha(dA/"beta/gamma.txt")),
        ("TOOLCHAIN-A.txt", sha(dA/"TOOLCHAIN-A.txt"))]
(dA/"SEAL-RECORD.yaml").write_text(seal_yaml("1.0", memA, "TOOLCHAIN-A.txt", sha(dA/"TOOLCHAIN-A.txt")), encoding="utf-8")
d = F / "C2"; write_members(d, BODY)
toolchain(d, "TOOLCHAIN-A.txt", "toolchain sintetico A — produtor real, versao 1\n")
(d / "alpha.txt").write_text("conteudo do conjunto B, DIFERENTE de A\n", encoding="utf-8")
shutil.copyfile(dA / "SEAL-RECORD.yaml", d / "SEAL-RECORD.yaml")
reg += [f"C2_SET_A/SEAL-RECORD.yaml {sha(dA/'SEAL-RECORD.yaml')}", f"C2/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}"]

# --- C3: o selo lista a si mesmo
d, mem, sha_a = standard("C3")
selfh = sha(d / "SEAL-RECORD.yaml")
(d / "SEAL-RECORD.yaml").write_text(seal_yaml("1.0", mem + [("SEAL-RECORD.yaml", selfh)], "TOOLCHAIN-A.txt", sha_a), encoding="utf-8")
reg.append(f"C3/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")

# --- C4: DOIS produtores REAIS e DIVERGENTES  <<< a correcao desta rodada
standard("C4", producer_sha_override=shb)   # aponta para A, declara o sha REAL de B

# --- CTRL-INVALID: selo ilegivel (controle do instrumento)
d = F / "CTRL-INVALID"; write_members(d, BODY)
(d / "SEAL-RECORD.yaml").write_text("::: isto nao e YAML valido :::\n  - [a, b\n", encoding="utf-8")
reg.append(f"CTRL-INVALID/SEAL-RECORD.yaml {sha(d/'SEAL-RECORD.yaml')}")

REG.write_text("\n".join(reg) + "\n", encoding="utf-8")

# --- C5 / C6: identidade
d = F / "C5"; d.mkdir()
for nome, ph in [("pkg-A.json", "a"*64), ("pkg-B.json", "b"*64)]:
    (d/nome).write_text(json.dumps({"source_package_hash": ph,
        "items": [{"local_id": "EV-0001"}, {"local_id": "EV-0002"}], "cross_refs": []},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
d = F / "C6"; d.mkdir()
(d/"pkg-A.json").write_text(json.dumps({"source_package_hash": "c"*64,
    "items": [{"local_id": "EV-0001"}], "cross_refs": [{"local_id": "EV-0001"}]},
    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(d/"pkg-B.json").write_text(json.dumps({"source_package_hash": "d"*64,
    "items": [{"local_id": "EV-0009"}], "cross_refs": []}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for p in F.rglob("*"):
    if p.is_file(): os.chmod(p, 0o644)
print("ROUND 3 — fixtures construidas")
print(f"  TOOLCHAIN-A (produtor real presente em C4): {sha(F/'C4'/'TOOLCHAIN-A.txt')}")
print(f"  TOOLCHAIN-B (produtor real declarado)     : {shb}")
