"""Exact historical evaluator body for read-only receipt verification.

Uses Python 3.7+ subprocess aliases; current execution uses the current probe.
Do not normalize unknown program bodies into this accepted historical version."""

PROBE = r'''
import base64,hashlib,json,os,pathlib,subprocess
out=pathlib.Path('/audit');out.mkdir()
result={'role':ROLE,'tests_started':False}
def git(*args):
    return subprocess.run(['git','-c','safe.directory=/testbed',*args],cwd='/testbed',
                          capture_output=True,check=True,timeout=30).stdout
try:
    if git('rev-parse','HEAD').decode().strip()!=BASE:
        raise RuntimeError('Wrong checkout base')
    if TREE and git('rev-parse','HEAD^{tree}').decode().strip()!=TREE:
        raise RuntimeError('Wrong checkout tree')
    if git('status','--porcelain','--untracked-files=no').strip():
        raise RuntimeError('Checkout has tracked changes before evaluation')
    for name in ([ROLE] if ROLE in ('reference','candidate') else [])+['tests']:
        patch=pathlib.Path('/tmp/'+name+'.patch');patch.write_bytes(base64.b64decode(PATCHES[name]))
        if patch.stat().st_size:
            options=['--index'] if name=='candidate' else []
            git('apply',*options,'--check',str(patch));git('apply',*options,str(patch))
        if name=='candidate':
            changed=git('diff','--name-only','HEAD','--').decode().splitlines()
            if any(path not in ALLOWED_PATHS for path in changed):
                raise RuntimeError('Candidate changes outside task-specific source allowance')
    python=PYTHON
    source_path=globals().get('SOURCE_PYTHONPATH', '')
    origin_env={**os.environ, 'PYTHONPATH':source_path} if source_path else None
    origin=subprocess.run([python,'-c','import importlib; print(importlib.import_module('+repr(MODULE)+').__file__)'],cwd='/testbed',env=origin_env,
                          capture_output=True,text=True,timeout=30)
    result['import']={'returncode':origin.returncode,'stdout':origin.stdout.strip(),'stderr':origin.stderr}
    if origin.returncode or origin.stdout.strip()!=EXPECTED_ORIGIN:
        raise RuntimeError('Module does not import from task checkout')
    (out/'audit_plugin.py').write_text(PLUGIN)
    if globals().get('SESSION_RESOURCE_PAYLOAD'):
        import zlib
        (out/'session_resources.json').write_bytes(zlib.decompress(base64.b64decode(SESSION_RESOURCE_PAYLOAD)))
        (out/'session_resource_replay.py').write_text(SESSION_RESOURCE_ADAPTER)
    if RESOURCE_PAYLOAD:
        import zlib
        (out/'resources.json').write_bytes(zlib.decompress(base64.b64decode(RESOURCE_PAYLOAD)))
        (out/'offline_resources.py').write_text(RESOURCE_ADAPTER)
    env={**os.environ,'PYTHONPATH':'/audit'+(':'+source_path if source_path else ''),'PYTHONDONTWRITEBYTECODE':'1'}
    before=hashlib.sha256(git('diff','--binary','HEAD','--')).hexdigest()
    result['tests_started']=True
    with (out/'pytest.log').open('w') as log:
        test=subprocess.run([python,'-m','pytest','--no-header','-rA','--tb=line','--color=no',
            '-p','no:cacheprovider','-W','ignore::DeprecationWarning','-p','audit_plugin',
            '--junitxml=/audit/junit.xml',*TEST_TARGETS],cwd='/testbed',env=env,
            stdout=log,stderr=subprocess.STDOUT,timeout=240)
    result['pytest_exit']=test.returncode
    result['tracked_diff_unchanged_by_tests']=hashlib.sha256(git('diff','--binary','HEAD','--')).hexdigest()==before
except Exception as error:
    result['error_type']=type(error).__name__
    result['error']=str(error)[:2000]
finally:
    (out/'runtime.json').write_text(json.dumps(result))
'''
