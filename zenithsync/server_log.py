"""Keep the official inference server's log, which its stop() deletes.

`adk_submission.VllmServer.stop()` unlinks its temporary log file. A hard link
taken before stopping keeps every byte, shutdown lines included; the text is
then copied to `destination` and the link removed.
"""
import os
from pathlib import Path
import shutil


def stop_keeping_log(server, destination):
    """Stop `server`; write its full log to `destination`; return the text ('' if none)."""
    source = Path(server.log_path) if getattr(server, 'log_path', None) else None
    keep = None
    if source is not None and source.exists():
        keep = source.with_name(source.name + '.kept')
        if keep.exists():
            keep.unlink()
        os.link(source, keep)
    try:
        server.stop()
    finally:
        text = ''
        if keep is not None:
            shutil.copyfile(keep, destination)
            keep.unlink()
            text = Path(destination).read_text(errors='replace')
    return text
