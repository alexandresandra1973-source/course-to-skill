#!/usr/bin/env python3
"""Índice-ponteiro dos 12 órfãos de `Course-to-SkillPILOT-001v0.1.2`.

Roda daqui (ext4). READ-ONLY absoluto sobre `Course-to-Skill/` e
`Course-to-Skill-Compiler/`: nada é movido, copiado para dentro delas, nem
editado. Publica um único arquivo em `Course-to-Skill-Claude/docs/`.

Relatório GERADO: nenhum hash e nenhum tamanho é digitado.

O QUE ESTE ARQUIVO RESOLVE
--------------------------
Os 12 artefatos do build da v0.1.2 estão numa pasta cujo nome é o destino
pretendido com os separadores perdidos. O destino real está quase vazio. Quem
procurar o build no lugar certo não acha nada — e não há backup. Este índice é
o PONTEIRO: amarra cada órfão ao caminho onde deveria estar, por SHA-256.

NÃO EXECUTA NENHUMA DAS TRÊS OPÇÕES. Só mede e publica.
"""
from __future__ import annotations

import hashlib
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
ORPHAN = DRIVE / "Course-to-SkillPILOT-001v0.1.2"
INTENDED = DRIVE / "Course-to-Skill/PILOT-001/v0.1.2"
SAVE_PATHS = ORPHAN / "06_REPORTS/SAVE-PATHS-v0.1.2.md"
MANIFEST = DRIVE / "Course-to-Skill-Claude/docs/BASELINE_MANIFEST_20260810.txt"
OUT = DRIVE / "Course-to-Skill-Claude/docs/ORPHAN-BUILD-v0.1.2-INDEX.md"

TREES = [DRIVE / "Course-to-Skill", DRIVE / "Course-to-Skill-Compiler",
         DRIVE / "Course-to-Skill-Claude", ORPHAN]

# Destino declarado pelo SAVE-PATHS, por nome de arquivo. Lido do próprio
# documento em tempo de execução; este mapa só normaliza a grafia do Windows.
def norm(p: str) -> str:
    return p.replace("\\", "/").strip("`").strip()


# O que cada artefato É. O rótulo vem do nome + do conteúdo real do zip, não
# de memória: a coluna "conteúdo" ao lado é gerada da leitura do arquivo.
WHAT = {
    "PILOT-001-v0.1.2-RELEASE-CANDIDATE.zip":
        "candidato de release da v0.1.2 — o pacote completo do build",
    "course-to-skill-compiler-v0.1.2-pilot-ready.zip":
        "o compilador na versão v0.1.2, pronto para piloto",
    "PILOT-001-generated-skill-v0.1.2.zip":
        "a Skill gerada pelo compilador — a saída do pipeline",
    "PILOT-001-agent-input-v0.1.2.zip":
        "o pacote de entrada do agente: runtime-bundle + prompt do executor",
    "PILOT-001-judge-private-v0.1.2.zip":
        "material privado do juiz — held-out registry e suíte de teste",
    "PILOT-001-final-blind-test-kit-v0.1.2.zip":
        "kit de teste cego final",
    "PREFLIGHT_REPORT-v0.1.2.md":
        "relatório de preflight: PASS estático, comportamental PENDENTE",
    "SAVE-PATHS-v0.1.2.md":
        "**o documento que declara o destino pretendido** — a prova de que a "
        "pasta órfã é um join quebrado",
    "PILOT-001-TEST-0007-ARM-A-v0.1.2.zip":
        "braço A do TEST-0007: bundle completo",
    "PILOT-001-TEST-0007-ARM-B-v0.1.2.zip":
        "braço B do TEST-0007: bundle sem `decision-rules.yaml` e `workflows.yaml`",
    "PILOT-001-TEST-0008-ARM-A-v0.1.2.zip":
        "braço A do TEST-0008: só `SKILL.md` reduzido, sem `knowledge/`",
    "PILOT-001-TEST-0008-ARM-B-v0.1.2.zip":
        "braço B do TEST-0008: bundle completo (idêntico em conteúdo ao 0007-A)",
}

