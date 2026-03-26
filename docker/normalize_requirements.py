#!/usr/bin/env python3
"""
Normaliza `requirements.txt` para UTF-8 (evita problema de UTF-16 do Windows)
e remove linhas de dependências que nao existem no PyPI (ex.: flask-json-provider).
"""

from __future__ import annotations

import pathlib
import sys


DROP_PREFIXES = ("flask-json-provider",)


def decode_bytes(raw: bytes) -> tuple[str, str]:
    if raw.startswith(b"\xff\xfe"):
        return raw[2:].decode("utf-16-le"), "utf-16-le-bom"
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be"), "utf-16-be-bom"
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8"), "utf-8-bom"

    sample = raw[: min(4096, len(raw))]
    # Heuristica: muito byte nulo => provavelmente UTF-16
    if sample.count(0) > max(8, len(sample) // 8):
        return raw.decode("utf-16-le", errors="strict"), "utf-16-le-heuristic"

    return raw.decode("utf-8", errors="strict"), "utf-8"


def should_drop(line: str) -> bool:
    code = line.split("#", 1)[0].strip()
    if not code:
        return False
    low = code.lower()
    return any(low.startswith(p) for p in DROP_PREFIXES)


def main() -> None:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "requirements.txt")
    raw = path.read_bytes()
    text, _encoding_branch = decode_bytes(raw)

    # Remove \r e \n duplicado e processa linha a linha
    normalized = text.replace("\r\n", "\n")
    kept: list[str] = []
    for line in normalized.splitlines():
        if should_drop(line):
            continue
        kept.append(line)

    out = "\n".join(kept).rstrip() + "\n"
    path.write_text(out, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

