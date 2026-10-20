"""Build read-only, credential-free P1 handoff indexes; never hydrate placeholders."""
import ast
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import stat
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SECRET_NAMES = {'.env', 'recovery.env', '.env.local'}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def available(path):
    s = path.lstat()
    return stat.S_ISREG(s.st_mode) and not s.st_flags & getattr(stat, 'UF_DATALESS', 0x40000000)
def write_json(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
def link(path):
    return '../../'+str(path.relative_to(ROOT))
files=[];symbols=[];parse_errors=[]
for folder in ('zenithsync','scripts','tests','configs','requirements','examples','candidates'):
    for path in sorted((ROOT/folder).rglob('*')):
        if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts or path.name in SECRET_NAMES or path.suffix=='.pyc':continue
        rel=str(path.relative_to(ROOT));record={'path':rel,'bytes':path.stat().st_size,'materialized':available(path)}
        if not available(path):files.append(record);continue
        # Hash code/config, not large model or binary payloads in candidates.
        if path.stat().st_size>2*1024**2:files.append(record);continue
        record['sha256']=sha(path)
        if path.suffix=='.py':
            try:
                tree=ast.parse(path.read_text());record['description']=ast.get_docstring(tree) or '(No module docstring; inspect source.)'
                for node in ast.walk(tree):
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                        signature=node.name
                        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):signature+='('+ast.unparse(node.args)+')'
                        symbols.append({'file':rel,'line':node.lineno,'kind':type(node).__name__,'symbol':signature,'description':ast.get_docstring(node) or ''})
            except (SyntaxError,UnicodeError) as error:parse_errors.append({'file':rel,'error':type(error).__name__})
        files.append(record)
write_json('code-inventory.json',files);write_json('symbols.json',symbols)
with (OUT/'code-catalog.md').open('w') as f:
    f.write('# Complete code, configuration and test catalog\n\nGenerated from the current checkout. Presence/docstrings are not proof of qualification.\nSee `code-inventory.json` for hashes and `symbols.json` for every parsed class/function in materialized files,\nincluding test methods and line numbers. Tests describe intended checks, not results.\n\n')
    for record in files:
        f.write('## ['+record['path']+'](../../'+record['path']+')\n\n')
        f.write(record.get('description','Configuration, dependency specification or non-Python asset; inspect linked content.')+'\n\n')
        f.write(f"Size: {record['bytes']} bytes. Materialized: {record['materialized']}.\n\n")
# Every repository evidence/artifact file is indexed without opening its contents.
counts=Counter();packages=Counter();bytes_by=Counter();index_count=0
with (OUT/'artifact-files.tsv').open('w',newline='') as stream:
    writer=csv.writer(stream,delimiter='\t');writer.writerow(['path','logical_bytes','allocated_bytes','materialized','symlink'])
    for category in ('evidence','artifacts','reproduction'):
        for directory,subdirs,names in os.walk(ROOT/category,followlinks=False):
            subdirs[:]=sorted(d for d in subdirs if not (Path(directory)/d).is_symlink() and d!='__pycache__')
            for name in sorted(names):
                path=Path(directory)/name
                if name in SECRET_NAMES or name.endswith(('.env','.pem','.key','.pyc')):continue
                s=path.lstat();rel=path.relative_to(ROOT);materialized=stat.S_ISREG(s.st_mode) and not s.st_flags & getattr(stat,'UF_DATALESS',0x40000000)
                writer.writerow([str(rel),s.st_size,s.st_blocks*512,materialized,stat.S_ISLNK(s.st_mode)])
                index_count+=1;counts[category]+=1
                package='/'.join(rel.parts[:3]);packages[package]+=1;bytes_by[package]+=s.st_size
with (OUT/'evidence-catalog.md').open('w') as f:
    f.write('# Evidence and artifact directory index\n\nEvery non-secret file is listed in `artifact-files.tsv`, including failed and\nsuperseded attempts. Logical bytes include placeholders and are not resident usage.\nDirectory names do not establish pass/fail or current status; consult receipts.\n\n| Directory | Files | Logical bytes |\n|---|---:|---:|\n')
    for package,count in sorted(packages.items()):f.write(f'| [{package}](../../{package}) | {count} | {bytes_by[package]} |\n')
# All existing planning/research documents remain authoritative historical source material.
with (OUT/'document-map.md').open('w') as f:
    f.write('# Existing document map\n\nDocuments are versioned narratives; later receipts override earlier status claims.\nHeadings below are extracted verbatim. Research 01–18 is not proof of implementation.\n\n')
    for path in sorted((ROOT/'docs').glob('*.md')):
        if path.name.startswith('41-') or not available(path):continue
        f.write('## ['+path.name+'](../'+path.name+')\n\n')
        f.write('\n'.join('- '+line.lstrip('# ') for line in path.read_text().splitlines() if line.startswith(('# ','## ','### ')))+'\n\n')
base=Path('/Users/jiangshengbo/.codex/zenithsync-p1-recovered/corpus072')
manifest=json.loads((base/'corpus.json').read_text());reviews=json.loads((ROOT/'evidence/data/corpus072-integration-001/task-reviews.json').read_text())
review_by={r['task_id']:r for r in reviews['task_reviews']};tasks=[]
for row in manifest['examples']:
    audit=json.loads((base/row['audit']['path']).read_text());tokens=json.loads((base/row['tokens']['path']).read_text())
    tasks.append({**row,'input_tokens':len(tokens['input_ids']),'shifted_targets':sum(x!=-100 for x in tokens['labels'][1:]),'history':audit['history'],'synthetic_provenance':audit.get('synthetic_provenance'),'review':review_by[row['task_id']]})
write_json('current-task-ledger.json',tasks)
with (OUT/'current-task-ledger.md').open('w') as f:
    f.write('# Every selected Corpus072 task\n\nAll 51 are quarantined, provisionally train, and development-exposed.\nTask acceptance is bounded behavioral review, not training/rights approval.\nFull identities, repository/leakage groups and review rationale: `current-task-ledger.json`.\nAbsent synthetic metadata does not mean an untouched human or model trajectory.\n\n| Task | Repository | Inputs | Shifted targets | Explicit synthetic | Review |\n|---|---|---:|---:|---|---|\n')
    for r in tasks:f.write(f"| {r['task_id']} | {r['repository_group']} | {r['input_tokens']} | {r['shifted_targets']} | {bool(r['synthetic_provenance'])} | {r['review']['decision']} |\n")
write_json('inventory-report.json',{'code_files':len(files),'symbols':len(symbols),'parse_errors':parse_errors,'artifact_files':index_count,'artifact_counts':dict(counts),'evidence_packages':len(packages),'tasks':len(tasks),'input_tokens':sum(r['input_tokens'] for r in tasks),'shifted_targets':sum(r['shifted_targets'] for r in tasks),'corpus_sha256':sha(base/'corpus.json'),'limitations':['Filesystem snapshot only; no remote cloud state read.','No secret values, hidden environments or private keys copied.','Artifact file listing does not verify artifact contents.','External recovery directory and model location documented separately; not recursively copied.']})
print(json.dumps({'code_files':len(files),'symbols':len(symbols),'artifact_files':index_count,'tasks':len(tasks),'parse_errors':parse_errors}))
