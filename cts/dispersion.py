"""Degeneração por dispersão (ADR-0005).

Para um campo categórico F de domínio de tamanho k observado em N registros:

    H(F)      = - sum( p_v * log2 p_v )
    H_norm(F) = H(F) / log2(k)

COLLAPSED       distinct == 1 e N >= N_MIN   -> FAIL
NEAR_COLLAPSED  H_norm < theta e N >= N_MIN  -> WARN
UNDERPOWERED    N < N_MIN                    -> não avalia, reduz o teto
OK              caso contrário

O limiar de COLLAPSED não é calibrado: um campo de valor único carrega
exatamente 0 bits e, por R2, não pode mudar o comportamento de consumidor
nenhum. Decorre da definição.

THETA é EM ABERTO (ADR-0005): precisa de >=2 corpora de qualidade conhecida.
O valor abaixo é declarado como PROVISÓRIO e todo relatório o marca como tal —
não é resultado de calibração e não deve ser lido como se fosse.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

N_MIN = 20
THETA_PROVISORIO = 0.50   # EM ABERTO — ver ADR-0005


@dataclass
class FieldDispersion:
    field: str
    n: int
    k: int
    distinct: int
    entropy_bits: float
    h_norm: float
    state: str
    counts: dict


def measure(field: str, values: list, domain_size: int,
            theta: float = THETA_PROVISORIO, n_min: int = N_MIN) -> FieldDispersion:
    values = [v for v in values if v is not None]
    n = len(values)
    counts = Counter(values)
    if n == 0:
        return FieldDispersion(field, 0, domain_size, 0, 0.0, 0.0, "DATA_DEFECT", {})
    H = -sum((c / n) * math.log2(c / n) for c in counts.values())
    H = 0.0 if H == 0 else H          # evita -0.0 na apresentacao
    hn = H / math.log2(domain_size) if domain_size > 1 else 0.0
    if n < n_min:
        # ADR-0014: distinct==1 com base pequena e suspeito, mas inconcluso.
        state = "SUSPECT_UNDERPOWERED" if len(counts) == 1 else "UNDERPOWERED"
    elif len(counts) == 1:
        state = "COLLAPSED"
    elif hn < theta:
        state = "NEAR_COLLAPSED"
    else:
        state = "OK"
    return FieldDispersion(field, n, domain_size, len(counts),
                           round(H, 4), round(hn, 4), state, dict(counts))
