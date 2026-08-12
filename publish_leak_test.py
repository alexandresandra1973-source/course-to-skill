#!/usr/bin/env python3
"""Publica o TESTE DE VAZAMENTO da régua do juiz. Sem interpretar o veredito."""
from __future__ import annotations
import hashlib, json, yaml
from datetime import datetime, timezone
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); DOCS = DRIVE / "Course-to-Skill-Claude/docs"
PKG = DOCS / "TEST-0008-RUBRIC-AUDIT-PACKAGE"
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
FULL = json.loads((T / "leak-test.json").read_text(encoding="utf-8"))
TRUNC = json.loads((T / "leak-test-TRUNCADA.json").read_text(encoding="utf-8"))
JR = DOCS / "TEST-0008-JUDGE-PACKAGE/RUBRIC-JUDGE.yaml"


def shp(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    r = yaml.safe_load(JR.read_text(encoding="utf-8"))["rubric"]
    same = sum(1 for c in r
               if c["score_anchors"]["APLICACAO_ESTRUTURAL"]["l0_anchor"]["quote"]
               == c["score_anchors"]["APLICACAO_INFERENCIAL"]["l0_anchor"]["quote"])

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "TEST-0008-JUDGE-RUBRIC-LEAK-TEST",
        "artifact_status": "MEDICAO_EXECUTADA",
        "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "o_que_converte": ("a ressalva 'o varredor pega o literal, paráfrase passa' "
                           "deixa de ser ressalva e vira medição"),
        "setup": {
            "entrada": "SOMENTE RUBRIC-JUDGE.yaml",
            "rubric_sha256": shp(JR),
            "system_prompt": None,
            "nao_informado_a_chamada": ["que existem condições", "que é experimento "
                                        "comparativo", "os outputs", "o projeto",
                                        "qualquer instrução de tarefa"],
            "pergunta": FULL["question"],
            "model": "claude-opus-5",
        },
        "chamadas": {
            "total": 2,
            "por_que_duas": ("a primeira bateu no max_tokens=4000 que EU configurei e "
                             "saiu cortada. Defeito de parâmetro meu, não resultado. "
                             "Refeita com 16000 para entregar a resposta inteira, que "
                             "era o que o revisor pediu. As duas ficam registradas."),
            "call_1_truncada": {"max_tokens": 4000,
                                "output_tokens": TRUNC["usage"]["output"],
                                "answer_sha256": TRUNC["answer_sha256"],
                                "answer": TRUNC["answer"]},
            "call_2_completa": {"max_tokens": 16000,
                                "output_tokens": FULL["usage"]["output"],
                                "answer_sha256": FULL["answer_sha256"],
                                "answer": FULL["answer"]},
        },
        "criterio_de_leitura_declarado_antes": {
            "VAZA": ("a resposta reconstrói três condições, ou descreve algo "
                     "equivalente a 'um artefato estruturado, um texto em prosa, e um "
                     "texto em prosa apresentado como estruturado'"),
            "SUSTENTA": ("descreve só quatro faixas de comportamento sem inferir a "
                         "origem dos materiais"),
        },
        "fatos_mecanicos_da_resposta": {
            "numero_de_tipos_inferido": 3,
            "inferiu_que_diferem_pela_forma_da_representacao_da_fonte": True,
            "citacao": ("'eles quase certamente NÃO diferem por modelo, prompt ou "
                        "autor, mas pela FORMA DA REPRESENTAÇÃO DA FONTE entregue a "
                        "quem produziu o texto'"),
            "reconstruiu_estruturado_e_prosa": True,
            "reconstruiu_o_terceiro_corretamente": False,
            "terceiro_que_supos": ("controle mínimo sem fonte, só priors do modelo — "
                                   "e NÃO 'prosa apresentada como estruturada'"),
            "leu_as_faixas_como_predicao_dos_bracos": True,
            "citacao_2": ("'As faixas de pontuação são, na prática, uma predição "
                          "ordenada dos três braços.'"),
            "nao_interpretado_aqui": ("o veredito entre VAZA e SUSTENTA é do revisor. "
                                      "Acima estão só contagens e citações literais."),
        },
        "achados_colaterais_verificaveis_por_script": {
            "faixas_90_100_e_70_89_compartilham_a_citacao_identica": {
                "criterios_afetados": f"{same} de {len(r)}",
                "confirmado_por_medicao": True,
                "consequencia": ("a distinção que mais importa ao estudo — com ou sem "
                                 "camada operacional — não tem nenhuma âncora textual "
                                 "que a discrimine; repousa só na definição genérica"),
                "origem": ("strip_for_judge mapeia as duas faixas para a mesma chave "
                           "de citação. É defeito meu, encontrado por este teste, e "
                           "independente da questão do vazamento."),
            },
            "faixas_altas_ancoradas_em_trechos_procedimentais_e_a_baixa_em_aforismos": {
                "faixa_30_69_com_citacao_distinta": f"{sum(1 for c in r if c['score_anchors']['ASSERCAO_SEM_SUBSTANCIA']['l0_anchor']['quote'] != c['score_anchors']['APLICACAO_ESTRUTURAL']['l0_anchor']['quote'])} de {len(r)}",
                "leitura_da_resposta": ("'Isso embute uma hipótese explícita: sob "
                                        "transmissão em prosa, o bordão sobrevive e o "
                                        "detalhe operacional evapora. É uma aposta "
                                        "sobre mecanismo de produção, não sobre "
                                        "mérito.'"),
                "por_que_importa": ("é circularidade do tipo que o auditor externo "
                                    "deveria procurar, encontrada por uma leitura "
                                    "cega da própria régua"),
            },
        },
        "binds_to": {"rubric_judge_sha256": shp(JR),
                     "audit_package_index": "TEST-0008-RUBRIC-AUDIT-PACKAGE.yaml"},
        "estado_do_pacote": ("NADA foi alterado na régua por causa deste teste. A "
                             "decisão sobre o conserto é do revisor."),
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
    print(f"tipos inferidos: 3 · estruturado+prosa reconstruídos · terceiro NÃO")
    print(f"faixas 90-100 e 70-89 com citação idêntica: {same}/{len(r)}")
    print(f"pacote: {len(sums)} arquivos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
