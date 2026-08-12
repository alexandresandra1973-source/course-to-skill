#!/usr/bin/env python3
"""(C4) REFEITO com o expoente CAUSAL k=0,631 derivado do experimento de corte.

Zero chamadas de modelo. READ-ONLY. Não escreve em pilots/, não toca o
compilador congelado. §12 intacta.

Desenho, idêntico ao (C4) original — só o k muda:
  ajusta y = A·dur^k nos 41 segmentos do PILOT-002 e PREVÊ, FORA DA AMOSTRA,
  o yield/segundo agregado do PILOT-001 (observado 149/885 = 0,16836).

Duas constantes A, ambas reportadas:
  A_obs : reajustada nos dados do PILOT-002 com k travado em 0,631
  A_exp : recalibrada pelo experimento de corte — SEG-013 inteiro, 22/218^k

Critério declarado ANTES (pelo revisor):
  dentro de ~10% de 0,16836  → residual FECHA
  30%+ abaixo                → residual é real, repouso vale, paramos
"""
from __future__ import annotations
import json, math, yaml
from pathlib import Path
DRIVE=Path("/mnt/g/Meu Drive/Chat GPT"); CL=DRIVE/"Course-to-Skill-Claude"
P1=CL/"pilots/PILOT-001-v2"; P2=CL/"pilots/PILOT-002-v2"
# janelas removidas do L0 do PILOT-002 (held-out). Segmento que as cruza é FANTASMA.
LOCKS=[(708,908),(2674,3000)]
K_OBS=0.846      # ajuste observacional, sem fantasmas — CONFUNDIDO
K_EXP=0.631      # causal: 3^(1-k)=1.500 -> 1-k=ln1.5/ln3
OBS_P1=149/885   # yield/segundo agregado observado do PILOT-001

def hh(t):
    q=[int(x) for x in str(t).split(":")]
    return q[0]*3600+q[1]*60+q[2] if len(q)==3 else q[0]*60+q[1]
