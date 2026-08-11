#!/usr/bin/env python3
"""Create the content-addressed pre-run lock registry and opening record.

The resulting registry must be frozen before any blind prompt is sent. The
opening record stores the registry SHA-256; the scorer later verifies this
chain and never relies on filesystem mtimes.
"""
from __future__ import annotations
import argparse, hashlib
from datetime import datetime, timezone
from pathlib import Path
import yaml


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding='utf-8')) or {}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--comparison-lock', required=True)
    ap.add_argument('--metric-lock', required=True)
    ap.add_argument('--registry-out', required=True)
    ap.add_argument('--opening-record-out', required=True)
    ap.add_argument('--extra-artifact', action='append', default=[], help='Additional frozen artifact as NAME=PATH; may be repeated')
    args=ap.parse_args()
    comp=Path(args.comparison_lock); metric=Path(args.metric_lock)
    if not comp.exists() or not metric.exists():
        print('INVALID: both lock files must exist'); return 2
    if load(comp).get('artifact_status')!='LOCKED' or load(metric).get('artifact_status')!='LOCKED':
        print('INVALID: both lock files must be LOCKED before registry freeze'); return 2
    extras={}
    for item in args.extra_artifact:
        if '=' not in item:
            print(f'INVALID: --extra-artifact must be NAME=PATH, got {item!r}'); return 2
        name, raw = item.split('=',1); name=name.strip(); ep=Path(raw)
        if not name or not ep.exists():
            print(f'INVALID: additional artifact missing or unnamed: {item!r}'); return 2
        data=load(ep) if ep.suffix.lower() in {'.yaml','.yml'} else {}
        extras[name]={'path':ep.name,'sha256':sha256_file(ep),'artifact_status':data.get('artifact_status') if isinstance(data,dict) else None}
    now=datetime.now(timezone.utc).isoformat()
    registry={
        'schema_version':'0.1.0',
        'artifact_status':'LOCKED_PRE_RUN',
        'candidate_version':'0.1.3',
        'frozen_before_blind_round':True,
        'registered_at_utc':now,
        'locks':{
            'comparison_margin':{'path':comp.name,'sha256':sha256_file(comp)},
            'metric_derivation':{'path':metric.name,'sha256':sha256_file(metric)},
        },
        'artifacts': extras,
        'mtime_used_as_evidence':False,
    }
    reg=Path(args.registry_out)
    reg.write_text(yaml.safe_dump(registry,sort_keys=False,allow_unicode=True),encoding='utf-8')
    reg_sha=sha256_file(reg)
    opening={
        'schema_version':'0.1.0',
        'artifact_status':'FROZEN_BEFORE_BLIND_ROUND',
        'candidate_version':'0.1.3',
        'opened_at_utc':now,
        'pre_run_lock_registry_path':reg.name,
        'pre_run_lock_registry_sha256':reg_sha,
        'comparison_lock_sha256':sha256_file(comp),
        'metric_lock_sha256':sha256_file(metric),
        'additional_artifact_hashes':{k:v['sha256'] for k,v in extras.items()},
        'instruction':'Persist this opening record before sending any blind candidate prompt.',
        'external_temporal_anchor_required':True,
        'external_anchor_message_template':'PRE-RUN-OPENING-RECORD SHA-256: <sha256>',
        'scorer_claim_limit':'This content-addressed chain proves integrity; transcript anchoring supplies temporal witness.',
    }
    op=Path(args.opening_record_out)
    op.write_text(yaml.safe_dump(opening,sort_keys=False,allow_unicode=True),encoding='utf-8')
    opening_sha=sha256_file(op)
    print(f'VALID: registry={reg_sha} opening_record={opening_sha}')
    print(f'ANCHOR_FIRST_MESSAGE: PRE-RUN-OPENING-RECORD SHA-256: {opening_sha}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
