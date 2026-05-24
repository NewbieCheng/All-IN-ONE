from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

from all_in_one.cli.errors import CLIError, ErrorCategory


def format_output(data: Any, output: str = "json") -> str:
    if output == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    if output == "pretty":
        return _pretty(data)
    raise CLIError(ErrorCategory.OUTPUT_ERROR, f"Unsupported output format: {output}")


def write_output(data: Any, output: str = "json", path: Optional[Path] = None) -> str:
    if output == "file":
        if path is None:
            raise CLIError(ErrorCategory.OUTPUT_ERROR, "--path is required for file output")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(target)
    return format_output(data, output=output)


def _pretty(data: Any, indent: int = 0) -> str:
    prefix = " " * indent
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_pretty(value, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {value}")
        return "\n".join(lines)
    if isinstance(data, list):
        return "\n".join(f"{prefix}- {_pretty(item, indent + 2).lstrip()}" for item in data)
    return f"{prefix}{data}"


def verbose_log(message: str, verbose: bool = False) -> None:
    if verbose:
        print(f"[aione] {message}", file=sys.stderr)
