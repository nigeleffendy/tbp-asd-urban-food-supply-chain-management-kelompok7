# 🌾 Urban Food Supply Chain Management
**ELT60213 – Algoritma dan Struktur Data | TA 2025/2026**  
Topik 10 | Teknik Elektro, Universitas Negeri Yogyakarta

---

## tbp-asd-urban-food-supply-chain-management-kelompok-7
## 👥 Anggota Kelompok

| No.| Nama                         | NIM           | Modul            |
|--- |---                           |---            |---               |
| 1  | Nigel Efendi Sebastian Purba |  25051030115  | Modul 6          |
| 2  | Kaysan Nawfal Supriyadi      |  25051030124  | Modul 4, 5       |
| 3  | Muhammad Farhan Mustanir     |  25051030111  | Modul 1, 2       |
| 4  | Muhammad Asri Athallah       |  25051030100  | Modul 3          |

---


## 📋 Deskripsi Proyek

Sistem manajemen rantai pasok pangan kota berbasis struktur data untuk mensimulasikan jaringan distribusi **26 node** (10 Petani, 5 Distributor, 8 Pasar, 3 Gudang) dan **12 jenis produk** pangan di Yogyakarta.

| Struktur Data                    | Digunakan Untuk              | Big-O                       |
|---                               |---                           |---                          |
| **Graph (Adjacency List)**       | Jaringan distribusi berbobot | tambah O(1), BFS/DFS O(V+E) |
| **Circular Queue (Array)**       | Buffer FIFO stok gudang      | enqueue/dequeue O(1)        |
| **Priority Queue (Linked List)** | Antrian pengiriman prioritas | enqueue O(n), dequeue O(1)  |
| **BST**                          | Katalog produk               | insert/search O(log n)      |
| **Stack (Linked List)**          | Log transaksi                | push/pop O(1)               |
| **Dijkstra (manual)**            | Jalur distribusi termurah    | O(V²+E)                     |

---

## 🗂️ Struktur Folder Utama

```
tbp-asd-kelompok-XX/
├── src/
│   ├── data_structures/
│   │   ├── linked_list.py       # Node terpisah untuk stack dan PQ
│   │   ├── bst.py               # BST Katalog Produk
│   │   ├── circular_queue.py    # Circular Queue Buffer Gudang
│   │   ├── dijkstra.py          # Algoritma Dijkstra Manual
│   │   ├── graph.py             # Graph Rantai Pasok
│   │   ├── priority_queue.py    # Priority Queue Pengiriman
│   │   ├── stack.py             # Stack Log Transaksi
│   │   └── 
│   ├── modules/
│   │   ├── modul_1.py           # Graph & BFS/DFS Audit
│   │   ├── modul_2.py           # Circular Queue Buffer
│   │   ├── modul_3.py           # Priority Queue Pengiriman
│   │   ├── modul_4.py           # BST Katalog Produk
│   │   ├── modul_5.py           # Dijkstra Biaya Minimum
│   │   └── modul_6.py           # CLI Rantai Pasok
│   │   
│   ├── data_generator.py        # generate_rantai_pasok(seed=61)
│   ├── data_models.py           # @dataclass Produk, Pengiriman
│   └── main.py                  # Entry point
├── tests/
│   ├── test_bst.py
│   ├── test_circular_queue.py
│   ├── test_dijkstra.py
│   ├── test_graph.py
│   ├── test_priority_queue.py
│   └── test_stack.py
├── experiments/
│   └── benchmark.py             # Benchmark 3 ukuran data
├── docs/
│   ├── laporan_final.pdf
│   └── slide_presentasi.pptx
├── AI_Log/
│   ├── Log_prompt.txt
│   └── screenshots/
├── README.md
└── requirements.txt
```

---

## ⚙️ Cara Install

### Prasyarat
- Python 3.11+
- pip

### Install Dependencies
```bash
pip install numpy
```

> Tidak ada library struktur data bawaan Python yang digunakan  
> (`heapq`, `deque`, `sortedcontainers` **tidak digunakan** sesuai ketentuan).

---

## 🚀 Cara Menjalankan

### 1. Sistem Utama (CLI)
```bash
# Dari root project
python -m src.main
```

**Output awal:**
```
══════════════════════════════════════════════════════════════════
  Food Supply Chain System  –  Kota Yogyakarta
  Ketik BANTUAN untuk daftar perintah, KELUAR untuk berhenti.
══════════════════════════════════════════════════════════════════

>>
```

### 2. Unit Test
```bash
python -m pytest tests/ -v
```

**Expected output:**
```
tests/test_bst.py::TestInsert::test_insert_satu_produk PASSED
tests/test_bst.py::TestSearch::test_search_produk_ada PASSED
...
====== 120 passed in X.XXs ======
```

### 3. Benchmark Runtime
```bash
python -m experiments.benchmark
```

---

## 💻 Daftar Perintah CLI

