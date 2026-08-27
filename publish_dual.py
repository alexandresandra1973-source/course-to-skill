#!/usr/bin/env python3
"""Publicação com CÓPIA EM MÍDIA INDEPENDENTE. Regra nova, aplicada a si mesma.

O hash CONFIRMA um artefato; não o RECONSTRÓI. Este projeto amarra tudo por hash
há trinta horas e o limite disso só apareceu quando o Drive caiu no meio de uma
execução de cinco horas: o `p003-pass1.json` guardava o SHA-256 do temporal-map
em ext4, e o temporal-map só existia no Drive. O digest sobreviveu e não
reconstruía nada.

REGRA: onde houver hash de artefato crítico, tem de haver CÓPIA do artefato em
mídia independente. Toda publicação passa por aqui: grava nos DOIS lados, relê
os DOIS, e falha alto se qualquer um divergir.
"""
from __future__ import annotations
import hashlib, shutil, sys
from pathlib import Path

DRIVE_ROOT = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude")
EXT4_ROOT = Path("/home/mtx/course-to-skill-claude/_mirror")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def publish(src: Path, rel: str) -> dict:
    """Grava em Drive e ext4, relê os dois, compara. Falha alto se divergir."""
    want = sha(src)
    out = {}
    for name, root in (("drive", DRIVE_ROOT), ("ext4", EXT4_ROOT)):
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        got = sha(dst)                       # RELÊ do destino, não confia na escrita
        out[name] = {"path": str(dst), "sha256": got, "ok": got == want}
    out["sha256"] = want
    out["both_ok"] = out["drive"]["ok"] and out["ext4"]["ok"]
    if not out["both_ok"]:
        raise IOError(f"publicação divergiu para {rel}: {out}")
    return out


def main() -> int:
    if len(sys.argv) < 3:
        print("uso: publish_dual.py <arquivo> <caminho/relativo/no/repo>")
        return 2
    r = publish(Path(sys.argv[1]), sys.argv[2])
    print(f"  sha256 {r['sha256']}")
    print(f"  drive  {r['drive']['ok']}  {r['drive']['path']}")
    print(f"  ext4   {r['ext4']['ok']}   {r['ext4']['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
