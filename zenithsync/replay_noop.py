"""Verify a rejected identical edit without replacing its native observation."""
import hashlib
import json
from pathlib import PurePosixPath
import re
import shlex


def identical_edit(arguments):
    return (isinstance(arguments, dict)
            and isinstance(arguments.get('old_str'), str)
            and bool(arguments['old_str'])
            and arguments.get('new_str') == arguments['old_str'])


def snapshot_file(manager, container_id, path, text):
    """Read a bounded regular UTF-8 source file inside the owned container."""
    relative = PurePosixPath(path)
    if (not isinstance(path, str) or relative.is_absolute()
            or relative.as_posix() != path or '..' in relative.parts or path == '.'):
        raise ValueError('Canonical relative no-op path required')
    program = r'''
import hashlib,json,pathlib,stat,sys
p=pathlib.Path('/workspace')/sys.argv[1]
assert p.resolve()==p
before=p.stat()
assert stat.S_ISREG(before.st_mode) and before.st_size<=4*1024**2
with p.open('rb') as stream:body=stream.read(4*1024**2+1)
assert len(body)==before.st_size
fields=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
assert fields(before)==fields(p.stat())
print(json.dumps({'sha256':hashlib.sha256(body).hexdigest(),'size_bytes':len(body),'stat':list(fields(before)),'occurrences':body.decode('utf-8').count(sys.argv[2])}))
'''
    result = manager.exec(container_id, shlex.join(['python', '-c', program, path, text]), timeout=10)
    if result.exit_code:
        raise ValueError('No-op file snapshot failed')
    value = json.loads(result.stdout)
    if (not isinstance(value, dict)
            or set(value) != {'sha256', 'size_bytes', 'stat', 'occurrences'}
            or not isinstance(value['sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', value['sha256']) is None
            or type(value['size_bytes']) is not int or not 0 < value['size_bytes'] <= 4*1024**2
            or type(value['occurrences']) is not int or value['occurrences'] != 1
            or not isinstance(value['stat'], list) or len(value['stat']) != 6
            or any(type(part) is not int for part in value['stat'])):
        raise ValueError('Unique matching no-op source required')
    return value


def verify_rejected_noop(arguments, result, before, after):
    if not identical_edit(arguments):
        raise ValueError('Nonempty identical edit required')
    expected = {'status': 'error', 'error_type': 'FileEditError',
                'error_message': 'No changes to apply. old_string and new_string are identical.'}
    if result != expected:
        raise ValueError('Unexpected no-op editor result')
    if before != after or before.get('occurrences') != 1:
        raise ValueError('No-op target changed or match was not unique')
    return {'kind': 'verified_rejected_identical_edit', 'before': before, 'after': after,
            'text_sha256': hashlib.sha256(arguments['old_str'].encode('utf-8')).hexdigest(),
            'native_error_preserved': True}
