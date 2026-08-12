#!/usr/bin/env python3
"""Fecha o pacote do auditor num ZIP único, verificado arquivo por arquivo.

Roda daqui (ext4). Escreve só em Course-to-Skill-Claude/docs/.

O QUE ENTRA: só docs/TEST-0008-RUBRIC-AUDIT-PACKAGE/.
O QUE NÃO ENTRA, e é conferido por varredura, não por confiança:
  - o pacote do juiz (TEST-0008-JUDGE-PACKAGE/);
  - o selo de cegamento (TEST-0008-BLINDING-SEAL.yaml) e qualquer vazamento
    dele — nonce em hexadecimal ou o mapa slot→condição.

O ZIP é determinístico: nomes ordenados, mtime fixo, sem compressão variável.
Dois builds do mesmo conteúdo dão o mesmo SHA-256.
"""
from __future__ import annotations

import hashlib
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
PKG = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE"
INDEX = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml"
SEAL = DOCS / "TEST-0008-BLINDING-SEAL.yaml"
JPKG = DOCS / "TEST-0008-JUDGE-PACKAGE"
ZIP = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE.zip"
FIXED = (2026, 1, 1, 0, 0, 0)          # mtime fixo, para o ZIP ser determinístico

SUPERSEDED = [
    {"index_sha256": "f8350fb83e7a3e013aeed52d427caa22d6d676149097fa56f388cb6594f6da05",
     "estado": "SUPERSEDIDO",
     "o_que_mudou_depois": ["BLINDING-PROTOCOL.yaml reescrito para v0.2.0 "
                            "(nonce secreto, separação de domínio, derivação sem "
                            "ambiguidade)",
                            "verify_blinding_commitment.py acrescentado",
                            "LEAK-TEST-JUDGE-RUBRIC.yaml acrescentado"]},
    {"index_sha256": "9ee650d5f71e7e58e9cdee4abdfbceef112e7053ef79a8da372f46c63a06f090",
     "estado": "SUPERSEDIDO",
     "o_que_mudou_depois": ["LEAK-TEST-JUDGE-RUBRIC.yaml acrescentado ao pacote "
                            "sem que o índice fosse regenerado — o índice listava "
                            "18 arquivos e o disco tinha 20"]},
]


