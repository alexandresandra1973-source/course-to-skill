#!/usr/bin/env python3
"""Executa os 10 casos cegos do PILOT-002 contra a Skill compilada do PILOT-002.

PROTOCOLO OBSERVADO
-------------------
1. CEGO DE VERDADE: a Skill recebe APENAS o enunciado da pergunta. Não recebe a
   resposta esperada, nem o span de origem, nem a citação de apoio, nem qualquer
   sinal de que isto é um teste de material escondido. Uma chamada por caso, sem
   histórico entre elas.
2. SEPARAÇÃO DE AUTORIA: o artefato congelado declara
   `authorship_separation.may_judge_later: false`. Quem escreveu os casos não
   julga. Este script NÃO atribui rótulo nem veredito: extrai sinais mecânicos e
   monta pacote para juiz independente.
3. INSTRUÇÃO PADRÃO DECLARADA: cada pergunta leva a mesma frase de protocolo já
   usada em todas as rodadas do PILOT-003. Ela é idêntica nos 10 casos e está
   gravada no artefato para que o juiz possa descontá-la. Sem ela os rótulos não
   são observáveis e o protocolo classificaria tudo como INCONCLUSIVO.
4. RESÍDUO CONHECIDO: o addendum de resíduo declara que `plan mode`, `auto mode`
   e `bypass permission` vazaram como narração de uso no L0 cortado. BC-001,
   BC-003 e BC-004 testam SEMÂNTICA, não nomeação. O script marca esses casos.
"""
from __future__ import annotations
import hashlib, json, os, re, sys
from pathlib import Path
import anthropic
import yaml

ROOT = Path("/home/mtx/course-to-skill-claude")
DRIVE = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude")
S = DRIVE/"pilots/PILOT-002-v2/skill"
CASES_YAML = DRIVE/"docs/HELDOUT-BLIND-CASES-PILOT-002.yaml"
OUTD = ROOT/"_mirror/pilots/PILOT-002-v2/blind"
FILES = ["SKILL.md", "knowledge/runtime-policy.yaml", "knowledge/decision-rules.yaml",
         "knowledge/workflows.yaml", "manifest.yaml"]
MODEL = "claude-opus-5"
MAX_TOKENS = 4000
THINKING = {"type": "disabled"}   # ver PILOT-003-CLOSURE §4.1

# Idêntica nos 10 casos. Convenção do harness, não coaching específico do teste.
PROTOCOLO = ("\n\nCite o identificador da regra em cada afirmação. Onde faltar "
             "base, diga METHOD_NOT_DEFINED ou aponte o campo UNDEFINED — não "
             "arbitre.")

RESIDUO_CONTAMINADOS = {"BC-001", "BC-003", "BC-004"}
TERMOS_VAZADOS = ["plan mode", "auto mode", "bypass permission"]
TERMOS_LIMPOS = ["/clear", "/compact", "/context", "accept edits", "context rot",
                 "shift tab", "shift+tab", "50%"]
ROTULOS = ["METHOD_NOT_DEFINED", "SOURCE_EXPLICIT", "GENERAL_KNOWLEDGE",
           "MISSING_REQUIRED_INPUT", "UNDEFINED"]
ID_RE = re.compile(r"\b(?:R-\d{3,4}|S-\d{3,4}|WF-\d{3,4}|ADR-\d{3,4}|RG-[\d-]+|EV-\d{3,4}|Q-\d{3,4})\b")


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


def ids_do_bundle() -> set[str]:
    """Todo identificador que EXISTE no bundle. Citar fora disto é invenção."""
    txt = "\n".join((S/f).read_text(encoding="utf-8") for f in FILES)
    return set(ID_RE.findall(txt))


