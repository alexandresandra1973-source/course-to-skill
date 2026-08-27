#!/usr/bin/env python3
"""RE-JULGAMENTO com o neutralizador corrigido.

DEFEITO: o mapa de neutralização substituía por SUBSTRING, sem fronteira de
palavra. `recursos` virava `rematerial de origems` e `Cursor` virava
`Material de origemr`. Oito ocorrências nos três pacotes. O juiz do teste de
falso-negativo apontou o artefato sozinho, no item (d) do veredito dele.

Correção: substituição por REGEX COM FRONTEIRA DE PALAVRA. `curso` e `cursos`
casam; `recursos`, `Cursor` e `percurso` não.

As RESPOSTAS NÃO SÃO RE-EXECUTADAS. Só o julgamento roda de novo, sobre os mesmos
artefatos gravados. Os julgamentos antigos são preservados em
`judgment_superseded`; nada é apagado.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, sys
from pathlib import Path
import anthropic

ROOT = Path("/home/mtx/course-to-skill-claude")
B = ROOT/"_mirror/pilots/PILOT-002-v2/blind"
MODEL = "claude-opus-5"
THINKING = {"type": "disabled"}

# (padrão regex, substituto). Ordem importa: mais específico primeiro.
NEUTRALIZA = [
    (r"COURSE-GAP-REPORT", "o relatório de lacunas"),
    (r"\bPILOT-002-SKILL\b", "o sistema"),
    (r"\bPILOT-002\b", "o sistema"),
    (r"\bClaude Code\b", "a ferramenta"),
    (r"\bclaude code\b", "a ferramenta"),
    (r"\bclaw code\b", "a ferramenta"),
    (r"\bClaw Code\b", "a ferramenta"),
    (r"\bcursos?\b", "material de origem"),
    (r"\bCursos?\b", "Material de origem"),
    (r"\bcourses?\b", "material de origem"),
    (r"\bCourses?\b", "Material de origem"),
    (r"\bpilotos?\b", "ensaio"),
    (r"\bPilotos?\b", "Ensaio"),
]
PROIBIDOS = re.compile(
    r"pilot|curso|course|youtube|mtx|google ads|claude code|claw code|skill compilad|"
    r"gabarito|held.?out|residu|residue|blind|cego|BC-0\d\d", re.I)
# `recursos`/`Cursor` contêm o radical proibido mas NÃO identificam o projeto.
ISENTOS = re.compile(r"\b\w*(?:recurso|Recurso|cursor|Cursor)\w*\b")


def neutraliza(s: str) -> str:
    for pat, rep in NEUTRALIZA:
        s = re.sub(pat, rep, s)
    return s


def vazamento(payload: str) -> list[str]:
    """Ignora ocorrências dentro de palavras isentas (recursos, Cursor)."""
    limpo = ISENTOS.sub("§", payload)
    return sorted({m.group(0).lower() for m in PROIBIDOS.finditer(limpo)})


def carrega(nome: str, arquivo: str):
    spec = importlib.util.spec_from_file_location(nome, ROOT/arquivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def key() -> str:
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    for f in (ROOT/".env", Path.home()/".anthropic_key"):
        if f.exists():
            for l in f.read_text(encoding="utf-8").splitlines():
                if l.startswith("ANTHROPIC_API_KEY") or l.strip().startswith("sk-"):
                    return (l.split("=", 1)[1] if "=" in l else l).strip().strip('"\'')
    sys.exit("ANTHROPIC_API_KEY ausente")


def main() -> int:
    j10 = carrega("j10", "p002_judge.py")
    jup = carrega("jup", "p002_unprimed.py")
    jfn = carrega("jfn", "p002_false_negative_run.py")
    client = anthropic.Anthropic(api_key=key())

    def payload_10(d):
        return j10.RUBRICA + "\n\n" + "\n\n".join(
            f"===== RESPOSTA {i} =====\n{neutraliza(r['answer'])}"
            for i, r in enumerate(d["results"], 1))

    def payload_up(d):
        n_ids = sum(len(r["sinais"]["identificadores_citados"]) for r in d["results"])
        n_inv = sum(len(r["sinais"]["identificadores_inexistentes_no_bundle"]) for r in d["results"])
        return jup.RUBRICA.format(n_ids=n_ids, n_inv=n_inv) + "\n\n" + "\n\n".join(
            f"===== RESPOSTA {i} =====\n{neutraliza(r['answer'])}"
            for i, r in enumerate(d["results"], 1))

    def payload_fn(d):
        return jfn.RUBRICA + "\n\n" + "\n\n".join(
            f"===== ITEM {i} =====\nCONTEÚDO ESPERADO: {neutraliza(r['action_esperada'])}\n\n"
            f"RESPOSTA DO SISTEMA:\n{neutraliza(r['answer'])}"
            for i, r in enumerate(d["results"], 1))

    alvos = [("p002-judge.json", "p002-blind-run.json", payload_10, 8000),
             ("p002-unprimed-run.json", None, payload_up, 6000),
             ("p002-fn-run.json", None, payload_fn, 8000)]

    for destino, fonte, mk, maxtok in alvos:
        dest = json.loads((B/destino).read_text(encoding="utf-8"))
        src = json.loads((B/(fonte or destino)).read_text(encoding="utf-8"))
        payload = mk(src)
        vaz = vazamento(payload)
        if vaz:
            print(f"ABORTA {destino}: {vaz}")
            return 2
        antes = len(re.findall(r"rematerial de origem|Material de origemr", payload))
        m = client.messages.create(model=MODEL, max_tokens=maxtok, thinking=THINKING,
                                   messages=[{"role": "user", "content": payload}])
        ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")

        no = dest.get("judge", dest)
        no["judgment_superseded"] = {
            "raw": no.get("judgment_raw"),
            "payload_sha256": no.get("payload_sha256"),
            "motivo": ("neutralizador substituía por substring; `recursos` e `Cursor` "
                       "eram corrompidos. Preservado, não apagado."),
        }
        no["judgment_raw"] = ans
        no["payload_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
        no["neutralizador"] = {"tipo": "regex com fronteira de palavra",
                               "mapa": [{"padrao": p, "para": r} for p, r in NEUTRALIZA],
                               "isentos_da_varredura": ISENTOS.pattern,
                               "palavras_corrompidas_neste_payload": antes}
        no["usage"] = {"in": m.usage.input_tokens, "out": m.usage.output_tokens}
        (B/destino).write_text(json.dumps(dest, ensure_ascii=False, indent=1), encoding="utf-8")

        agg = re.search(r'"agregado":\s*\{[^}]*\}', ans)
        print(f"{destino:26} corrompidas agora: {antes} · {agg.group(0) if agg else ans[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