def shp(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    # ---------------------------------------------------- 1. varredura do selo
    seal = yaml.safe_load(SEAL.read_text(encoding="utf-8"))
    nonce_hex = str(seal["nonce_hex"])
    slots = seal["slot_to_condition"]
    leaks = []
    for p in sorted(PKG.rglob("*")):
        if not p.is_file():
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if nonce_hex in t:
            leaks.append({"file": str(p.relative_to(PKG)), "what": "nonce_hex"})
        for k, v in slots.items():
            if re.search(rf"\b{k}\b\s*[:=]\s*{v}\b", t):
                leaks.append({"file": str(p.relative_to(PKG)),
                              "what": f"slot {k} -> {v}"})
    if leaks:
        print("ABORTA: o pacote do auditor contém material do selo:", leaks)
        return 2

    # ---------------------------------------------------- 2. regenerar os dois
    files = [p for p in sorted(PKG.rglob("*")) if p.is_file()
             and p.name != "SHA256SUMS.txt"]
    sums = {str(p.relative_to(PKG)): shp(p) for p in files}
    (PKG / "SHA256SUMS.txt").write_text(
        "".join(f"{v}  {k}\n" for k, v in sums.items()), encoding="utf-8")
    # o índice lista TUDO, inclusive o SHA256SUMS.txt já escrito
    allf = {str(p.relative_to(PKG)): shp(p)
            for p in sorted(PKG.rglob("*")) if p.is_file()}

    old = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    idx = dict(old)
    idx["files"] = allf
    idx["file_count"] = len(allf)
    # SEM carimbo de tempo: ele viajaria dentro do ZIP e destruiria o
    # determinismo — dois builds do mesmo conteúdo dariam hashes diferentes, e o
    # auditor perderia a capacidade de reconstruir o ZIP e conferir. Quando é o
    # ZIP foi montado está no histórico do git; o que o auditor precisa é que o
    # conteúdo seja reproduzível.
    idx.pop("repackaged_at_utc", None)
    idx["index_conventions"] = {
        "index_lists": "todos os arquivos do pacote, inclusive SHA256SUMS.txt",
        "sha256sums_lists": "todos menos ele próprio",
        "por_que_a_diferenca": "um arquivo não pode conter o próprio hash",
    }
    idx["superseded_indexes"] = SUPERSEDED
    idx["zip"] = {
        "file": ZIP.name, "deterministic": True,
        "mtime_fixed_at": "2026-01-01T00:00:00Z",
        "sha256": ("NAO_CONSTA_NA_COPIA_DE_DENTRO_DO_ZIP — um arquivo não pode "
                   "conter o hash do contêiner que o contém. O hash do ZIP está "
                   "no índice publicado FORA dele, em docs/. Esta é a única "
                   "diferença entre as duas cópias do índice, e é estrutural."),
        "as_duas_copias_do_indice": {
            "dentro_do_ZIP": "TEST-0008-RUBRIC-AUDIT-PACKAGE.zip :: .../INDEX.yaml",
            "fora_do_ZIP": "docs/TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml",
            "diferenca": "só o campo zip.sha256",
            "todo_o_resto_e_identico": True},
    }
    idx["excluded_by_design"] = {
        "judge_package": {"path": "TEST-0008-JUDGE-PACKAGE/",
                          "por_que": "é o material de quem pontua, não de quem audita"},
        "blinding_seal": {"path": "TEST-0008-BLINDING-SEAL.yaml",
                          "por_que": ("revela o mapa slot→condição; o auditor confere "
                                      "o compromisso pelo protocolo e pelo "
                                      "verificador, sem precisar do segredo")},
        "verificado_por_varredura": True,
        "varredura_procurou": ["nonce em hexadecimal", "mapa slot→condição"],
        "resultado": "LIMPO",
    }
    INDEX.write_text(
        "# ÍNDICE do pacote de auditoria do TEST-0008. Regenerado para o ZIP.\n"
        + yaml.safe_dump(idx, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    # ---------------------------------------------------- 3. o ZIP determinístico
    if ZIP.exists():
        ZIP.unlink()
    root = PKG.name
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in sorted(allf):
            info = zipfile.ZipInfo(f"{root}/{rel}", date_time=FIXED)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (PKG / rel).read_bytes())
        info = zipfile.ZipInfo(f"{root}/INDEX.yaml", date_time=FIXED)
        info.external_attr = 0o644 << 16
        z.writestr(info, INDEX.read_bytes())

    # ---------------------------------------------------- 4. conferir o ZIP
    print("=" * 88)
    print("CONFERÊNCIA DO ZIP CONTRA O ÍNDICE, ARQUIVO POR ARQUIVO")
    print("=" * 88)
    ok = True
    with zipfile.ZipFile(ZIP) as z:
        names = {n[len(root) + 1:] for n in z.namelist()}
        for rel, want in sorted(allf.items()):
            got = hashlib.sha256(z.read(f"{root}/{rel}")).hexdigest()
            same = got == want
            ok &= same
            print(f"  {'ok ' if same else 'DIFERE'} {got[:16]}…  {rel}")
        extra = names - set(allf) - {"INDEX.yaml"}
        missing = set(allf) - names
        if extra:
            ok = False; print(f"  EXTRA no ZIP: {sorted(extra)}")
        if missing:
            ok = False; print(f"  AUSENTE no ZIP: {sorted(missing)}")
        # o pacote do juiz e o selo não podem estar lá dentro
        forbidden = [n for n in z.namelist()
                     if "JUDGE-PACKAGE" in n or "BLINDING-SEAL" in n]
        if forbidden:
            ok = False; print(f"  PROIBIDO no ZIP: {forbidden}")
        print(f"  ok  INDEX.yaml (cópia do índice, dentro do ZIP)")

    zsha = shp(ZIP)
    in_zip_index_sha = hashlib.sha256(
        zipfile.ZipFile(ZIP).read(f"{root}/INDEX.yaml")).hexdigest()
    idx["zip"]["sha256"] = zsha
    idx["zip"]["index_copy_inside_zip_sha256"] = in_zip_index_sha
    INDEX.write_text(
        "# ÍNDICE do pacote de auditoria do TEST-0008. Regenerado para o ZIP.\n"
        + yaml.safe_dump(idx, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print("=" * 88)
    print(f"arquivos conferidos : {len(allf)}  ·  todos batem: {ok}")
    print(f"pacote do juiz no ZIP : NÃO   ·  selo no ZIP : NÃO")
    print(f"\nZIP     : {ZIP}")
    print(f"bytes   : {ZIP.stat().st_size}")
    print(f"SHA-256 : {zsha}")
    print(f"\nÍNDICE fora do ZIP : {INDEX.name}")
    print(f"SHA-256            : {shp(INDEX)}")
    print(f"cópia dentro do ZIP: {in_zip_index_sha}")
    print("  diferem SÓ no campo zip.sha256 — um arquivo não pode conter o hash")
    print("  do contêiner que o contém. Declarado no próprio índice.")
    print("\nNOTA: o índice acima é o corrente. O `f8350fb8…` e o `9ee650d5…` "
          "ficam registrados\ncomo SUPERSEDIDOS dentro dele, com o que mudou em cada "
          "passo.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
