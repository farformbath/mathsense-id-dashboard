"""5 mock soal lengkap untuk unblocker. JANGAN diubah."""
MOCK_SOAL = [
    {
        "text": "Budi membeli 3 apel seharga Rp 15.000. Berapa harga 1 apel?",
        "entities_gt": [
            {"text": "3 apel", "value": 3.0, "unit": "apel", "role": "quantity", "confidence": 1.0},
            {"text": "15.000", "value": 15000.0, "unit": "rupiah", "role": "price", "confidence": 1.0},
        ],
        "relations_gt": [
            {"head": "3 apel", "tail": "15.000", "relation": "membeli_seharga", "operation": "*", "confidence": 1.0}
        ],
        "equation_gt": "3*x=15000",
        "solution_gt": 5000.0,
        "template_id": "T1",
    },
    {
        "text": "Ani punya 10 buku, membeli 5 lagi. Berapa total?",
        "entities_gt": [
            {"text": "10 buku", "value": 10.0, "unit": "buku", "role": "quantity", "confidence": 1.0},
            {"text": "5", "value": 5.0, "unit": "buku", "role": "quantity", "confidence": 1.0},
        ],
        "relations_gt": [
            {"head": "10 buku", "tail": "5", "relation": "membeli_lagi", "operation": "+", "confidence": 1.0}
        ],
        "equation_gt": "x=10+5",
        "solution_gt": 15.0,
        "template_id": "T2",
    },
    {
        "text": "Siti punya 20 kue, memberi 7 ke teman. Berapa sisa?",
        "entities_gt": [
            {"text": "20 kue", "value": 20.0, "unit": "kue", "role": "quantity", "confidence": 1.0},
            {"text": "7", "value": 7.0, "unit": "kue", "role": "quantity", "confidence": 1.0},
        ],
        "relations_gt": [
            {"head": "20 kue", "tail": "7", "relation": "memberi", "operation": "-", "confidence": 1.0}
        ],
        "equation_gt": "x=20-7",
        "solution_gt": 13.0,
        "template_id": "T3",
    },
    {
        "text": "Andi beli 4 pensil @ Rp 2.000. Berapa total?",
        "entities_gt": [
            {"text": "4 pensil", "value": 4.0, "unit": "pensil", "role": "quantity", "confidence": 1.0},
            {"text": "2.000", "value": 2000.0, "unit": "rupiah", "role": "price", "confidence": 1.0},
        ],
        "relations_gt": [
            {"head": "4 pensil", "tail": "2.000", "relation": "seharga", "operation": "*", "confidence": 1.0}
        ],
        "equation_gt": "x=4*2000",
        "solution_gt": 8000.0,
        "template_id": "T4",
    },
    {
        "text": "Dina beli 6 buku seharga Rp 30.000. Berapa harga 4 buku?",
        "entities_gt": [
            {"text": "6 buku", "value": 6.0, "unit": "buku", "role": "quantity", "confidence": 1.0},
            {"text": "30.000", "value": 30000.0, "unit": "rupiah", "role": "price", "confidence": 1.0},
            {"text": "4 buku", "value": 4.0, "unit": "buku", "role": "variable", "confidence": 1.0},
        ],
        "relations_gt": [
            {"head": "6 buku", "tail": "30.000", "relation": "seharga", "operation": "*", "confidence": 1.0}
        ],
        "equation_gt": "x=(30000/6)*4",
        "solution_gt": 20000.0,
        "template_id": "T5",
    },
]
