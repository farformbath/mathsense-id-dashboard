"""NLP Module untuk MathSense-ID.
Menyediakan:
- extract_entities(text: str) -> List[ExtractedEntity]
- extract_relations(text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]
- detect_question_type(text: str) -> str ("T1", "T2", "T3", "T4", "T5", atau "UNKNOWN")
"""
import re
from typing import List, Optional

try:
    from contracts import ExtractedEntity, ExtractedRelation
    from src.kamus_operasi import SATUAN_BARANG, SATUAN_UANG, KAMUS_OPERASI, is_satuan_barang, is_satuan_uang
    from src.regex_patterns import ANGKA_PATTERN, parse_number
except ImportError:
    try:
        from contracts import ExtractedEntity, ExtractedRelation
        from kamus_operasi import SATUAN_BARANG, SATUAN_UANG, KAMUS_OPERASI, is_satuan_barang, is_satuan_uang
        from regex_patterns import ANGKA_PATTERN, parse_number
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from contracts import ExtractedEntity, ExtractedRelation
        from src.kamus_operasi import SATUAN_BARANG, SATUAN_UANG, KAMUS_OPERASI, is_satuan_barang, is_satuan_uang
        from src.regex_patterns import ANGKA_PATTERN, parse_number


def detect_question_type(text: str) -> str:
    """Klasifikasi template soal MWP ke salah satu dari:
    - T1: Harga satuan (misal: Beli 3 apel Rp 15.000. Berapa harga 1 apel?)
    - T2: Penjumlahan total (misal: Punya 10 buku, beli 5 lagi. Berapa total?)
    - T3: Pengurangan sisa (misal: Punya 20 kue, beri 7. Berapa sisa?)
    - T4: Perkalian total (misal: Beli 4 pensil @ Rp 2.000. Berapa total?)
    - T5: Harga sejumlah (misal: Beli 6 buku Rp 30.000. Berapa harga 4 buku?)
    - UNKNOWN: Out of scope
    """
    if not isinstance(text, str) or not text.strip():
        return "UNKNOWN"

    t = text.lower()
    asks_price = bool(re.search(r'berapa(?:kah)?(?:\s+\w+)?\s+(?:harga|biaya|tarif|uang)|harga|biaya|tarif', t))
    asks_total = bool(re.search(r'berapa(?:kah)?\s+total|total|jumlah|seluruhnya', t))
    asks_sisa = bool(re.search(r'berapa(?:kah)?\s+sisa|sisa', t))
    has_penambahan = bool(re.search(r'penambahan|menambah|menambahkan|membeli(?:\s+\w+)?\s+lagi|beli(?:\s+\w+)?\s+lagi|mendapat|mendapatkan|diberi(?:\s+\w+)?\s+lagi|memberi(?:\s+\w+)?\s+lagi|mengambil(?:\s+\w+)?\s+lagi', t))
    has_memberi = bool(re.search(r'memberi|memberikan|menghilang|hilang|rusak|pecah|busuk|dimakan|dipinjam|terjual', t))
    has_per_unit = bool(re.search(r'@|\bsetiap\b|\bper\s|harga\s+sebuah|harga\s+satuan|masing-masing|\btiap\b', t))

    # Match target number in the QUESTION clause specifically
    m = re.search(r'berapa(?:kah)?(?:\s+\w+)?\s+(?:harga|biaya|tarif|uang)?(?:\s+(?:untuk|jika\s+membeli))?\s+(\d+(?:[.,]\d+)?|satu|sebuah)', t)
    num_asked = None
    if m and m.group(1):
        raw_val = m.group(1).lower().replace(',', '.')
        if raw_val in ("satu", "sebuah"):
            num_asked = 1.0
        else:
            try:
                num_asked = float(raw_val)
            except Exception:
                num_asked = None

    if asks_price and num_asked is not None and num_asked > 1:
        return "T5"
    if has_per_unit and asks_total:
        return "T4"
    if asks_price and (num_asked == 1 or 'satu' in t or '1 ' in t):
        return "T1"
    if has_penambahan and (asks_total or not asks_sisa):
        return "T2"
    if has_memberi or asks_sisa:
        if not has_penambahan:
            return "T3"
    if asks_total:
        return "T2"
    if asks_price:
        return "T1"
    return "UNKNOWN"


