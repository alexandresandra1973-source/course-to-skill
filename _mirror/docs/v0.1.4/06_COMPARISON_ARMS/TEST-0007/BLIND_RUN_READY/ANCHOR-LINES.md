# Linhas de âncora — PRIMEIRA mensagem

## 1. Conversa CANDIDATA

Cole o conteúdo integral de `agent-input/RUNNER_PROMPT.md` do pacote, sem
editar. Ele exige esta resposta, que é a âncora de confirmação:

```
PILOT-001 v0.1.4 runtime loaded — ready for blind cases.
```

Resposta diferente disso = conversa suja. Descarte e abra outra.

## 2. Conversa JUIZ

A âncora do juiz é o hash do opening record, no formato que o próprio
`freeze_pre_run_registry.py` imprime:

```
PRE-RUN-OPENING-RECORD SHA-256: <sha do opening record>
```

**BLOQUEADA.** O opening record não foi congelado — ver `PRE-RUN-CHAIN-v0.1.4.md`. Sem ele não há hash para colar.
