# runners-p003/ — REGISTRO HISTÓRICO. Não editar.

Publicado em 2026-08-15. Destino: `Course-to-Skill-Claude/runners-p003/LEIA-ME.md`

## O que são estes arquivos

Os 12 runners que executaram o **PILOT-003**, publicados pela Lenovo em
2026-08-13 e conferidos aqui **12/12** contra o
`RUNNERS-HASHES-EXT4-LENOVO-20260813.txt`.

São a única amarra que resta entre o PILOT-003 e um código conhecido. O
`COMPILATION_MANIFEST` do P003 **nomeia** o runner (`p003_pass2_ckpt.py`) mas
**não pina hash dele** — a conferência possível foi contra o manifesto da
Lenovo, e ela passou.

## Rodaram em `claude-opus-5`

Os quatro que chamam a API estão em Opus 5:

| arquivo | linha |
|---|---|
| `p003_pass1.py` | 63 |
| `p003_apply_step1.py` | 54 |
| `p003_apply_step2.py` | 40 |
| `p003_apply_step3.py` | 63 |

## NÃO EDITAR — decisão de Alexandre/auditor, 2026-08-15

Trocar o modelo aqui destruiria a proveniência: o hash deixaria de bater com o
manifesto da Lenovo, e o PILOT-003 perderia a única ligação verificável com o
código que o produziu. **História intacta.**

## Reuso: derivar dos runners do PILOT-004

A linhagem viva está em `pilots/PILOT-004/runners/`, já em **`claude-sonnet-5`**
(ver `FREEZE-RECORD-v0.2.2` do compiler-v2). Quem precisar de um runner novo
**deriva dali**, não daqui.

Os runners do P004 são eles próprios cópias declaradas destes, com diff mínimo
registrado em `pilots/PILOT-004/00_SOURCE/RUNNER-DIFF-DECLARADO.json` — 7
substituições no PASS 1 e 8 no PASS 2, só caminhos, ids e pinos. Nenhuma lógica,
prompt, schema, `WIN` ou `TARGET` alterado.

## Nota de comparabilidade

Qualquer número de evidência do PILOT-003 foi produzido em **Opus 5**. Comparar
com extrações futuras em **Sonnet 5** exige a nota de comparabilidade registrada
no `FREEZE-RECORD-v0.2.2`.

## Relacionados

- `RUNNERS-HASHES-EXT4-LENOVO-20260813.txt` — manifesto da Lenovo, 12/12 conferido
- `pilots/PILOT-004/00_SOURCE/RUNNER-DIFF-DECLARADO.json` — o diff declarado
- `compiler-v2-v0.2.2/FREEZE-RECORD-v0.2.2.yaml` — troca de modelo e nota de comparabilidade