def segs(d):
    tm=yaml.safe_load((d/"temporal-map.yaml").read_text(encoding="utf-8"))["temporal_map"]
    ev=[json.loads(l) for l in (d/"EVIDENCE.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    n={}
    for e in ev: n[e["segment_id"]]=n.get(e["segment_id"],0)+1
    return [{"id":s["segment_id"],"dur":hh(s["end"])-hh(s["start"]),
             "a":hh(s["start"]),"b":hh(s["end"]),"y":n.get(s["segment_id"],0)} for s in tm]
def ghost(s): return any(s["a"]<b and a<s["b"] for a,b in LOCKS)

s1=segs(P1); s2=segs(P2)
s2c=[s for s in s2 if not ghost(s)]
print("="*74); print("(C4) REFEITO — expoente causal do experimento de corte"); print("="*74)
print(f"PILOT-001: {len(s1)} segs · soma {sum(s['dur'] for s in s1)}s · "
      f"dur min/med/max {min(s['dur'] for s in s1)}/{sum(s['dur'] for s in s1)/len(s1):.0f}/{max(s['dur'] for s in s1)}s")
print(f"PILOT-002: {len(s2)} segs ({len(s2c)} sem fantasmas) · soma {sum(s['dur'] for s in s2c)}s · "
      f"dur min/med/max {min(s['dur'] for s in s2c)}/{sum(s['dur'] for s in s2c)/len(s2c):.0f}/{max(s['dur'] for s in s2c)}s")
# desvio-padrão da duração: é ele que a concavidade penaliza (Jensen)
for lbl,S in (("PILOT-001",s1),("PILOT-002",s2c)):
    m=sum(s["dur"] for s in S)/len(S); sd=math.sqrt(sum((s["dur"]-m)**2 for s in S)/len(S))
    print(f"  {lbl}: dp(duração)={sd:.1f}s  CV={sd/m:.3f}")

def fitA(S,k):  # mínimos quadrados em log com inclinação TRAVADA em k
    pts=[s for s in S if s["y"]>0]
    return math.exp(sum(math.log(s["y"])-k*math.log(s["dur"]) for s in pts)/len(pts))
def fitAk(S):   # ajuste livre, para conferir que reproduzo o k original
    pts=[s for s in S if s["y"]>0]; n=len(pts)
    lx=[math.log(s["dur"]) for s in pts]; ly=[math.log(s["y"]) for s in pts]
    mx,my=sum(lx)/n,sum(ly)/n
    k=sum((a-mx)*(b-my) for a,b in zip(lx,ly))/sum((a-mx)**2 for a in lx)
    return math.exp(my-k*mx),k
def predict(S,A,k): return sum(A*s["dur"]**k for s in S)/sum(s["dur"] for s in S)

A_free,k_free=fitAk(s2c)
print(f"\nconferência do ajuste livre no PILOT-002 sem fantasmas: "
      f"k={k_free:.3f} (o (C4) original usou {K_OBS})")
A_obs=fitA(s2c,K_EXP)
A_exp=22/218**K_EXP
print(f"\nconstantes A com k travado em {K_EXP}:")
print(f"  A_obs (reajustada nos 41 do PILOT-002) : {A_obs:.5f}")
print(f"  A_exp (SEG-013 inteiro, 22/218^k)      : {A_exp:.5f}   razão {A_exp/A_obs:.3f}×")
print("\n"+"="*74); print("PREVISÃO FORA DA AMOSTRA — yield/segundo agregado do PILOT-001")
print("="*74)
print(f"OBSERVADO: 149/885 = {OBS_P1:.5f}\n")
rows=[("k=0,846 (observacional, CONFUNDIDO)",fitA(s2c,K_OBS),K_OBS,"A_obs"),
      ("k=0,631 causal · A_obs",A_obs,K_EXP,"A_obs"),
      ("k=0,631 causal · A_exp",A_exp,K_EXP,"A_exp")]
for lbl,A,k,_ in rows:
    p=predict(s1,A,k); d=(p-OBS_P1)/OBS_P1
    ver=("FECHA (dentro de 10%)" if abs(d)<=0.10 else
         "NAO FECHA — 30%+ abaixo" if d<=-0.30 else
         "NAO FECHA — 30%+ acima" if d>=0.30 else "zona intermediária (10–30%)")
    print(f"  {lbl:<38} previsto {p:.5f}   {d:+6.1%}   {ver}")
# controle: o mesmo ajuste reproduz o PILOT-002 dentro da amostra?
print(f"\ncontrole dentro da amostra (PILOT-002, observado "
      f"{sum(s['y'] for s in s2c)/sum(s['dur'] for s in s2c):.5f}):")
for lbl,A,k,_ in rows:
    print(f"  {lbl:<38} previsto {predict(s2c,A,k):.5f}")

# ---------------------------------------------------------------- diagnóstico
print("\n"+"="*74); print("DIAGNÓSTICO: quanto de diferença ENTRE PILOTOS a concavidade consegue gerar")
print("="*74)
obs2=sum(s['y'] for s in s2c)/sum(s['dur'] for s in s2c)
print(f"razão OBSERVADA  P1/P2 = {OBS_P1:.5f}/{obs2:.5f} = {OBS_P1/obs2:.4f}")
print("razão PREVISTA pela concavidade (A cancela — só a distribuição de duração importa):")
for k in (1.0,0.846,0.631,0.4,0.2,0.0,-0.5,-1.0,-2.0):
    r=predict(s1,1.0,k)/predict(s2c,1.0,k)
    print(f"  k={k:>5.3f}  →  {r:.4f}")
lo,hi=-40.0,1.0
for _ in range(200):
    mid=(lo+hi)/2
    if predict(s1,1.0,mid)/predict(s2c,1.0,mid) < OBS_P1/obs2: hi=mid
    else: lo=mid
print(f"\nk necessário para a concavidade sozinha explicar a razão observada: {(lo+hi)/2:.3f}")
print("\nsegmentos FANTASMA excluídos:")
for s in s2:
    if ghost(s): print(f"  {s['id']}  {s['a']}–{s['b']}s ({s['dur']}s)  yield {s['y']}")
top=sorted(s2c,key=lambda s:-s['dur'])[:3]
print(f"maiores durações REAIS do PILOT-002: {[(s['id'],s['dur']) for s in top]}")