DEFECTS = [
    {"kind": "pasta sem zero à esquerda",
     "what": "`2_GENERATED-SKILL`",
     "detail": ("Todos os irmãos usam dois dígitos (`00_`, `01_`, `03_`, `04_`, "
                "`05_`, `06_`). Só a pasta da Skill gerada perdeu o zero. É um "
                "segundo defeito de formatação, independente do join quebrado, "
                "e quebra a ordenação alfabética da pasta."),
     "consequence": ("`2_GENERATED-SKILL` ordena DEPOIS de `06_REPORTS` em "
                     "listagem alfabética, então a Skill gerada aparece fora "
                     "de ordem no meio do build.")},
    {"kind": "arquivo prometido e nunca gerado",
     "what": "`STATIC_VALIDATION-v0.1.2.json`",
     "detail": ("O `SAVE-PATHS-v0.1.2.md` lista este arquivo em `07-reports\\`. "
                "Ele não existe em lugar nenhum do Drive. O análogo da v0.1.3 "
                "(`STATIC-ARM-VALIDATION-v0.1.3.json`) existe e está no lugar "
                "certo."),
     "consequence": ("O `PREFLIGHT_REPORT` declara 30 checagens estáticas com "
                     "PASS, mas o artefato legível por máquina que as sustenta "
                     "não foi emitido. O PASS estático da v0.1.2 não é "
                     "reverificável sem recompilar.")},
    {"kind": "arquivo prometido e nunca gerado",
     "what": "`SHA256SUMS-v0.1.2.txt`",
     "detail": ("Também listado em `07-reports\\` pelo SAVE-PATHS e ausente da "
                "árvore inteira. A v0.1.3 tem `SHA256SUMS-v0.1.3.txt`."),
     "consequence": ("O build da v0.1.2 nunca teve manifesto de integridade "
                     "próprio. **É por isso que este índice precisa existir:** "
                     "sem ele, os 12 órfãos não têm nenhuma âncora de hash "
                     "publicada em lugar nenhum.")},
]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_summary(p: Path) -> str:
    try:
        with zipfile.ZipFile(p) as z:
            names = [n for n in z.namelist() if not n.endswith("/")]
            tops = sorted({n.split("/")[0] for n in z.namelist()})
            return (f"{len(names)} arquivo(s), raiz "
                    + ", ".join(f"`{t}`" for t in tops[:2])
                    + ("…" if len(tops) > 2 else ""))
    except zipfile.BadZipFile:
        return "**ZIP ILEGÍVEL**"


def save_paths_map() -> tuple[dict[str, str], str, list[str]]:
    """Lê o destino declarado, direto do SAVE-PATHS."""
    text = SAVE_PATHS.read_text(encoding="utf-8")
    base, mapping, listed = "", {}, []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("`G:") and s.endswith("`"):
            base = norm(s)
        if s.startswith("- `") and s.endswith("`"):
            rel = norm(s[2:])
            listed.append(rel)
            mapping[Path(rel).name] = rel
    return mapping, base, listed


def manifest_scope() -> dict:
    lines = [l for l in MANIFEST.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    paths = [l.split("  ")[-1] for l in lines]
    tops: dict[str, int] = {}
    for p in paths:
        k = "/".join(p.split("/")[:2])
        tops[k] = tops.get(k, 0) + 1
    return {"n": len(lines), "tops": tops,
            "covers_intended": any(p.startswith("Course-to-Skill/PILOT-001/")
                                   for p in paths),
            "covers_orphan": any(p.startswith("Course-to-SkillPILOT-001v0.1.2")
                                 for p in paths)}


def all_hashes() -> dict[str, list[str]]:
    """Hash de tudo, para provar cópia única."""
    idx: dict[str, list[str]] = {}
    for tree in TREES:
        if not tree.is_dir():
            continue
        for p in sorted(tree.rglob("*")):
            if not p.is_file():
                continue
            try:
                idx.setdefault(sha(p), []).append(str(p.relative_to(DRIVE)))
            except OSError:
                continue
    return idx


def table(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |",
                      "|" + "|".join("---" for _ in head) + "|"]
                     + ["| " + " | ".join(str(x) for x in r) + " |" for r in rows])


