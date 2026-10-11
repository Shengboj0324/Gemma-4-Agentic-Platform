"""Validate explicit checkout-relative import roots for offline Python runtimes."""
import re


def source_pythonpath(import_root, checkout):
    """Map a reviewed relative directory without accepting path-list injection.

    This validates lexical paths only. Runtime module-origin checks must still
    prove that imports resolve to the intended checkout file.
    """
    if checkout not in ('/workspace', '/testbed'):
        raise ValueError('Unsupported checkout root')
    if (not isinstance(import_root, str)
            or re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*', import_root) is None):
        raise ValueError('Canonical relative import directory required')
    return checkout + '/' + import_root
