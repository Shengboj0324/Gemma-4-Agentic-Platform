"""Conservative source-text credential indicators, never credential validation.

Reports contain only rule names and character locations. Absence of indicators
is not proof of absence of secrets; flagged examples require review, not silent
redaction that would break trajectory provenance.
"""
import json
import re

_MAX_JSON_LAYERS = 16
_MAX_JSON_CHARACTERS = 16 * 1024**2


def _preserve_json_members(pairs):
    # Keep duplicate keys: ordinary JSON decoding would discard earlier values.
    return [{key: value} for key, value in pairs]

_RULES = (
    ('private_key_header', re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----')),
    ('aws_access_key_id', re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
    ('github_token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b')),
    ('authorization_literal', re.compile(
        r'''(?ix)\b(?:proxy-)?authorization\b["']?\s*[:=]\s*["']?
        (?:bearer\s+|basic\s+)?(?P<value>[A-Za-z0-9_./+~=-]{20,})''')),
)


def scan_text(text):
    """Return deterministic non-secret diagnostics; offsets are Unicode characters."""
    if not isinstance(text, str):
        raise TypeError('Source text must be a string')
    findings = []
    for rule, pattern in _RULES:
        for match in pattern.finditer(text):
            start, end = match.span('value') if 'value' in pattern.groupindex else match.span()
            findings.append({'rule': rule, 'start': start, 'end': end,
                             'line': text.count('\n', 0, start) + 1})
    return sorted(findings, key=lambda row: (row['start'], row['end'], row['rule']))


def require_no_credential_indicators(value):
    """Reject indicators anywhere in a decoded source message tree before replay.

    Dictionary authorization fields are scanned together with their values.
    JSON-encoded observations are also decoded, preserving duplicate members.
    Decoding has aggregate character and nesting limits; exceeding either fails
    closed. Malformed JSON is still scanned as text, not executed or repaired.
    Errors deliberately omit values, field names and snippets. This is a narrow
    indicator gate, not a general secret detector or training admission gate.
    """
    pending = [(value, 0)]
    # Retain objects as well as IDs: decoded objects must not be collected and
    # have their IDs reused while another branch remains to be scanned.
    visited = {}
    decoded_characters = 0
    while pending:
        current, layers = pending.pop()
        if isinstance(current, str):
            if scan_text(current):
                raise ValueError('Source credential indicator requires review before replay')
            stripped = current.strip()
            if stripped[:1] in ('{', '[', '"'):
                decoded_characters += len(current)
                if layers >= _MAX_JSON_LAYERS or decoded_characters > _MAX_JSON_CHARACTERS:
                    raise ValueError('Source credential screening JSON limit exceeded')
                try:
                    decoded = json.loads(current, object_pairs_hook=_preserve_json_members)
                except json.JSONDecodeError:
                    continue
                except RecursionError:
                    raise ValueError('Source credential screening JSON limit exceeded') from None
                pending.append((decoded, layers + 1))
        elif isinstance(current, (dict, list)):
            identity = id(current)
            if identity in visited:
                continue
            visited[identity] = current
            if isinstance(current, dict):
                for key, item in current.items():
                    if isinstance(key, str) and key.casefold() in ('authorization', 'proxy-authorization'):
                        if isinstance(item, str) and scan_text('Authorization: ' + item):
                            raise ValueError('Source credential indicator requires review before replay')
                    pending.extend(((key, layers), (item, layers)))
            else:
                pending.extend((item, layers) for item in current)