def extract_entities(text: str) -> List[ExtractedEntity]:
    """Ekstraksi entitas numerik dengan unit, role, dan confidence score.
    
    Formula confidence:
    - 0.9: Exact regex + unit known (SATUAN_BARANG / SATUAN_UANG)
    - 0.7: Fuzzy unit (inferred from sentence context / unlisted noun)
    - 0.5: Number only (tanpa unit)
    - 0.3: Ambiguous context
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Normalisasi spasi antara prefix mata uang dan angka (e.g. "Rp15.000" -> "Rp 15.000")
    norm_text = re.sub(r'(?i)\b(rp|idr)\.?(\d)', r'\1 \2', text)

    q_type = detect_question_type(norm_text)
    entities: List[ExtractedEntity] = []

    # Cari nomor pertanyaan pada "berapa harga N"
    m_target = re.search(r'(?i)berapa(?:kah)?(?:\s+\w+)?\s+(?:harga|biaya|tarif|uang)?(?:\s+(?:untuk|jika\s+membeli))?\s+(\d+(?:[.,]\d+)?)', norm_text)
    target_num_pos = m_target.start(1) if m_target else -1

    # Indeks awal pertanyaan "Berapa ..." jika ada
    m_q_start = re.search(r'(?i)\bberapa\b', norm_text)
    q_start_idx = m_q_start.start() if m_q_start else len(norm_text)

    last_known_unit: Optional[str] = None

    for m in ANGKA_PATTERN.finditer(norm_text):
        raw_str = m.group(0)
        start, end = m.start(), m.end()

        try:
            val = parse_number(raw_str)
        except Exception:
            continue

        prefix_context = norm_text[max(0, start - 25):start].strip()
        suffix_context = norm_text[end:min(len(norm_text), end + 35)].strip()

        # Deteksi jika angka adalah target pada pertanyaan "Berapa harga 1 apel?" pada T1 -> abaikan dari entitas premis
        is_in_question = (start >= q_start_idx)
        if (start == target_num_pos or is_in_question) and q_type == "T1" and val == 1.0:
            continue

        # Cek apakah angka adalah variabel yang ditanyakan pada T5 ("Berapa harga 4 buku?")
        is_variable_target = (start == target_num_pos) and q_type == "T5" and val > 1

        # Periksa unit barang di suffix terlebih dahulu
        tokens = suffix_context.split() if suffix_context else []
        first_word = tokens[0].lower().strip(",.?!;:\"'") if tokens else ""
        has_item_unit = False
        if first_word and is_satuan_barang(first_word):
            has_item_unit = True
        elif len(tokens) >= 2 and is_satuan_barang(f"{first_word} {tokens[1].lower().strip(',.?!;:\"')}"):
            has_item_unit = True

        # Cek mata uang / harga tanpa terhalang digit lain di prefix
        has_currency_prefix = bool(re.search(r'(?i)(?:rp\.?|idr|seharga\s+rp\.?|seharga|@)[^\d]*$', prefix_context)) or prefix_context.endswith('@')
        has_currency_suffix = bool(re.search(r'(?i)^(?:rupiah|ribu\s+rupiah|juta\s+rupiah|ribu|juta|perak)\b', suffix_context))

        # Angka yang diikuti langsung satuan barang bukan merupakan harga/mata uang
        is_price = (has_currency_prefix or has_currency_suffix) and not is_variable_target and not has_item_unit

        if is_price:
            role = "price"
            unit = "rupiah"
            confidence = 0.9
            ent_text = raw_str
            entities.append(ExtractedEntity(
                text=ent_text,
                value=float(val),
                unit=unit,
                role=role,
                confidence=confidence
            ))
            continue

        # Klasifikasi Quantity atau Variable
        role = "variable" if is_variable_target else "quantity"

        # Deteksi unit dari kata setelah angka
        unit = ""
        confidence = 0.5
        ent_text = raw_str

        tokens = suffix_context.split() if suffix_context else []
        first_token = tokens[0] if tokens else ""
        first_word = first_token.lower().strip(",.?!;:\"'") if tokens else ""
        second_token = tokens[1] if len(tokens) > 1 else ""
        second_word = second_token.lower().strip(",.?!;:\"'") if len(tokens) > 1 else ""

        # Cek apakah unit berupa kombinasi misal "kg apel"
        if first_word in ("kg", "kilogram", "gram", "gr", "ons", "liter", "l", "meter", "m") and second_word and is_satuan_barang(second_word):
            unit = first_word
            confidence = 0.9
            ent_text = f"{raw_str} {first_word}"
            last_known_unit = second_word
        elif is_satuan_barang(first_word):
            unit = first_word
            confidence = 0.9
            ent_text = f"{raw_str} {first_word}"
            last_known_unit = first_word
        elif first_word and first_word.isalpha() and len(first_word) >= 2 and first_word not in {
            "lagi", "dan", "yang", "ke", "kepada", "di", "dari", "untuk", "dengan",
            "seharga", "beli", "membeli", "memberi", "punya", "memiliki", "teman", "orang"
        }:
            # Fuzzy unit
            unit = first_word
            confidence = 0.7
            ent_text = f"{raw_str} {first_word}"
            last_known_unit = first_word
        else:
            # Tidak ada unit langsung setelah angka (misal "membeli 5 lagi")
            # Coba inferensi unit dari konteks kalimat sebelumnya
            if last_known_unit:
                unit = last_known_unit
                confidence = 0.7
                ent_text = raw_str
            else:
                unit = "unit"
                confidence = 0.5
                ent_text = raw_str

        entities.append(ExtractedEntity(
            text=ent_text,
            value=float(val),
            unit=unit,
            role=role,
            confidence=confidence
        ))

    return entities


def extract_relations(text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
    """Ekstraksi relasi matematika antar entitas.
    
    Formula confidence:
    - 0.9: Kata kunci dalam jarak <= 5 karakter
    - 0.7: Kata kunci dalam jarak <= 20 karakter
    - 0.5: Inferred dari tipe template soal
    - 0.3: Fallback default
    """
    if not isinstance(text, str) or len(entities) < 2:
        return []

    q_type = detect_question_type(text)
    t = text.lower()
    relations: List[ExtractedRelation] = []

    quantities = [e for e in entities if e.role == "quantity"]
    prices = [e for e in entities if e.role == "price"]
    variables = [e for e in entities if e.role == "variable"]

    # Kasus 1: Quantity - Price pair (T1, T4, T5)
    if quantities and prices:
        head_ent = quantities[0]
        tail_ent = prices[0]

        head_core = head_ent.text.split()[0]
        tail_core = tail_ent.text

        pos_head = t.find(head_ent.text.lower())
        if pos_head == -1:
            pos_head = t.find(head_core.lower())

        pos_tail = t.find(tail_core.lower())

        # Cari teks antara head dan tail
        if pos_head != -1 and pos_tail != -1:
            start_b = min(pos_head + len(head_ent.text), pos_tail + len(tail_core))
            end_b = max(pos_head, pos_tail)
            between = t[start_b:end_b].strip()
        else:
            between = t

        operation = "*"
        rel_name = "seharga"
        confidence = 0.7

        # Prioritaskan pencarian kata kunci pada segmen between terlebih dahulu
        if ("membeli" in t or "beli" in t) and ("seharga" in between or "harga" in between):
            rel_name = "membeli_seharga"
            confidence = 0.9
        elif "seharga" in between or "@" in between:
            rel_name = "seharga"
            confidence = 0.9
        elif "membeli" in between or "beli" in between:
            rel_name = "membeli"
            confidence = 0.9
        else:
            # Fallback jika tidak ada di between, cari di teks global
            kw_match = re.search(r'seharga|@|harga|beli', t)
            if kw_match and pos_head != -1:
                kw_start = kw_match.start()
                head_end = pos_head + len(head_ent.text)
                dist = min(abs(kw_start - head_end), abs(pos_tail - kw_match.end()))
                if dist <= 5:
                    confidence = 0.9
                elif dist <= 20:
                    confidence = 0.7
                else:
                    confidence = 0.5
            else:
                confidence = 0.5

        relations.append(ExtractedRelation(
            head=head_ent.text,
            tail=tail_ent.text,
            relation=rel_name,
            operation=operation,
            confidence=confidence
        ))
        return relations

    # Kasus 2: Dua Quantity (T2, T3)
    if len(quantities) >= 2:
        head_ent = quantities[0]
        tail_ent = quantities[1]

        head_core = head_ent.text.split()[0]
        tail_core = tail_ent.text.split()[0]

        pos_head = t.find(head_ent.text.lower())
        if pos_head == -1:
            pos_head = t.find(head_core.lower())

        pos_tail = t.find(tail_ent.text.lower(), pos_head + 1 if pos_head != -1 else 0)
        if pos_tail == -1:
            pos_tail = t.find(tail_core.lower(), pos_head + 1 if pos_head != -1 else 0)

        head_end = (pos_head + len(head_ent.text)) if pos_head != -1 else -1

        if pos_head != -1 and pos_tail != -1:
            start_b = head_end
            end_b = pos_tail
            between = t[start_b:end_b].strip()
        else:
            between = t

        # Cek kata kunci operasi — prioritaskan between sebelum t global
        is_subtraction = False
        is_addition = False
        rel_name = "hubungan"
        operation = "+"
        kw_found_pos = -1
        kw_len = 0

        # Prioritas 1: Periksa kata kunci pengurangan di dalam 'between'
        minus_kws = ["memberikan", "memberi", "diberikan", "hilang", "rusak", "pecah", "busuk", "dimakan", "dipinjam", "terjual", "kurang", "sisa"]
        for kw in minus_kws:
            if kw in between:
                is_subtraction = True
                rel_name = kw
                operation = "-"
                kw_found_pos = t.find(kw, pos_head) if pos_head != -1 else t.find(kw)
                kw_len = len(kw)
                break

        # Prioritas 2: Periksa kata kunci penambahan di dalam 'between'
        if not is_subtraction:
            if ("membeli" in between or "beli" in between) and "lagi" in t:
                is_addition = True
                rel_name = "membeli_lagi"
                operation = "+"
                kw = "membeli" if "membeli" in between else "beli"
                kw_found_pos = t.find(kw, pos_head) if pos_head != -1 else t.find(kw)
                kw_len = len(kw)
            else:
                plus_kws = ["menambah", "mendapat", "dapat lagi", "tambah", "dan", "lagi"]
                for kw in plus_kws:
                    if kw in between:
                        is_addition = True
                        rel_name = kw.replace(" ", "_")
                        operation = "+"
                        kw_found_pos = t.find(kw, pos_head) if pos_head != -1 else t.find(kw)
                        kw_len = len(kw)
                        break

        # Prioritas 3: Jika di between tidak ada kata kunci operasi, baru cari di konteks global t
        if not is_subtraction and not is_addition:
            for kw in minus_kws:
                if kw in t:
                    is_subtraction = True
                    rel_name = kw
                    operation = "-"
                    kw_found_pos = t.find(kw)
                    kw_len = len(kw)
                    break

        if not is_subtraction and not is_addition:
            if "membeli lagi" in t or "beli lagi" in t:
                is_addition = True
                rel_name = "membeli_lagi"
                operation = "+"
                kw_found_pos = t.find("membeli") if "membeli" in t else t.find("beli")
                kw_len = len("membeli") if "membeli" in t else len("beli")
            else:
                for kw in plus_kws:
                    if kw in t:
                        is_addition = True
                        rel_name = kw.replace(" ", "_")
                        operation = "+"
                        kw_found_pos = t.find(kw)
                        kw_len = len(kw)
                        break

        # Tentukan confidence berdasarkan formula jarak
        if kw_found_pos != -1 and pos_head != -1 and head_end != -1:
            dist = min(abs(kw_found_pos - head_end), abs(pos_tail - (kw_found_pos + kw_len)))
            if dist <= 5:
                confidence = 0.9
            elif dist <= 20:
                confidence = 0.7
            else:
                confidence = 0.5
        elif q_type in ("T2", "T3"):
            operation = "-" if q_type == "T3" else "+"
            rel_name = "kurang" if q_type == "T3" else "tambah"
            confidence = 0.5  # inferred
        else:
            operation = "+"
            rel_name = "tambah"
            confidence = 0.3  # fallback

        relations.append(ExtractedRelation(
            head=head_ent.text,
            tail=tail_ent.text,
            relation=rel_name,
            operation=operation,
            confidence=confidence
        ))
        return relations

    # Kasus 3: Fallback untuk pasangan entitas apa pun yang tersedia
    head_ent = entities[0]
    tail_ent = entities[1]
    op = "+"
    if q_type == "T3":
        op = "-"
    elif q_type in ("T1", "T4", "T5"):
        op = "*"

    relations.append(ExtractedRelation(
        head=head_ent.text,
        tail=tail_ent.text,
        relation="terkait",
        operation=op,
        confidence=0.3
    ))
    return relations
