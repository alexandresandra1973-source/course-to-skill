#!/usr/bin/env python3
"""FRENTE 3 — ensaio seco da maquinaria do TEST-0008, com notas sintéticas.

Roda daqui (ext4). Trabalha em /tmp. READ-ONLY sobre Course-to-Skill/.
Nada congelado, nada em pasta definitiva, nenhuma Skill compilada.

O 0008 tem TRÊS condições, DUAS comparações e uma regra de interpretação. Nada
disso nunca rodou, nem com nota sintética. Este ensaio exercita a aritmética e,
principalmente, inventaria o que a maquinaria exige e ainda NÃO existe.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path

import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "DRY-RUN-TEST-0008.md"
TMP = Path("/tmp/dryrun-0008")
CS = DRIVE / "Course-to-Skill"

CRITERIA = [("EXECUTION_QUALITY", Decimal("0.4")),
            ("CONSISTENCY", Decimal("0.2")),
            ("HUMAN_CHECKPOINT_COMPLIANCE", Decimal("0.2")),
            ("METHODOLOGY_FIDELITY", Decimal("0.2"))]

# Notas SINTÉTICAS por condição e regime. Inteiras, como o contrato do juiz usa.
REGIMES = [
    ("R1", "framing pequeno em relação a P",
     {"FULL_SKILL": [95, 90, 95, 90], "SUMMARY_AS_SUMMARY": [55, 60, 50, 45],
      "SUMMARY_AS_SKILL": [57, 62, 50, 47]}),
    ("R2", "framing fração material de P",
     {"FULL_SKILL": [95, 90, 95, 90], "SUMMARY_AS_SUMMARY": [55, 60, 50, 45],
      "SUMMARY_AS_SKILL": [70, 72, 62, 60]}),
    ("R3", "framing da ordem de P",
     {"FULL_SKILL": [95, 90, 95, 90], "SUMMARY_AS_SUMMARY": [55, 60, 50, 45],
      "SUMMARY_AS_SKILL": [92, 88, 92, 88]}),
    ("R4", "framing em direção OPOSTA a P",
     {"FULL_SKILL": [95, 90, 95, 90], "SUMMARY_AS_SUMMARY": [55, 60, 50, 45],
      "SUMMARY_AS_SKILL": [48, 52, 45, 40]}),
]

# O que a maquinaria do 0008 exige. `probe` diz como procurar no disco.
# O que a maquinaria do 0008 exige. A sonda casa por IDENTIDADE — nome de
# arquivo ou `artifact_id` — e não por menção no texto. Um documento que fala
# do artefato não é o artefato; foi assim que a primeira versão desta sonda deu
# 7 falsos positivos.
REQUIRED = [
    ("rubrica do TEST-0008 CONGELADA",
     r"TEST-0008.*RUBRIC(?!-DRAFT)", "FROZEN",
     "sem régua congelada não há critério, peso nem piso"),
    ("addendum de âncora do TEST-0008",
     r"TEST-0008.*RUBRIC.*ANCHOR.*ADDENDUM", None,
     "as âncoras por perfil de comportamento, como o 0007 tem"),
    ("lista canônica de comparison_metrics congelada",
     r"COMPARISON-METRICS|comparison_metrics.*(LOCK|FROZEN)", "FROZEN",
     "bloqueador 1 do ADR: a discrepância 5×6 tem de ser resolvida antes"),
    ("variância do avaliador do TEST-0008",
     r"TEST-0008.*(RETEST|VARIANCE)", None,
     "sem ela não há largura de incerteza própria; o ADR proíbe herdar o w do 0007"),
    ("bandas de interpretação F/P, numéricas e congeladas",
     r"TEST-0008.*(FRAMING|BAND|INTERPRETATION).*(LOCK|BAND)", None,
     "os três regimes precisam de pontos de corte numéricos, da variância"),
    ("teto estrutural do TEST-0008",
     r"TEST-0008.*STRUCTURAL-CEILING", None,
     "o que a régua do 0008 consegue separar, antes da rodada"),
    ("regra de decisão do TEST-0008",
     r"TEST-0008.*DECISION-RULE", None,
     "limiar, zona inconclusiva e piso de discriminabilidade próprios"),
    ("pacotes congelados das três condições",
     r"TEST-0008.*(CONDITIONS?|ARMS?).*(FROZEN|FREEZE)", None,
     "hashes dos três pacotes, como os três braços do 0007"),
    ("addendum de saída do juiz para o 0008",
     r"TEST-0008.*JUDGE-OUTPUT-ADDENDUM", None,
     "campos obrigatórios: selected_anchor, anchor_ambiguity"),
    ("instruções de rodada cega do 0008",
     r"TEST-0008.*JUDGE-BLIND-RUN", None,
     "o que anexar e em que ordem"),
    ("margin lock, registry e opening record do 0008",
     r"TEST-0008.*(MARGIN-LOCK|PRE-RUN-LOCK|OPENING-RECORD)", None,
     "a cadeia pré-run, que no 0007 já fecha"),
    ("contrato de pontuação cobrindo o 0008", "CODE",
     "comparative_tests com chave TEST-0008",
     "hoje `comparative_tests` é chaveado por teste, e o 0008 não está lá"),
    ("suporte a DUAS comparações no mesmo teste", "SHAPE", None,
     "o 0008 precisa de P e F; o modelo de dados expressa um par só"),
    ("suporte a TRÊS condições", "SHAPE", None,
     "o modelo atual é par esquerda/direita mais preservação antes/depois"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def total(scores: list[int]) -> F:
    return sum(F(w) * F(s) for (_, w), s in zip(CRITERIA, scores))


def dec(f: F, places: int = 6) -> str:
    neg, f = f < 0, abs(f)
    ip = f.numerator // f.denominator
    rem, out = f - ip, str(ip)
    if rem:
        ds = []
        for _ in range(places):
            rem *= 10
            d = rem.numerator // rem.denominator
            ds.append(str(d))
            rem -= d
            if rem == 0:
                break
        out += "." + "".join(ds)
    return ("-" if neg else "") + out


def scan_disk() -> dict:
    """Índice do que existe, para o inventário do que falta."""
    idx = []
    for root in (CS, DRIVE / "Course-to-Skill-Compiler",
                 DRIVE / "Course-to-Skill-Claude"):
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rec = {"path": str(p.relative_to(DRIVE)), "name": p.name, "text": ""}
            if p.suffix.lower() in (".yaml", ".yml", ".md", ".txt", ".json", ".py"):
                try:
                    rec["text"] = p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass
            idx.append(rec)
            if p.suffix.lower() == ".zip":
                try:
                    with zipfile.ZipFile(p) as z:
                        for n in z.namelist():
                            if n.endswith("/"):
                                continue
                            t = ""
                            if n.lower().endswith((".yaml", ".yml", ".md", ".txt",
                                                   ".json", ".py")):
                                t = z.read(n).decode("utf-8", "replace")
                            idx.append({"path": f"{p.relative_to(DRIVE)} :: {n}",
                                        "name": n.split("/")[-1], "text": t})
                except zipfile.BadZipFile:
                    pass
    return idx


ARTIFACT_ID_RE = re.compile(r"^artifact_id:\s*(\S+)", re.M)


def find_identity(idx, pattern: str, status: str | None) -> list[str]:
    """Casa por IDENTIDADE: nome do arquivo ou `artifact_id` declarado.

    Menção no corpo do texto NÃO conta. Um relatório que discute a régua do
    0008 não é a régua do 0008.
    """
    rx = re.compile(pattern, re.I)
    hits = []
    for rec in idx:
        ids = ARTIFACT_ID_RE.findall(rec["text"]) if rec["text"] else []
        identity = [rec["name"]] + ids
        if not any(rx.search(x) for x in identity):
            continue
        if status and status not in rec["text"]:
            continue
        hits.append(rec["path"])
    return hits[:3]


def scorer_knows_0008(idx) -> list[str]:
    """TEST-0008 é CHAVE de `comparative_tests` em algum contrato?

    Citar os dois termos no mesmo arquivo não basta — um plano de revisão que
    fala dos dois não é um contrato que cobre o 0008. Parseia o YAML e olha a
    chave.
    """
    hits = []
    for rec in idx:
        if not rec["name"].endswith((".yaml", ".yml")):
            continue
        if "comparative_tests" not in rec["text"]:
            continue
        try:
            d = yaml.safe_load(rec["text"])
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("comparative_tests"), dict) \
                and "TEST-0008" in d["comparative_tests"]:
            hits.append(rec["path"])
    # e o scorer: cita TEST-0008 em qualquer ramo de código?
    for rec in idx:
        if rec["name"].endswith(".py") and "TEST-0008" in rec["text"]:
            hits.append(rec["path"] + " (código)")
    return hits[:3]


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / "SYNTHETIC_DRY_RUN.md").write_text(
        "# SYNTHETIC_DRY_RUN — TEST-0008\n\nNotas fabricadas. Nenhuma condição "
        "foi executada, nenhuma Skill compilada, nada congelado.\n",
        encoding="utf-8")

    rows = []
    for rid, label, cond in REGIMES:
        t = {k: total(v) for k, v in cond.items()}
        P = t["FULL_SKILL"] - t["SUMMARY_AS_SUMMARY"]
        Fr = t["SUMMARY_AS_SKILL"] - t["SUMMARY_AS_SUMMARY"]
        ratio = (Fr / P) if P != 0 else None
        aratio = (abs(Fr) / abs(P)) if P != 0 else None
        rows.append({"id": rid, "label": label, "scores": cond,
                     "totals": {k: dec(v) for k, v in t.items()},
                     "P": P, "F": Fr, "absP": abs(P), "absF": abs(Fr),
                     "F_over_P": ratio, "absF_over_absP": aratio,
                     "same_direction": (Fr == 0) or ((Fr > 0) == (P > 0))})

    (TMP / "synthetic-scores.json").write_text(
        json.dumps({"marker": "SYNTHETIC_DRY_RUN",
                    "regimes": [{k: (dec(v) if isinstance(v, F) else v)
                                 for k, v in r.items()} for r in rows]},
                   indent=1, ensure_ascii=False, default=str), encoding="utf-8")

    idx = scan_disk()

    # Entrada legada do 0008 em contrato antigo: nem ausência, nem suficiência.
    legacy = []
    for rec in idx:
        if not rec["name"].endswith((".yaml", ".yml")):
            continue
        if "comparative_tests" not in rec["text"]:
            continue
        try:
            d = yaml.safe_load(rec["text"])
        except Exception:
            continue
        ct = (d or {}).get("comparative_tests")
        if isinstance(ct, dict) and "TEST-0008" in ct:
            legacy.append({"path": rec["path"], "entry": ct["TEST-0008"]})
    missing, present = [], []
    for name, pat, status, why in REQUIRED:
        if pat == "SHAPE":
            missing.append({"item": name, "why": why,
                            "evidence": "inspeção do modelo de dados do contrato "
                                        "e do freezer"})
            continue
        if pat == "CODE":
            hits = scorer_knows_0008(idx)
        else:
            hits = find_identity(idx, pat, status)
        (present if hits else missing).append(
            {"item": name, "why": why,
             "evidence": hits or "nenhum artefato com essa identidade"})

    L, w = [], None
    w = L.append
    w("# Ensaio seco da maquinaria do TEST-0008")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w(f"- Notas **sintéticas**, marcadas `SYNTHETIC_DRY_RUN`, em `{TMP}`.")
    w("- Nenhuma condição executada, nenhuma Skill compilada, nada congelado, "
      "nada em pasta definitiva.")
    w("- Aritmética exata (`Fraction`), como na prova de alcançabilidade.")
    w("")
    w("## 1. As duas comparações, sobre notas sintéticas")
    w("")
    w("`P = FULL_SKILL − SUMMARY_AS_SUMMARY` (primária) · "
      "`F = SUMMARY_AS_SKILL − SUMMARY_AS_SUMMARY` (enquadramento)")
    w("")
    w("| regime | FULL | SaSummary | SaSkill | P | F | \\|F\\| | F/P | \\|F\\|/\\|P\\| | mesma direção |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        w(f"| **{r['id']}** — {r['label']} | {r['totals']['FULL_SKILL']} | "
          f"{r['totals']['SUMMARY_AS_SUMMARY']} | {r['totals']['SUMMARY_AS_SKILL']} | "
          f"**{dec(r['P'])}** | **{dec(r['F'])}** | {dec(r['absF'])} | "
          f"{dec(r['F_over_P'], 4)} | {dec(r['absF_over_absP'], 4)} | "
          f"{'sim' if r['same_direction'] else '**não**'} |")
    w("")
    w("As cinco quantidades que o ADR manda publicar — `F`, `P`, `|F|`, `|P|`, "
      "`F/P` e `|F|/|P|` — são todas computáveis com o que existe. **A aritmética "
      "não é o gargalo.**")
    w("")
    w("## 2. As três leituras pré-declaradas")
    w("")
    w("| regime | leitura que o ADR manda aplicar |")
    w("|---|---|")
    w(f"| **R1** F/P = {dec(rows[0]['F_over_P'], 4)} | enquadramento não explica "
      "o resultado primário; P pode sustentar a alegação de valor estrutural |")
    w(f"| **R2** F/P = {dec(rows[1]['F_over_P'], 4)} | publicar a parcela de "
      "enquadramento e qualificar proporcionalmente a alegação |")
    w(f"| **R3** F/P = {dec(rows[2]['F_over_P'], 4)} | resultado primário só é "
      "interpretável como efeito de enquadramento; **não sustenta a premissa** |")
    w(f"| **R4** F/P = {dec(rows[3]['F_over_P'], 4)} | direção oposta: publicar a "
      "direção; não explica vantagem da Skill, mas entra na sensibilidade |")
    w("")
    w("> **O que este ensaio NÃO consegue fazer.** Ele mostra em que regime cada "
      "conjunto de notas cai *se* os pontos de corte já existissem. Eles não "
      "existem. \"Pequeno\", \"fração material\" e \"da ordem de\" são rótulos "
      "qualitativos até alguém congelar números — e o ADR exige que esses "
      "números venham da variância medida sob a régua final do 0008, proibindo "
      "herdar o `w` do 0007. Atribuí os regimes acima por construção das notas, "
      "não por regra vigente.")
    w("")
    w("## 3. O que a maquinaria exige e NÃO existe")
    w("")
    w(f"**{len(missing)} de {len(REQUIRED)} itens ausentes.**")
    w("")
    w("| item | por que é exigido |")
    w("|---|---|")
    for m in missing:
        w(f"| **{m['item']}** | {m['why']} |")
    w("")
    if present:
        w("Existem:")
        w("")
        for p in present:
            ev = p["evidence"]
            w(f"- {p['item']} — `{ev[0] if isinstance(ev, list) else ev}`")
        w("")
    if legacy:
        w("### A entrada legada do 0008, que existe e não serve")
        w("")
        w(f"Encontrei **{len(legacy)}** contrato(s) antigo(s) com `TEST-0008` "
          "declarado em `comparative_tests`:")
        w("")
        for lg in legacy[:3]:
            w(f"- `{lg['path']}`")
            for k, v in (lg["entry"] or {}).items():
                w(f"  - `{k}`: `{v}`")
        w("")
        w("Isso é pior que ausência, e por isso vale destaque. A entrada declara "
          "**uma** comparação, `SKILL_MINUS_SUMMARY`, e um limiar adiado. Ela "
          "codifica o desenho de **duas** condições — Skill contra resumo — que o "
          "ADR de paridade de informação substituiu por **três** condições e "
          "**duas** comparações. `SKILL_MINUS_SUMMARY` não desambigua entre `P` "
          "(FULL − SUMMARY_AS_SUMMARY) e `F` (SUMMARY_AS_SKILL − "
          "SUMMARY_AS_SUMMARY): sob o desenho novo, os dois cabem no nome.")
        w("")
        w("Quem rodar a cadeia com esse contrato sem reler o ADR vai medir uma "
          "comparação só e não vai saber qual das duas mediu.")
        w("")
    w("### Os dois que não são falta de arquivo, e sim de forma")
    w("")
    w("1. **Uma comparação por teste.** No contrato, `comparative_tests` é um "
      "mapa `test_id → política`, com um único par `left`/`right`. O 0008 precisa "
      "de **duas** comparações sobre o mesmo teste, `P` e `F`. Não é preencher "
      "campo: é estender o modelo de dados.")
    w("2. **Duas condições por comparação, três no teste.** O modelo atual é par "
      "esquerda/direita mais preservação antes/depois — desenhado para ablação. "
      "As três condições do 0008 não cabem nesse formato sem mudança.")
    w("")
    w("E `TEST-0008` não aparece em nenhum dos scripts da cadeia: nem no freezer, "
      "nem no registry, nem no scorer.")
    w("")
    w("## 4. Quanto falta, honestamente")
    w("")
    w("A cadeia do 0007 fecha hoje. A do 0008 não está a um patch de distância: "
      "faltam artefatos de conteúdo (régua congelada, âncoras, variância, bandas, "
      "teto, regra de decisão, pacotes das três condições) **e** mudança de forma "
      "no contrato e nos scripts para caber duas comparações e três condições.")
    w("")
    w("A ordem importa e está no ADR: a lista canônica de `comparison_metrics` "
      "precisa ser resolvida primeiro — é o bloqueador 1 — porque régua, âncoras "
      "e derivação de métrica dependem dela. Depois vem a variância, e só então "
      "as bandas numéricas.")
    w("")
    w("Nada aqui foi congelado. Nenhuma conversa cega foi aberta.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    for r in rows:
        print(f"  {r['id']} P={dec(r['P'])} F={dec(r['F'])} "
              f"F/P={dec(r['F_over_P'], 4)} mesma_direcao={r['same_direction']}")
    print(f"ausentes: {len(missing)}/{len(REQUIRED)}")
    for m in missing:
        print(f"  - {m['item']}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
