#!/usr/bin/env python3
"""Achado dos SEGMENTOS FANTASMA + cobertura corrigida do PILOT-002.

READ-ONLY. Publica só em docs/. Recomputar cobertura excluindo território
fantasma é MEDIÇÃO, não mudança de compilador.
"""
from __future__ import annotations
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).parent))
from cts import coverage as C

DRIVE=Path("/mnt/g/Meu Drive/Chat GPT"); CL=DRIVE/"Course-to-Skill-Claude"
DOCS=CL/"docs"; OUT=DOCS/"GHOST-SEGMENTS-AND-CORRECTED-COVERAGE.yaml"
RUN=CL/"pilots/PILOT-002-v2"; MAN=RUN/"COMPILATION_MANIFEST.yaml"; EV=RUN/"EVIDENCE.jsonl"
LOCK=DOCS/"HELDOUT-LOCK-PILOT-002.yaml"; RESID=DOCS/"HELDOUT-RESIDUE-ADDENDUM-PILOT-002.yaml"
TMAP=CL/"pilots/PILOT-002/02_MEASUREMENTS/PASS1-TENDENCY-RERUN/temporal-map(1).yaml"
ADR=CL/"pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

rows=[json.loads(l) for l in EV.read_text(encoding="utf-8").splitlines() if l.strip()]
cits=[C.Citation(r["source_excerpt"]["span"]["start_s"],r["source_excerpt"]["span"]["end_s"],"e",r["evidence_id"]) for r in rows]
EXT=4384; LOCKW=[(715,908),(2680,3000)]; MARKW=[(708,908),(2674,3000)]
def carve(bl,holes):
    out=[]
    for b in bl:
        pcs=[(b.start,b.end)]
        for h0,h1 in holes:
            nx=[]
            for p0,p1 in pcs:
                if h1<=p0 or h0>=p1: nx.append((p0,p1)); continue
                if p0<h0: nx.append((p0,h0))
                if h1<p1: nx.append((h1,p1))
            pcs=nx
        out+=[C.Block(a,b_) for a,b_ in pcs if b_>a]
    return out
u=C.merge(cits); bruto=sum(b.dur for b in u)
cl=sum(b.dur for b in carve(u,LOCKW)); cm=sum(b.dur for b in carve(u,MARKW))
def ev(i): return next(r for r in rows if r["evidence_id"]==i)
e79,e264=ev("EV-0079"),ev("EV-0264")
seg8=[r for r in rows if r["segment_id"]=="SEG-008"]; seg21=[r for r in rows if r["segment_id"]=="SEG-021"]

