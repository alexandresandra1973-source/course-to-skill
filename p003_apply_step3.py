#!/usr/bin/env python3
"""ETAPA 3 — a Skill recebe as respostas do Bloco A e conclui. Mesmo bundle."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import anthropic

S = Path("/home/mtx/course-to-skill-claude/_mirror/pilots/PILOT-003-v2/skill")
T = Path("/tmp/claude-1000/-home-mtx-course-to-skill-claude")
FILES = ["SKILL.md", "knowledge/runtime-policy.yaml", "knowledge/decision-rules.yaml",
         "knowledge/workflows.yaml", "manifest.yaml"]
R = json.loads((T/"p003-recortes.json").read_text(encoding="utf-8"))
A2 = json.loads((T/"p003-apply2.json").read_text(encoding="utf-8"))["answer"]

MSG = """Respostas aos seus pedidos 1, 5, 6, 14, 11 e 12.

1 — MARGEM DE CONTRIBUIÇÃO: 50%. De R$100 de venda sobram R$50 depois de custo do
produto, frete e taxa de pagamento, antes de custo fixo, salário e marketing.
(O dono declarou margem de contribuição, não margem bruta, e não informou AOV nem
COGS fixo por pedido separadamente. Use o que foi dado; se faltar componente para
alguma fórmula sua, diga qual falta em vez de arbitrar.)

5 — Palavras de marca, como os clientes buscam:
mtx imports · mtx · mtximports · mtx motoparts · MTX Parts · mtximports.com.br ·
mtxparts.com.br

6 — Vance & Hines: marca que a MTX DISTRIBUI COM EXCLUSIVIDADE no Brasil desde
2011. Não é concorrente, não é marca própria.

14 — Objetivo: LUCRO JÁ NO PRIMEIRO PEDIDO. Não aceita perder no primeiro pedido
para ganhar na recompra.

11 — Faturamento ~R$380.000 POR MÊS, somando site, Mercado Livre e balcão.
Marketing ~R$8.500/mês: R$5.000 de mensalidade de agência (inclui produção de
conteúdo, filmagem e vídeo) + R$3.500 de mídia no Google.

12 — NÃO SE SABE se a exportação de campanhas incluía REMOVIDAS. Trate sua
conclusão sobre campanhas ausentes como válida apenas para ATIVAS e PAUSADAS, e
declare essa limitação onde ela aparecer.

NÃO ATENDIDOS, e continuam sem resposta: seus pedidos 2, 3, 4, 7, 8, 9, 10 e 13.
Nada de parcela de impressão, nada da tela de ações de conversão, nada de
relatório de produtos, assets, landing pages ou script de PMax.

RESSALVA QUE PERMANECE ABERTA: o ROAS depende de o valor de conversão ser real.
Há R$7.730 (4,5%) não reconciliados entre o valor de conversão do CSV
(R$172.730,01) e as telas da conta (~R$165.000), com o custo batendo nos dois. E
ninguém viu a configuração das ações de conversão.

Agora calcule e conclua. Cite o identificador da regra em cada conclusão. Onde
faltar dado, diga METHOD_NOT_DEFINED ou aponte o campo UNDEFINED — não arbitre.
Ordene as recomendações da mais específica para a mais genérica."""


def main() -> int:
    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" +
              "\n\n".join(f"=== {f} ===\n{(S/f).read_text(encoding='utf-8')}" for f in FILES))
    payload = (MSG + "\n\n=== SUA AUDITORIA ANTERIOR ===\n" + A2[:9000] +
               "\n\n=== RECORTES (com as três colunas quebradas que você já identificou) ===\n" +
               json.dumps(R, ensure_ascii=False, indent=1)[:45000])
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with client.messages.stream(model="claude-opus-5", max_tokens=32000, system=system,
                                messages=[{"role": "user", "content": payload}]) as s:
        m = s.get_final_message()
    ans = "".join(getattr(b, "text", "") for b in m.content if b.type == "text")
    (T/"p003-apply3.json").write_text(json.dumps(
        {"answer": ans, "sha256": hashlib.sha256(ans.encode()).hexdigest(),
         "usage": {"in": m.usage.input_tokens, "out": m.usage.output_tokens}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"len {len(ans)} · tokens {m.usage.input_tokens}/{m.usage.output_tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
