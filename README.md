# 🧮 MathSense-ID — Neuro-Symbolic Math Word Problem Solver

> **Indonesian Math Word Problem (MWP) Reasoning System**  
> *Rule-based Named Entity Recognition (NER), Knowledge Graph (KG), and Deterministic Symbolic Algebra Engine.*  
> [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mathsenseid-solver.streamlit.app/)
MathSense-ID adalah sistem penalaran otomatis pemecahan soal cerita matematika berbahasa Indonesia berbasis pendekatan **Neuro-Simbolik**. Sistem ini mengeliminasi halusinasi aritmatika (*arithmetic hallucination*) yang sering terjadi pada model Large Language Model (LLM) dengan memisahkan pemahaman bahasa dari kalkulasi matematis eksak.

---

## 📌 Fitur Utama Dashboard

1. **🚀 Solver Interaktif (Live Problem Solver)**:
   - Input soal cerita matematika bahasa Indonesia secara bebas dengan preset ragam tipe soal (T1 hingga T5).
   - Rincian 4 tahap penalaran transparan:
     - **Tahap 1**: Ekstraksi Entitas & Kuantitas (NER).
     - **Tahap 2**: Ekstraksi Relasi Operasi Matematis (`+`, `-`, `*`, `/`).
     - **Tahap 3**: Visualisasi Graf Pengetahuan Relasi (Knowledge Graph) berbasis NetworkX.
     - **Tahap 4**: Perumusan Persamaan Aljabar Simbolik & Evaluasi Deterministik (SymPy).

2. **📊 Evaluasi & Benchmark Analisis**:
   - **Akurasi 100%** pada test set terverifikasi dan 100% pada evaluasi Out-of-Distribution (OOD).
   - Seluruh 95/95 rangkaian pengujian unit (Pytest) lolos tanpa kegagalan.
   - Tabel komparasi keunggulan arsitektur Neuro-Simbolik vs LLM Generatif.

3. **🔬 Arsitektur Pipeline 4-Tahap**:
   - Dokumentasi lengkap mengenai normalisasi mata uang rupiah (`Rp. 15.000`), penanganan desimal (`2.5` / `2,5`), penelusuran relasi tanpa kebocoran entitas (*no entity role bleed-over*), dan kanonisasi aljabar.

4. **📋 Dataset Explorer**:
   - Penelusuran 500+ dataset soal cerita matematika dengan pencarian kata kunci dan filter kategori kesulitan.
   - Fitur ekspor CSV interaktif.

---

## 🚀 Cara Menjalankan

### Menggunakan Batch Script (Windows):
Klik ganda file `run_dashboard.bat`.

### Menggunakan Terminal / Command Prompt:
```bash
cd C:\projects\mathsense-id-dashboard
python -m streamlit run app.py
```
Aplikasi akan terbuka otomatis di browser Anda pada alamat:
👉 **`http://localhost:8501`**
