# HANDOFF — três frentes

`2026-08-11T04:58:13+00:00` · gerado por `handoff_tres_frentes.py` · READ-ONLY sobre `Course-to-Skill/` e `Course-to-Skill-Compiler/` · **nada congelado** (lock/registry/opening record), nenhuma conversa cega aberta, nenhuma Skill compilada, nenhum script auditado editado.

## Veredito da prova de alcançabilidade, em uma linha

**Minha alegação se sustenta como foi enunciada — com nota inteira nenhuma margem alcançável entra na faixa que TOL atravessa, e a folga é 0.031335907 contra TOL de 0,01 — mas ela é mais frágil do que eu dei a entender: a leitura simétrica já falha com uma casa decimal, e a de um lado só falha com duas.**

## Pronto

| artefato | sha256 | bytes |
|---|---|---|
| `TOL-REACHABILITY-PROOF.md` | `a05a2be0d0e554e4…` | 3879 |
| `HELDOUT-BLIND-CASES-PILOT-002.yaml` | `50c6abe99431fecf…` | 12070 |
| `HELDOUT-BLIND-CASES-FREEZE-RECORD-PILOT-002.yaml` | `f1d3b3a5b4148b15…` | 1253 |
| `DRY-RUN-TEST-0008.md` | `6d75f9bc6b69358c…` | 6842 |

### Frente 1 — prova por enumeração

Enumeração **completa** do espaço alcançável em aritmética **exata** (`Fraction` sobre `Decimal`; float aqui seria o próprio erro sob investigação). Três grades de nota testadas. O resultado por grade e a checagem simétrica estão no relatório.

O que mudou em relação ao que eu tinha afirmado: eu conferi quatro valores à mão e concluí que o desvio "não pode" mudar veredito. A enumeração confirma isso para nota inteira, e mostra que a folga é propriedade das fronteiras escolhidas, não margem de segurança projetada. Se o contrato do juiz aceitar nota fracionária, a prova precisa ser refeita.

### Frente 2 — casos cegos, escritos antes de existir Skill

**10 casos congelados**, 10/10 com citação verificada contra o L0 íntegro. Cinco da seção de modos de permissão, cinco da de janela de contexto.

A varredura confirmou que **nenhuma Skill do PILOT-002 existe** — a árvore do piloto tem 3 arquivos, todos de fonte. Está no freeze record, com os hashes do L0 íntegro e do cortado.

A expectativa de cada caso é **rótulo**, não silêncio: responder e rotular como conhecimento geral é aceitável; apresentar como metodologia da fonte é falha; recusar por ausência é aceitável. Acerto factual sem rótulo fica INCONCLUSIVO, porque não separa memória do modelo de conhecimento da fonte.

**Registrado no artefato: quem escreveu os casos não pode ser o juiz depois.** Eu escrevi; eu não julgo.

### Frente 3 — ensaio seco do TEST-0008

As duas comparações e os quatro regimes foram exercitados sobre notas sintéticas, em aritmética exata. **A aritmética não é o gargalo.**

## O que falta para o 0008 rodar

**13 de 14 itens exigidos não existem.** A lista completa está no relatório; os que mais pesam:

- régua do 0008 **congelada** (só existe rascunho, e ele precisa de auditoria externa antes)
- lista canônica de `comparison_metrics` congelada — **bloqueador 1 do ADR**, e do qual régua, âncoras e derivação de métrica dependem
- variância do avaliador do 0008, que o ADR proíbe herdar do 0007
- bandas numéricas de interpretação `F/P`, que só podem sair da variância
- teto estrutural, regra de decisão, pacotes das três condições, addendum de saída do juiz, instruções de rodada cega, e a cadeia pré-run inteira

**Dois não são falta de arquivo, são falta de forma:** o contrato expressa **uma** comparação por teste, e o 0008 precisa de duas (`P` e `F`); e o modelo é par esquerda/direita mais preservação antes/depois, desenhado para ablação, não para três condições.

**E há uma armadilha.** 13 contratos antigos já declaram `TEST-0008` com uma comparação só, `SKILL_MINUS_SUMMARY`, e limiar adiado. Isso codifica o desenho de duas condições que o ADR substituiu. `SKILL_MINUS_SUMMARY` não desambigua entre `P` e `F` — quem rodar com esse contrato mede uma comparação e não sabe qual.

## O que sobrou para o Alexandre

1. **Decidir se a prova de TOL basta para liberar a rodada.** Ela vale para o contrato atual, de nota inteira. Se o juiz puder devolver nota fracionária, não vale — e isso é uma linha do contrato, não uma suposição minha.
2. **Nomear outro juiz para os casos cegos do PILOT-002.** Eu os escrevi; a separação está declarada no artefato e depende de você cumpri-la.
3. **Resolver a discrepância 5×6** antes de qualquer coisa do 0008. É o primeiro dominó: régua, âncoras e métrica dependem dela.
4. **Decidir se o 0008 vale o custo agora**, com a lista do que falta em mãos. Não é um patch de distância do 0007.
5. **Aposentar ou marcar os 13 contratos legados** com a entrada velha do 0008, para ninguém rodar com o desenho de duas condições.
6. **O limiar da v0.1.4** continua aberto, de sessões atrás.

