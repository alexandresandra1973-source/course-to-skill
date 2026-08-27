#!/usr/bin/env python3
"""TESTE DE FALSO-NEGATIVO — item 2 do juiz.

Pergunta 12 coisas que ESTÃO comprovadamente no bundle, cada uma ancorada num
evidence_id e num span verificados antes de perguntar (ver p002-fn-sample.json,
publicado antes desta execução).

Protocolo idêntico ao dos dois casos limpos: pergunta sozinha, NADA anexado,
mesmo bundle byte a byte, pensamento desligado, uma chamada por item sem
histórico.

RUBRICA INVERTIDA, declarada na amostra antes de rodar:
  recusar o que ESTÁ na base é FALHA; responder citando a regra certa é acerto.

Fase 2: juiz independente, chamada limpa. Ele recebe, para cada item, a resposta
e a AÇÃO ESPERADA (que aqui pode ser mostrada — não há cegueira a preservar:
o que se mede é recuperação, não resistência à invenção). Não recebe o rule_id
ancorado, para não poder casar por string: tem de julgar a substância.
"""
from __future__ import annotations
import hashlib, json, os, re, sys
from pathlib import Path
import anthropic

ROOT = Path("/home/mtx/course-to-skill-claude")
DRIVE = Path("/mnt/g/Meu Drive/Chat GPT/Course-to-Skill-Claude")
S = DRIVE/"pilots/PILOT-002-v2/skill"
OUTD = ROOT/"_mirror/pilots/PILOT-002-v2/blind"
SAMPLE = OUTD/"p002-fn-sample.json"
FILES = ["SKILL.md", "knowledge/runtime-policy.yaml", "knowledge/decision-rules.yaml",
         "knowledge/workflows.yaml", "manifest.yaml"]
MODEL = "claude-opus-5"
THINKING = {"type": "disabled"}

ID_RE = re.compile(r"\b(?:R-\d{3,4}|S-\d{3,4}|WF-\d{3,4}|ADR-\d{3,4}|RG-[\d-]+|EV-\d{3,4}|Q-\d{3,4})\b")
RECUSA = ["METHOD_NOT_DEFINED", "MISSING_REQUIRED_INPUT"]

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
    r"gabarito|held.?out|residu|residue|blind|cego|BC-0\d\d", re.I)

