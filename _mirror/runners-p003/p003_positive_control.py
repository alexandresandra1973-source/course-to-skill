#!/usr/bin/env python3
"""CONTROLE POSITIVO por tema. Nenhuma alegação de ausência sai sem etiqueta.

O risco que isto ataca é de PRODUTO, não de instrumento: a saída principal — "o
curso não cobre X" — tem exatamente o mesmo formato quando o matcher está
quebrado. Quatro versões do medidor de temas produziram achados falsos com essa
cara. Quem lê o relatório não tem como separar.

REGRA: para todo tema com 0 ou 1 evidência, contar o termo NO L0 CRU.
  muitas em L0 + 0 evidências  -> LACUNA_DE_EXTRACAO      (defeito NOSSO)
  poucas em L0 + 0 evidências  -> COBERTURA_RASA_DO_CURSO (achado de produto)
  ausente em L0                -> ARTEFATO_DE_ROTULACAO   (não é achado)

ARMADILHA DE IDIOMA, e ela quase inverteu tudo: os temas vêm do PASS 1, que
escreveu em português; o L0 é inglês. Buscar 'rotina semanal' em texto inglês dá
zero SEMPRE, e marcaria tudo como artefato de rotulação. Por isso a busca é POR
TOKEN, e cada token é classificado antes: token técnico/invariante (kpi, cpc,
instream, shorts, roas, pmax) é buscável; token português não é, e a busca fica
declarada INVÁLIDA em vez de devolver zero.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

W = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-work")
TH = json.loads(Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-themes.json")
                .read_text(encoding="utf-8"))
OUT = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/p003-control.json")
MUITAS, POUCAS = 20, 1          # limiares pré-declarados, antes de ver contagem

# Token é buscável em L0 se for sigla/termo técnico que não se traduz. A lista é
# derivada mecanicamente: token que JÁ APARECE no L0 inglês é, por construção,
# buscável. Não há escolha minha sobre o que "deveria" estar lá.
PT_ONLY = re.compile(r"[àáâãéêíóôõúç]|ção$|ções$|mente$|ário$|ária$")


def main() -> int:
    l0 = (W/"00_SOURCE/L0-transcript.txt").read_text(encoding="utf-8").lower()
    l0 = " " + " ".join(re.sub(r"\*\*\d{1,3}:[0-5]\d\*\*", " ", l0).split()) + " "
    alvo = [t for t in TH["themes"] if t["evidence_mentions"] <= 1]
    extra = ["negative keyword", "negative keywords"]
    rows = []
    for t in alvo:
        toks = [w for w in t["theme"].split() if len(w) > 2]
        det = []
        for w in toks:
            pt = bool(PT_ONLY.search(w))
            n = len(re.findall(rf"\b{re.escape(w)}\b", l0))
            det.append({"token": w, "portugues": pt, "ocorrencias_L0": n,
                        "busca_valida": (not pt) or n > 0})
        # CORRECAO do proprio rotulo: a versao anterior chamava de
        # ARTEFATO_DE_ROTULACAO todo tema cujos tokens davam zero em L0. Mas
        # token portugues SEM acento ("rotina", "semanal", "caso") tambem da
        # zero em texto ingles, e isso nao prova ausencia — prova que a busca
        # nao se aplica. Confundir as duas devolve "o curso nao cobre X" quando
        # o correto e "nao sei dizer".
        #
        # Regra: so decide quem tem ao menos UM token PRESENTE no L0. Esse token
        # prova que o termo pertence ao vocabulario da fonte. Sem nenhum, a
        # busca e declarada invalida.
        presentes = [d for d in det if d["ocorrencias_L0"] > 0]
        if not presentes:
            tag, why = "BUSCA_INVALIDA_POR_IDIOMA", (
                "nenhum token do tema aparece no L0. Os temas vem do PASS 1 em "
                "portugues e o L0 e ingles: zero aqui nao distingue ausencia de "
                "traducao. NAO e alegacao sobre o curso.")
            n_l0 = None
        else:
            n_l0 = min(d["ocorrencias_L0"] for d in presentes)
            if n_l0 > MUITAS:
                tag, why = "LACUNA_DE_EXTRACAO", ("o curso fala disso muitas vezes e a "
                           "extracao nao produziu evidencia — defeito NOSSO")
            else:
                tag, why = "COBERTURA_RASA_DO_CURSO", ("o curso menciona poucas vezes e a "
                           "extracao acompanhou — achado legitimo sobre o curso")
        rows.append({"theme": t["theme"], "evidence_mentions": t["evidence_mentions"],
                     "named_in_topics": t["named_in_topics"], "l0_min_token_hits": n_l0,
                     "tag": tag, "why": why, "tokens": det})
    for term in extra:
        n = len(re.findall(rf"\b{re.escape(term)}\b", l0))
        rows.append({"theme": term, "evidence_mentions": None, "named_in_topics": None,
                     "l0_min_token_hits": n,
                     "tag": ("COBERTURA_RASA_DO_CURSO" if 0 < n <= MUITAS
                             else "ARTEFATO_DE_ROTULACAO" if n == 0 else "BEM_COBERTO"),
                     "why": "termo em inglês, busca direta válida", "tokens": []})
    OUT.write_text(json.dumps({"thresholds": {"MUITAS": MUITAS, "POUCAS": POUCAS},
                               "rows": rows}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"limiares PRÉ-DECLARADOS: muitas > {MUITAS} · poucas <= {MUITAS}\n")
    print(f"  {'tema':<26} {'ev':>3} {'L0':>5}  etiqueta")
    for r in sorted(rows, key=lambda x: (x["tag"], -(x["l0_min_token_hits"] or 0))):
        n = "—" if r["l0_min_token_hits"] is None else r["l0_min_token_hits"]
        e = "—" if r["evidence_mentions"] is None else r["evidence_mentions"]
        print(f"  {r['theme']:<26} {e:>3} {n:>5}  {r['tag']}")
    from collections import Counter
    print("\n", dict(Counter(r["tag"] for r in rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
