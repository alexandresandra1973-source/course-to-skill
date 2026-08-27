#!/usr/bin/env python3
"""ETAPA 4 — a Skill recebe AOV, custo fixo por pedido e o faturamento do site
separado dos outros canais. Destrava R-0134 (break-even CPA), que a própria Skill
declarou ser o KPI PRIMÁRIO da fonte, e resolve o denominador quebrado de R-0032.

Mesmo bundle da etapa 3, byte a byte. Nenhum conhecimento de Google Ads meu entra:
os dados vão verbatim como o dono os informou, e a auditoria anterior vai inteira,
com a nota de correção anexada, para que a Skill opere sobre números corretos.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import anthropic

ROOT = Path("/home/mtx/course-to-skill-claude")
S = ROOT/"_mirror/pilots/PILOT-003-v2/skill"
OUTD = ROOT/"_mirror/pilots/PILOT-003-v2/apply"
FILES = ["SKILL.md", "knowledge/runtime-policy.yaml", "knowledge/decision-rules.yaml",
         "knowledge/workflows.yaml", "manifest.yaml"]
MODEL = "claude-opus-5"
MAX_TOKENS = 32000
# O alias claude-opus-5 se moveu entre 12/08 e 27/08: o snapshot atual liga
# pensamento estendido por conta própria em prompts complexos, e esses tokens
# consomem o max_tokens. A primeira execução da etapa 4 gastou 32.000 tokens
# dentro de um bloco `thinking` e devolveu ZERO texto. Desligo explicitamente
# para manter comparabilidade com as etapas 1-3, que rodaram sem pensamento.
THINKING = {"type": "disabled"}

MSG = """Respostas aos seus pedidos em aberto. Três blocos: dados novos, uma
CORREÇÃO de dado que você já usou, e uma observação para você avaliar.

═══ BLOCO 1 — DADOS NOVOS ═══

7 — TICKET MÉDIO DO SITE (AOV), mesma janela do Google Ads (15/05–12/08/2026):
    R$ 2.533,86
    Base: 161 pedidos finalizados de 218 totais, somando R$ 407.951,51.
    Estabilidade: o AOV mensal de 2026 fica entre R$ 2.030,88 e R$ 3.361,10.

7b — CUSTO FIXO DE COGS POR PEDIDO, além de produto, frete e taxa de pagamento:
    ZERO. Não há embalagem, picking ou etiqueta custeados à parte.

§5.4 — FATURAMENTO DO SITE, separado dos outros canais:
    maio R$ 123.255 · junho R$ 179.871 · julho R$ 146.552
    média R$ 149.892/mês, apenas o site.

═══ BLOCO 2 — CORREÇÃO DE DADO QUE VOCÊ JÁ USOU ═══

O dado 11 que você recebeu na rodada anterior dizia "faturamento ~R$380.000/mês
somando site, Mercado Livre e balcão". O número correto é ~R$525.000/mês bruto,
todos os canais somados. O marketing continua ~R$8.500/mês (R$5.000 de agência +
R$3.500 de mídia no Google).

Recalcule o que dependia de R$380.000. Diga explicitamente o que muda e o que não
muda.

Sua auditoria anterior também carrega um erro aritmético meu, já corrigido na nota
no topo do documento que segue: o custo total da conta é R$9.577,32 (não
9.586,54), o ROAS da conta é 18,04 (não 18,02), o CPA da conta é R$125,40 (não
125,51) e a reconciliação mensal dá R$3.192,44/mês (não 3.195,51). Use os
corrigidos. Os CPAs por campanha (193,10 · 157,98 · 82,17) não foram afetados.

═══ BLOCO 3 — PERGUNTA EM ABERTO, PARA VOCÊ AVALIAR ═══

A conta registra 48 COMPRAS (tela de Metas) e 76,38 CONVERSÕES no CSV, com valor
total de R$ 172.730,01. O AOV real do site é R$ 2.533,86.

    Valor ÷ compras     = R$ 3.598,00
    Valor ÷ conversões  = R$ 2.261,46

