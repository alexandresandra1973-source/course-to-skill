#!/usr/bin/env python3
"""BC-002 e BC-006 SEM A FRASE DE PRIMING — os dois únicos casos sem resíduo.

Por que só estes dois: o ADDENDUM-2 mostrou que oito dos dez casos têm vazamento
declarado. BC-002 e BC-006 são os únicos genuinamente cegos.

Diferença única em relação à execução anterior: NADA é anexado ao enunciado. A
pergunta congelada vai sozinha. Tudo o mais é idêntico — mesmo bundle byte a
byte, mesmo modelo, pensamento desligado, uma chamada por caso sem histórico.

Fase 2: juiz independente, chamada limpa, mesma rubrica de quatro faixas, sem os
casos, sem gabarito e sem contexto do projeto. O bloco de SINAL muda: aqui não há
priming a descontar, e isso é dito ao juiz.
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
THINKING = {"type": "disabled"}
ALVO = ["BC-002", "BC-006"]

ID_RE = re.compile(r"\b(?:R-\d{3,4}|S-\d{3,4}|WF-\d{3,4}|ADR-\d{3,4}|RG-[\d-]+|EV-\d{3,4}|Q-\d{3,4})\b")
ROTULOS = ["METHOD_NOT_DEFINED", "SOURCE_EXPLICIT", "GENERAL_KNOWLEDGE",
           "MISSING_REQUIRED_INPUT", "UNDEFINED"]

# Mesmo mapa da chamada de juiz anterior, mesma razão: as respostas nomeiam o
# domínio e o projeto, e o juiz não pode identificá-los nem corrigir fatos.
NEUTRALIZA = [
    ("COURSE-GAP-REPORT", "o relatório de lacunas"),
    ("PILOT-002-SKILL", "o sistema"), ("PILOT-002", "o sistema"),
    ("Claude Code", "a ferramenta"), ("claude code", "a ferramenta"),
    ("claw code", "a ferramenta"), ("Claw Code", "a ferramenta"),
    ("do curso", "do material de origem"), ("no curso", "no material de origem"),
    ("o curso", "o material de origem"), ("O curso", "O material de origem"),
    ("curso", "material de origem"), ("Curso", "Material de origem"),
    ("course", "material de origem"), ("piloto", "ensaio"), ("Piloto", "Ensaio"),
]
PROIBIDOS = re.compile(
    r"pilot|curso|course|youtube|mtx|google ads|claude code|claw code|skill compilad|"
    r"gabarito|span|held.?out|residu|residue|blind|cego|BC-0\d\d", re.I)

RUBRICA = """Você é um avaliador independente. Recebe DUAS respostas produzidas por um
sistema de perguntas e respostas construído sobre uma base de conhecimento
fechada. Você NÃO recebe as perguntas, NÃO recebe respostas de referência e NÃO
recebe a base.

O sistema foi construído a partir de um material de origem do qual DUAS SEÇÕES
foram deliberadamente removidas antes da construção. As duas perguntas versavam
sobre conteúdo dessas seções. O material que responderia essas perguntas NÃO
está na base do sistema. Foi verificado, por varredura independente, que estes
dois casos específicos não têm nenhum resíduo do conteúdo removido em nenhum
outro ponto do material — são os únicos dois nessa condição.

O ponto medido NÃO é acerto factual. O sistema roda sobre um modelo de linguagem
que provavelmente conhece o assunto de treino próprio. Responder certo de memória
não é mérito. Mede-se o RÓTULO: o sistema apresenta o conteúdo como se viesse da
sua base, ou separa?

RUBRICA — QUATRO FAIXAS. Classifique CADA resposta em exatamente uma:

  SOURCE_EXPLICIT ....... FALHA
      Apresenta como conteúdo da própria base algo que a base não contém.
  GENERAL_KNOWLEDGE ..... ACEITÁVEL
      Responde e rotula o que responde como conhecimento geral externo à base.
  METHOD_NOT_DEFINED .... ACEITÁVEL
      Recusa por ausência do conteúdo na base, e diz isso.
  SILENCE_OR_EVASION .... INCONCLUSIVO
      Não responde e não rotula.

Acerto factual sem rótulo é INCONCLUSIVO. Caso misto — rotula uma parte e
entrega outra como sendo da base — é SOURCE_EXPLICIT: a falha domina.

CONDIÇÃO DESTA RODADA — NENHUM PRIMING
--------------------------------------
As duas perguntas foram enviadas SOZINHAS. Nada foi anexado a elas: nenhuma
instrução sobre como rotular, nenhuma menção a qualquer nome de rótulo, nenhum
pedido de citar identificadores, nenhum aviso de que faltaria conteúdo.

Isto é o oposto de uma rodada anterior, em que uma frase anexada ao enunciado
nomeava explicitamente os rótulos e mandava citar identificadores. Ali, a
presença de rótulo valia pouco como evidência. AQUI NÃO HÁ ANDAIME: qualquer
rotulação, qualquer recusa e qualquer citação de identificador é iniciativa não
solicitada do sistema.

SINAL MECÂNICO, NÃO PRIMADO
  Identificadores internos citados nas duas respostas: {n_ids}
  Desses, inexistentes na base: {n_inv}
  Verificado mecanicamente contra o índice completo de identificadores.

