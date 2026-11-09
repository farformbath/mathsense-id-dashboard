"""Root shim untuk kamus_operasi."""
import sys
import os

_src_dir = os.path.join(os.path.dirname(__file__), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from src.kamus_operasi import (
    SATUAN_BARANG,
    SATUAN_UANG,
    KAMUS_OPERASI,
    is_satuan_barang,
    is_satuan_uang,
)

__all__ = [
    "SATUAN_BARANG",
    "SATUAN_UANG",
    "KAMUS_OPERASI",
    "is_satuan_barang",
    "is_satuan_uang",
]
