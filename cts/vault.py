"""Vault L0: armazenamento imutável endereçado por conteúdo (ADR-0001).

O vault é o único referente externo da arquitetura. Toda verificação termina
aqui. Reescrever a fonte muda o sha256 e quebra todos os spans — que é o
comportamento desejado.

O vault vive em ext4 (~/course-to-skill-claude/work/vault). As pastas do Drive
são DADO DE ENTRADA, somente leitura: `ingest` copia bytes para dentro do vault
e nunca escreve na origem.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .spans import Span, Resolution, hhmmss_to_mark

# Marca de tempo como aparece no transcript do PILOT-001: **12:23**
MARK_RE = re.compile(r"\*\*(\d{1,3}:[0-5]\d)\*\*")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class VaultObject:
    sha256: str
    bytes_: int
    origin: str          # caminho de origem, informativo
    mime: str


class Vault:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.objects = self.root / "objects"
        self.manifest_path = self.root / "manifest.jsonl"
        self.objects.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, VaultObject] = {}
        self._text_cache: dict[str, str] = {}
        self._marks_cache: dict[str, dict[str, int]] = {}
        if self.manifest_path.exists():
            for line in self.manifest_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    self._index[d["sha256"]] = VaultObject(
                        d["sha256"], d["bytes"], d["origin"], d["mime"])

    # ---------- ingestão ----------

    def ingest(self, src: Path, mime: str = "application/octet-stream") -> VaultObject:
        src = Path(src)
        digest = sha256_file(src)
        dest = self.objects / digest
        if not dest.exists():
            dest.write_bytes(src.read_bytes())
        obj = VaultObject(digest, dest.stat().st_size, str(src), mime)
        if digest not in self._index:
            self._index[digest] = obj
            with open(self.manifest_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"sha256": digest, "bytes": obj.bytes_,
                                     "origin": obj.origin, "mime": mime},
                                    ensure_ascii=False) + "\n")
        return obj

    # ---------- acesso ----------

    def has(self, sha12: str) -> str | None:
        for d in self._index:
            if d.startswith(sha12):
                return d
        return None

    def text(self, sha256: str) -> str:
        if sha256 not in self._text_cache:
            self._text_cache[sha256] = (self.objects / sha256).read_text(
                encoding="utf-8", errors="replace")
        return self._text_cache[sha256]

    def marks(self, sha256: str) -> dict[str, int]:
        """Índice marca-de-tempo -> offset de caractere logo após a marca."""
        if sha256 not in self._marks_cache:
            t = self.text(sha256)
            self._marks_cache[sha256] = {m.group(1): m.end() for m in MARK_RE.finditer(t)}
        return self._marks_cache[sha256]

    # ---------- resolução de span ----------

    def resolve(self, raw_span: str) -> Resolution:
        sp = Span.parse(raw_span)
        if sp is None:
            return Resolution(raw_span, False, "MALFORMED_SPAN")
        full = self.has(sp.obj)
        if full is None:
            return Resolution(raw_span, False, "OBJECT_NOT_IN_VAULT")

        if sp.kind == "char":
            t = self.text(full)
            if sp.b > len(t) or sp.a < 0 or sp.a > sp.b:
                return Resolution(raw_span, False, "RANGE_OUT_OF_BOUNDS",
                                  detail=f"len={len(t)}")
            frag = t[sp.a:sp.b]
            if not frag:
                return Resolution(raw_span, False, "EMPTY_RANGE")
            return Resolution(raw_span, True, "OK", text=frag)

        if sp.kind == "time":
            marks = self.marks(full)
            m0, m1 = hhmmss_to_mark(sp.a), hhmmss_to_mark(sp.b)
            if m0 not in marks:
                return Resolution(raw_span, False, "START_MARK_NOT_FOUND",
                                  detail=f"marca '{m0}' ausente ({len(marks)} marcas no objeto)")
            if m1 not in marks:
                return Resolution(raw_span, False, "END_MARK_NOT_FOUND",
                                  detail=f"marca '{m1}' ausente ({len(marks)} marcas no objeto)")
            t = self.text(full)
            a, b = marks[m0], marks[m1]
            if b <= a:
                return Resolution(raw_span, False, "EMPTY_RANGE",
                                  detail=f"offset início={a} fim={b}")
            return Resolution(raw_span, True, "OK", text=t[a:b])

        # frame: existe no vault ou não
        if self.has(sp.a):
            return Resolution(raw_span, True, "OK", text="")
        return Resolution(raw_span, False, "OBJECT_NOT_IN_VAULT",
                          detail=f"frame {sp.a}")

    def object_for_origin(self, needle: str) -> str | None:
        for d, o in self._index.items():
            if needle in o.origin:
                return d
        return None
