# REGRA — hash confirma, não reconstrói

**Status:** REGRA_ATIVA · registrada 2026-08-12 · aplica-se a todo o projeto

## O que aconteceu

O Drive caiu no meio de uma execução de PASS 2 de ~5h no PILOT-003. Ao apurar o
estrago, encontrei o seguinte:

| artefato | onde estava o CONTEÚDO | onde estava o HASH | sobreviveu? |
|---|---|---|---|
| `p003-raw.json` (transcrição bruta) | ext4 | — | **sim** |
| `L0-transcript.txt` | Drive | ext4 (`p003-pass1.json`) | sim, por sorte |
| `temporal-map.yaml` | **só Drive** | ext4 | sim, por sorte |
| rastro do PASS 2 | memória do processo | — | **não** |

O `L0` foi recuperável porque a transcrição bruta estava em ext4 e eu podia
reconstruí-lo. O `temporal-map` **não era reconstruível**: eu tinha o
`2c09e3ce74afce8c…` gravado em segurança e ele não me devolvia uma única linha
do arquivo. Só sobreviveu porque o Drive voltou.

## A lição, e ela é geral

**Gravar o hash de um artefato em lugar seguro não protege o artefato.**
O hash CONFIRMA; não RECONSTRÓI.

Este projeto amarra tudo por hash desde o começo — locks, manifests, freeze
records, pacotes de auditoria, o compromisso de cegamento. A disciplina está
certa e pegou erros reais. Mas ela responde à pergunta *"é o mesmo arquivo?"*, e
nunca à pergunta *"e se o arquivo sumir?"*. Foram trinta horas de trabalho até
essa distinção aparecer, e ela apareceu por acidente de infraestrutura, não por
raciocínio.

## A regra

**Onde houver hash de artefato crítico, tem de haver CÓPIA do artefato em mídia
independente — não só o digest.**

Consequências operacionais:

1. Toda publicação grava nos DOIS lados (Drive e ext4), relê os DOIS do destino
   e compara. Divergência falha alto. Implementado em `publish_dual.py`.
2. Execução longa trabalha em ext4 com os insumos COPIADOS, não referenciados.
   O Drive é ponto único de falha e já derrubou trabalho mais de uma vez.
3. Rastro de execução grava incrementalmente em disco, nunca só em memória.
   Um rastro que só existe no fim não é rastro: é aposta.

## O que esta regra NÃO resolve

Duas cópias na mesma máquina não protegem contra perda da máquina. A regra
reduz o risco de ponto único de falha por MONTAGEM, que é o que de fato ocorreu
aqui. Não é backup, e não vou chamá-la de backup.