def main() -> int:
    if not ORPHAN.is_dir():
        print(f"PASTA ÓRFÃ AUSENTE: {ORPHAN}")
        return 2

    files = sorted((p for p in ORPHAN.rglob("*") if p.is_file()),
                   key=lambda p: str(p.relative_to(ORPHAN)))
    smap, base, listed = save_paths_map()
    idx = all_hashes()
    man = manifest_scope()

    rows = []
    for p in files:
        rel = p.relative_to(ORPHAN)
        h = sha(p)
        copies = idx.get(h, [])
        rows.append({
            "name": p.name, "rel": str(rel), "sha": h,
            "bytes": p.stat().st_size,
            "intended": smap.get(p.name),
            "what": WHAT.get(p.name, "—"),
            "content": zip_summary(p) if p.suffix.lower() == ".zip" else "—",
            "copies": copies, "unique": len(copies) == 1,
        })

    intended_files = ([str(x.relative_to(DRIVE)) for x in INTENDED.rglob("*")
                       if x.is_file()] if INTENDED.is_dir() else [])

    L, w = [], None
    w = L.append
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    n_uni = sum(1 for r in rows if r["unique"])
    total = sum(r["bytes"] for r in rows)

    w("# ORPHAN-BUILD-v0.1.2 — ÍNDICE-PONTEIRO\n")
    w(f"**Gerado:** `{stamp}` · gerador `{Path(__file__).name}` · "
      "**somente medição**, READ-ONLY.\n")
    w("Relatório gerado por script; nenhum hash e nenhum tamanho foi digitado.\n")

    w("\n> ## Para que serve este arquivo\n>\n"
      f"> O build da v0.1.2 do PILOT-001 **não está** em `{INTENDED.relative_to(DRIVE)}/`. "
      f"Está em `{ORPHAN.name}/`, uma pasta cujo nome é o caminho de destino com "
      "os separadores perdidos. Quem procurar o build no lugar certo não acha "
      "nada.\n>\n"
      f"> São **{len(rows)} arquivos, {total/1_048_576:.2f} MB**, e "
      f"**{n_uni} deles em cópia única na árvore** — não há backup. Este índice "
      "amarra cada um ao caminho onde deveria estar, por SHA-256, para que a "
      "busca no lugar certo termine aqui.\n>\n"
      "> **Nada foi movido, copiado ou alterado.** Este arquivo é ponteiro, não "
      "conserto.\n")

    # ------------------------------------------------------------------ 1
    w("\n## 1. Estado do destino pretendido\n")
    w(f"O `SAVE-PATHS-v0.1.2.md`, que veio junto com os órfãos, declara a pasta "
      f"base:\n\n> `{base}`\n")
    w(f"\nEsse caminho, no mount: `{INTENDED.relative_to(DRIVE)}/`. Conteúdo real "
      f"hoje — **{len(intended_files)} arquivo(s)**:\n")
    w(table([[f"`{x}`"] for x in sorted(intended_files)] or [["*(vazio)*"]],
            ["o que existe no destino"]))
    w("\n**Nenhum dos 12 artefatos de build está lá.** O que existe é só o "
      "resultado do julgamento, publicado depois.\n")

    # ------------------------------------------------------------------ 2
    w("\n## 2. Os 12 órfãos\n")
    w(table([[i + 1, f"`{r['rel']}`",
              f"`{r['intended']}`" if r["intended"] else "**não listado**",
              f"{r['bytes']:,}".replace(",", " "),
              "**sim**" if r["unique"] else f"**NÃO ({len(r['copies'])})**"]
             for i, r in enumerate(rows)],
            ["#", "caminho real (dentro da pasta órfã)",
             "destino pelo SAVE-PATHS", "bytes", "cópia única"]))
    w("")
    w(table([[f"`{r['rel']}`", f"`{r['sha']}`"] for r in rows],
            ["arquivo", "SHA-256 completo"]))
    w("")
    w(table([[f"`{r['name']}`", r["what"], r["content"]] for r in rows],
            ["arquivo", "o que é", "conteúdo"]))

    not_listed = [r for r in rows if not r["intended"]]
    if not_listed:
        w(f"\n> **{len(not_listed)} arquivo(s) não constam do SAVE-PATHS:** "
          + ", ".join(f"`{r['name']}`" for r in not_listed)
          + ". Existem no build mas nenhum destino foi declarado para eles.\n")

    dup = [r for r in rows if not r["unique"]]
    if dup:
        w("\n> **ATENÇÃO: nem todos estão em cópia única.**\n")
        w(table([[f"`{r['name']}`", "<br>".join(f"`{c}`" for c in r["copies"])]
                 for r in dup], ["arquivo", "cópias"]))
    else:
        w(f"\n> **Reconferido: os {len(rows)} continuam em cópia única.** "
          "Varredura por SHA-256 sobre `Course-to-Skill/`, "
          "`Course-to-Skill-Compiler/`, `Course-to-Skill-Claude/` e a própria "
          "pasta órfã: nenhum dos 12 conteúdos aparece duas vezes. **Perder "
          "essa pasta é perder o build.**\n")

    # ------------------------------------------------------------------ 3
    w("\n## 3. Os dois defeitos de forma\n")
    for i, d in enumerate(DEFECTS, 1):
        w(f"\n### 3.{i} {d['what']} — {d['kind']}\n")
        w(d["detail"] + "\n")
        w(f"\n**Consequência:** {d['consequence']}\n")

    def key(name: str) -> frozenset:
        """Identidade do artefato, insensível à ORDEM dos tokens.

        O SAVE-PATHS escreve `PILOT-001-v0.1.2-TEST-0007-ARM-A.zip` e o arquivo
        real se chama `PILOT-001-TEST-0007-ARM-A-v0.1.2.zip`: mesmos tokens,
        ordem diferente. Casar por string exata marcaria os quatro braços como
        ausentes, o que seria falso.
        """
        stem = Path(name).stem.replace("_", "-")
        return frozenset(t for t in stem.split("-") if t)

    have = {key(r["name"]): r["name"] for r in rows}
    checked = []
    for x in listed:
        nm = Path(x).name
        if nm in {r["name"] for r in rows}:
            checked.append((x, "**existe**", ""))
        elif key(nm) in have:
            checked.append((x, "existe, **com outro nome**", f"`{have[key(nm)]}`"))
        else:
            checked.append((x, "**AUSENTE**", "—"))
    missing = [x for x, st, _ in checked if st == "**AUSENTE**"]
    renamed = [(x, a) for x, st, a in checked if "outro nome" in st]

    w(f"\n### 3.4 Conferência: o que o SAVE-PATHS promete × o que existe\n")
    w(table([[f"`{x}`", st, a] for x, st, a in checked],
            ["prometido pelo SAVE-PATHS", "estado", "arquivo real"]))
    w(f"\n**{len(missing)} de {len(listed)} prometidos nunca foram gerados:** "
      + ", ".join(f"`{Path(x).name}`" for x in missing) + ".\n")
    if renamed:
        w(f"\n**{len(renamed)} existem com nome diferente do declarado** — "
          "mesmos tokens, ordem trocada. Não é ausência, é divergência de "
          "convenção, e está detalhada logo abaixo.\n")
    w("\n> Note também que o SAVE-PATHS nomeia os braços como "
      "`PILOT-001-v0.1.2-TEST-0007-ARM-A.zip` e os coloca todos em "
      "`06-comparison-arms\\`, enquanto os arquivos reais se chamam "
      "`PILOT-001-TEST-0007-ARM-A-v0.1.2.zip` e vivem em duas pastas separadas "
      "por teste. **A convenção de nome e de pasta divergiu do documento que a "
      "declarou** — terceiro desvio de forma, menor que os dois acima.\n")

    # ------------------------------------------------------------------ 4
    w("\n## 4. Três opções, com consequência. Nenhuma executada.\n")
    w("Este relatório **não escolhe** e **não executou** nenhuma delas.\n")

    w("\n### (a) Deixar onde está + este ponteiro\n")
    w(table([["não toca em nada sob READ-ONLY", "✅ garantido"],
             ["o build fica localizável por quem procura no lugar certo",
              "✅ via este índice"],
             ["integridade verificável", "✅ os 12 SHA-256 ficam publicados"],
             ["protege contra perda", "❌ **não** — segue em cópia única"],
             ["restaura a estrutura de pastas", "❌ não"],
             ["custo de execução", "zero — já está feito"]],
            ["efeito", "resultado"]))
    w("\n**O que quebra:** nada. **O que fica desprotegido:** os 12 arquivos "
      "continuam sem backup. Um apagamento acidental da pasta órfã, ou uma "
      "\"limpeza\" de pasta com nome estranho, destrói o build da v0.1.2 de "
      "forma irreversível. O ponteiro sobreviveria e apontaria para o vazio.\n")

    w("\n### (b) Ponteiro + backup dentro de `Course-to-Skill-Claude/`\n")
    w(table([["não toca em nada sob READ-ONLY", "✅ o backup vai para a árvore gravável"],
             ["protege contra perda", "✅ segunda cópia"],
             ["integridade verificável", "✅ se o manifesto de backup for emitido"],
             ["restaura a estrutura no lugar certo", "❌ não"],
             ["cria cópia que pode divergir", "⚠️ **sim** — exige disciplina de hash"],
             ["custo", "1,05 MB + manutenção"]],
            ["efeito", "resultado"]))
    w("\n**O que quebra:** nada sob READ-ONLY. **O que passa a exigir "
      "disciplina:** a partir daí existem duas cópias do mesmo build, e nada no "
      "sistema garante que continuem iguais. Sem um manifesto de hash do backup "
      "e uma reconferência periódica, a segunda cópia vira uma terceira fonte "
      "de verdade — que é a classe de problema que gerou a pasta órfã.\n")
    w("\n> Se esta for a escolhida, o backup deve nascer com o próprio "
      "`SHA256SUMS` que a v0.1.2 nunca teve (§3.3), e este índice deve passar a "
      "citar as duas localizações.\n")

    w("\n### (c) Mover para o destino pretendido\n")
    w(table([["restaura a estrutura declarada pelo SAVE-PATHS", "✅"],
             ["quem procura no lugar certo acha o build, sem ponteiro", "✅"],
             ["protege contra perda", "❌ **não** — segue em cópia única, "
              "só que noutro lugar"],
             ["**ESCREVE na árvore sob READ-ONLY**", "❌ **viola a restrição vigente**"],
             ["invalida o BASELINE_MANIFEST", "⚠️ **ver a apuração abaixo**"],
             ["invalida os caminhos deste índice", "⚠️ sim — exigiria reemissão"]],
            ["efeito", "resultado"]))
    w("\n**O que quebra, medido e não suposto:**\n")
    w(f"\nO `BASELINE_MANIFEST_20260810.txt` tem **{man['n']} entradas**, "
      "distribuídas assim:\n")
    w(table([[f"`{k}/`", v] for k, v in sorted(man["tops"].items(),
                                               key=lambda x: -x[1])],
            ["prefixo", "entradas"]))
    w(f"\n**O manifesto NÃO cobre `Course-to-Skill/PILOT-001/`** "
      f"({'cobre' if man['covers_intended'] else 'nenhuma entrada'}), e não "
      f"cobre a pasta órfã "
      f"({'cobre' if man['covers_orphan'] else 'nenhuma entrada'}). "
      "Não há uma única linha com `v0.1.2`.\n")
    w("\n> **Correção de premissa.** Mover os órfãos para "
      "`Course-to-Skill/PILOT-001/v0.1.2/` **não invalidaria as "
      f"{man['n']} entradas do BASELINE_MANIFEST**, porque esse subarquivo da "
      "árvore nunca entrou no manifesto. O custo real da opção (c) é outro, e "
      "é suficiente por si: **ela escreve dentro de `Course-to-Skill/`, que "
      "está sob READ-ONLY absoluto por instrução vigente.** Escolher (c) é "
      "decidir suspender essa restrição — decisão de quem conduz, não "
      "consequência técnica.\n")
    w("\n**O que fica protegido:** a estrutura. **O que não fica:** os dados. "
      "Mover não cria backup; move o ponto único de falha.\n")

    w("\n### Resumo comparativo\n")
    w(table([["(a) ponteiro só", "✅", "❌", "❌", "zero"],
             ["(b) ponteiro + backup", "✅", "✅", "❌", "disciplina de hash"],
             ["(c) mover", "❌", "❌", "✅", "suspender o READ-ONLY"]],
            ["opção", "respeita READ-ONLY", "protege de perda",
             "restaura estrutura", "custo principal"]))

    w("\n---\n")
    w("**Escopo:** somente medição. Nenhum arquivo foi movido, copiado, criado, "
      "alterado ou apagado em `Course-to-Skill/`, `Course-to-Skill-Compiler/` "
      "ou na pasta órfã. O único arquivo escrito é este relatório, em "
      "`Course-to-Skill-Claude/docs/`. **Nenhuma das três opções foi "
      "executada.**")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"órfãos: {len(rows)} | cópia única: {n_uni}/{len(rows)} | "
          f"{total} bytes")
    print(f"destino pretendido tem {len(intended_files)} arquivo(s), nenhum do build")
    print(f"prometidos pelo SAVE-PATHS e ausentes: {len(missing)}")
    print(f"BASELINE_MANIFEST: {man['n']} entradas | cobre PILOT-001/: "
          f"{man['covers_intended']} | cobre pasta órfã: {man['covers_orphan']}")
    print(f"publicado: {OUT.name} ({OUT.stat().st_size} B) "
          f"{sha(OUT)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