Qual dos dois é o valor por PEDIDO depende de quais ações de conversão carregam
valor — informação que você já pediu (pedido #4) e não recebeu.

Não é afirmação de anomalia; é uma pergunta que o dado disponível não fecha.
Avalie com as regras que tiver. Se não houver regra que cubra, diga
METHOD_NOT_DEFINED.

═══ CONTINUAM SEM RESPOSTA ═══

Seus pedidos 2, 3, 4, 8, 9, 10 e 13: parcela de impressão, estratégias de lance e
orçamentos por campanha, tela das ações de conversão, status do GMC, relatório de
produtos, assets e script de PMax. Nada disso foi fornecido.

A ressalva dos R$7.730 (4,5%) entre o valor de conversão do CSV (R$172.730,01) e
as telas (~R$165.000) permanece aberta e não reconciliada.

═══ O QUE ENTREGAR ═══

1. O BREAK-EVEN CPA por R-0134 / WF-0134, com a fórmula da fonte e os componentes
   agora disponíveis. Se ainda faltar componente, diga qual.
2. O VEREDITO POR CAMPANHA contra esse break-even CPA — as três campanhas e a
   conta, uma a uma, passa ou não passa.
3. O QUE MUDA agora que o KPI que você mesma classificou como PRIMÁRIO (R-0523:
   break-even CPA prevalece; ROAS é irrelevante em comparação) está disponível.
   Você declarou que tudo na auditoria anterior rodava no KPI secundário. Diga o
   que se confirma, o que se inverte e o que continua indeterminado.
4. O QUE VOCÊ CONCLUI sobre a pergunta do bloco 3 — 48 compras contra
   76,38 conversões sobre o mesmo valor, e o AOV real ao lado. Diga o que
   é decidível com o que existe e o que exige o pedido #4.
5. AS RECOMENDAÇÕES REORDENADAS, da mais específica para a mais genérica, dizendo
   quais mudaram de posição e por quê.

Cite o identificador da regra em cada conclusão. Onde faltar dado, diga
METHOD_NOT_DEFINED ou aponte o campo UNDEFINED — não arbitre. Registre
explicitamente todo dado que você precisar e não tiver."""


def build():
    system = ("Você está executando a Skill abaixo. Os arquivos presentes no bundle "
              "são exatamente estes: " + ", ".join(FILES) + "\n\n" +
              "\n\n".join(f"=== {f} ===\n{(S/f).read_text(encoding='utf-8')}" for f in FILES))
    audit = (ROOT/"_mirror/docs/PILOT-003-ACCOUNT-AUDIT.md").read_text(encoding="utf-8")
    recortes = (OUTD/"p003-recortes.json").read_text(encoding="utf-8")
    payload = (MSG +
               "\n\n=== SUA AUDITORIA ANTERIOR, ÍNTEGRA, COM A NOTA DE CORREÇÃO ===\n" +
               audit +
               "\n\n=== RECORTES, RECONSTRUÍDOS DOS MESMOS CSVs ===\n" + recortes)
    return system, payload


def main() -> int:
    system, payload = build()
    key = os.environ.get("ANTHROPIC_API_KEY") or next(
        ((l.split("=", 1)[1] if "=" in l else l).strip().strip('"\'')
         for f in (ROOT/".env", Path.home()/".anthropic_key")
         if f.exists()
         for l in f.read_text(encoding="utf-8").splitlines()
         if l.startswith("ANTHROPIC_API_KEY") or l.strip().startswith("sk-")),
        None)
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY ausente: exporte, ou grave em "
                         f"{ROOT/'.env'} ou {Path.home()/'.anthropic_key'}")
    client = anthropic.Anthropic(api_key=key)

    # MEDIÇÃO DECLARADA — três contagens pela API count_tokens, mesmo modelo:
    #   A) sistema (o bundle) + mensagem de 1 caractere  -> piso por invocação
    #   B) mensagem de 1 caractere, sem sistema          -> overhead a subtrair
    #   C) esta invocação inteira                        -> custo real da rodada
    ct = lambda **kw: client.messages.count_tokens(model=MODEL, **kw).input_tokens
    a = ct(system=system, messages=[{"role": "user", "content": "."}])
    b = ct(messages=[{"role": "user", "content": "."}])
    c = ct(system=system, messages=[{"role": "user", "content": payload}])
    med = {"modelo": MODEL, "bundle_mais_overhead": a, "overhead_msg_minima": b,
           "bundle_isolado": a - b, "invocacao_completa": c,
           "payload_desta_rodada": c - a + b,
           "bytes_bundle": sum(len((S/f).read_bytes()) for f in FILES),
           "chars_bundle": sum(len((S/f).read_bytes().decode("utf-8")) for f in FILES)}
    (OUTD/"p003-medicao-tokens.json").write_text(
        json.dumps(med, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(med, ensure_ascii=False, indent=1))

    with client.messages.stream(model=MODEL, max_tokens=MAX_TOKENS, system=system,
                                thinking=THINKING,
                                messages=[{"role": "user", "content": payload}]) as s:
        m = s.get_final_message()
    blocos = [bl.type for bl in m.content]
    ans = "".join(getattr(bl, "text", "") for bl in m.content if bl.type == "text")
    (OUTD/"p003-apply4.json").write_text(json.dumps(
        {"answer": ans, "sha256": hashlib.sha256(ans.encode()).hexdigest(),
         "model": MODEL, "model_resolvido": m.model,
         "stop_reason": m.stop_reason, "blocos": blocos,
         "thinking": THINKING,
         "usage": {"in": m.usage.input_tokens, "out": m.usage.output_tokens},
         "medicao": med}, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUTD/"p003-apply4.md").write_text(ans, encoding="utf-8")
    print(f"\nlen {len(ans)} · stop {m.stop_reason} · blocos {blocos} · "
          f"resolvido {m.model} · "
          f"tokens {m.usage.input_tokens}/{m.usage.output_tokens}")
    if not ans.strip():
        print("ERRO: resposta VAZIA — artefato nao utilizavel")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
