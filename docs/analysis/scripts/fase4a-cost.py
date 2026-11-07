import json, os, sys, glob, collections, datetime

ROOT = sys.argv[1]
T = os.path.join(ROOT, 'transcripts')
ses = json.load(open(os.path.join(ROOT, 'sesiones.json'), encoding='utf-8'))

# USD per million tokens (input, output), as the retro used (prompts/models.md); Fable valued as Opus
PRICE = {'opus': (4, 20), 'fable': (4, 20), 'sonnet': (2, 10), 'haiku': (1, 5)}

def fam(model):
    m = (model or '').lower()
    for k in PRICE:
        if k in m:
            return k
    return None

def cost(u, model):
    f = fam(model)
    if not f:
        return 0.0
    pi, po = PRICE[f]
    i = u.get('input_tokens', 0) + 1.25 * u.get('cache_creation_input_tokens', 0) + 0.1 * u.get('cache_read_input_tokens', 0)
    return (i * pi + u.get('output_tokens', 0) * po) / 1e6

owner = {}  # cli id -> (role, part)
for s in ses['sessions']:
    for c in s.get('cliTranscripts', []):
        owner[c] = (s['role'], s.get('part'))
    for c in s.get('sideQuestions', []):
        owner[c] = ('coordinator-side', None)

seen = set()
PH = collections.Counter()
agg = collections.defaultdict(lambda: {'usd': 0.0, 'in': 0, 'out': 0, 'cw': 0, 'cr': 0, 'msgs': 0, 'models': collections.Counter(), 'first': None, 'last': None})

def add(key, d):
    m = d.get('message') or {}
    mid = m.get('id')
    u = m.get('usage')
    ts = d.get('timestamp')
    a = agg[key]
    if ts and d.get('type')=='assistant' and u and mid and mid not in seen:
        ph = 'A' if ts < '2026-10-31T03:18:36' else ('B' if ts < '2026-10-31T09:30' else 'C')
        PH[(key if key.startswith('coord') else key.split(':')[0], ph)] += cost(u, m.get('model'))
    if ts:
        a['first'] = min(a['first'] or ts, ts)
        a['last'] = max(a['last'] or ts, ts)
    if d.get('type') != 'assistant' or not u or not mid or mid in seen:
        return
    seen.add(mid)
    a['usd'] += cost(u, m.get('model'))
    a['in'] += u.get('input_tokens', 0)
    a['out'] += u.get('output_tokens', 0)
    a['cw'] += u.get('cache_creation_input_tokens', 0)
    a['cr'] += u.get('cache_read_input_tokens', 0)
    a['msgs'] += 1
    a['models'][m.get('model')] += 1

def rows(path):
    with open(path, encoding='utf-8') as fh:
        for l in fh:
            try:
                yield json.loads(l)
            except Exception:
                pass

def classify_sub(meta, parent_role):
    desc = (meta.get('description') or '').lower()
    at = (meta.get('agentType') or '').lower()
    if parent_role.startswith('coordinator'):
        if 'retro' in desc:
            return 'coord-sub:retro'
        if 'qa' in desc.split() :
            return 'coord-sub:qa'
        if any(w in desc for w in ('review', 'audit', 'auditor', 'revis', 'delta', 'final', 'slice', 'batch', 'lote')):
            return 'coord-sub:review/audit'
        if 'implement' in desc or 'q5' in desc or 'cierre' in desc:
            return 'coord-sub:implementer'
        return 'coord-sub:other'
    if 'critic' in desc or 'critic' in at:
        return 'impl-sub:critic'
    if 'reviewer' in at or 'review' in desc or 'revis' in desc:
        return 'impl-sub:reviewer'
    return 'impl-sub:other'

subdesc = collections.defaultdict(list)
# main transcripts first, so dedupe keeps the owner of a message that appears in side-question copies
order = [c for s in ses['sessions'] for c in s.get('cliTranscripts', [])] + [c for s in ses['sessions'] for c in s.get('sideQuestions', [])]
for cid in order:
    role, part = owner[cid]
    key = 'coordinator' if role.startswith('coordinator') else f'impl:{part}'
    p = os.path.join(T, cid + '.jsonl')
    if os.path.exists(p):
        for d in rows(p):
            add(key, d)
for cid in order:
    role, part = owner[cid]
    for sp in sorted(glob.glob(os.path.join(T, cid, 'subagents', '*.jsonl'))):
        mp = sp[:-6] + '.meta.json'
        meta = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
        k = classify_sub(meta, role)
        bucket = k if k.startswith('coord') else f'{k}:{part}'
        n0 = len(seen)
        for d in rows(sp):
            add(bucket, d)
        if len(seen) > n0:
            subdesc[bucket].append((meta.get('description'), meta.get('model'), meta.get('agentType')))

out = {}
for k, a in sorted(agg.items()):
    out[k] = {'usd': round(a['usd'], 2), 'msgs': a['msgs'], 'out': a['out'], 'in_total': a['in'] + a['cw'] + a['cr'], 'models': dict(a['models']), 'first': a['first'], 'last': a['last']}
json.dump({'agg': out, 'subs': {k: v for k, v in subdesc.items()}}, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('PHASES'); [print(k, round(v,2)) for k,v in sorted(PH.items())]
tot = sum(a['usd'] for a in agg.values())
print('TOTAL', round(tot, 2))
for k, a in sorted(out.items(), key=lambda x: -x[1]['usd']):
    print(f"{k:40} {a['usd']:9.2f} {a['msgs']:6} {a['first'][:16] if a['first'] else ''} {a['last'][:16] if a['last'] else ''} {a['models']}")
