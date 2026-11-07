import json, os, sys, collections, re

ROOT = sys.argv[1]
T = os.path.join(ROOT, 'transcripts')
COORD = ['e5da6d1e-5b9b-49d5-8fb2-212602867809', 'e15027ef-b2bb-4f95-b5bd-64a48b26de37', '7df70928-d0da-4ed3-bc51-6d2218f9e4b8', 'ee541cfc-b95e-4df1-a344-9a6fcbdbf1c5']

def rows(p):
    for l in open(p, encoding='utf-8'):
        try:
            yield json.loads(l)
        except Exception:
            pass

def text_of(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return '\n'.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
    return ''

turns = []          # (ts, kind, phase, snippet)
starts = []         # (ts, initiation, ok, snippet)
sends = collections.Counter()
sendq = []
compacts = []
seen_uuid = set()
pending = {}
for cid in COORD:
    for d in rows(os.path.join(T, cid + '.jsonl')):
        u = d.get('uuid')
        if u in seen_uuid:
            continue
        seen_uuid.add(u)
        ts = d.get('timestamp', '')
        if d.get('type') == 'system' and d.get('subtype') == 'compact_boundary':
            compacts.append(ts)
        m = d.get('message') or {}
        c = m.get('content')
        t = None
        if d.get('type') == 'user' and not d.get('isMeta') and not d.get('isCompactSummary'):
            t = text_of(c)
            if not t.strip():
                t = None
        if d.get('type') == 'user' and not d.get('isMeta') and not d.get('isCompactSummary') and t:
            if '<side-sessions-event' in t:
                k = 'side-sessions-event'
            elif '<cross-session-message' in t or t.startswith('From ') or 'Another Claude session sent a message' in t:
                k = 'peer-message'
            elif '<task-notification' in t:
                k = 'task-notification'
            elif '<command-name>' in t or t.startswith('Base directory for this skill'):
                k = 'skill-load'
            elif '<system-reminder>' in t and len(re.sub(r'<system-reminder>.*?</system-reminder>', '', t, flags=re.S).strip()) == 0:
                k = 'reminder-only'
            elif 'session you started' in t and 'finished a turn' in t:
                k = 'side-sessions-event'
            else:
                k = 'person'
            ph = 'A' if ts < '2026-10-31T03:18:36' else ('B' if ts < '2026-10-31T09:30' else 'C')
            snippet = re.sub(r'<system-reminder>.*?</system-reminder>', '', t, flags=re.S).strip().replace('\n', ' ')[:140]
            turns.append((ts, k, ph, snippet))
        if d.get('type') == 'assistant' and isinstance(c, list):
            for x in c:
                if x.get('type') == 'tool_use':
                    n = x.get('name', '')
                    if 'start_session' in n:
                        pending[x['id']] = ('start', ts, x['input'].get('initiation'), x['input'].get('name') or x['input'].get('title'))
                    elif n in ('SendMessage',) or n.endswith('send_message'):
                        pending[x['id']] = ('send', ts, None, None)
                        sends[ts[:10]] += 1
        if d.get('type') == 'user' and isinstance(c, list):
            for x in c:
                if x.get('type') == 'tool_result' and x.get('tool_use_id') in pending:
                    kind, t0, ini, nm = pending.pop(x['tool_use_id'])
                    r = json.dumps(x.get('content'), ensure_ascii=False)
                    if kind == 'start':
                        ok = 'Started session' in r or 'session_id' in r and 'Proposed' not in r
                        starts.append((t0, ini, nm, r[:180]))
                    elif 'queued' in r.lower():
                        sendq.append((t0, r[:120]))

cnt = collections.Counter((k, ph) for _, k, ph, _ in turns)
print('TURNS by kind/phase', dict(sorted(cnt.items())))
print('COMPACTIONS', len(compacts), compacts)
print('SENDS total', sum(sends.values()), 'queued', len(sendq))
for q in sendq:
    print('  Q', q)
print('STARTS', len(starts))
for s in starts:
    print('  S', s)
print('PERSON TURNS')
for ts, k, ph, sn in turns:
    if k == 'person':
        print('  ', ts[:16], ph, sn)
