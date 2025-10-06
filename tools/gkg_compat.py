#!/usr/bin/env python3
"""
Minimal compatibility layer that provides a `Volume` class with a
`read()` method and `getHeader()`/`header()` accessors. It reads GIS
MINF sidecars (<base>.dim.minf, <base>.ima.minf, <base>.minf) and
exposes the `attributes` dict in a small Header wrapper.

This is intentionally tiny and safe: it does not depend on the
installed `gkg` implementation and only parses the MINF sidecars that
are plain Python files containing an `attributes = {...}` mapping.
"""
import os
from typing import Any, Dict, Iterable, Optional


def _read_minf_attrs(ima_path: str) -> Dict[str, Any]:
    """Return the 'attributes' mapping found in the first existing MINF sidecar.
    Checks in order: <base>.dim.minf, <base>.ima.minf, <base>.minf.
    If none found or parse fails, returns {}.
    """
    base, _ = os.path.splitext(ima_path)
    for cand in (base + ".dim.minf", base + ".ima.minf", base + ".minf"):
        if os.path.isfile(cand):
            try:
                ns = {}
                with open(cand, "r") as f:
                    code = f.read()
                # MINF files in this project are simple python snippets that
                # define `attributes = {...}`. Use exec in a restricted ns.
                exec(code, ns)
                attrs = ns.get("attributes", {})
                if isinstance(attrs, dict):
                    return attrs
            except Exception:
                # swallow and try next candidate
                pass
    return {}


class Header:
    """Light wrapper around the attributes dict providing the
    methods that the pipeline's introspection expects:
      - getAttributeNames()
      - getAttribute(k)
      - get(k, default)
      - keys() (iterable)
    Also supports dict-like access (h[k]).
    """
    def __init__(self, attrs: Optional[Dict[str, Any]]):
        self._attrs = dict(attrs or {})

    def getAttributeNames(self) -> Iterable[str]:
        return list(self._attrs.keys())

    def getAttribute(self, key: str, default: Any = None) -> Any:
        return self._attrs.get(key, default)

    def get(self, key: str, default: Any = None) -> Any:
        return self._attrs.get(key, default)

    def keys(self):
        return list(self._attrs.keys())

    def __len__(self):
        return len(self._attrs)

    def __getitem__(self, key):
        return self._attrs[key]

    def __contains__(self, key):
        return key in self._attrs

    def items(self):
        return self._attrs.items()

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._attrs)


class Volume:
    """Minimal surrogate Volume object: Volume.read(path) returns an
    instance with `getHeader()` and `header()` methods returning a
    `Header` instance.
    """
    def __init__(self, path: str, attrs: Dict[str, Any]):
        self.path = path
        self._header = Header(attrs)

    @classmethod
    def read(cls, path: str) -> 'Volume':
        # Accept both .ima and any path; rely on MINF sidecars to find attrs
        attrs = _read_minf_attrs(path)
        return cls(path, attrs)

    # Provide both accessor names used in the repo / quick checks
    def getHeader(self) -> Header:
        return self._header

    def header(self) -> Header:
        return self._header


def _test():
    import sys
    if len(sys.argv) > 1:
        p = sys.argv[1]
        v = Volume.read(p)
        h = v.getHeader()
        print("HEADER_KEYS:", sorted(h.getAttributeNames()))


if __name__ == '__main__':
    _test()
