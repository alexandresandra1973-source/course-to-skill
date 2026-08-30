#!/usr/bin/env python3
"""ROUND 2 — controles PRE-DECLARADOS do juiz e do isolamento.

Escolhidos ANTES de qualquer geracao da Round 2, a partir da evidencia real dos
dois pacotes, com exclusividade verificada mecanicamente.

CORRECAO 2 (isolamento): estatistica de vocabulario esta PROIBIDA como prova de
exclusividade. O teste agora e de PROVENIENCIA/ASSERCAO:
    proposicao de A + evidencia de A  -> ENTAILED
    proposicao de A + evidencia de B  -> NAO ENTAILED
e o espelho. Isso testa FALSA ATRIBUICAO, nao ocorrencia lexical.
"""
from __future__ import annotations

# evidencias de ancoragem, por local_id no pacote respectivo
ISO_A = {"control_id": "ISO-A", "package": "A", "chapter": 12,
         "proposition": "When inspecting a change, the green section shows what is being added and the red section shows what is on the left.",
         "positive_evidence_ids": ["EV-0011"],
         "porque_exclusiva": "'green', 'red section' e 'being added' ocorrem nas quotes de A e NAO nas de B (verificado mecanicamente)"}
ISO_B = {"control_id": "ISO-B", "package": "B", "chapter": 13,
         "proposition": "MCP stands for Model Context Protocol and can be thought of as a USB port for artificial intelligence.",
         "positive_evidence_ids": ["EV-0006", "EV-0008"],
         "porque_exclusiva": "'mcp', 'model context protocol' e 'usb port' ocorrem nas quotes de B e NAO nas de A (verificado mecanicamente)"}

# --- controles do JUIZ: os tres estados + as duas travessias cross-source
def judge_controls(pkgs):
    def q(k, ids): return [i["quote"] for i in pkgs[k]["items"] if i["local_id"] in ids]
    # amostra de evidencia do pacote OPOSTO, para o teste cross-source
    other_A = [i["quote"] for i in pkgs["B"]["items"][:6]]
    other_B = [i["quote"] for i in pkgs["A"]["items"][:6]]
    return [
      {"control_id": "JC-POSITIVE", "expected": "ENTAILED",
       "claim": ISO_A["proposition"], "evidence": q("A", ISO_A["positive_evidence_ids"]),
       "porque": "a proposicao segue integralmente da evidencia de A"},
      {"control_id": "JC-NEGATIVE", "expected": "NOT_ENTAILED",
       "claim": "The green section shows what is being added, and this is why GitHub charges a fee for private repositories.",
       "evidence": q("A", ISO_A["positive_evidence_ids"]),
       "porque": "acrescenta causalidade e um fato de cobranca que a evidencia NAO sustenta"},
      {"control_id": "JC-INDETERMINATE", "expected": "INDETERMINATE",
       "claim": "Most developers prefer reviewing changes in the rich diff view rather than the plain view.",
       "evidence": q("A", ["EV-0012"]),
       "porque": "a evidencia menciona a rich difference mas NAO diz o que a maioria prefere; insuficiente para concluir e insuficiente para negar"},
      {"control_id": "JC-CROSS-A-IN-B", "expected": "NOT_ENTAILED",
       "claim": ISO_A["proposition"], "evidence": other_A,
       "porque": "proposicao exclusiva de A julgada contra evidencia de B: aprovar seria falsa atribuicao cross-source"},
      {"control_id": "JC-CROSS-B-IN-A", "expected": "NOT_ENTAILED",
       "claim": ISO_B["proposition"], "evidence": other_B,
       "porque": "proposicao exclusiva de B julgada contra evidencia de A: aprovar seria falsa atribuicao cross-source"},
    ]

# --- controles positivos do BLOCKER, com o tokenizador corrigido
BLOCK_CONTROLS = [
  {"control_id": "BLK-CTRL-01",
   "a_text": "The repository must be initialized before pushing commits to github.",
   "b_text": "Authenticate the github repository before deploying through the cli."},
  {"control_id": "BLK-CTRL-02",
   "a_text": "Commit changes locally before syncing the remote repository.",
   "b_text": "The remote repository connection is configured before the deploy step."},
]
