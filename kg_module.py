"""Root proxy shim for src/kg_module.py."""
import sys
import os

# Add src to sys.path if not present
_src_dir = os.path.join(os.path.dirname(__file__), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from src.kg_module import (
    build_knowledge_graph,
    visualize_kg,
    ascii_kg,
    build_equation,
)

__all__ = [
    "build_knowledge_graph",
    "visualize_kg",
    "ascii_kg",
    "build_equation",
]
