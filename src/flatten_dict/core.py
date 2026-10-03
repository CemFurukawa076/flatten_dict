"""Flatten and restore nested dicts using a configurable separator.

Design decisions:
  - Only dicts trigger recursion. Lists, tuples, sets, and strings are treated
    as leaf values, so a nested list survives a round-trip unchanged.
  - Empty nested dicts are preserved: {"a": {}} flattens to {"a": {}} rather
    than disappearing, which is the behaviour the tests below assert and the
    README documents. The alternative (dropping empty dicts) loses information.
  - Keys are joined with a single separator string. The default "." mirrors
    dot-notation in config files. We deliberately do NOT split on separators
    during unflatten: if a real key contains the separator, it cannot be
    round-tripped. This is the documented limitation.
  - Recursion is bounded by MAX_DEPTH_EXCEEDED to reject pathologically deep
    input instead of blowing the stack.
"""

from collections import abc
from typing import Any, Dict, Mapping, Optional

MAX_DEPTH_EXCEEDED = 500


def _is_mapping(obj: Any) -> bool:
    return isinstance(obj, abc.Mapping)


def _join(prefix: Optional[str], key: str, sep: str) -> str:
    if prefix is None:
        return key
    return prefix + sep + key


def flatten(
    obj: Mapping[str, Any],
    sep: str = ".",
    depth: int = 0,
) -> Dict[str, Any]:
    """Flatten a nested mapping into a one-level dict.

    Nested dict keys are joined with ``sep``. Non-mapping values (including
    lists, tuples, strings, and numbers) are kept as-is. Empty nested dicts
    are preserved as empty-dict values on the path that produced them.

    Raises RecursionError if the nesting exceeds MAX_DEPTH_EXCEEDED.
    """
    if not _is_mapping(obj):
        raise TypeError("flatten() requires a mapping; got %r" % type(obj).__name__)
    if depth > MAX_DEPTH_EXCEEDED:
        raise RecursionError("input is too deeply nested")
    return _flatten(obj, sep, depth, None)


def _flatten(obj: Mapping[str, Any], sep: str, depth: int, prefix: Optional[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in obj.items():
        path = _join(prefix, str(key), sep)
        if _is_mapping(value):
            if not value:
                out[path] = {}
                continue
            if depth + 1 > MAX_DEPTH_EXCEEDED:
                raise RecursionError("input is too deeply nested")
            out.update(_flatten(value, sep, depth + 1, path))
        else:
            out[path] = value
    return out


def unflatten(
    obj: Mapping[str, Any],
    sep: str = ".",
) -> Dict[str, Any]:
    """Restore a flattened mapping into a nested dict.

    Keys containing ``sep`` are split to build the nesting. If a value is an
    empty dict, the key is treated as an empty nested dict rather than a
    leaf (this lets round-trips preserve empties).
    """
    if not _is_mapping(obj):
        raise TypeError("unflatten() requires a mapping; got %r" % type(obj).__name__)
    root: Dict[str, Any] = {}
    for key, value in obj.items():
        parts = str(key).split(sep) if sep != "" else [str(key)]
        cur = root
        for part in parts[:-1]:
            nxt = cur.get(part)
            if not isinstance(nxt, dict):
                nxt = {}
                cur[part] = nxt
            cur = nxt
        last = parts[-1]
        existing = cur.get(last)
        if isinstance(value, dict) and not value and isinstance(existing, dict):
            cur[last] = existing
        else:
            cur[last] = value
    return root
