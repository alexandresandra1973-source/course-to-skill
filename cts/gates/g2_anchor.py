"""G2 — portão de ancoragem (ADR-0002).

Toda afirmação precisa de:
  span  que RESOLVE contra o vault, e
  quote que é substring byte-exata (após normalização de espaço) do texto
        devolvido por aquele span.

Quote ausente não é "campo opcional vazio": é impossibilidade de verificação.
O portão distingue os dois modos de falha porque eles têm causas diferentes:
NO_QUOTE é defeito de extração; SPAN_UNRESOLVED é defeito de endereço.
"""
from __future__ import annotations

import re
import unicodedata

from ..result import GateResult, PASS, FAIL
from ..vault import Vault


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def run(vault: Vault, records: list[dict], subject: str) -> GateResult:
    """records: [{id, spans: [...], quote: str|None, claim: str}]"""
    n = len(records)
    no_span, no_quote, unresolved, mismatch, ok = [], [], [], [], []
    resolutions = {"OK": 0}

    for r in records:
        spans = r.get("spans") or []
        if not spans:
            no_span.append({"id": r["id"], "reason": "NO_SPAN"})
            continue

        res = [vault.resolve(s) for s in spans]
        for x in res:
            resolutions[x.reason] = resolutions.get(x.reason, 0) + 1
        bad = [x for x in res if not x.ok]
        if bad:
            unresolved.append({"id": r["id"],
                               "spans": [{"span": x.span, "reason": x.reason,
                                          "detail": x.detail} for x in bad]})

        q = r.get("quote")
        if not q or not str(q).strip():
            no_quote.append({"id": r["id"], "reason": "NO_QUOTE"})
            continue

        hay = " ".join(_norm(x.text) for x in res if x.ok)
        if _norm(q) and _norm(q) in hay:
            ok.append(r["id"])
        else:
            mismatch.append({"id": r["id"], "reason": "QUOTE_NOT_IN_SPAN",
                             "quote_head": str(q)[:80]})

    n_span_refs = sum(len(r.get("spans") or []) for r in records)
    n_resolved = resolutions.get("OK", 0)

    state = PASS if (len(ok) == n and n > 0) else FAIL
    return GateResult(
        gate="G2-anchor",
        state=state,
        subject=subject,
        evidence={
            "records": n,
            "records_anchored_ok": len(ok),
            "records_without_quote": len(no_quote),
            "records_without_span": len(no_span),
            "records_with_unresolved_span": len(unresolved),
            "records_quote_mismatch": len(mismatch),
            "span_refs_total": n_span_refs,
            "span_refs_resolved": n_resolved,
            "span_refs_unresolved": n_span_refs - n_resolved,
            "resolution_reasons": resolutions,
        },
        findings=(no_span + no_quote[:3] + unresolved + mismatch[:5]),
        note=("quote ausente impede qualquer verificação lexical; "
              "span não resolvido é endereço inválido contra L0"),
    )
