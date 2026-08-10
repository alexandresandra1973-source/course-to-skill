# course-to-skill-claude — espinha vertical (Fase 4)

Implementação da fatia vertical proposta em `CLAUDE_ARCHITECTURE_PROPOSAL.md`.
Roda **daqui** (ext4). O Drive é dado de entrada, somente leitura.

    python3 spine.py       # roda a espinha contra o material real do PILOT-001
    python3 run_tests.py   # meta-testes: cada portao dispara e passa
    python3 publish.py     # publica o relatorio no Drive

## Escopo implementado
| Componente | ADR |
|---|---|
| Vault L0 imutavel, enderecado por conteudo | ADR-0001 |
| Cutter de held-out em L0 por span          | ADR-0003 |
| G2 anchor (span+quote resolve em L0)       | ADR-0002 |
| G3 dispersao                                | ADR-0005 |
| G5 fechamento pos-compilacao (+ origin)    | ADR-0007, ADR-0008 |
| G6 teto de maturidade por corpus            | ADR-0010 |

Fora de escopo nesta fase: Extractor, Judge, CLI.

## Regras que o codigo respeita
- Portao devolve estado nomeado + evidencia. Nunca booleano nu.
- Erro de dado de entrada e resultado (`DATA_DEFECT`, `NOT_ESTABLISHED`), nao excecao.
- Nada de mock nos portoes: leem arquivo real ou nao rodam.
- O material do piloto nao e consertado para teste passar.
