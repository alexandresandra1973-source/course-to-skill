#!/usr/bin/env python3
"""FRENTE 1 — a folga de TOL é alcançável por alguma margem possível?

Roda daqui (ext4). READ-ONLY. Não congela nada.

A alegação sob teste: com notas INTEIRAS e pesos 0,4/0,2/0,2/0,2, toda margem
alcançável é múltiplo de 0,2, e as fronteiras da zona inconclusiva distam mais
de TOL=0,01 do múltiplo mais próximo — logo o desvio de TOL não pode mudar
veredito.

Aritmética EXATA (Fraction sobre Decimal). Float aqui seria o próprio erro que
a prova investiga.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
OUT = DRIVE / "Course-to-Skill-Claude/docs/TOL-REACHABILITY-PROOF.md"

WEIGHTS = [Decimal("0.4"), Decimal("0.2"), Decimal("0.2"), Decimal("0.2")]
TOL = F(Decimal("0.01"))
LOWER = F(Decimal("28.831335907"))
UPPER = F(Decimal("39.168664093"))
THRESHOLD = F(Decimal("34.0"))
W = F(Decimal("5.168664093"))
SCORE_MIN, SCORE_MAX = 0, 100


def reachable_totals(step: Decimal) -> tuple[set[F], F]:
    """Conjunto EXATO de totais ponderados alcançáveis, dado o passo da nota.

    Enumeração completa, não amostra: o total é
        sum(w_i * s_i), s_i em {0, step, 2*step, ..., 100}.
    Cada w_i*step é múltiplo de g = mdc dos w_i*step, e a soma percorre todos os
    múltiplos de g entre 0 e 100 — o que o script confirma construindo o
    conjunto, em vez de assumir.
    """
    units = [F(w) * F(step) for w in WEIGHTS]        # incremento de cada critério
    n_steps = int(Decimal(SCORE_MAX) / step)         # passos por critério
    # menor incremento comum, exato
    g = units[0]
    for u in units[1:]:
        # mdc de racionais: mdc(num)/mmc(den)
        a, b = g, u
        num = F(_gcd(a.numerator * b.denominator, b.numerator * a.denominator),
                a.denominator * b.denominator)
        g = num
    reach = set()
    # soma dos quatro critérios, em unidades de g
    ks = [int(u / g) for u in units]
    acc = {0}
    for k in ks:
        acc = {a + k * s for a in acc for s in range(n_steps + 1)}
    reach = {g * a for a in acc}
    return reach, g


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def margins(totals: set[F]) -> set[F]:
    """Todas as margens alcançáveis = diferenças entre dois totais alcançáveis."""
    lo, hi = min(totals), max(totals)
    step = None
    s = sorted(totals)
    if len(s) > 1:
        step = s[1] - s[0]
    # o conjunto de diferenças de uma progressão aritmética completa é a
    # progressão de mesmo passo entre -(hi-lo) e +(hi-lo); construído, não suposto
    out, cur = set(), -(hi - lo)
    while cur <= hi - lo:
        out.add(cur)
        cur += step
    return out


def check(margs: set[F], label: str) -> dict:
    """Alguma margem cai nas faixas que TOL poderia atravessar?"""
    above_upper = sorted(m for m in margs if UPPER < m <= UPPER + TOL)
    below_lower = sorted(m for m in margs if LOWER - TOL <= m < LOWER)
    # distância da fronteira à margem alcançável mais próxima de cada lado
    gt_upper = min((m for m in margs if m > UPPER), default=None)
    lt_lower = max((m for m in margs if m < LOWER), default=None)
    # e a checagem simétrica, mais forte
    near_upper = sorted(m for m in margs if abs(m - UPPER) <= TOL)
    near_lower = sorted(m for m in margs if abs(m - LOWER) <= TOL)
    return {
        "label": label,
        "n_margins": len(margs),
        "in_upper_band": above_upper,
        "in_lower_band": below_lower,
        "reachable_just_above_upper": gt_upper,
        "gap_above_upper": (gt_upper - UPPER) if gt_upper is not None else None,
        "reachable_just_below_lower": lt_lower,
        "gap_below_lower": (LOWER - lt_lower) if lt_lower is not None else None,
        "two_sided_near_upper": near_upper,
        "two_sided_near_lower": near_lower,
        "safe_one_sided": not above_upper and not below_lower,
        "safe_two_sided": not near_upper and not near_lower,
    }


def dec(f: F, places: int = 12) -> str:
    """Racional como decimal exato, sem float."""
    neg = f < 0
    f = abs(f)
    ip = f.numerator // f.denominator
    rem = f - ip
    out = str(ip)
    if rem:
        digits = []
        for _ in range(places):
            rem *= 10
            d = rem.numerator // rem.denominator
            digits.append(str(d))
            rem -= d
            if rem == 0:
                break
        out += "." + "".join(digits)
    return ("-" if neg else "") + out


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    grids = [("inteira", Decimal("1")),
             ("1 casa decimal", Decimal("0.1")),
             ("2 casas decimais", Decimal("0.01"))]
    results = []
    for label, step in grids:
        totals, g = reachable_totals(step)
        margs = margins(totals)
        r = check(margs, label)
        r["step"] = str(step)
        r["margin_grid"] = g
        r["n_totals"] = len(totals)
        results.append(r)

    integer = results[0]
    claim_holds = integer["safe_one_sided"]
    first_unsafe = next((r for r in results if not r["safe_one_sided"]), None)

    L, w = [], None
    w = L.append
    if claim_holds:
        w("# A alegação se sustenta para notas inteiras — e quebra a partir de "
          "duas casas decimais")
    else:
        w("# A ALEGAÇÃO ESTÁ ERRADA")
    w("")
    w(f"- Gerado: `{stamp}` · gerador `{Path(__file__).name}`")
    w("- Aritmética **exata** (`Fraction` sobre `Decimal`). Nenhum float entra "
      "na prova — float seria o próprio erro que ela investiga.")
    w("- Enumeração **completa** do espaço alcançável, não amostra.")
    w("")
    w("## Veredito")
    w("")
    if claim_holds:
        w("**Confirmada para notas inteiras.** Nenhuma margem alcançável cai em "
          f"`(upper, upper+TOL]` nem em `[lower-TOL, lower)`. A margem "
          f"alcançável mais próxima acima de `upper` está a "
          f"**{dec(integer['gap_above_upper'])}** dele, e a mais próxima abaixo "
          f"de `lower` a **{dec(integer['gap_below_lower'])}** — ambas maiores "
          f"que TOL = {dec(TOL)}.")
    else:
        w("**Refutada.** Existe margem alcançável dentro da faixa que TOL "
          "atravessa. Ver a tabela.")
    w("")
    if first_unsafe:
        w(f"**Mas a folga é fina.** Com notas de **{first_unsafe['label']}** o "
          "desvio passa a ser alcançável: "
          + ", ".join(f"`{dec(x)}`" for x in (first_unsafe["in_upper_band"]
                                              + first_unsafe["in_lower_band"])[:4])
          + ". Se o contrato do juiz algum dia aceitar nota fracionária além de "
            "uma casa, esta prova deixa de valer.")
        w("")
    w("## Método")
    w("")
    w("O total ponderado de um braço é `0,4·a + 0,2·b + 0,2·c + 0,2·d`. O script "
      "**constrói** o conjunto de totais alcançáveis somando os quatro "
      "critérios sobre toda a grade de notas — não assume que o resultado é "
      "aritmético. Depois constrói o conjunto de margens como todas as "
      "diferenças entre dois totais alcançáveis, e testa a pertinência às duas "
      "faixas.")
    w("")
    w("Fronteiras testadas, da regra de decisão congelada `540df728…`:")
    w("")
    w(f"- limiar canônico: `{dec(THRESHOLD)}`")
    w(f"- meia-largura `w`: `{dec(W)}`")
    w(f"- `lower` = limiar − w = `{dec(LOWER)}`")
    w(f"- `upper` = limiar + w = `{dec(UPPER)}`")
    w(f"- `TOL` do scorer: `{dec(TOL)}`")
    w("")
    w("## Resultado por grade de nota")
    w("")
    w("| grade | passo da margem | margens possíveis | cai em `(upper, upper+TOL]` | "
      "cai em `[lower-TOL, lower)` | folga acima de `upper` | folga abaixo de `lower` |")
    w("|---|---|---|---|---|---|---|")
    for r in results:
        w(f"| {r['label']} | `{dec(r['margin_grid'])}` | {r['n_margins']} | "
          f"{'**' + ', '.join(dec(x) for x in r['in_upper_band'][:3]) + ('…' if len(r['in_upper_band'])>3 else '') + '**' if r['in_upper_band'] else 'nenhuma'} | "
          f"{'**' + ', '.join(dec(x) for x in r['in_lower_band'][:3]) + ('…' if len(r['in_lower_band'])>3 else '') + '**' if r['in_lower_band'] else 'nenhuma'} | "
          f"`{dec(r['gap_above_upper'])}` | `{dec(r['gap_below_lower'])}` |")
    w("")
    w("## A checagem simétrica, que é mais dura")
    w("")
    w("As duas faixas do enunciado são de um lado só. A pergunta mais forte é se "
      "existe margem alcançável a menos de TOL de uma fronteira, para qualquer "
      "lado — porque um desvio pode empurrar para dentro ou para fora.")
    w("")
    w("| grade | margens a ≤ TOL de `upper` | margens a ≤ TOL de `lower` | seguro |")
    w("|---|---|---|---|")
    for r in results:
        w(f"| {r['label']} | "
          f"{', '.join(dec(x) for x in r['two_sided_near_upper'][:3]) + ('…' if len(r['two_sided_near_upper'])>3 else '') or 'nenhuma'} | "
          f"{', '.join(dec(x) for x in r['two_sided_near_lower'][:3]) + ('…' if len(r['two_sided_near_lower'])>3 else '') or 'nenhuma'} | "
          f"{'sim' if r['safe_two_sided'] else '**não**'} |")
    w("")
    first_two_sided = next((r for r in results if not r["safe_two_sided"]), None)
    if first_two_sided:
        w(f"**A leitura conservadora já falha em {first_two_sided['label']}.** "
          f"Com uma casa decimal existe margem alcançável a "
          f"`{dec(min(abs(x - UPPER) for x in first_two_sided['two_sided_near_upper']))}` "
          f"de `upper` — abaixo de TOL. Ela está do lado de DENTRO, então a "
          "faixa de um lado só do enunciado não a pega; a pergunta simétrica "
          "pega. A alegação original é verdadeira como foi enunciada, e a "
          "margem de segurança é menor do que o enunciado sugere.")
        w("")
    w("## O que esta prova NÃO cobre")
    w("")
    w("1. **Só o modelo aritmético declarado.** Pesos exatamente 0,4/0,2/0,2/0,2, "
      "quatro critérios, margem como diferença de dois totais ponderados. Se o "
      "scorer arredondar em outro ponto do cálculo, ou se algum critério mudar "
      "de peso, a prova precisa ser refeita.")
    w("2. **Não diz que TOL é inofensivo em geral** — diz que, nesta grade de "
      "notas e nestas fronteiras, ele não alcança nenhuma margem possível. São "
      "coisas diferentes.")
    w("3. **A folga depende da grade.** Ela é confortável com nota inteira e "
      "some com duas casas decimais. Isso é propriedade das fronteiras "
      "escolhidas, não uma margem de segurança projetada.")
    w("")
    w("> **Ressalva sobre a origem da alegação.** Ela é minha, e antes disto "
      "estava conferida em quatro valores à mão. Amostra de quatro não distingue "
      "\"nenhuma margem cai na faixa\" de \"as quatro que olhei não caíam\". "
      "Esta enumeração distingue.")
    w("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"grade inteira: seguro={integer['safe_one_sided']} | "
          f"folga acima={dec(integer['gap_above_upper'])} | "
          f"folga abaixo={dec(integer['gap_below_lower'])}")
    for r in results:
        print(f"  {r['label']:18s} passo={dec(r['margin_grid']):8s} "
              f"margens={r['n_margins']:7d} seguro={r['safe_one_sided']}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