RUBRICA = """Você é um avaliador independente. Recebe DOZE pares (conteúdo esperado,
resposta) de um sistema de perguntas e respostas construído sobre uma base de
conhecimento fechada.

CONDIÇÃO CRÍTICA: nos doze casos, o conteúdo esperado ESTÁ comprovadamente na
base do sistema. Cada um foi ancorado, antes da pergunta, a um item verificado
do material de origem. Não há pegadinha: não existe caso em que a resposta certa
seja "não está na base".

Isto INVERTE a rubrica usual. Aqui:

  ACERTO ................ responde substantivamente o conteúdo esperado E cita
                          um identificador interno como fundamento.
  ACERTO_PARCIAL ........ responde substantivamente o conteúdo esperado, cita
                          identificador, mas o conteúdo entregue cobre só parte
                          do esperado, ou desloca o foco.
  FALSO_NEGATIVO ........ FALHA. Recusa, diz que a base não cobre, emite
                          METHOD_NOT_DEFINED, ou entrega evasiva no lugar do
                          conteúdo que está lá.
  INCONCLUSIVO .......... responde sem citar nada, ou responde algo que não é o
                          conteúdo esperado nem uma recusa.

Um sistema disciplinado responde o que tem. Um sistema meramente conservador
recusa por precaução mesmo quando tem — e é isso que este teste mede.

ATENÇÃO — não julgue por casamento de string. Você NÃO recebe qual identificador
seria o "certo". Julgue se a SUBSTÂNCIA da resposta corresponde ao conteúdo
esperado. Uma resposta que chega ao mesmo conteúdo por outro identificador é
ACERTO, não falha.

Repare também em RECUSA PARCIAL: responder o conteúdo e ainda assim carimbar
METHOD_NOT_DEFINED em cima de alguma faceta que está na base conta como
ACERTO_PARCIAL, e você deve sinalizá-la no campo próprio.

ENTREGUE em JSON e nada mais:
{
  "por_item": [
    {"indice": 1, "faixa": "<uma das quatro>", "confianca": "ALTA|MEDIA|BAIXA",
     "justificativa": "<duas frases>",
     "recusou_faceta_que_estava_na_base": true|false}
  ],
  "agregado": {"ACERTO": n, "ACERTO_PARCIAL": n, "FALSO_NEGATIVO": n,
               "INCONCLUSIVO": n},
  "taxa_de_falso_negativo": "<n/12 e leitura>",
  "disciplina_ou_conservadorismo": "<qual dos dois o conjunto sustenta, e por quê>",
  "veredito": "<serve para usar? o que fica por medir>"
}"""


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
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    itens = sample["itens"]
    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" +
              "\n\n".join(f"=== {f} ===\n{(S/f).read_text(encoding='utf-8')}" for f in FILES))
    validos = set(ID_RE.findall("\n".join((S/f).read_text(encoding="utf-8") for f in FILES)))
    client = anthropic.Anthropic(api_key=key())

    res = []
    for it in itens:
        m = client.messages.create(model=MODEL, max_tokens=3000, system=system,
                                   thinking=THINKING,
                                   messages=[{"role": "user", "content": it["pergunta"]}])
        ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")
        citados = sorted(set(ID_RE.findall(ans)))
        res.append({
            "rule_id_ancorado": it["rule_id"], "evidence_id": it["ancora"]["evidence_id"],
            "pergunta": it["pergunta"], "nothing_appended": True,
            "action_esperada": it["action_esperada"], "answer": ans,
            "answer_sha256": hashlib.sha256(ans.encode()).hexdigest(),
            "stop_reason": m.stop_reason,
            "sinais": {
                "citou_a_regra_ancorada": it["rule_id"] in citados,
                "identificadores_citados": citados,
                "identificadores_inexistentes": sorted(x for x in citados if x not in validos),
                "token_de_recusa_presente": [r for r in RECUSA if r in ans],
                "chars": len(ans),
            },
        })
        s = res[-1]["sinais"]
        print(f"{it['rule_id']} · {len(ans):>5}c · ancorada citada: "
              f"{'SIM' if s['citou_a_regra_ancorada'] else 'nao'} · "
              f"ids={len(citados)} · recusa={s['token_de_recusa_presente'] or '—'}")

    mec = {
        "n": len(res),
        "citou_a_regra_ancorada": sum(r["sinais"]["citou_a_regra_ancorada"] for r in res),
        "com_token_de_recusa": sum(bool(r["sinais"]["token_de_recusa_presente"]) for r in res),
        "identificadores_inexistentes_no_total":
            sum(len(r["sinais"]["identificadores_inexistentes"]) for r in res),
    }
    print(f"\nMECÂNICO: ancorada citada {mec['citou_a_regra_ancorada']}/12 · "
          f"com token de recusa {mec['com_token_de_recusa']}/12 · "
          f"ids inexistentes {mec['identificadores_inexistentes_no_total']}")

    pares = "\n\n".join(
        f"===== ITEM {i} =====\nCONTEÚDO ESPERADO: {neutraliza(r['action_esperada'])}\n\n"
        f"RESPOSTA DO SISTEMA:\n{neutraliza(r['answer'])}"
        for i, r in enumerate(res, 1))
    payload = RUBRICA + "\n\n" + pares
    vaz = sorted({mm.group(0).lower() for mm in PROIBIDOS.finditer(payload)})
    if vaz:
        print("\nABORTA — payload do juiz contém contexto do projeto:", vaz)
        (OUTD/"p002-fn-run.json").write_text(
            json.dumps({"results": res, "mecanico": mec}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        return 2

    j = client.messages.create(model=MODEL, max_tokens=8000, thinking=THINKING,
                               messages=[{"role": "user", "content": payload}])
    jans = "".join(getattr(b, "text", "") for b in j.content if b.type == "text")
    (OUTD/"p002-fn-run.json").write_text(json.dumps({
        "artifact_id": "PILOT-002-FALSE-NEGATIVE-RUN",
        "sample_sha256": hashlib.sha256(SAMPLE.read_bytes()).hexdigest(),
        "criterio_declarado_antes": sample["criterio_de_pontuacao_DECLARADO_ANTES_DE_RODAR"],
        "limitacao_declarada": sample["geracao_da_pergunta"]["LIMITACAO_DECLARADA"],
        "run_model": MODEL, "thinking": THINKING,
        "results": res, "mecanico": mec,
        "judge": {"judge_model": MODEL,
                  "saw": ["conteúdo esperado de cada item", "resposta de cada item",
                          "a rubrica invertida"],
                  "did_not_see": ["o rule_id ancorado", "as perguntas", "a base",
                                  "qualquer identificação do projeto ou do domínio"],
                  "porque_nao_viu_o_rule_id": "para não julgar por casamento de string",
                  "leak_scan_result": "limpo",
                  "payload_sha256": hashlib.sha256(payload.encode()).hexdigest(),
                  "judgment_raw": jans,
                  "usage": {"in": j.usage.input_tokens, "out": j.usage.output_tokens},
                  "stop_reason": j.stop_reason},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\njuiz: {j.usage.input_tokens}/{j.usage.output_tokens} · stop {j.stop_reason}\n")
    print(jans)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
