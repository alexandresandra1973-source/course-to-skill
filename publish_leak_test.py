#!/usr/bin/env python3
"""Publica o TESTE DE VAZAMENTO da régua do juiz. Sem interpretar o veredito."""
from __future__ import annotations
import hashlib, json, yaml
from datetime import datetime, timezone
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); DOCS = DRIVE / "Course-to-Skill-Claude/docs"
PKG = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE"
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
R3 = json.loads((T / "leak-test-r3.json").read_text(encoding="utf-8"))
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
        "artifact_status": "TRES_RODADAS_EXECUTADAS",
        "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "setup": {
            "entrada": "SOMENTE a régua de pontuação", "system_prompt": None,
            "nao_informado": ["que existem condições", "que é experimento comparativo",
                              "os outputs", "o projeto", "qualquer instrução de tarefa"],
            "pergunta_verbatim_nas_tres_rodadas": R3["question"],
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
        "rodada_2_VOCABULARIO_DE_INSUMO_REMOVIDO": {
            "rubric_sha256": "b0a29fa4e314b95c2039f74eb26bf18715f24edfef348ef018f423b9f87d2307",
            "answer_sha256": "c254c9bff1c453dca585d423f690b3b84138dd9daaf24010a07c1d4a171493b1",
            "veredito_do_revisor": "AINDA_NAO_ENVIAR",
            "answer": "PERDIDO_DO_ARTEFATO",
            "PERDA_DECLARADA": {
                "o_que": ("o texto verbatim desta rodada não está mais em disco: o "
                          "gerador da rubrica APAGA e recria o pacote a cada execução, "
                          "e o rastro em /tmp foi sobrescrito pela rodada 3 antes que "
                          "eu o copiasse"),
                "de_quem_e_a_falha": "minha, na ordem das operações",
                "o_que_sobra": ("o SHA-256 da resposta, que a identifica sem "
                                "ambiguidade, e as passagens citadas no relatório da "
                                "sessão; a resposta inteira foi entregue ao revisor "
                                "naquele momento"),
                "nao_reconstituido": ("não vou reescrever de memória o que foi medido: "
                                      "seria fabricar evidência"),
                "conserto": ("os rastros passam a ser gravados com nome por rodada "
                             "(leak-test-r1/r2/r3.json), fora do diretório que o "
                             "gerador apaga"),
            },
            "achado_central": ("as scoring_cautions viraram 'o negativo fotográfico "
                               "dos materiais': cada advertência declarava o material "
                               "contra o qual protegia")},
        "conserto_2": {
            "1_pisos": ("todo critério não-portão baixado para 70, o início da faixa "
                        "APLICADO_SEM_CRITERIO; HUMAN_REVIEW mantém 90 e STEP_ORDER 80 "
                        "por decisão registrada"),
            "2_scoring_cautions": ("reescritas como scoring_rules, propriedade positiva; "
                                   "as que não se deixavam reescrever assim foram "
                                   "REMOVIDAS — de quatro sobraram duas"),
            "3_aliases_yaml": "eliminados; citação repetida por extenso",
        },
        "rodada_3_DEPOIS_DO_SEGUNDO_CONSERTO": {
            "rubric_sha256": R3["rubric_sha256"],
            "answer_sha256": R3["answer_sha256"],
            "answer": R3["answer"]},
        "LEITURA_DA_RODADA_3": {
            "criterio": {"AINDA_VAZA": "reconstruir os três braços ou a forma do insumo",
                         "PASSA": "só faixas de comportamento, sem inferir a origem"},
            "o_que_sumiu": [
                ("a tese de que os braços diferem pela forma da REPRESENTAÇÃO DA "
                 "FONTE — central na rodada 1 — não voltou"),
                "o 'negativo fotográfico' das quatro cautions: duas foram removidas",
            ],
            "o_que_PERMANECE_e_por_qual_clausula": {
                "inferencia_de_formato": {
                    "citacao": ("'A cláusula de neutralidade de formato (tabela, lista "
                                "e texto corrido valem igual) sugere que os materiais "
                                "DIFEREM EM FORMATO e que o autor previu esse "
                                "confundidor — provavelmente um em tabela/checklist, "
                                "outro em prosa.'"),
                    "clausula_responsavel": "scoring_rules[0], neutralidade de formato",
                    "nomeia_prosa": True,
                    "veredito_mecanico": ("é inferência sobre a FORMA do material, que "
                                          "o critério declarado classifica como "
                                          "AINDA_VAZA"),
                },
                "pisos_desiguais_lidos_como_armadilha": {
                    "citacao": ("'Os limiares desiguais são armadilhas desenhadas. "
                                "(...) Isso só se constrói quando já se sabe que algum "
                                "material vai encalhar exatamente ali.'"),
                    "efeito_colateral_do_conserto_1": (
                        "baixar os outros seis pisos para 70 fez os dois pisos de "
                        "portão — 90 e 80 — ficarem SALIENTES por contraste. O "
                        "conserto tornou o desenho mais mensurável E mais legível."),
                },
                "placeholders_ainda_visiveis": {
                    "citacao": ("'São placeholders não preenchidos — a rubrica foi "
                                "gerada por template, critério a critério, e esses "
                                "dois ficaram pela metade.'"),
                    "nota": ("é a lacuna de L0 que eu DECLAREI. A declaração está no "
                             "operador; a régua do juiz mostra só a repetição, e ela "
                             "é lida como descuido em vez de achado sobre a fonte."),
                },
            },
        },
        "PADRAO_ESTRUTURAL_QUE_AS_TRES_RODADAS_MOSTRAM": {
            "enunciado": ("Toda instrução que a régua dá para NEUTRALIZAR um "
                          "confundidor descreve o confundidor. Mitigação e vazamento "
                          "são a mesma frase lida de dois lados."),
            "ocorrencias": [
                "rodada 1: band_rule negando a correspondência faixa↔origem",
                "rodada 2: as quatro scoring_cautions",
                "rodada 3: a cláusula de neutralidade de formato que sobrou",
            ],
            "consequencia": ("editar mais a régua do juiz tende a trocar um canal por "
                             "outro, não a fechar o último. As opções que restam são "
                             "de DESENHO, não de redação, e são do revisor."),
            "nao_editado_alem_do_pedido": True,
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
