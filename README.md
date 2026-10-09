# flatten_dict

Flatten nested mappings to flat dicts and restore them, with a configurable separator. Pure Python standard library.

## Usage

```python
from flatten_dict import flatten, unflatten

flat = flatten({"a": {"b": {"c": 1}}, "d": 2})
# {"a.b.c": 1, "d": 2}

nested = unflatten(flat)
# {"a": {"b": {"c": 1}}, "d": 2}
```

The default separator is `"."`. Pass `sep="/"` (or any string) to both functions and they stay consistent.

## Why

Flattened dicts are convenient for config loading, diffing, and serialization to key/value stores that have no nesting. This library keeps a single, obvious interpretation: only mappings recurse. Lists, tuples, strings, and scalars are leaves, so `{"a": [1, 2]}` survives a round-trip unchanged. Empty nested dicts are preserved rather than silently dropped, because dropping them loses information the caller may have intended.

## Edge case you will hit

If a real key contains the separator string, it cannot round-trip. `flatten({"a.b": 1})` yields `{"a.b": 1}` and `unflatten` of that produces `{"a": {"b": 1}}`. Pick a separator that cannot appear in your keys. There is no escaping mechanism, by design — escaping adds complexity and ambiguity that this library declines to take on.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

