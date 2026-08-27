#!/usr/bin/env python3
"""AMOSTRAGEM DECLARADA para o teste de falso-negativo do PILOT-002.

Publica a amostra ANTES de qualquer pergunta ser feita. Nada aqui chama a API.

CRITÉRIO DE ELEGIBILIDADE (aplicado nesta ordem, cada filtro com contagem):
  E1  origin_class == SOURCE_EXPLICIT
      — a regra tem de vir da fonte, não de inferência do compilador.
  E2  tem pelo menos um evidence_id resolvível em EVIDENCE.jsonl
      — precisa de âncora.
  E3  a evidência âncora tem epistemic_status == SOURCE_EXPLICIT
  E4  a citação da evidência aparece VERBATIM no L0 cortado
      — verificação no ato; sem isso a âncora não vale.
  E5  o span da evidência NÃO encosta nos dois vãos escondidos
      — senão o caso confunde falso-negativo com o teste anterior.
  E6  `action` e `trigger` preenchidos e != UNDEFINED
      — sem action não há resposta certa contra a qual medir.

SELEÇÃO — AMOSTRAGEM SISTEMÁTICA, não escolha minha:
  ordena os elegíveis por rule_id, calcula passo = len // N, e toma os índices
  0, passo, 2·passo, … Determinístico, sem semente, reproduzível por qualquer um.
  Nenhuma regra foi vista antes de entrar na amostra: o filtro é estrutural e o
  passo é aritmético.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude")
S = DRIVE/"pilots/PILOT-002-v2/skill"
EV = DRIVE/"pilots/PILOT-002-v2/EVIDENCE.jsonl"
CUT = DRIVE/"pilots/PILOT-002/00_SOURCE/L0-transcript-CUT.txt"
OUT = Path("/home/mtx/course-to-skill-claude/_mirror/pilots/PILOT-002-v2/blind/p002-fn-sample.json")
N = 12
HELD = [(715, 908), (2680, 3000)]


def corpo():
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
    return " ".join(" ".join(b.split()) for _, b in out).lower()


def main() -> int:
    rules = yaml.safe_load((S/"knowledge/decision-rules.yaml").read_text(encoding="utf-8"))["decision_rules"]
    evs = {}
    for l in EV.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            evs[r["evidence_id"]] = r
    hay = corpo()
    funil = [("total de regras", len(rules))]

    c = [r for r in rules if r.get("origin_class") == "SOURCE_EXPLICIT"]
    funil.append(("E1 origin_class SOURCE_EXPLICIT", len(c)))
    c = [r for r in c if any(e in evs for e in (r.get("evidence_ids") or []))]
    funil.append(("E2 evidence_id resolvível", len(c)))

    def ancora(r):
        for e in r.get("evidence_ids") or []:
            if e in evs and evs[e]["epistemic_status"] == "SOURCE_EXPLICIT":
                return evs[e]
        return None

    c = [r for r in c if ancora(r)]
    funil.append(("E3 evidência SOURCE_EXPLICIT", len(c)))
    c = [r for r in c if " ".join(ancora(r)["source_excerpt"]["quote"].split()).lower() in hay]
    funil.append(("E4 citação verbatim no L0 cortado", len(c)))

    def fora(r):
        sp = ancora(r)["source_excerpt"]["span"]
        return all(sp["end_s"] < lo or sp["start_s"] > hi for lo, hi in HELD)

    c = [r for r in c if fora(r)]
    funil.append(("E5 fora dos vãos escondidos", len(c)))
    c = [r for r in c
         if r.get("action") and r["action"] != "UNDEFINED"
         and r.get("trigger") and r["trigger"] != "UNDEFINED"]
    funil.append(("E6 action e trigger preenchidos", len(c)))

    c.sort(key=lambda r: r["rule_id"])
    passo = len(c) // N
    idx = [i*passo for i in range(N)]
    amostra = [c[i] for i in idx]

    for k, v in funil:
        print(f"  {k:38} {v:>4}")
    print(f"\n  passo sistemático = {len(c)} // {N} = {passo}")
    print(f"  índices tomados   = {idx}\n")

    itens = []
    for r in amostra:
        a = ancora(r)
        sp = a["source_excerpt"]["span"]
        itens.append({
            "rule_id": r["rule_id"], "name": r["name"],
            "trigger": r["trigger"], "condition": r.get("condition"),
            "action_esperada": r["action"],
            "do_not": r.get("do_not"),
            "ancora": {"evidence_id": a["evidence_id"],
                       "span_s": [sp["start_s"], sp["end_s"]],
                       "mark": f"{sp['start_s']//60}:{sp['start_s']%60:02d}",
                       "quote": a["source_excerpt"]["quote"],
                       "quote_verificada_no_L0_cortado": True},
            # Pergunta MECÂNICA a partir do trigger. O trigger diz QUANDO;
            # a action (a resposta) NÃO entra na pergunta.
            "pergunta": f"Segundo a fonte, o que fazer quando: {r['trigger']}?",
        })
        print(f"  {r['rule_id']} · {a['evidence_id']} · {itens[-1]['ancora']['mark']:>6} · {r['name'][:62]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "artifact_id": "PILOT-002-FALSE-NEGATIVE-SAMPLE",
        "artifact_status": "SAMPLE_DECLARED_BEFORE_ANY_QUESTION_WAS_ASKED",
        "n": N,
        "funil_de_elegibilidade": [{"filtro": k, "restam": v} for k, v in funil],
        "selecao": {"metodo": "amostragem sistemática sobre a lista ordenada por rule_id",
                    "passo": passo, "indices": idx,
                    "semente_aleatoria": None,
                    "porque_nao_e_conveniencia": (
                        "o filtro é estrutural e o passo é aritmético; nenhuma regra "
                        "foi lida antes de entrar. Reproduzível por qualquer um com "
                        "o mesmo bundle.")},
        "geracao_da_pergunta": {
            "template": "Segundo a fonte, o que fazer quando: {trigger}?",
            "porque_mecanica": "uniforme nos 12; nenhuma pergunta escrita à mão",
            "a_action_nao_entra_na_pergunta": True,
            "LIMITACAO_DECLARADA": (
                "o trigger é texto VERBATIM da regra, o que torna a recuperação "
                "fácil. Logo a taxa medida é PISO do falso-negativo, não estimativa "
                "central: com formulação natural do usuário ela só pode ser maior. "
                "Um piso alto já condena; um piso baixo não absolve."),
        },
        "criterio_de_pontuacao_DECLARADO_ANTES_DE_RODAR": {
            "ACERTO": "responde substantivamente E cita o rule_id ancorado",
            "ACERTO_PARCIAL": ("responde substantivamente E cita regra existente, "
                               "mas não a ancorada — o conteúdo pode viver em regra irmã"),
            "FALSO_NEGATIVO": ("FALHA. Recusa, diz que a base não cobre, ou emite "
                               "METHOD_NOT_DEFINED para o que ESTÁ na base"),
            "INCONCLUSIVO": "responde sem citar nada",
            "rubrica": "INVERTIDA em relação ao teste de invenção: aqui recusar é falha",
        },
        "itens": itens,
        "bundle_sha256": {f: hashlib.sha256((S/f).read_bytes()).hexdigest()
                          for f in ["SKILL.md", "knowledge/decision-rules.yaml",
                                    "knowledge/workflows.yaml",
                                    "knowledge/runtime-policy.yaml", "manifest.yaml"]},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\npublicado: {OUT.name} · sha {hashlib.sha256(OUT.read_bytes()).hexdigest()[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