doc={"schema_version":"0.1.0","artifact_id":"GHOST-SEGMENTS-AND-CORRECTED-COVERAGE",
 "artifact_status":"ACHADO_E_MEDICAO_PUBLICADOS",
 "published_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
 "generator":Path(__file__).name,
 "nature":{"additive_only":True,"changes_the_compiler":False,"changes_the_gate":False,
  "statement":("Achado estrutural mais recomputação de métrica. Recomputar a "
   "cobertura excluindo território fantasma é MEDIÇÃO sobre o resultado "
   "existente; não altera o compilador, o portão nem a rodada.")},
 "binds_to":{
  "heldout_lock":{"path":str(LOCK.relative_to(DRIVE)),"sha256":sha(LOCK)},
  "residue_addendum":{"path":str(RESID.relative_to(DRIVE)),"sha256":sha(RESID)},
  "temporal_map":{"path":str(TMAP.relative_to(DRIVE)),"sha256":sha(TMAP)},
  "manifest":{"path":str(MAN.relative_to(DRIVE)),"sha256":sha(MAN)},
  "evidence":{"path":str(EV.relative_to(DRIVE)),"sha256":sha(EV)},
  "adr":{"path":str(ADR.relative_to(DRIVE)),"sha256":sha(ADR)}},

 "o_mecanismo":{"nome":"SEGMENTO FANTASMA",
  "cadeia":["corte de held-out por span",
   "o TÍTULO de seção sobrevive: não tem marca de tempo, logo o corte por span não o alcança",
   "o PASS 1 lê o título como fronteira de tópico",
   "cria um segmento cujo span cobre território REMOVIDO",
   "o extractor recebe um título que NOMEIA o assunto removido, com pouco ou nenhum texto"],
  "novidade_em_relacao_ao_aditivo_de_residuo":(
   "O aditivo declarou que o título nomeia o assunto retirado — consequência de "
   "VOCABULÁRIO. Não previu que o título, por ser fronteira de tópico sem marca, "
   "FABRICA UM SEGMENTO sobre território inexistente — consequência de "
   "SEGMENTAÇÃO. É estrutural: qualquer piloto futuro com corte por span reproduz."),
  "reprodutibilidade":"estrutural, não acidente deste corpus"},

 "caso_1_SEG_021_VALIDACAO":{
  "veredito":"VALIDACAO_DA_RESISTENCIA_A_INVENCAO",
  "span_declarado_s":[2674,3000],"duracao_declarada_s":326,
  "o_que_o_extractor_recebeu":{"chars":170,"marcas":1,"blocos_de_fala":2,
   "conteudo":("uma marca, a deixa truncada 'The next we're going to take a look "
    "at is our context. Now what is' e o título sobrevivente '## Managing Your "
    "Context Window and Token Usage'")},
  "evidencias_produzidas":len(seg21),
  "a_evidencia":{"id":e264["evidence_id"],"span_s":[e264["source_excerpt"]["span"]["start_s"],e264["source_excerpt"]["span"]["end_s"]],
   "epistemic_status":e264["epistemic_status"],"claim":e264["claim"],
   "quote":e264["source_excerpt"]["quote"]},
  "por_que_e_o_caso_mais_dificil":(
   "O título NOMEIA o tópico removido; a deixa termina no meio da pergunta "
   "('Now what is'); e o conteúdo do held-out — /compact, /clear, limiar de 50%, "
   "context rot — é conhecimento comum de modelo. Todos os ingredientes da "
   "invenção estavam presentes e sinalizados."),
  "o_que_o_compilador_fez":(
   "Extraiu apenas a frase de transição que a fonte literalmente contém, "
   "declarou span de 1 SEGUNDO em vez dos 326s do segmento, e não afirmou nada "
   "sobre janela de contexto."),
  "leitura":("Resistência a invenção funcionando no caso mais difícil "
   "construível. É evidência mais forte que qualquer número de cobertura, "
   "porque cobertura mede quanto foi alcançado e isto mede o que NÃO foi "
   "inventado quando inventar era fácil e convidativo.")},

 "caso_2_SEG_008_CONTABILIDADE":{
  "veredito":"ARTEFATO_DE_CONTABILIDADE_NAO_VAZAMENTO",
  "span_declarado_s":[708,944],"evidencias_produzidas":len(seg8),
  "a_evidencia_problematica":{"id":e79["evidence_id"],
   "span_s":[e79["source_excerpt"]["span"]["start_s"],e79["source_excerpt"]["span"]["end_s"]],
   "epistemic_status":e79["epistemic_status"],"claim":e79["claim"],
   "quote":e79["source_excerpt"]["quote"]},
  "classificacao_do_revisor":"ARTEFATO DE SEGMENTAÇÃO, NÃO VAZAMENTO",
  "razoes_registradas":[
   "o conteúdo já era resíduo DECLARADO no aditivo, que por isso converteu BC-001/003/004 de nomear para semântica",
   "o rótulo MODEL_INFERENCE está correto",
   "a quote resolve porque o título está no corpus de treino",
   "nenhuma informação nova atravessou o corte"],
  "por_que_refazer_nao_conserta":(
   "O título continuaria no corpus e só o span mudaria. Clipar span é mudança "
   "de compilador, proibida entre os dois pilotos pela §12."),
  "o_dano_real":"de CONTABILIDADE: território inexistente entra na união declarada"},

 "cobertura":{
  "uniao_declarada_bruta_s":bruto,
  "apos_carve_janelas_do_lock_s":cl,"cobertura_reportada_pct":round(100*cl/EXT,2),
  "apos_carve_janelas_da_marca_s":cm,"cobertura_CORRIGIDA_pct":round(100*cm/EXT,2),
  "territorio_fantasma_remanescente_s":cl-cm,
  "inflacao_pontos_percentuais":round(100*(cl-cm)/EXT,2),
  "nota_sobre_magnitude":(
   "O portão JÁ fazia carve das janelas do lock, então a cobertura reportada já "
   "excluía 715–908 e 2680–3000. O fantasma remanescente é apenas a faixa entre "
   "a marca que abre o corte e o início declarado dele. Uma estimativa anterior "
   "de ~4,6 pontos percentuais estava errada por um fator de 25: ela presumiu o "
   "comportamento da métrica em vez de ler o código."),
  "qual_entra_na_comparacao":"A CORRIGIDA",
  "por_que":(
   "O PILOT-001 não tem held-out e portanto não tem span fantasma. Usar a "
   "inflada favoreceria o PILOT-002. A diferença é pequena, mas o critério não "
   "depende do tamanho: comparar números computados de formas diferentes é "
   "errado independentemente da magnitude."),
  "piso":0.735,"corrigida_supera_o_piso":bool(100*cm/EXT>73.5)},

 "consequencia_para_pilotos_futuros":{
  "regra":("Todo piloto com corte de held-out por span vai gerar segmentos "
   "fantasma sobre as janelas cortadas, porque o título sobrevive ao corte."),
  "conserto_estrutural_possivel":[
   "clipar os spans dos segmentos às janelas do corpus de treino no PASS 1",
   "ou remover o título junto com a seção, o que exigiria cortar além do span declarado",
   "ou declarar as janelas ao extractor para que ele não emita span sobre elas"],
  "estado":"NENHUM APLICADO — todos são mudança de compilador, proibida pela §12 entre os pilotos",
  "quando":"depois de os dois pilotos rodarem sob o mesmo congelamento"},

 "status":"ACHADO_E_MEDICAO_PUBLICADOS","compilador_alterado":False,"portao_alterado":False}

OUT.write_text("# SEGMENTOS FANTASMA + cobertura corrigida do PILOT-002.\n"
 "# Amarrado ao holdout lock e ao aditivo de resíduo. NÃO altera compilador nem portão.\n"
 +yaml.safe_dump(doc,allow_unicode=True,sort_keys=False,width=100),encoding="utf-8")
print(f"SEG-021: {len(seg21)} evidência(s) · span declarado 326s · span usado 1s → VALIDAÇÃO")
print(f"SEG-008: {len(seg8)} evidência(s) · EV-0079 span 708-908 → contabilidade")
print(f"cobertura reportada {100*cl/EXT:.2f}%  ·  CORRIGIDA {100*cm/EXT:.2f}%  ·  fantasma {cl-cm}s")
print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
print(f"SHA-256: {sha(OUT)}")
