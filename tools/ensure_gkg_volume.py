#!/usr/bin/env python3
"""Ensure the installed `gkg` module exposes `Volume` with `read()`.

Usage: import ensure_gkg_volume  # will monkey-patch gkg if needed
or run as a script to print info.
"""
import importlib
import sys
import types
import pkgutil
import inspect
from pathlib import Path


def ensure():
    try:
        gkg = importlib.import_module('gkg')
    except Exception:
        return False, 'gkg not importable'

    if hasattr(gkg, 'Volume'):
        return True, 'Volume already present'

    # Try to import our local compat
    here = Path(__file__).resolve().parent
    compat_path = str(here)
    if compat_path not in sys.path:
        sys.path.insert(0, compat_path)

    # First, attempt to discover a real Volume implementation inside gkg
    try:
        # If gkg is a package, iterate submodules
        if hasattr(gkg, '__path__'):
            for finder, name, ispkg in pkgutil.iter_modules(gkg.__path__):
                full = f"gkg.{name}"
                try:
                    sub = importlib.import_module(full)
                except Exception:
                    continue
                # Look for a class literally named 'Volume'
                for attr_name, attr in vars(sub).items():
                    if inspect.isclass(attr) and attr.__name__ == 'Volume':
                        setattr(gkg, 'Volume', attr)
                        return True, f'bound Volume from {full}.{attr_name}'
                # Look for classes with 'volume' or 'image' in their name
                for attr_name, attr in vars(sub).items():
                    if inspect.isclass(attr) and ('volume' in attr.__name__.lower() or 'image' in attr.__name__.lower()):
                        setattr(gkg, 'Volume', attr)
                        return True, f'bound {attr.__name__} from {full} as Volume'
                # Look for module-level factory functions that look like readers
                for attr_name, attr in vars(sub).items():
                    if inspect.isfunction(attr) and 'read' in attr_name.lower():
                        # attach the function as a helper named Volume_read on gkg
                        try:
                            setattr(gkg, attr_name, attr)
                            return True, f'bound reader function {full}.{attr_name} on gkg as {attr_name}'
                        except Exception:
                            pass
        # If discovery failed, fall back to the compat shim
    except Exception as e:
        # continue to fallback path but include debug info
        debug_err = str(e)

    try:
        from gkg_compat import Volume as CompatVolume  # noqa: E402
    except Exception as e:
        return False, f'failed to import compat: {e} ({locals().get("debug_err")})'

    # Attach compat Volume
    try:
        setattr(gkg, 'Volume', CompatVolume)
        return True, 'injected Volume from tools/gkg_compat (fallback)'
    except Exception as e:
        return False, f'failed to attach Volume: {e} ({locals().get("debug_err")})'


if __name__ == '__main__':
    ok, msg = ensure()
    print(ok, msg)
