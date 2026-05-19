# =============================================================================
#  data_generator.py  –  Generator Data Awal Rantai Pasok
# =============================================================================
#  Fungsi ini dipanggil SEKALI saat program pertama kali dijalankan (di main()).
#  Tugasnya adalah menghasilkan "database awal" sistem secara deterministik
#  menggunakan seed=61, sehingga setiap kali dijalankan hasilnya SELALU SAMA.
#
#  Output yang dihasilkan:
#    nodes       : 26 node (10 PETANI + 5 DISTRIBUTOR + 8 PASAR + 3 GUDANG)
#    edges       : ~38 jalur distribusi berbobot (jarak_km, biaya_per_km)
#    produk_list : 12 objek Produk (Beras, Cabai, Tomat, dst.)
#
#  Kenapa dipisah dari main()?
#    → Single Responsibility: generator hanya urusin data, bukan logika CLI.
#    → Mudah di-reuse di unit test tanpa harus menjalankan seluruh sistem.
#    → Memudahkan penggantian data (misal dari database nyata) di masa depan.
#
#  Kenapa seed=61? → Agar jaringan bisa direproduksi.
# =============================================================================

import numpy as np
import random

from src.data_models import Produk

# Konstanta kategori produk yang tersedia
KATEGORI_PRODUK = ['SAYUR', 'BUAH', 'DAGING', 'IKAN', 'BAHAN_POKOK']


def generate_rantai_pasok(seed: int = 61):
    """
    Hasilkan data awal jaringan rantai pasok secara deterministik.

    Parameter:
        seed : int - angka seed untuk reproduksibilitas (default 61)

    Kembalikan:
        nodes       : list of (node_id: str, tipe: str)
        edges       : list of (u, v, jarak_km, biaya_per_km)
        produk_list : list of Produk
    """
    # gunakan dua RNG terpisah agar konsisten dengan starter code dosen
    rng = np.random.default_rng(seed)
    random.seed(seed)

    # ── Buat 26 node sesuai spesifikasi sistem ──
    nodes = []
    for i in range(10): nodes.append((f'PTN{i:02d}', 'PETANI'))        # 10 petani
    for i in range(5):  nodes.append((f'DST{i:02d}', 'DISTRIBUTOR'))   # 5 distributor
    for i in range(8):  nodes.append((f'PSR{i:02d}', 'PASAR'))         # 8 pasar
    for i in range(3):  nodes.append((f'GDG{i:02d}', 'GUDANG'))        # 3 gudang
    n = len(nodes)  # total = 26 node

    # ── Buat spanning tree acak (pastikan semua node terhubung) ──
    # permutasi acak node, lalu hubungkan secara berantai → jamin konektivitas
    perm  = rng.permutation(n)
    edges = []
    for i in range(1, n):
        u, v = nodes[perm[i - 1]][0], nodes[perm[i]][0]
        edges.append((
            u, v,
            int(rng.integers(5, 200)),                   # jarak 5–199 km
            round(float(rng.uniform(500, 3000)), 0)      # biaya Rp500–3000/km
        ))

    # ── Tambah 12 edge acak ekstra (membuat graph lebih realistis) ──
    for _ in range(12):
        i, j = rng.choice(n, 2, replace=False)
        edges.append((
            nodes[i][0], nodes[j][0],
            int(rng.integers(5, 200)),
            round(float(rng.uniform(500, 3000)), 0)
        ))

    # ── Buat 12 produk dengan data acak (tapi deterministik) ──
    nama_produk = [
        'Beras', 'Cabai', 'Tomat', 'Ayam', 'Ikan Lele', 'Kangkung',
        'Wortel', 'Kentang', 'Telur', 'Tahu', 'Tempe', 'Minyak'
    ]
    produk_list = []
    for i, nama in enumerate(nama_produk):
        produk_list.append(Produk(
            kode                = f'PRD-{i:03d}',
            nama                = nama,
            kategori            = random.choice(KATEGORI_PRODUK),
            harga_satuan        = round(random.uniform(2000, 50000), -2),
            stok                = random.randint(50, 500),
            masa_kadaluarsa_hari= random.randint(1, 30)
        ))

    return nodes, edges, produk_list