"""Pola regex dan parser angka untuk MathSense-ID."""
import re
from typing import Union
try:
    from src.kamus_operasi import SATUAN_BARANG, SATUAN_UANG, KAMUS_OPERASI
except ImportError:
    from kamus_operasi import SATUAN_BARANG, SATUAN_UANG, KAMUS_OPERASI

# Pola angka fleksibel: mencakup ribuan dengan titik (15.000, 1.000.000),
# desimal dengan koma atau titik (1,5 atau 2.5), dan angka bulat polos (3, 15000).
# Urutan cabang regex memprioritaskan format terpanjang/terspesifik terlebih dahulu.
ANGKA_PATTERN = re.compile(
    r'\b(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+[.,]\d+|\d+)\b'
)

# Pola deteksi prefix mata uang
REGEX_CURRENCY_PREFIX = re.compile(
    r'(?i)(?:rp\.?|idr|harga\s+rp\.?|seharga\s+rp\.?|@\s*rp\.?|@)'
)

# Pola deteksi suffix mata uang
REGEX_CURRENCY_SUFFIX = re.compile(
    r'(?i)\b(?:rupiah|ribu\s+rupiah|juta\s+rupiah|ribu|juta|perak)\b'
)


def parse_number(s: Union[str, int, float]) -> float:
    """Konversi string angka bahasa Indonesia / internasional menjadi float.
    
    Contoh:
    - parse_number("15.000") -> 15000.0
    - parse_number("1,5") -> 1.5
    - parse_number("2.5") -> 2.5
    - parse_number("3") -> 3.0
    - parse_number("15000") -> 15000.0
    - parse_number("1.000.000") -> 1000000.0
    """
    if isinstance(s, (int, float)):
        return float(s)
    
    if not isinstance(s, str):
        raise TypeError(f"Expected str or number, got {type(s)}")
        
    cleaned = s.strip()
    # Ekstrak karakter angka yang diawali digit (menangani awalan seperti "Rp." dengan aman)
    m = re.search(r'\d+(?:[.,]\d+)*|\d+', cleaned)
    if not m:
        raise ValueError(f"Tidak dapat mengekstrak angka dari: '{s}'")
    
    num_str = m.group(0)
    
    # Format campuran: titik sebagai ribuan, koma sebagai desimal (e.g. 15.000,5)
    if '.' in num_str and ',' in num_str:
        num_str = num_str.replace('.', '').replace(',', '.')
        return float(num_str)
        
    # Format desimal Indonesia: koma sebagai desimal (e.g. 1,5)
    if ',' in num_str:
        return float(num_str.replace(',', '.'))
        
    # Format dengan titik
    if '.' in num_str:
        parts = num_str.split('.')
        # Jika semua bagian setelah bagian pertama memiliki panjang tepat 3 digit,
        # ini adalah pemisah ribuan (e.g. 15.000, 2.000, 1.000.000)
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            return float(''.join(parts))
        else:
            # Desimal dengan titik standar (e.g. 1.5, 2.5, 3.14)
            return float(num_str)
            
    return float(num_str)
