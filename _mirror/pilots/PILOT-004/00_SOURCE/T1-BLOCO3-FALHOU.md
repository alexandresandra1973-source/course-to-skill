# T1 — BLOCO 3 · **FALHOU** (bloqueio real, 2 tentativas)

Noite de 14/08, bot-04. Nenhuma chamada de API gasta nesta tarefa.

## O bloqueio

O estágio evidência→Skill é do **compiler-s3**, e o
`compiler-s3/ctss/classify.py` — que faz exatamente a pré-classificação pelos 3
caminhos que o T1 exige **antes** de qualquer regra — não importa nesta máquina:

```
ModuleNotFoundError: No module named 'scan_source_corruption'
```

Ele faz, no topo do arquivo:

```python
sys.path.insert(0, "/home/mtx/course-to-skill-claude")
from scan_source_corruption import lost_negation, corrupted_name   # caminho P1
from detector_recall_fix import corrupted_name_lower               # caminho P2
```

Os dois módulos são da **Lenovo** e não estão no Drive. É o mesmo padrão do
`cts/` no BLOCO 2b, com outros dois arquivos.

### Tentativa 1
Rodar o canário do compiler-s3 em cópia local. Parou antes, em caminho `/mnt/g`
hard-coded apontando para `PILOT-002-v2/EVIDENCE.jsonl`.

### Tentativa 2
Importar `ctss.classify` direto. Falhou no `ModuleNotFoundError` acima.

Parei aqui, conforme R2 — nada de laço de retry.

## Falta também um terceiro insumo

`run_compile.py` lê `distance-lines-{PILOT}.json` de `/tmp/...` da Lenovo para
alimentar o caminho **P4** (`PARAPHRASE` — "sem distância medida da citação").
Esse arquivo não existe aqui e não é derivável do que está publicado.

Ou seja: dos 4 caminhos da pré-classificação, **P1, P2 e P4 estão indisponíveis**.
Só o **P3 (ALIAS)** é local — é o dicionário dentro do próprio `classify.py`,
onde entrariam os alias `Suitech` e `Metaed` que o T1 manda declarar.

## Por que não reimplementei os detectores — R4

Reescrever `lost_negation`, `corrupted_name` e `corrupted_name_lower` seria
**trocar o instrumento de medição** por um que eu escrevi, sem nunca ter visto o
original. As classes `TRANSCRIPTION_CORRECTION` e `PARAPHRASE` do P004 sairiam
de um detector diferente do que produziu as do P002 e do P003
(`TRANSCRIPTION_CORRECTION: 47`, `PARAPHRASE: 59` no manifesto do P003-v2), e
qualquer comparação entre pilotos ficaria contaminada em silêncio.

Isso é mudança de critério de medição. **R4: PENDENTE-ALEXANDRE.**

## Uma imprecisão na instrução, que vale corrigir antes de amanhã

O T1 diz "compilar as 134 evidências com o compiler selado no v0.2.1". O v0.2.1
que selei na noite anterior é o **compiler-v2**, que faz PASS 1 e PASS 2
(segmentação e extração de evidência). Ele **não** faz evidência→regra.

Quem faz é o **compiler-s3/0.1.0**, conforme o próprio
`pilots/PILOT-003-v2/skill/COMPILATION_MANIFEST.yaml` (`compiler: compiler-s3/0.1.0`).
E o compiler-s3 **não tem FREEZE-RECORD nenhum** — nem 0.2.0, nem v0.2.1. Tem só
dois resultados de canário (`CANARY-STATIC-RESULT.json` e
`CANARY-FAILCLOSED-RESULT.json`, ambos `approved: true`) sem registro de freeze
que os ancore a um conjunto de arquivos.

Então, além dos módulos ausentes, o BLOCO 3 rodaria sobre um compilador **não
congelado**. Recomendo repetir para o s3 o que fizemos para o v2: inventário de
hash, canário datado nesta máquina, e um FREEZE-RECORD próprio — antes de
compilar a Skill do P004.

## O que destrava

Publicar da Lenovo, no Drive:

1. `scan_source_corruption.py`
2. `detector_recall_fix.py`
3. `distance-lines-PILOT-003.json` (ou o script que o gera) — se o P4 tiver de
   valer também para o P004, o gerador é o que interessa, não o arquivo do P003
4. um manifesto de hash desses arquivos, como o `CTS-HASHES`

Com isso, T1 roda em ~13 chamadas (uma por segmento), dentro do teto.

## Efeito em cascata

**T3 (BLOCO 4 preliminar) não pôde rodar**, porque sua condição de entrada é
"só se T1 produziu Skill válida". Não há Skill. Registrado sem tentativa, para
não gastar chamada nem produzir resultado que não significaria nada.
