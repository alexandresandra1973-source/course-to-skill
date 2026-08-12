#!/usr/bin/env python3
"""Pendência pós-pilotos: a regra de fidelidade escapa corrupção de uma letra.

READ-ONLY. Publica só em docs/. NÃO altera o compilador — mudá-lo entre os dois
pilotos quebraria a trava de comparabilidade da §12 da ADR.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import yaml

DRIVE=Path("/mnt/g/Meu Drive/Chat GPT"); CLAUDE=DRIVE/"Course-to-Skill-Claude"
DOCS=CLAUDE/"docs"; OUT=DOCS/"FIDELITY-RULE-PENDENCY.yaml"
EV=CLAUDE/"pilots/PILOT-001-v2/EVIDENCE.jsonl"
EV2=CLAUDE/"pilots/PILOT-002-v2/EVIDENCE.jsonl"
SUPERSEDED="6e0588ac26e160f2a7fcec7e2e6cb1a66d8f3a4c8a4b807421dee2bdfea7d9c1"
MAN=CLAUDE/"pilots/PILOT-001-v2/COMPILATION_MANIFEST.yaml"
ADR=CLAUDE/"pilots/PILOT-002/adr/ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE.md"
FREEZE=CLAUDE/"compiler-v2/FREEZE-RECORD.yaml"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

rows=[json.loads(l) for l in EV.read_text(encoding="utf-8").splitlines() if l.strip()]
ev43=next((r for r in rows if r["evidence_id"]=="EV-0043"),None)

doc={
 "schema_version":"0.1.0","artifact_id":"FIDELITY-RULE-PENDENCY",
 "artifact_status":"PENDENCIA_POS_PILOTOS",
 "registered_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
 "generator":Path(__file__).name,
 "nature":{"additive_only":True,"changes_the_compiler":False,
   "statement":("Registro de pendência. NÃO altera o compilador nem o prompt: "
     "mudá-los entre PILOT-001 e PILOT-002 quebraria a trava de comparabilidade "
     "da §12 da ADR, que exige os dois pilotos sob a MESMA versão congelada.")},
 "binds_to":{
   "evidence_pilot001_v2":{"path":str(EV.relative_to(DRIVE)),"sha256":sha(EV)},
   "manifest_pilot001_v2":{"path":str(MAN.relative_to(DRIVE)),"sha256":sha(MAN)},
   "adr":{"path":str(ADR.relative_to(DRIVE)),"sha256":sha(ADR)},
   "compiler_v2_freeze":{"path":str(FREEZE.relative_to(DRIVE)),"sha256":sha(FREEZE)}},
 "supersedes":{"versao_anterior_sha256":SUPERSEDED,
   "o_que_mudou":("Acrescentado o achado do PILOT-002 (cluster Vercel) e a "
     "leitura corrigida da falha: INCONSISTÊNCIA, não falha sistemática. "
     "Nenhuma conclusão anterior foi removida.")},
 "achado_confirmado":{
   "classe":"CORRUPCAO_DA_FONTE_PROPAGADA_COMO_SOURCE_EXPLICIT",
   "gravidade":("A mais grave que este compilador pode cometer: o registro "
     "afirma como fonte explícita algo que a fonte literalmente não diz."),
   "caso":{"evidence_id":"EV-0043",
     "corrupcao":"a fonte diz 'Gardner'; a claim afirma 'Gartner'",
     "similaridade":0.86,
     "epistemic_status":ev43["epistemic_status"] if ev43 else None,
     "claim":ev43["claim"] if ev43 else None,
     "quote":ev43["source_excerpt"]["quote"] if ev43 else None},
   "taxa_medida":{"corrupcoes_detectadas":3,"em_evidencias":len(rows),
     "rotuladas_MODEL_INFERENCE":2,"propagadas_como_SOURCE_EXPLICIT":1,
     "cobertura_da_regra":"2 de 3"}},
 "por_que_a_regra_escapou":(
   "A regra de fidelidade pede MODEL_INFERENCE quando a claim corrige o "
   "literal. Ela pegou a negação perdida (EV-0026) e o nome grosseiramente "
   "corrompido (Chad GBT → ChatGPT), e escapou a diferença de UMA LETRA num "
   "nome próprio. É plausível que o modelo nem tenha registrado 'Gardner' como "
   "erro — leu, reconheceu a entidade e escreveu o nome certo sem perceber que "
   "estava corrigindo."),
 "conserto_proposto_NAO_APLICADO":{
   "onde":"prompt do extractor, seção 'Fidelidade ao literal'",
   "o_que":("instrução explícita para nome próprio: se o nome na fonte difere "
     "do nome conhecido por qualquer quantidade de caracteres, isso é correção "
     "e exige MODEL_INFERENCE — inclusive uma letra"),
   "verificador_complementar":("a varredura mecânica de nome corrompido já "
     "existe e pegou o caso; pode virar aviso no rastro, com a âncora de "
     "capitalização que a torna robusta entre idiomas"),
   "por_que_NAO_agora":("mudar o prompt muda o comportamento do extractor, e a "
     "§12 exige que os dois pilotos rodem sob a mesma versão congelada. "
     "Aplicar agora invalidaria a comparação PILOT-001 × PILOT-002, que é o "
     "objeto do experimento."),
   "quando":"depois de os dois pilotos terminarem sob o congelamento atual"},
 "achado_pilot002_cluster_vercel":{
   "o_que":("A transcrição erra o MESMO nome de produto de quatro maneiras — "
     "Versel, Versell, Verscell (2×) — e a claim escreve 'Vercel' nas quatro, "
     "sem rotular nenhuma como MODEL_INFERENCE."),
   "casos":["EV-0289 Vercel ← Versel","EV-0356 Vercel ← Verscell",
            "EV-0358 Vercel ← Versell","EV-0372 Vercel ← Verscell"],
   "cobertura_da_regra_no_pilot002":"7 de 11 corrupções de nome rotuladas",
   "leitura_corrigida":(
     "Isto é INCONSISTÊNCIA, não falha sistemática. Uma falha sistemática — a "
     "regra nunca pega corrupção de nome — seria previsível e contornável: "
     "bastaria varrer todas. O que se observa é pior para previsibilidade: o "
     "MESMO tipo de item, o mesmo nome de produto no mesmo corpus, às vezes é "
     "rotulado e às vezes não, sem critério visível. Quem consome o corpus não "
     "tem como saber quais registros SOURCE_EXPLICIT são confiáveis, porque a "
     "fronteira não é uma propriedade do item."),
   "taxa_estavel_entre_corpora":{"PILOT-001-v2":"1/149 = 0,7%",
     "PILOT-002-v2":"4/448 = 0,9%",
     "leitura":("A taxa de dano é estável entre corpora de tamanho e domínio "
       "muito diferentes, o que sugere propriedade do mecanismo e não do texto.")}},
 "risco_aceito_conscientemente":(
   "O PILOT-002 roda com a mesma lacuna. Se houver corrupção de nome próprio "
   "no corpus dele, ela pode sair como SOURCE_EXPLICIT. A varredura mecânica "
   "roda sobre o resultado e mede o tamanho do problema — o que não se pode é "
   "consertar no meio."),
 "status":"PENDENCIA_POS_PILOTOS","compilador_alterado":False}

OUT.write_text("# PENDÊNCIA PÓS-PILOTOS: regra de fidelidade escapa corrupção de uma letra.\n"
 "# NÃO altera o compilador — a §12 exige os dois pilotos sob o mesmo congelamento.\n"
 +yaml.safe_dump(doc,allow_unicode=True,sort_keys=False,width=100),encoding="utf-8")
print(f"caso: EV-0043 · rotulado {ev43['epistemic_status'] if ev43 else '?'}")
print(f"taxa: 2 de 3 corrupções pegas pela regra")
print(f"publicado: {OUT.name} ({OUT.stat().st_size} B)")
print(f"SHA-256: {sha(OUT)}")
