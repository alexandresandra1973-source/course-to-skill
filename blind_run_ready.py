#!/usr/bin/env python3
"""A5 — pasta pronta para a rodada cega do TEST-0007 v0.1.4.

Roda daqui (ext4). READ-ONLY sobre Course-to-Skill/: os pacotes NÃO são copiados
nem movidos; a pasta os REFERENCIA por hash e caminho.

A pasta é montada em Course-to-Skill-Claude/docs/, não em Course-to-Skill/,
porque esta sessão declara Course-to-Skill/ read-only absoluto.

Não abre conversa, não congela nada.
"""
from __future__ import annotations

import hashlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path

DRIVE = Path("/mnt/g/Meu Drive/Chat GPT")
DOCS = DRIVE / "Course-to-Skill-Claude/docs"
OUT = DOCS / "BLIND_RUN_READY-v0.1.4"
V013 = DRIVE / "Course-to-Skill/PILOT-001/v0.1.3/06_COMPARISON_ARMS/TEST-0007"

ARMS = {
    "FULL@BEFORE_DEDUP": ("PILOT-001-TEST-0007-FULL-BEFORE_DEDUP-v0.1.4.zip",
                          "555a70295ca23f89878150ddf2b0c207fba393137f1b8e4383bd9be18e7cedfb"),
    "FULL@AFTER_DEDUP": ("PILOT-001-TEST-0007-FULL-AFTER_DEDUP-v0.1.4.zip",
                         "b30c1da365af5c06b38efd91715f72c8cc312d0efac8c4dd999ac811b690f028"),
    "ABLATED@AFTER_DEDUP": ("PILOT-001-TEST-0007-ABLATED-AFTER_DEDUP-v0.1.4.zip",
                            "da9b326dbd80af1711c67a5f95999118bdc54ce6b84b6e54dbd756b4d657a205"),
}
JUDGE_REFS = {
    "TEST-0007-RUBRIC-v0.1.3.yaml":
        "66aa33c0c39430fc02a23fc536a475eda8afbd6b18c0f34b01ef075ebf522e9f",
    "TEST-0007-RUBRIC-ANCHOR-ADDENDUM-v0.1.3.yaml":
        "909e38ed245ac8aa0dd32503cdf08f856c8a1227fada22d27639689adc223810",
    "TEST-0007-DECISION-RULE-v0.1.3.yaml":
        "540df7283405aba5dfd2569511e8e11ad42015f55876b39284b3c8c61d160856",
}


def sha256b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def locate(want: str) -> str | None:
    for p in sorted((DRIVE / "Course-to-Skill").rglob("*")):
        if not p.is_file():
            continue
        try:
            if sha256b(p.read_bytes()) == want:
                return str(p.relative_to(DRIVE))
            if p.suffix.lower() == ".zip":
                with zipfile.ZipFile(p) as z:
                    for n in z.namelist():
                        if not n.endswith("/") and sha256b(z.read(n)) == want:
                            return f"{p.relative_to(DRIVE)} :: {n}"
        except (OSError, zipfile.BadZipFile):
            continue
    return None


