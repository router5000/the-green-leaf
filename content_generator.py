#!/usr/bin/env python3
"""Cannabis Content Generator — multipart zlib payload (MCP push size limits)."""
import zlib as _zlib
import base64 as _base64
from pathlib import Path as _Path
_p = _Path(__file__).resolve().parent
_PAYLOAD = "".join((_p / f"_cg_payload_{i}.txt").read_text() for i in range(3))
exec(
    compile(
        _zlib.decompress(_base64.b64decode("".join(_PAYLOAD.split()))),
        __file__,
        "exec",
    ),
    globals(),
)
