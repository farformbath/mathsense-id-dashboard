"""Kamus Operasi dan Satuan untuk MathSense-ID NLP Pipeline."""

# Satuan barang yang sering muncul dalam Math Word Problems (MWP) Bahasa Indonesia
SATUAN_BARANG = {
    # Satuan umum & wadah
    "buah", "biji", "butir", "lembar", "ekor", "potong", "pasang", "bungkus",
    "botol", "kotak", "dus", "kardus", "lusin", "kodi", "rim", "gross",
    "paket", "porsi", "karung", "ikat", "batang", "helai",
    
    # Satuan ukuran & berat
    "kg", "kilogram", "gram", "gr", "ons", "liter", "l", "ml", "mililiter",
    "meter", "m", "cm", "centimeter", "sentimeter", "km", "kilometer",
    
    # Makanan & buah-buahan
    "apel", "jeruk", "mangga", "pisang", "kue", "roti", "permen", "telur",
    "bakso", "cokelat", "donat", "semangka", "alpukat", "nasi",
    
    # Alat tulis & perlengkapan sekolah
    "buku", "pensil", "pulpen", "penghapus", "penggaris", "spidol", "buku tulis",
    "buku gambar", "pensil warna", "kotak pensil", "rautan",
    
    # Pakaian & perlengkapan
    "baju", "celana", "kaos", "topi", "sepatu", "tas", "seragam", "kaus",
    
    # Perabot & mainan
    "meja", "kursi", "piring", "gelas", "mangkok", "sendok", "garpu",
    "kelereng", "balon", "stiker", "mainan", "kartu", "boneka"
}

# Satuan mata uang & nominal uang
SATUAN_UANG = {
    "rupiah", "rp", "rp.", "idr", "ribu", "juta", "perak"
}

# Kamus operasi matematika berdasarkan kata kunci bahasa Indonesia
KAMUS_OPERASI = {
    "+": [
        "membeli lagi", "beli lagi", "menambah", "menambahkan", "tambah", "tambahan",
        "mendapat", "mendapatkan", "dapat lagi", "diberi", "diberikan lagi",
        "memperoleh", "mengumpulkan", "lagi", "dan", "total", "jumlah", "seluruhnya"
    ],
    "-": [
        "memberi", "memberikan", "diberikan ke", "diberikan kepada", "diberi kepada",
        "menghilang", "hilang", "rusak", "busuk", "pecah", "basi",
        "terjual", "menjual", "dikurangi", "kurang", "sisa",
        "membuang", "jatuh", "dipinjam", "dimakan", "habis", "hilang sebanyak"
    ],
    "*": [
        "membeli seharga", "beli seharga", "seharga", "harga", "membeli", "beli",
        "@", "setiap", "tiap", "tiap-tiap", "masing-masing", "per", "kali",
        "dikalikan", "dikalikan dengan", "seharga rp", "harga rp"
    ],
    "/": [
        "dibagi", "membagi", "dibagikan", "dibagikan kepada", "per", "setiap",
        "rata-rata", "masing-masing", "dibagi rata"
    ]
}


def is_satuan_barang(word: str) -> bool:
    """Cek apakah kata merupakan satuan barang yang dikenal."""
    if not word:
        return False
    w = word.lower().strip(",.?!:;\"'")
    return w in SATUAN_BARANG


def is_satuan_uang(word: str) -> bool:
    """Cek apakah kata merupakan satuan mata uang."""
    if not word:
        return False
    w = word.lower().strip(",.?!:;\"'")
    return w in SATUAN_UANG