def runner_prompt() -> str | None:
    """RUNNER_PROMPT.md verbatim de dentro do braço congelado."""
    loc = locate(ARMS["FULL@AFTER_DEDUP"][1])
    if not loc or " :: " not in loc:
        return None
    zpath, inner = loc.split(" :: ")
    with zipfile.ZipFile(DRIVE / zpath) as z:
        arm = z.read(inner)
    with zipfile.ZipFile(__import__("io").BytesIO(arm)) as z2:
        n = [x for x in z2.namelist() if x.endswith("RUNNER_PROMPT.md")][0]
        return z2.read(n).decode("utf-8")


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    OUT.mkdir(parents=True, exist_ok=True)

    arm_loc = {k: locate(h) for k, (_, h) in ARMS.items()}
    judge_loc = {k: locate(h) for k, h in JUDGE_REFS.items()}
    rp = runner_prompt()
    anchor = None
    if rp:
        for line in rp.splitlines():
            if "reply only" in line.lower():
                anchor = line.split("`")[1] if "`" in line else line.strip()
    (OUT / "CANDIDATE-ATTACHMENTS.md").write_text(
        "# Conversa CANDIDATA — o que anexar\n\n"
        "Uma conversa NOVA por braço. Nunca dois braços na mesma conversa.\n\n"
        "| ordem | braço | anexar | sha256 |\n|---|---|---|---|\n"
        + "".join(f"| {i} | `{k}` | `{ARMS[k][0]}` | `{ARMS[k][1]}` |\n"
                 for i, k in enumerate(ARMS, 1))
        + "\nOrigem de cada pacote (não copiar, referenciar):\n\n"
        + "".join(f"- `{k}` → `{arm_loc[k]}`\n" for k in ARMS)
        + "\nDentro do zip, anexar apenas `agent-input/runtime-bundle/` como Skill e\n"
          "seguir `agent-input/RUNNER_PROMPT.md`. Não fornecer régua, testes,\n"
          "respostas esperadas nem qualquer material judge-private.\n",
        encoding="utf-8")

    (OUT / "JUDGE-ATTACHMENTS.md").write_text(
        "# Conversa JUIZ — o que anexar\n\n"
        "Uma conversa nova, sem contexto prévio de PILOT-001.\n\n"
        "Anexar as três saídas cruas das conversas candidatas, mais:\n\n"
        "| artefato | sha256 | origem |\n|---|---|---|\n"
        + "".join(f"| `{k}` | `{v}` | `{judge_loc[k]}` |\n"
                 for k, v in JUDGE_REFS.items())
        + "\n**Falta um artefato:** não existe `JUDGE-BLIND-RUN-INSTRUCTIONS` da\n"
          "v0.1.4. O da v0.1.3 está em\n"
          "`PILOT-001-v0.1.3-TEST-0007-JUDGE-BLIND-RUN.zip` e serve de modelo, mas\n"
          "precisa ser reemitido e congelado para a v0.1.4 antes da rodada. Não foi\n"
          "gerado aqui: seria inventar artefato congelado.\n",
        encoding="utf-8")

    (OUT / "ANCHOR-LINES.md").write_text(
        "# Linha de âncora — PRIMEIRA mensagem\n\n"
        "## Conversa CANDIDATA\n\n"
        "A primeira mensagem é o conteúdo integral de `agent-input/RUNNER_PROMPT.md`\n"
        "do pacote anexado, colado sem editar. Ele termina exigindo esta resposta,\n"
        "que é a âncora de confirmação:\n\n"
        f"```\n{anchor or 'NAO_EXTRAIDO'}\n```\n\n"
        "Se a resposta vier diferente disso, a conversa não está limpa: descartar e\n"
        "abrir outra.\n\n"
        "## Conversa JUIZ\n\n"
        "**PENDENTE.** A linha de âncora do juiz sai do `JUDGE-BLIND-RUN-INSTRUCTIONS`\n"
        "da v0.1.4, que ainda não existe. Não foi improvisada aqui.\n",
        encoding="utf-8")

    readme = (
        "# Abertura da rodada cega — TEST-0007 v0.1.4\n"
        "\n"
        "**NÃO ABRA AINDA.** Falta congelar a cadeia (margin lock → registry →\n"
        "opening record) e reemitir as instruções do juiz para a v0.1.4.\n"
        "\n"
        "Quando liberado, nesta ordem:\n"
        "\n"
        "1. Abra 3 conversas candidatas novas, uma por braço: BEFORE, AFTER,\n"
        "   ABLATED (`CANDIDATE-ATTACHMENTS.md`).\n"
        "2. Cole o `RUNNER_PROMPT.md` do pacote como primeira mensagem e confira a\n"
        "   âncora (`ANCHOR-LINES.md`).\n"
        "3. Dê o caso de teste. Salve a saída crua de cada conversa.\n"
        "4. Abra 1 conversa de juiz nova. Anexe as 3 saídas e o que está em\n"
        "   `JUDGE-ATTACHMENTS.md`.\n"
        "5. Confira tudo contra `SHA256SUMS.txt` antes de começar.\n")
    n_lines = len(readme.splitlines())
    if n_lines > 15:
        raise SystemExit(f"README-ABERTURA.md tem {n_lines} linhas; limite 15")
    (OUT / "README-ABERTURA.md").write_text(readme, encoding="utf-8")

    files = sorted(p for p in OUT.iterdir() if p.is_file()
                   and p.name != "SHA256SUMS.txt")
    (OUT / "SHA256SUMS.txt").write_text(
        f"# BLIND_RUN_READY v0.1.4 — gerado {stamp}\n"
        "# Hashes dos arquivos DESTA pasta. Os pacotes de braço são referenciados,\n"
        "# não copiados; os hashes deles estão em CANDIDATE-ATTACHMENTS.md.\n"
        + "".join(f"{sha256b(p.read_bytes())}  {p.stat().st_size}  {p.name}\n"
                 for p in files),
        encoding="utf-8")

    n = len(open(OUT / "README-ABERTURA.md", encoding="utf-8").read().splitlines())
    print(f"pasta: {OUT}")
    print(f"README-ABERTURA.md: {n} linhas (limite 15)")
    print(f"âncora candidata: {anchor!r}")
    for p in sorted(OUT.iterdir()):
        print(f"  {p.stat().st_size:6d}  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
