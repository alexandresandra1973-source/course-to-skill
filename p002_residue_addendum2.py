#!/usr/bin/env python3
"""ADITIVO 2 do resíduo do PILOT-002 — varredura por RADICAL, não por forma literal.

O addendum 1 buscou formas literais (`/compact`, `/context`, `accept edits`) e
declarou limpas coisas que estavam lá em outra forma. Esta varredura busca por
RADICAL e publica o que mais apareceu.

ADITIVO ESTRITO: o lock, os casos congelados, o freeze record e o addendum 1 são
lidos apenas para HASH. Nenhum deles é aberto para escrita.
"""
from __future__ import annotations
import hashlib, re, sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude")
DOCS = DRIVE/"docs"
P2 = DRIVE/"pilots/PILOT-002"
INTACT, CUT = P2/"00_SOURCE/L0-transcript.txt", P2/"00_SOURCE/L0-transcript-CUT.txt"
MIRROR = Path("/home/mtx/course-to-skill-claude/_mirror/docs")
OUT = DOCS/"HELDOUT-RESIDUE-ADDENDUM-2-PILOT-002.yaml"

IMUTAVEIS = {
    "heldout_lock": DOCS/"HELDOUT-LOCK-PILOT-002.yaml",
    "blind_cases": DOCS/"HELDOUT-BLIND-CASES-PILOT-002.yaml",
    "blind_cases_freeze_record": DOCS/"HELDOUT-BLIND-CASES-FREEZE-RECORD-PILOT-002.yaml",
    "residue_addendum_1": DOCS/"HELDOUT-RESIDUE-ADDENDUM-PILOT-002.yaml",
}
ESPERADO = {"l0_intact": "43b58271", "l0_cut": "85ea2290"}
HELD = [("Understanding Permission Modes", 715, 908),
        ("Managing Your Context Window and Token Usage", 2680, 3000)]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def corpo_falado():
    """Só fala. Linhas de título e marcas de tempo fora da busca."""
    MARK = re.compile(r"^\*\*(\d{1,3}:[0-5]\d)\*\*$")
    cur, out = None, []
    for blk in [x.strip() for x in CUT.read_text(encoding="utf-8").split("\n\n") if x.strip()]:
        m = MARK.match(blk)
        if m:
            a, b = m.group(1).split(":")
            cur = int(a)*60 + int(b)
            continue
        if blk.startswith("## ") or cur is None:
            continue
        out.append((cur, blk))
    return out


def mark(s: int) -> str:
    return f"{s//60}:{s%60:02d}"