```
╔══════════════════════════════════════════════════════════════════╗
║        FOOD SUPPLY CHAIN SYSTEM  -  Daftar Perintah              ║
╠══════════════════════════════════════════════════════════════════╣
║  KIRIM <dari> <ke> <kode> <jumlah>                               ║
║      Buat pengiriman baru ke antrian prioritas.                  ║
║      Contoh: KIRIM PTN00 PSR02 PRD-001 50                        ║
║                                                                  ║
║  PROSES_KIRIM                                                    ║
║      Proses satu pengiriman paling mendesak dari antrian.        ║
║                                                                  ║
║  RUTE_MURAH <dari> <ke>                                          ║
║      Tampilkan jalur distribusi termurah (Dijkstra).             ║
║      Contoh: RUTE_MURAH PTN00 GDG02                              ║
║                                                                  ║
║  CEK_STOK <kode>                                                 ║
║      Cek stok & info produk dari katalog BST.                    ║
║      Contoh: CEK_STOK PRD-003                                    ║
║                                                                  ║
║  KATALOG                                                         ║
║      Tampilkan seluruh katalog produk (BST inorder).             ║
║                                                                  ║
║  KADALUARSA <maks_hari>                                          ║
║      Daftar produk yang kadaluarsa dalam N hari ke depan.        ║
║      Contoh: KADALUARSA 7                                        ║
║                                                                  ║
║  LAPORAN_DISTRIBUSI                                              ║
║      Ringkasan lengkap: jaringan, katalog, antrian, log.         ║
║                                                                  ║
║  BUFFER <node_id>                                                ║
║      Lihat isi circular queue buffer gudang suatu node.          ║
║      Contoh: BUFFER GDG00                                        ║
║                                                                  ║
║  AUDIT_JARINGAN                                                  ║
║      Uji konektivitas seluruh jaringan distribusi (BFS/DFS).     ║
║                                                                  ║
║  ANTRIAN                                                         ║
║      Tampilkan semua pengiriman yang sedang menunggu.            ║
║                                                                  ║
║  BANTUAN                                                         ║
║      Tampilkan daftar perintah ini.                              ║
║                                                                  ║
║  KELUAR                                                          ║
║      Keluar dari sistem.                                         ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 📥 Contoh Sesi CLI

```
>> KIRIM PTN00 PSR02 PRD-001 50
  [OK] Pengiriman #1 ditambahkan ke antrian.
       Produk   : Beras (PRD-001)
       Rute     : PTN00 -> PSR02
       Jumlah   : 50  |  Prioritas: MENDESAK (kadaluarsa 1 hari)
       Antrian  : 1 kiriman menunggu

>> RUTE_MURAH PTN00 GDG00
  ══════════════════════════════════════════════════════════════════
  Jalur Termurah  PTN00  →  GDG00
  ══════════════════════════════════════════════════════════════════
  Segmen                         Jarak      Biaya/km      Subtotal
  ──────────────────────────────────────────────────────────────────
  PTN00  →  DST02               45 km    Rp  1,200     Rp  54,000
  DST02  →  GDG00               32 km    Rp  2,100     Rp  67,200
  ──────────────────────────────────────────────────────────────────
  TOTAL BIAYA                                         Rp 121,200

>> CEK_STOK PRD-003
  ══════════════════════════════════════════════════════════════════
  Info Produk  –  Tomat
  ══════════════════════════════════════════════════════════════════
  Kode          : PRD-003
  Kategori      : SAYUR
  Harga Satuan  : Rp 12,000
  Stok          : 87 unit
  Kadaluarsa    : 5 hari
  Status        : REGULER

>> AUDIT_JARINGAN
  BFS dari 'PTN00': 26 node dijangkau dari 26 total
  Status jaringan: TERHUBUNG PENUH ✓
```

---

## 🧪 Parameter Sistem

| Parameter         | Nilai                                               |
|---                |---                                                  |
| Node rantai pasok | 26 (10 Petani + 5 Distributor + 8 Pasar + 3 Gudang) |
| Jalur distribusi  | ~38 edge berbobot                                   |
| Jenis produk      | 12 (Beras, Cabai, Tomat, Ayam, dll.)                |
| `np.random.seed`  | **61** (jangan diubah)                              |
| Kapasitas buffer  | 50 slot per node (CircularQueue)                    |
| Operasi minimum   | 350 event campuran                                  |

---

## 📊 Ringkasan Big-O

| Operasi                  | Kompleksitas |         Keterangan           |
|---                       |---           |---                           |
| CQ enqueue / dequeue     | O(1)         | Pointer modulo, no traversal |
| Stack push / pop         | O(1)         | Insert di head linked list   |
| PQ enqueue               | O(n)         | Insertion terurut            |
| PQ dequeue               | O(1)         | Ambil head                   |
| BST insert / search      | O(log n)     | h = log n rata-rata          |
| BST inorder / filter     | O(n)         | Traversal semua node         |
| Graph tambah node/jalur  | O(1)         | Dict + prepend linked list   |
| Graph BFS / DFS          | O(V+E)       | Kunjungi semua node & edge   |
| Dijkstra                 | O(V²+E)      | Tanpa heap                   |
| Rekonstruksi jalur       | O(V)         | Traversal parent array       |

---