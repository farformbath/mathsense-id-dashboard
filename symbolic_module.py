"""Root proxy shim for src/symbolic_module.py."""
import sys
import os

_src_dir = os.path.join(os.path.dirname(__file__), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from src.symbolic_module import (
    solve_symbolic,
    _manual_solve,
    build_equation,
)

__all__ = [
    "solve_symbolic",
    "_manual_solve",
    "build_equation",
]
