#!/usr/bin/env python3
"""Publica o TESTE DE VAZAMENTO da régua do juiz. Sem interpretar o veredito."""
from __future__ import annotations
import hashlib, json, yaml
from datetime import datetime, timezone
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); DOCS = DRIVE / "Course-to-Skill-Claude/docs"
PKG = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE"
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
R2 = json.loads((T / "leak-test.json").read_text(encoding="utf-8"))
R1 = json.loads((T / "leak-test-r1.json").read_text(encoding="utf-8"))
JR = DOCS / "TEST-0008-JUDGE-PACKAGE/RUBRIC-JUDGE.yaml"


def shp(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    r = yaml.safe_load(JR.read_text(encoding="utf-8"))["rubric"]
    same = sum(1 for c in r
               if c["score_anchors"]["CRITERIO_REGISTRADO"]["source_anchor"]["quote"]
               == c["score_anchors"]["APLICADO_SEM_CRITERIO"]["source_anchor"]["quote"])

    doc = {
        "schema_version": "0.2.0",
        "artifact_id": "TEST-0008-JUDGE-RUBRIC-LEAK-TEST",
        "artifact_status": "DUAS_RODADAS_EXECUTADAS",
        "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "setup": {
            "entrada": "SOMENTE a régua de pontuação", "system_prompt": None,
            "nao_informado": ["que existem condições", "que é experimento comparativo",
                              "os outputs", "o projeto", "qualquer instrução de tarefa"],
            "pergunta_verbatim_nas_duas_rodadas": R2["question"],
            "model": "claude-opus-5"},
        "rodada_1_ANTES_DO_CONSERTO": {
            "rubric_sha256": R1["rubric_sha256"],
            "answer_sha256": R1["answer_sha256"],
            "veredito_do_revisor": "REPROVOU",
            "achado_central": ("'eles quase certamente NÃO diferem por modelo, prompt "
                               "ou autor, mas pela FORMA DA REPRESENTAÇÃO DA FONTE "
                               "entregue a quem produziu o texto'"),
            "answer": R1["answer"]},
        "conserto_aplicado": {
            "1_faixas_reescritas_como_propriedade_do_output": True,
            "2_band_rule_removido": True,
            "3_ancora_propria_para_as_duas_faixas_de_cima": "8 de 8, era 0 de 8",
            "4_lacunas_de_L0_declaradas": True,
            "5_vocabulario_de_insumo_e_de_projeto_removido": [
                "L0 -> source", "PILOT-001/TEST-0008/0.1.4 removidos",
                "slot/embaralhada/cega removidos", "prosa/camada operacional removidos"],
            "ordenacao_e_pesos": "INALTERADOS",
        },
        "rodada_2_DEPOIS_DO_CONSERTO": {
            "rubric_sha256": R2["rubric_sha256"],
            "answer_sha256": R2["answer_sha256"],
            "answer": R2["answer"]},
        "criterio_de_leitura_declarado_antes": {
            "AINDA_VAZA": "reconstruir os três braços ou a forma do insumo",
            "PASSA": ("descrever só faixas de comportamento sem inferir a origem dos "
                      "materiais")},
        "o_que_mudou_entre_as_duas": {
            "inferencia_sobre_a_FORMA_DO_INSUMO": {
                "rodada_1": ("PRESENTE e central: os braços diferem pela forma da "
                             "representação da fonte — estruturada, prosa, e prosa "
                             "com rótulo de estruturada"),
                "rodada_2": ("AUSENTE. E negada explicitamente: 'Nada indica se algum "
                             "material é humano, se são modelos diferentes ou o mesmo "
                             "modelo em condições distintas, nem qual rótulo "
                             "corresponde a qual tipo.'")},
            "tres_tipos_descritos": {
                "rodada_1": "por INSUMO (artefato estruturado / prosa / controle sem fonte)",
                "rodada_2": ("por COMPORTAMENTO (o executor / o recapitulador polido / "
                             "o divergente) — que é a própria escada de faixas "
                             "instanciada")},
            "faixas_lidas_como_predicao_dos_bracos": {"rodada_1": True, "rodada_2": False},
        },
        "VAZAMENTOS_RESIDUAIS_NOVOS": {
            "1_scoring_cautions_como_negativo_fotografico": {
                "citacao": ("'As scoring_cautions são o negativo fotográfico dos "
                            "materiais. Cada uma antecipa um modo de engano "
                            "específico, e ninguém escreve essas quatro advertências "
                            "no abstrato.'"),
                "origem": ("as cautions foram ACRESCENTADAS por mim para mitigar a "
                           "heurística de formato apontada na rodada 1"),
                "consequencia": ("a mitigação virou canal de vazamento: cada advertência "
                                 "declara a existência do material que ela protege "
                                 "contra"),
                "gravidade": "o conserto criou o defeito seguinte",
            },
            "2_lacunas_declaradas_lidas_como_calibracao_pos_hoc": {
                "citacao": ("'Onde o autor tinha um texto falhando na mão, a âncora "
                            "ficou afiada; onde não tinha, ficou template. (...) a "
                            "rubrica foi calibrada olhando pelo menos um dos "
                            "materiais.'"),
                "nota": ("a leitura é FALSA quanto ao fato — nenhum output existe — mas "
                         "o sinal que a produziu é real: 5 critérios com 4 citações "
                         "distintas e 3 com repetição. Declarar a lacuna foi o certo; "
                         "o efeito colateral é este."),
            },
            "3_alias_de_YAML_tornam_a_repeticao_conspicua": {
                "medido": f"{7} ocorrências de &id/*id na régua do juiz",
                "efeito": ("o serializador transforma citação repetida em âncora YAML, "
                           "o que sinaliza a repetição mais do que o texto sozinho"),
                "conserto_possivel": "dump sem aliases",
            },
        },
        "ACHADO_DE_DESENHO_INDEPENDENTE_DO_VAZAMENTO": {
            "o_que": ("os pisos obrigatórios cortam a faixa do meio em 8 de 8 "
                      "critérios"),
            "medido_por_script": True,
            "faixa_APLICADO_SEM_CRITERIO": [70, 89],
            "pisos": {c["criterion"]: c["minimum_score"] for c in r},
            "consequencia": ("nota 70-79 reprova o piso em 6 de 8 critérios; em "
                             "HUMAN_REVIEW_30_DAYS, piso 90, só a faixa de topo passa. "
                             "Um texto que aplica os sete passos corretamente SEM "
                             "registrar o critério reprova em bloco."),
            "citacao_da_rodada_2": ("'O desenho pressupõe que quase tudo falhe; o "
                                    "resultado interessante é onde.'"),
            "por_que_importa": ("a faixa do meio é a que o TEST-0008 existe para medir, "
                                "e ela está parcialmente inviável. NÃO é vazamento e "
                                "NÃO foi consertado: pisos são decisão de desenho e o "
                                "revisor mandou não tocá-los."),
        },
        "binds_to": {"rubric_judge_sha256": shp(JR)},
        "estado": "o veredito e a decisão de enviar ou não são do revisor",
    }
    out = PKG / "LEAK-TEST-JUDGE-RUBRIC.yaml"
    out.write_text(
        "# TESTE DE VAZAMENTO — a régua do juiz lida SOZINHA, por uma chamada limpa.\n"
        "# Resposta INTEIRA publicada. O veredito é do revisor.\n"
        + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")
    sums = {str(p.relative_to(PKG)): shp(p) for p in sorted(PKG.rglob("*"))
            if p.is_file() and p.name != "SHA256SUMS.txt"}
    (PKG / "SHA256SUMS.txt").write_text(
        "".join(f"{v}  {k}\n" for k, v in sums.items()), encoding="utf-8")
    print(f"publicado: {out.name} sha256 {shp(out)}")
    print(f"faixas de cima com citação IDÊNTICA: {same}/{len(r)}  (era 8/8)")
    print(f"pacote: {len(sums)} arquivos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