def main() -> int:
    si, sc = sha(INTACT), sha(CUT)
    if not si.startswith(ESPERADO["l0_intact"]) or not sc.startswith(ESPERADO["l0_cut"]):
        sys.exit(f"FONTE ERRADA: íntegro {si[:8]} cortado {sc[:8]}")
    for nome, p in IMUTAVEIS.items():
        if not p.exists():
            sys.exit(f"ausente: {nome}")

    body = corpo_falado()
    # O corte é SEMIABERTO [início, fim): o bloco na marca de fim é o primeiro
    # bloco DEPOIS do corte, e sobrevive. É exatamente onde RES2-003 aparece.
    dentro = [(s, b) for s, b in body if any(lo <= s < hi for _, lo, hi in HELD)]
    assert not dentro, f"corpo cortado contém {len(dentro)} blocos dentro dos vãos"
    borda = [mark(s) for s, _ in body if any(s == hi for _, _, hi in HELD)]

    def hits(rad):
        return [(s, b) for s, b in body if rad in b.lower()]

    # --- vazamentos NOVOS, com citação verbatim conferida no ato ---
    novos = [
        {"leak_id": "RES2-001", "radical": "danger / skip", "mark": "29:02",
         "quote": "just going to type in claw dangerously skip or in this case, just "
                  "type in claw is fine",
         "o_que_vaza": "a rota de linha de comando para o modo sem restrição "
                       "(`--dangerously-skip-permissions`), em fala de demonstração",
         "afeta": ["BC-005"],
         "gravidade": "ALTA — o addendum 1 declarou BC-005 'segue como estava'. "
                      "Metade da resposta esperada de BC-005 é a flag de pular "
                      "permissões, e ela está no corpo falado fora do vão.",
         "continua_fora": "Shift+Tab para ciclar entre modos: `shift` tem ZERO "
                          "ocorrências no corpo falado."},
        {"leak_id": "RES2-002", "radical": "permiss", "mark": "78:17–78:24",
         "quote": "we talked about there's different five or four different permission "
                  "mode. Setting the right permission mode here is going to help you",
         "o_que_vaza": "a CONTAGEM aproximada de modos (ASR: 'five or four') e a "
                       "noção de que escolher o modo certo importa",
         "afeta": ["BC-001"],
         "gravidade": "MÉDIA — BC-001 já testava semântica e não nomeação pelo "
                      "addendum 1. Agora a contagem também não conta.",
         "continua_fora": "o que cada modo permite; nenhuma linha da tabela de modos."},
        {"leak_id": "RES2-003", "radical": "compact / summar", "mark": "50:00",
         "quote": "there's also compact. We also talk about that, right? You can "
                  "summarize the older conversations",
         "o_que_vaza": "a existência do comando de compactação e que ele resume "
                       "conversas antigas",
         "afeta": ["BC-008", "BC-009"],
         "gravidade": "ALTA — o addendum 1 listou `/compact` como verificado limpo. "
                      "Buscou COM barra; sem barra a palavra está lá, em 50:00, "
                      "exatamente na borda do vão 44:40–50:00. Produziu R-0087 no "
                      "bundle compilado.",
         "continua_fora": "o CUSTO de compactar (perda de informação) — que é "
                          "exatamente o que BC-008 pergunta."},
        {"leak_id": "RES2-004", "radical": "percent / window", "mark": "9:12 e 51:16",
         "quote": "percentage of the context window that we have consumed so far  |  "
                  "currently you can see we're at 26% for the context window here",
         "o_que_vaza": "ler o percentual de janela de contexto consumida, duas vezes, "
                       "ambas fora do vão",
         "afeta": ["BC-010", "BC-007"],
         "gravidade": "MÉDIA — o addendum 1 listou `/context` como limpo. O COMANDO "
                      "com barra segue ausente; o COMPORTAMENTO de ler o percentual "
                      "não. Produziu R-0018 no bundle.",
         "continua_fora": "o comando `/context`, suas quatro categorias (system "
                          "prompts, skills, memories, messages) e o limiar de 50% "
                          "— `50%` tem ZERO ocorrências."},
        {"leak_id": "RES2-005", "radical": "review", "mark": "26:14 e 27:02",
         "quote": "We have multiple agent spin up here to actually do the review  |  "
                  "we're going to have a human here to review that process",
         "o_que_vaza": "revisão automatizada com humano no laço, em demonstração de "
                       "workflow agêntico",
         "afeta": ["BC-003"],
         "gravidade": "BAIXA — CANDIDATO, NÃO CONFIRMADO. É revisão de workflow "
                      "agêntico, não a camada de IA que revisa o script do modo auto. "
                      "Semanticamente próximo, não idêntico. Registro sem arbitrar.",
         "continua_fora": "`accept edits` tem ZERO ocorrências; a distinção entre "
                          "accept edits e auto continua integralmente fora."},
    ]
    # Citação pode atravessar blocos (a fala é contínua; os blocos são só marcas
    # de tempo). Confere contra o corpo concatenado, normalizando espaço.
    corpo = " ".join(" ".join(b.split()) for _, b in body).lower()
    for n in novos:
        for q in n["quote"].split("  |  "):
            qn = " ".join(q.split()).lower()
            assert qn in corpo, f"citação não confere: {q[:50]}"

    # --- ruído que o radical produz e que a forma literal não produzia ---
    falsos = [
        {"radical": "rot", "casa_com": "protocol", "marks": ["0:34", "63:53", "64:01", "68:17"],
         "nota": "NÃO é `context rot`. `context rot` tem zero ocorrências."},
        {"radical": "fresh", "casa_com": "refresh / fresh design",
         "marks": ["28:40", "31:00", "59:44", "61:17"],
         "nota": "NÃO é `fresh context`."},
        {"radical": "window", "casa_com": "Windows (sistema operacional)", "marks": ["4:48"],
         "nota": "as outras quatro ocorrências são janela de contexto de verdade."},
        {"radical": "clear", "casa_com": "clear a terminal / clear plan / clear difference",
         "marks": ["10:48", "10:54", "17:48", "43:42"],
         "nota": "NÃO é `/clear`. O comando segue ausente."},
        {"radical": "flag", "casa_com": "flagging (num diff)", "marks": ["71:12"],
         "nota": "não é flag de linha de comando."},
    ]

    zero = [r for r in ["accept", "shift", "approv", "sandbox", "virtual environ",
                        "test environ", "human in the loop", "cycle", "degrad",
                        "thread", "memor", "monitor", "context rot", "50%"]
            if not hits(r)]

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "PILOT-002-HELDOUT-RESIDUE-ADDENDUM-2",
        "artifact_status": "ADDENDUM_ONLY_BASE_ARTIFACTS_UNMODIFIED",
        "pilot_id": "PILOT-002",
        "published_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "p002_residue_addendum2.py",
        "supersedes": None,
        "nature": {
            "additive_only": True,
            "base_artifacts_mutated": False,
            "statement": ("Aditivo ao addendum 1. Nem o lock, nem os casos congelados, "
                          "nem o freeze record, nem o addendum 1 foram abertos para "
                          "escrita. Este artefato acrescenta e se amarra por hash."),
        },
        "why_this_addendum_exists": (
            "O addendum 1 buscou FORMA LITERAL — `/compact`, `/context`, `accept edits` "
            "— e declarou limpos termos que estavam presentes em outra forma. Esta "
            "varredura busca por RADICAL sobre o mesmo corpo falado e publica o que "
            "mais apareceu. Ver REGRA: buscar por radical, nunca por forma exata."),
        "binds_to": {k: {"path": str(p.relative_to(DRIVE)), "sha256": sha(p)}
                     for k, p in IMUTAVEIS.items()}
                    | {"l0_cut": {"path": str(CUT.relative_to(DRIVE)), "sha256": sc},
                       "l0_intact": {"path": str(INTACT.relative_to(DRIVE)), "sha256": si}},
        "method": {
            "scan_scope": ("corpo falado do L0 cortado; linhas de título e marcas de "
                           f"tempo excluídas da busca ({len(body)} blocos)"),
            "search_kind": "RADICAL/substring, não forma literal",
            "held_out_spans_absent_from_scan_corpus": True,
            "cut_interval": "SEMIABERTO [início, fim). O bloco na marca de fim sobrevive ao corte e é o primeiro bloco depois dele.",
            "boundary_blocks_that_survived": borda,
            "quotes_verified_at_publish_time": True,
            "cost_disclosed": ("busca por radical produz falso positivo. Todos os que "
                               "apareceram estão listados em false_positives, não "
                               "descartados em silêncio."),
        },
        "newly_disclosed_residue": {"count": len(novos), "items": novos},
        "false_positives": {"count": len(falsos), "items": falsos},
        "verified_zero_occurrences": {"radicals": zero,
                                      "statement": "zero ocorrências no corpo falado do L0 cortado"},
        "effect_on_blind_cases": {
            "statement": ("Correção material do addendum 1: ele declarou BC-005 e a "
                          "seção inteira de janela de contexto como intocadas. Não "
                          "estão."),
            "BC-001": "contaminado (nomes pelo addendum 1, contagem por RES2-002)",
            "BC-002": "sem vazamento novo",
            "BC-003": "contaminado quanto a nomes; RES2-005 é candidato não confirmado",
            "BC-004": "contaminado quanto ao nome; condição e risco seguem fora",
            "BC-005": "REVISADO — era 'intocado', agora contaminado por RES2-001",
            "BC-006": "sem vazamento novo; `context rot` segue com zero ocorrências",
            "BC-007": "parcial — ler percentual vazou; o limiar de 50% não",
            "BC-008": "parcial — existência do compact vazou; o custo não",
            "BC-009": "parcial — compact vazou; `/clear` não",
            "BC-010": "parcial — ler percentual vazou; `/context` e as categorias não",
        },
        "does_not": ["não altera o lock congelado",
                     "não altera os casos cegos nem o freeze record",
                     "não altera o addendum 1",
                     "não recorta nada a mais do L0",
                     "não julga nenhuma resposta da execução cega"],
    }

    txt = ("# HELDOUT-RESIDUE-ADDENDUM 2 — PILOT-002\n"
           "# ADITIVO. Varredura por RADICAL. Nenhum artefato base foi tocado.\n"
           + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100))
    OUT.write_text(txt, encoding="utf-8")
    (MIRROR/OUT.name).write_text(txt, encoding="utf-8")
    print(f"vazamentos novos : {len(novos)}")
    print(f"falsos positivos : {len(falsos)} (declarados, não descartados)")
    print(f"radicais em zero : {len(zero)}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) {sha(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
