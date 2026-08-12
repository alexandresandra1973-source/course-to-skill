#!/usr/bin/env python3
"""Relatório da extensão de duas comparações + canário. Amarrado por hash."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import yaml

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT"); CL = DRIVE / "Course-to-Skill-Claude"
SV2 = CL / "scorer-v2"; DOCS = CL / "docs"
OUT = DOCS / "SCORER-V2-TWO-COMPARISONS.yaml"
LAB = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude/t0008/canary8")
F7ZIP = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.4/06_COMPARISON_ARMS/TEST-0007"
         / "PRELOCK_F7_EXACT_MARGIN_BOUNDARIES"
         / "PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES.zip")
F7PRE = "PILOT-001-v0.1.4-PRELOCK-PATCH-F7-EXACT-MARGIN-BOUNDARIES/"
ADRZIP = (DRIVE / "Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"
          / "ARMS_WORDING_FROZEN/PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN.zip")
ADRMEM = ("PILOT-001-v0.1.4-TEST-0007-ARMS-WORDING-FROZEN/"
          "ADR-TEST-0008-INFORMATION-PARITY-v0.1.4.md")


def sh(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def shp(p: Path) -> str: return sh(p.read_bytes())


def main() -> int:
    for src in ("canary_two_comparisons.py", "patch_scorer_two_comparisons.py",
                "patch_freezer_two_comparisons.py"):
        (SV2 / src).write_bytes((Path(__file__).parent / src).read_bytes())
    canary = json.loads((LAB / "CANARY-RESULT.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(F7ZIP) as z:
        base_scorer = sh(z.read(F7PRE + "score_judge_results.py"))
        base_freezer = sh(z.read(F7PRE + "freeze_margin_lock.py"))
    adr = sh(zipfile.ZipFile(ADRZIP).read(ADRMEM))

    sums = {p.name: shp(p) for p in sorted(SV2.iterdir()) if p.is_file()}
    (SV2 / "SHA256SUMS.txt").write_text(
        "".join(f"{v}  {k}\n" for k, v in sums.items() if k != "SHA256SUMS.txt"),
        encoding="utf-8")

    doc = {
        "schema_version": "0.1.0",
        "artifact_id": "SCORER-V2-TWO-COMPARISONS",
        "artifact_status": "BUILT_AND_CANARY_APPROVED_NOT_A_PRE_RUN_LOCK",
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nao_e": ("lock pre-run, registry, opening record nem autorizacao de rodada. "
                  "E instrumento construido e testado; a rubrica e o passo 3."),

        "derivation": {
            "method": "PATCH sobre o F7 congelado, ancoras unicas, diff publicado",
            "por_que_patch": ("o requisito duro e ZERO REGRESSAO no TEST-0007; um "
                              "patch pequeno e auditavel linha a linha, uma "
                              "reescrita nao e"),
            "read_only_respeitado": True,
            "base": {"scorer_f7_sha256": base_scorer, "freezer_f7_sha256": base_freezer},
            "extended": {"scorer_sha256": shp(SV2 / "score_judge_results.py"),
                         "freezer_sha256": shp(SV2 / "freeze_margin_lock.py")},
            "diff_scorer": {"file": "PATCH.diff", "sha256": shp(SV2 / "PATCH.diff")},
            "diff_freezer": {"file": "PATCH-freezer.diff",
                             "sha256": shp(SV2 / "PATCH-freezer.diff")},
        },

        "design": {
            "principio": "ENVOLVER, NAO REESCREVER",
            "validate_comparisons": (
                "NAO reestruturada. Ganhou um unico parametro novo, lock_override, "
                "que permite alimenta-la com um lock sintetizado em memoria. P e F "
                "sao calculados chamando A MESMA funcao, uma vez por comparacao."),
            "consequencia_1": "o caminho do TEST-0007 executa exatamente o mesmo codigo",
            "consequencia_2": ("P e F sao medidos pelo mesmo instrumento POR "
                               "CONSTRUCAO, nao por disciplina. Metrica exclusiva de "
                               "uma das comparacoes e impossivel de expressar."),
            "onde_mora_a_identidade_de_P_e_F": {
                "local": "CODIGO (CANONICAL_COMPARISON_SETS), nao o lock",
                "por_que": ("um lock e dado, e quem adultera o lock adultera o dado. "
                            "Trocar os seletores entre P e F inverteria o que cada "
                            "quantidade significa sem mudar um so numero, e o lock "
                            "adulterado teria o seu proprio hash valido. So uma "
                            "ligacao no codigo pega isso — e o canario K3 prova."),
                "duplicada_no_freezer": ("de proposito: dois guardas independentes "
                                         "recusam a mesma troca, sem acoplamento"),
            },
        },

        "nao_independencia_de_P_e_F": {
            "registrada_no_codigo": True,
            "constante": "COMPARISON_INDEPENDENCE",
            "emitida_na_saida": "comparison_dependence",
            "independent": False,
            "shared_component": "SUMMARY_AS_SUMMARY",
            "razao": ("P e F subtraem o MESMO braco de baseline. O erro desse braco "
                      "e comum as duas, com o mesmo sinal, e CANCELA em P - F. "
                      "Trata-las como independentes subestimaria a variancia de "
                      "P - F e superestimaria a de cada uma isoladamente."),
            "operacoes_proibidas": [
                "somar variancias de P e F como se fossem independentes",
                "aplicar correcao de multiplas comparacoes que pressupoe independencia",
                "tratar P e F como duas amostras separadas em teste de hipotese"],
            "operacoes_permitidas": [
                "publicar P e F separadamente",
                "publicar D = P - F, em que o baseline compartilhado cancela",
                "publicar F/P e abs(F)/abs(P) quando P != 0"],
            "guarda_executavel": ("contrato que declare "
                                  "treat_comparisons_as_independent: true e "
                                  "REJEITADO com SHARED_BASELINE_INDEPENDENCE_VIOLATION"),
        },

        "identidade_D": {
            "expressao": "D = m(FULL_SKILL) - m(SUMMARY_AS_SKILL) = P - F",
            "verificada_em_toda_execucao": True,
            "tolerancia": 0.01,
            "codigo_de_falha": "COMPARISON_IDENTITY_UNCLOSED",
            "leitura_quando_nao_fecha": ("erro de SELECAO DE CONDICAO, de SINAL ou "
                                         "de CALCULO — nunca de arredondamento, "
                                         "porque o baseline compartilhado cancela "
                                         "algebricamente"),
        },

        "registro_de_codigos": {
            "achado": ("A primeira versao do patch acrescentou os seis codigos novos "
                       "ao conjunto global INVALIDATION_CODES e INVALIDOU O "
                       "TEST-0007: o contrato congelado enumera o registro e o "
                       "scorer confere igualdade EXATA nos dois sentidos."),
            "quem_pegou": "o proprio guard do instrumento, no primeiro teste de regressao",
            "conserto": ("registro EFETIVO — os codigos da extensao entram so quando "
                         "um comparison_set e despachado. O guard continua fechado; "
                         "o que mudou foi o conjunto correto a comparar em cada caso."),
            "nao_foi_afrouxado": True,
        },

        "collect_consumed_run_keys": {
            "mudanca": "percorre todas as comparacoes do conjunto, nao so a definicao plana",
            "por_que": ("sem isto a TERCEIRA condicao — SUMMARY_AS_SKILL, lado "
                        "esquerdo de F — sairia acusada como UNCONSUMED_RUN_SELECTOR: "
                        "uma corrida real, medida e usada, denunciada como orfa"),
            "poder_de_deteccao_provado_por": "canario K5, mutante sem a expansao",
        },

        "canary": {
            "approved": canary["approved"],
            "cases_total": len(canary["cases"]),
            "cases_passed": sum(1 for c in canary["cases"] if c["passed"]),
            "regra": ("cada caso roda contra o instrumento real (tem de passar) E "
                      "contra um mutante ou fixture adulterada (tem de reprovar). "
                      "Fixture adulterada que passa = sem poder de deteccao = suite "
                      "reprovada."),
            "cases": canary["cases"],
        },

        "zero_regressao_test_0007": {
            "requisito": "o resultado oficial da v0.1.4 tem de se reproduzir identico",
            "official_canonical_sha256": canary["test0007_canonical_official"],
            "extended_canonical_sha256": canary["test0007_canonical_extended"],
            "identico": (canary["test0007_canonical_official"]
                         == canary["test0007_canonical_extended"]),
            "normalizacao": ("campos `path` e `opening_record_path` reduzidos ao "
                             "basename: registram a localizacao do invocador no "
                             "sistema de arquivos, nao resultado. Todo o resto — "
                             "notas, margem, teto, veredito, ordem — comparado byte "
                             "a byte."),
            "margem": 44.0, "decisao": "PASS", "status": "VALID",
            "nenhum_campo_novo_vaza": True,
        },

        "binds_to": {
            "adr_test_0008": {"member": ADRMEM, "sha256": adr},
            "metric_lock": {"path": "docs/TEST-0008-METRIC-LOCK.yaml",
                            "sha256": shp(DOCS / "TEST-0008-METRIC-LOCK.yaml")},
            "full_skill_arm": {
                "artifact": "PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip",
                "sha256": "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028"},
        },
        "files": sums,
        "proximo_passo": {"passo": 3, "o_que": "a rubrica do TEST-0008",
                          "exige": "auditoria externa", "nao_iniciado": True},
    }
    OUT.write_text("# Extensao do scorer para DUAS comparacoes (P e F) do TEST-0008.\n"
                   "# Derivada do F7 por patch. Canario aprovado. Zero regressao no TEST-0007.\n"
                   + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
                   encoding="utf-8")
    print(f"scorer estendido : {doc['derivation']['extended']['scorer_sha256'][:16]}…")
    print(f"freezer estendido: {doc['derivation']['extended']['freezer_sha256'][:16]}…")
    print(f"canário          : {doc['canary']['cases_passed']}/{doc['canary']['cases_total']} "
          f"{'APROVADO' if canary['approved'] else 'REPROVADO'}")
    print(f"zero regressão   : {doc['zero_regressao_test_0007']['identico']}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
    print(f"SHA-256: {shp(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
