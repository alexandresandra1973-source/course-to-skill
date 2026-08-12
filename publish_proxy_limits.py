#!/usr/bin/env python3
"""Correção do registro do (C3) + estado de repouso declarado ANTES do corte."""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import yaml
DRIVE=Path("/mnt/g/Meu Drive/Chat GPT"); CL=DRIVE/"Course-to-Skill-Claude"
DOCS=CL/"docs"; OUT=DOCS/"PROXY-LIMITS-AND-RESTING-STATE.yaml"
PRED=DOCS/"PREDICTION-COMPILER-V2.yaml"; RAT=DOCS/"PREDICTION-COMPILER-V2-BAND-RATIFICATION.yaml"
COR=DOCS/"PREDICTION-COMPILER-V2-BAND-CORRECTION.yaml"
ADR=CL/"pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

doc={"schema_version":"0.1.0","artifact_id":"PROXY-LIMITS-AND-RESTING-STATE",
 "artifact_status":"REGISTRADO_ANTES_DO_EXPERIMENTO_DE_CORTE",
 "registered_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
 "generator":Path(__file__).name,
 "nature":{"additive_only":True,"changes_the_gate":False,"changes_the_compiler":False},
 "binds_to":{"prediction":{"path":str(PRED.relative_to(DRIVE)),"sha256":sha(PRED)},
  "band_ratification":{"path":str(RAT.relative_to(DRIVE)),"sha256":sha(RAT)},
  "band_correction":{"path":str(COR.relative_to(DRIVE)),"sha256":sha(COR)},
  "adr":{"path":str(ADR.relative_to(DRIVE)),"sha256":sha(ADR)}},

 "correcao_do_registro_do_C3":{
  "o_que_eu_escrevi":("que o (C3) refutou a hipótese de que o residual vem da FONTE"),
  "o_que_o_C3_de_fato_refutou":(
   "a razão TIPO/TOKEN como PROXY de densidade da fonte. O TTR não prediz yield "
   "dentro de nenhum dos dois pilotos, então ele não serve como medida. Isso "
   "não diz nada sobre a propriedade que ele tentava medir."),
  "estado_correto_da_hipotese":{
   "hipotese":("os dois corpora diferem em densidade de METODOLOGIA EXTRAÍVEL "
     "por segundo de fonte"),
   "estado":"VIVA E NAO MEDIDA",
   "por_que_importa":("tratá-la como refutada fecharia por engano a explicação "
     "mais plausível do residual")},
  "padrao_que_isto_revela":{
   "enunciado":("Proxy mecânico para propriedade semântica falha "
     "sistematicamente neste projeto."),
   "ocorrencias":[
    {"proxy":"regex de densidade de decisão","resultado":"REPROVADO no canário"},
    {"proxy":"entidade nomeada no aviso claim×literal",
     "resultado":"aposentado — 46% de disparo, zero verdadeiro positivo além do rótulo do modelo"},
    {"proxy":"razão tipo/token como densidade de metodologia",
     "resultado":"correlação +0,003 dentro do piloto; não mede o que pretendia"}],
   "consequencia_metodologica":(
    "Um quarto proxy não deve ser tentado. O que mediria a hipótese é leitura "
    "estrutural ENUMERADA dos dois corpora — cara, manual e fora do escopo "
    "destes pilotos.")}},

 "estado_de_repouso_declarado":{
  "quando_se_aplica":("se o experimento de corte confirmar o teto por chamada "
    "em ~1,18 e AINDA sobrar residual na razão de yield"),
  "desfecho":("CONSERTO_PARCIAL com residual NOMEADO e declaradamente NÃO "
    "MEDIDO é desfecho legítimo."),
  "o_que_NAO_sera_feito":("caçar o residual com um quarto proxy mecânico"),
  "o_que_fecharia":("leitura estrutural enumerada dos dois corpora — cara, "
    "manual, fora do escopo destes pilotos"),
  "por_que_declarar_antes":(
   "Declarado ANTES do resultado para que aceitar o residual não medido seja "
   "decisão de escopo tomada com antecedência, e não racionalização de um "
   "número que decepcionou."),
  "status":"DECLARADO_ANTES_DO_RESULTADO"},

 "criterios_do_experimento_de_corte":{
  "segmento":"SEG-013 do PILOT-002, 218s",
  "desenho":"1 chamada com o segmento inteiro; 3 chamadas com terços contíguos",
  "previsao_quantitativa":"3^(1-0,846) = 3^0,154 ≈ 1,18",
  "confirma":">= 1,15 de ganho (partes somadas ÷ inteiro)",
  "refuta":"<= 1,05",
  "inconclusivo":"entre 1,05 e 1,15 com n=1 segmento",
  "controle_obrigatorio":("o ganho é reportado ANTES e DEPOIS da deduplicação; "
    "ganho que só existe antes é duplicação de fronteira, não teto"),
  "expoente_medido":{"com_fantasmas":0.608,"sem_fantasmas":0.846,
    "usado":0.846,"nota":("metade da curvatura era artefato dos segmentos "
      "fantasma SEG-008 e SEG-021")}},
 "status":"REGISTRADO_ANTES_DO_EXPERIMENTO_DE_CORTE"}

OUT.write_text("# Correção do registro do (C3) + estado de repouso declarado ANTES do corte.\n"
 +yaml.safe_dump(doc,allow_unicode=True,sort_keys=False,width=100),encoding="utf-8")
print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
print(f"SHA-256: {sha(OUT)}")