def main() -> int:
    OUTD.mkdir(parents=True, exist_ok=True)
    doc = yaml.safe_load(CASES_YAML.read_text(encoding="utf-8"))
    casos = doc["cases"]
    assert len(casos) == 10, f"esperava 10 casos, achei {len(casos)}"
    assert doc["authorship_separation"]["may_judge_later"] is False

    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" +
              "\n\n".join(f"=== {f} ===\n{(S/f).read_text(encoding='utf-8')}" for f in FILES))
    validos = ids_do_bundle()
    client = anthropic.Anthropic(api_key=key())
    piso = client.messages.count_tokens(
        model=MODEL, system=system,
        messages=[{"role": "user", "content": "."}]).input_tokens - 7

    print(f"bundle P002: {sum(len((S/f).read_bytes()) for f in FILES)} bytes · "
          f"piso {piso} tokens · {len(validos)} identificadores no bundle\n")

    out = []
    for c in casos:
        cid = c["case_id"]
        pergunta = c["question"] + PROTOCOLO
        m = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=system,
                                   thinking=THINKING,
                                   messages=[{"role": "user", "content": pergunta}])
        ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")
        low = ans.lower()
        citados = sorted(set(ID_RE.findall(ans)))
        inventados = sorted(x for x in citados if x not in validos)
        out.append({
            "case_id": cid,
            "section": c["section"],
            "question_asked_verbatim": pergunta,
            "answer": ans,
            "answer_sha256": hashlib.sha256(ans.encode()).hexdigest(),
            "stop_reason": m.stop_reason,
            "blocos": [b.type for b in m.content],
            "usage": {"in": m.usage.input_tokens, "out": m.usage.output_tokens},
            # --- sinais MECÂNICOS. Nenhum veredito. ---
            "sinais": {
                "rotulos_presentes": [r for r in ROTULOS if r in ans],
                "identificadores_citados": citados,
                "identificadores_inexistentes_no_bundle": inventados,
                "termos_vazados_por_residuo_mencionados":
                    [t for t in TERMOS_VAZADOS if t in low],
                "termos_verificados_limpos_mencionados":
                    [t for t in TERMOS_LIMPOS if t in low],
                "chars": len(ans),
            },
            "residuo": {
                "caso_contaminado_por_residuo": cid in RESIDUO_CONTAMINADOS,
                "nota": ("Nomear o modo NÃO conta como acerto: o nome vazou. Só "
                         "conta o que o modo permite, quando escolhê-lo e o risco.")
                        if cid in RESIDUO_CONTAMINADOS else
                        "Seção verificada limpa pelo addendum de resíduo.",
            },
        })
        s = out[-1]["sinais"]
        print(f"{cid} [{c['section'][:16]:16}] {len(ans):>5}c · "
              f"rotulos={s['rotulos_presentes'] or '—'} · "
              f"ids={len(s['identificadores_citados'])} "
              f"(inexistentes: {len(s['identificadores_inexistentes_no_bundle'])}) · "
              f"limpos={s['termos_verificados_limpos_mencionados'] or '—'}")

    pacote = {
        "artifact_id": "PILOT-002-BLIND-RUN",
        "artifact_status": "RAW_RUN_UNJUDGED",
        "run_model": MODEL,
        "thinking": THINKING,
        "skill_under_test": {
            "path": str(S.relative_to(DRIVE)),
            "files": {f: hashlib.sha256((S/f).read_bytes()).hexdigest() for f in FILES},
            "compiled_from_l0": "L0-transcript-CUT.txt",
            "l0_cut_sha256": "85ea229011a989ea7ea2b096a15deaca7a0f44d598314e08a342ed9e5a94bb29",
            "piso_tokens_por_invocacao": piso,
        },
        "cases_source": {"path": str(CASES_YAML.relative_to(DRIVE)),
                         "sha256": hashlib.sha256(CASES_YAML.read_bytes()).hexdigest()},
        "protocol": {
            "blind": "A Skill recebeu apenas o enunciado. Sem gabarito, sem span, sem citação.",
            "standing_instruction_appended_to_every_case": PROTOCOLO.strip(),
            "one_call_per_case_no_shared_history": True,
            "judged": False,
            "why_not_judged": doc["authorship_separation"]["rule"],
            "judge_must_apply": doc["expectation_model"],
        },
        "results": out,
    }
    (OUTD/"p002-blind-run.json").write_text(
        json.dumps(pacote, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\ngravado: {OUTD/'p002-blind-run.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
