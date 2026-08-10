#!/usr/bin/env python3
"""Runner mínimo — o ambiente não tem pytest e instalar dependência não é
decisão desta fase. Executa toda função test_* de tests/."""
import importlib.util, sys, traceback, shutil
from pathlib import Path

HERE = Path(__file__).parent
shutil.rmtree(HERE / "tests/_tmp", ignore_errors=True)
ok = fail = 0
falhas = []
for f in sorted((HERE / "tests").glob("test_*.py")):
    spec = importlib.util.spec_from_file_location(f.stem, f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name in sorted(dir(mod)):
        if not name.startswith("test_"):
            continue
        try:
            getattr(mod, name)()
            ok += 1
        except Exception:
            fail += 1
            falhas.append((f.name, name, traceback.format_exc().strip().splitlines()[-1]))
for a, b, c in falhas:
    print(f"FALHOU {a}::{b}\n    {c}")
print(f"\n{ok} passaram, {fail} falharam")
sys.exit(1 if fail else 0)
