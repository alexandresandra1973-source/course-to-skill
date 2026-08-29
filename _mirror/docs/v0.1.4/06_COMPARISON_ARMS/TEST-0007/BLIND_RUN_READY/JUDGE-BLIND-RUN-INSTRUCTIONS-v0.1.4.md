<!-- ARTEFATO DERIVADO, NÃO ORIGINAL.
     Origem: PILOT-001-v0.1.3-TEST-0007-JUDGE-BLIND-RUN/JUDGE-BLIND-RUN-INSTRUCTIONS.md (sha256 d62046601f170ec64ed28f544266a6a129a63b42146552451f8b230f02e65f4a)
     Derivado por script a partir da versão v0.1.3. Alterações:
       - título: 'TEST-0007 v0.1.3' → 'TEST-0007 v0.1.4'
       - acrescentada a tabela de hashes dos artefatos da rodada v0.1.4
     Os nomes de arquivo da régua e dos addenda SEGUEM v0.1.3 de propósito:
     esses artefatos não foram reemitidos e continuam sendo os da v0.1.3.
     NÃO congelado. Precisa de revisão antes de virar artefato de rodada. -->

# JUDGE-BLIND-RUN-INSTRUCTIONS — TEST-0007 v0.1.4

Evaluate exactly the three raw outputs in `raw_outputs/TEST-0007/`.

Order:
1. FULL@BEFORE_DEDUP
2. FULL@AFTER_DEDUP
3. ABLATED@AFTER_DEDUP

Use only:
- TEST-0007-RUBRIC-v0.1.3.yaml
- TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml
- TEST-0007-JUDGE-OUTPUT-ADDENDUM-v0.1.3.yaml
- JUDGE-SCORING-CONTRACT-ADDENDUM-F3-TRISTATE-v0.1.3.yaml
- ADR-TEST-0007-ROUTING-INTEGRITY-v0.1.3.md, if present
- the three raw outputs in this package.

Do not use web search.
Do not infer or seek a target margin, structural ceiling, pass threshold, or expected final verdict.
Score each run independently before comparing them.

For every criterion, return all required fields from TEST-0007-JUDGE-OUTPUT-ADDENDUM-v0.1.3.yaml.
In particular:
- `selected_anchor` is mandatory.
- `anchor_ambiguity` is mandatory.
- If genuinely uncertain between two anchors, set `anchor_ambiguity: true` and name `alternative_anchor`.
- Do not hide anchor uncertainty in a midpoint score.
- Assess all three automatic critical failures for every run.

Evidence must cite the supplied raw-output path and exact line range/quote.
Recompute weighted points and declared total arithmetically.

Return ONLY YAML with top-level key `runs:`. No prose before or after.

## Artefatos desta rodada (v0.1.4)

| artefato | sha256 |
|---|---|
| `PILOT-001-TEST-0007-FULL-BEFORE_DEDUP-v0.1.4.zip` | `555a70295ca23f89878150ddf2b0c207fba393137f1b8e4383bd9be18e7cedfb` |
| `PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip` | `b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028` |
| `PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.4.zip` | `da9b326dbd80af1711c67a5f95999118bdc54ce6b84b6e54dbd756b4d657a205` |
| `TEST-0007-RUBRIC-v0.1.3.yaml` | `66aa33c0c39430fc02a23fc536a475eda8afbd6b18c0f34b01ef075ebf522e9f` |
| `TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml` | `909e38ed245ac8aa0dd32503cdf08f856c8a1227fada22d27639689adc223810` |
| `TEST-0007-DECISION-RULE-v0.1.3.yaml` | `540df7283405aba5dfd2569511e8e11ad42015f55876b39284b3c8c61d160856` |
| `STRUCTURAL-CEILING-REPORT-v0.1.4.yaml` | `a3d659f34db290871e267138dcc551cd962445de81e67133d26a069cbd54d480` |
