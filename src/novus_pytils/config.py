"""Configuration files: load and save YAML or JSON, read and write dotted keys, merge layers.

Example:
    >>> from novus_pytils import config
    >>> cfg = config.load_config("app.yaml")
    >>> config.get_value(cfg, "database.port", default=5432)
    >>> config.set_value(cfg, "database.host", "db.local")
    >>> config.save_config(cfg, "app.yaml")
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Any

_YAML = {".yaml", ".yml"}
_JSON = {".json"}


def load_yaml(path: str | PathLike[str]) -> Any:
    """Parse a YAML file with the safe loader. An empty file gives ``None``."""
    import yaml

    with Path(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: Any, path: str | PathLike[str], indent: int = 2) -> Path:
    """Write ``data`` as block-style YAML, keys in the given order, creating parents."""
    import yaml

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data, f, default_flow_style=False, indent=indent, sort_keys=False, allow_unicode=True
        )
    return target


def load_config(path: str | PathLike[str]) -> dict[str, Any]:
    """Load a ``.yaml``/``.yml`` or ``.json`` file as a dict.

    An empty YAML file gives ``{}``.

    Raises:
        ValueError: If the extension is not YAML or JSON, or the file's top
            level is not a mapping.
    """
    source = Path(path)
    ext = source.suffix.lower()
    if ext in _YAML:
        data = load_yaml(source)
    elif ext in _JSON:
        data = json.loads(source.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Config files must be .yaml, .yml or .json, got {source.name!r}")
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{source.name} must contain a mapping at the top level")
    return data


def save_config(data: dict[str, Any], path: str | PathLike[str], indent: int = 2) -> Path:
    """Write a dict as YAML or JSON by the path's extension, creating parents.

    Raises:
        ValueError: If the extension is not YAML or JSON.
    """
    target = Path(path)
    ext = target.suffix.lower()
    if ext in _YAML:
        return save_yaml(data, target, indent=indent)
    if ext in _JSON:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(data, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return target
    raise ValueError(f"Config files must be .yaml, .yml or .json, got {target.name!r}")


def get_value(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Read a nested value by dotted key (``"database.port"``), or ``default``."""
    current: Any = data
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def set_value(data: dict[str, Any], key: str, value: Any) -> None:
    """Set a nested value by dotted key, creating intermediate dicts.

    Raises:
        TypeError: If an intermediate key holds something other than a dict.
    """
    parts = key.split(".")
    current = data
    for part in parts[:-1]:
        nxt = current.setdefault(part, {})
        if not isinstance(nxt, dict):
            raise TypeError(
                f"Cannot descend into {part!r} in {key!r}: it holds {type(nxt).__name__}"
            )
        current = nxt
    current[parts[-1]] = value


def missing_keys(data: dict[str, Any], required: Iterable[str]) -> list[str]:
    """The dotted keys from ``required`` that ``data`` does not have."""
    sentinel = object()
    return [k for k in required if get_value(data, k, sentinel) is sentinel]


def merge_configs(*layers: dict[str, Any]) -> dict[str, Any]:
    """Merge dicts left to right; nested dicts merge, anything else is replaced.

    The inputs are not modified.
    """
    result: dict[str, Any] = {}
    for layer in layers:
        for key, value in layer.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
    return result
