"""MS-002 — transporte de modelo. Route B: processo `claude -p` novo por chamada,
OAuth Claude Max. PAYG PROIBIDA. Contrato de invocacao congelado (DR MS-001B)."""
import os, json, shutil, subprocess, datetime, pathlib, hashlib

MODEL = "claude-opus-5"
CLAUDE = shutil.which("claude") or "/home/mtx/.local/bin/claude"
FORBIDDEN_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_USE_BEDROCK",
                 "CLAUDE_CODE_USE_VERTEX", "AWS_BEARER_TOKEN_BEDROCK")
FLAGS = ["-p", "--model", MODEL, "--tools", "", "--disable-slash-commands",
         "--strict-mcp-config", "--no-session-persistence", "--permission-mode", "dontAsk",
         "--setting-sources", "", "--settings", '{"alwaysThinkingEnabled":false}',
         "--output-format", "json"]
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()

def guard_env():
    bad = [v for v in FORBIDDEN_ENV if os.environ.get(v)]
    if bad:
        raise SystemExit(f"HARD STOP — variavel PAYG proibida definida: {bad}")

def child_env():
    e = dict(os.environ)
    for v in FORBIDDEN_ENV:
        e.pop(v, None)
    e["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    return e

class Budget:
    def __init__(self, cap): self.cap = cap; self.n = 0; self.calls = []

def call(budget, sysfile, user_text, outdir, label, timeout=2400):
    """Uma invocacao fresh. Devolve (texto, registro). Fail-closed."""
    guard_env()
    if budget.n >= budget.cap:
        raise SystemExit(f"HARD CAP {budget.cap} atingido — MS_002_INVALID")
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{label}-USER.txt").write_text(user_text, encoding="utf-8")
    t0 = datetime.datetime.now().astimezone().isoformat()
    p = subprocess.run([CLAUDE] + FLAGS + ["--system-prompt-file", str(sysfile)],
                       input=user_text, capture_output=True, text=True,
                       env=child_env(), cwd=str(outdir), timeout=timeout)
    t1 = datetime.datetime.now().astimezone().isoformat()
    (outdir / f"{label}-STDOUT.json").write_text(p.stdout, encoding="utf-8")
    if p.stderr:
        (outdir / f"{label}-STDERR.txt").write_text(p.stderr, encoding="utf-8")
    if p.returncode != 0:
        low = (p.stderr or "") + (p.stdout or "")
        if "limit" in low.lower() and "usage" in low.lower():
            raise SystemExit("MS_PROJECT_PAUSED_MAX_PLAN_LIMIT")
        raise SystemExit(f"HARD STOP — exit {p.returncode} em {label}: {p.stderr[:400]}")
    d = json.loads(p.stdout)
    if d.get("is_error"):
        r = str(d.get("result"))
        if "usage limit" in r.lower() or "rate limit" in r.lower():
            raise SystemExit("MS_PROJECT_PAUSED_MAX_PLAN_LIMIT")
        raise SystemExit(f"HARD STOP — is_error em {label}: {r[:400]}")
    models = list(d.get("modelUsage", {}).keys())
    if models != [MODEL]:
        raise SystemExit(f"model_resolved={models} != [{MODEL}] — MS_002_INVALID")
    txt = d["result"]
    (outdir / f"{label}-RAW.txt").write_text(txt, encoding="utf-8")
    budget.n += 1
    rec = {"call_seq": budget.n, "label": label, "model_requested": MODEL,
           "model_resolved": models[0], "stop_reason": d.get("stop_reason"),
           "num_turns": d.get("num_turns"),
           "thinking_tokens": d["usage"].get("output_tokens_details", {}).get("thinking_tokens"),
           "usage": {k: d["usage"].get(k) for k in
                     ("input_tokens", "cache_creation_input_tokens",
                      "cache_read_input_tokens", "output_tokens", "service_tier")},
           "system_sha256": sha(pathlib.Path(sysfile).read_text(encoding="utf-8")),
           "user_sha256": sha(user_text), "output_sha256": sha(txt),
           "exit_code": p.returncode, "started_at": t0, "finished_at": t1,
           "cost_estimate_usd_list_price": d.get("total_cost_usd"),
           "auth_path": "CLAUDE_CODE_MAX_OAUTH_PRINT_MODE", "payg": False}
    budget.calls.append(rec)
    return txt, rec

def jparse(t):
    t = t.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    a, b = t.find("{"), t.rfind("}")
    return t[a:b + 1] if a >= 0 else t

def split_prompt(t):
    a = t.index("[SYSTEM]"); b = t.index("[USER]")
    return t[a + 8:b].strip(), t[b + 6:].strip()