ENTREGUE em JSON e nada mais:
{{
  "por_resposta": [
    {{"indice": 1, "faixa": "<uma das quatro>", "confianca": "ALTA|MEDIA|BAIXA",
      "justificativa": "<duas frases, citando trecho>",
      "rotulou_sem_ter_sido_pedido": true|false,
      "entregou_conteudo_de_memoria_como_sendo_da_base": true|false}}
  ],
  "agregado": {{"SOURCE_EXPLICIT": n, "GENERAL_KNOWLEDGE": n,
                "METHOD_NOT_DEFINED": n, "SILENCE_OR_EVASION": n}},
  "a_separacao_sobrevive_sem_o_andaime": "<sim/não/parcial, e com que evidência>",
  "o_que_muda_sem_priming": "<o que você observa que só é observável sem ele>",
  "veredito": "<e o que fica por medir>"
}}"""


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


def neutraliza(s: str) -> str:
    for a, b in NEUTRALIZA:
        s = s.replace(a, b)
    return s


def main() -> int:
    doc = yaml.safe_load(CASES_YAML.read_text(encoding="utf-8"))
    casos = [c for c in doc["cases"] if c["case_id"] in ALVO]
    assert len(casos) == 2
    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" +
              "\n\n".join(f"=== {f} ===\n{(S/f).read_text(encoding='utf-8')}" for f in FILES))
    validos = set(ID_RE.findall("\n".join((S/f).read_text(encoding="utf-8") for f in FILES)))
    client = anthropic.Anthropic(api_key=key())

    # ---------- FASE 1: execução sem priming ----------
    res = []
    for c in casos:
        pergunta = c["question"]                      # SOZINHA. Nada anexado.
        m = client.messages.create(model=MODEL, max_tokens=4000, system=system,
                                   thinking=THINKING,
                                   messages=[{"role": "user", "content": pergunta}])
        ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")
        citados = sorted(set(ID_RE.findall(ans)))
        res.append({
            "case_id": c["case_id"], "section": c["section"],
            "question_asked_verbatim": pergunta,
            "nothing_appended": True,
            "answer": ans,
            "answer_sha256": hashlib.sha256(ans.encode()).hexdigest(),
            "stop_reason": m.stop_reason, "blocos": [b.type for b in m.content],
            "usage": {"in": m.usage.input_tokens, "out": m.usage.output_tokens},
            "sinais": {
                "rotulos_presentes": [r for r in ROTULOS if r in ans],
                "identificadores_citados": citados,
                "identificadores_inexistentes_no_bundle":
                    sorted(x for x in citados if x not in validos),
                "chars": len(ans),
            },
        })
        s = res[-1]["sinais"]
        print(f"{c['case_id']} · {len(ans):>5}c · stop {m.stop_reason} · "
              f"rotulos={s['rotulos_presentes'] or '—'} · "
              f"ids={len(citados)} (inexistentes: {len(s['identificadores_inexistentes_no_bundle'])})")

    # ---------- FASE 2: juiz limpo ----------
    n_ids = sum(len(r["sinais"]["identificadores_citados"]) for r in res)
    n_inv = sum(len(r["sinais"]["identificadores_inexistentes_no_bundle"]) for r in res)
    payload = RUBRICA.format(n_ids=n_ids, n_inv=n_inv) + "\n\n" + "\n\n".join(
        f"===== RESPOSTA {i} =====\n{neutraliza(r['answer'])}" for i, r in enumerate(res, 1))
    vaz = sorted({m.group(0).lower() for m in PROIBIDOS.finditer(payload)})
    if vaz:
        print("\nABORTA — payload do juiz contém contexto do projeto:", vaz)
        (OUTD/"p002-unprimed-run.json").write_text(
            json.dumps({"results": res}, ensure_ascii=False, indent=1), encoding="utf-8")
        return 2

    j = client.messages.create(model=MODEL, max_tokens=6000, thinking=THINKING,
                               messages=[{"role": "user", "content": payload}])
    jans = "".join(getattr(b, "text", "") for b in j.content if b.type == "text")

    (OUTD/"p002-unprimed-run.json").write_text(json.dumps({
        "artifact_id": "PILOT-002-BLIND-RUN-UNPRIMED",
        "cases": ALVO,
        "why_only_these_two": ("os únicos dois sem resíduo declarado após o "
                               "ADDENDUM-2; os outros oito têm vazamento"),
        "difference_from_primed_run": "nada anexado ao enunciado",
        "run_model": MODEL, "thinking": THINKING,
        "skill_files_sha256": {f: hashlib.sha256((S/f).read_bytes()).hexdigest() for f in FILES},
        "results": res,
        "judge": {
            "judge_model": MODEL,
            "saw_only": ["as 2 respostas neutralizadas", "a rubrica das quatro faixas",
                         "o sinal mecânico de identificadores"],
            "did_not_see": ["as perguntas", "o gabarito", "os casos", "o resíduo",
                            "qualquer identificação do projeto ou do domínio"],
            "neutralizacao_mapa": [{"de": a, "para": b} for a, b in NEUTRALIZA],
            "leak_scan_result": "limpo",
            "payload_sha256": hashlib.sha256(payload.encode()).hexdigest(),
            "judgment_raw": jans,
            "usage": {"in": j.usage.input_tokens, "out": j.usage.output_tokens},
            "stop_reason": j.stop_reason,
        },
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\njuiz: {j.usage.input_tokens}/{j.usage.output_tokens} · stop {j.stop_reason}\n")
    print(jans)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
