# =============================================================================
#  modul_6.py  –  Modul CLI Rantai Pasok
# =============================================================================
#
#  Modul ini adalah ANTARMUKA UTAMA pengguna — semua perintah CLI ditangani
#  di sini. Modul 6 bersifat "orchestrator": ia memanggil fungsi dari
#  modul 1–5 sesuai perintah yang diketik pengguna.
#
#  Perintah yang tersedia:
#    KIRIM <dari> <ke> <kode> <jumlah>  – buat pengiriman baru
#    PROSES_KIRIM                       – proses satu pengiriman teratas
#    RUTE_MURAH <dari> <ke>             – cari jalur distribusi termurah
#    CEK_STOK <kode>                    – info produk dari katalog BST
#    KATALOG                            – tampilkan seluruh katalog produk (BST inorder)
#    KADALUARSA <maks_hari>             – daftar produk mendekati kadaluarsa
#    LAPORAN_DISTRIBUSI                 – ringkasan lengkap seluruh sistem
#    BUFFER <node_id>                   – cek isi circular queue buffer gudang
#    AUDIT_JARINGAN                     – BFS konektivitas seluruh jaringan
#    ANTRIAN                            – tampilkan isi antrian pengiriman
#    BANTUAN                            – daftar perintah
#    KELUAR                             – keluar dari sistem
# =============================================================================

from src.data_structures.graph          import GraphRantaiPasok
from src.data_structures.bst            import BSTKatalog
from src.data_structures.priority_queue import PriorityQueueKirim
from src.data_structures.stack          import Stack
from src.data_structures.circular_queue import CircularQueue

from src.modules.modul_1 import (
    audit_konektivitas,
    audit_dfs,
    tampilkan_info_node,
    tampilkan_semua_node
)
from src.modules.modul_2 import (
    cek_buffer_node,
    laporan_semua_buffer
)
from src.modules.modul_3 import (
    buat_pengiriman,
    proses_pengiriman,
    tampilkan_antrian,
    ringkasan_antrian
)
from src.modules.modul_4 import (
    cek_stok_produk,
    tampilkan_produk,
    tampilkan_kadaluarsa,
    daftar_kadaluarsa,
    tampilkan_katalog,
    ringkasan_katalog
)
from src.modules.modul_5 import (
    cari_rute_termurah,
    tampilkan_rute,
    semua_rute_dari_node
)


# ─────────────────────────────────────────────
#  TEKS BANTUAN
# ─────────────────────────────────────────────

TEKS_BANTUAN = """
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
"""


# ─────────────────────────────────────────────
#  HELPER CETAK
# ─────────────────────────────────────────────

def _garis(karakter: str = '─', panjang: int = 62):
    print(f"  {karakter * panjang}")

def _header(judul: str):
    print(f"\n  {'═' * 62}")
    print(f"  {judul}")
    print(f"  {'═' * 62}")


# ─────────────────────────────────────────────
#  HANDLER TIAP PERINTAH
# ─────────────────────────────────────────────

def _handle_kirim(bagian, graph, pq_kirim, log_transaksi, bst_katalog, kirim_counter):
    """Handler perintah KIRIM <dari> <ke> <kode> <jumlah>."""
    if len(bagian) < 5:
        print("  [!] Format: KIRIM <dari> <ke> <kode> <jumlah>")
        print("      Contoh: KIRIM PTN00 PSR02 PRD-001 50")
        return

    dari_node, ke_node, kode = bagian[1], bagian[2], bagian[3]

    try:
        jumlah = int(bagian[4])
        if jumlah <= 0:
            print("  [!] Jumlah harus lebih dari 0.")
            return
    except ValueError:
        print("  [!] Jumlah harus berupa bilangan bulat positif.")
        return

    # validasi node ada di jaringan
    if dari_node not in graph.adj:
        print(f"  [!] Node asal '{dari_node}' tidak ditemukan. "
              f"Gunakan AUDIT_JARINGAN untuk melihat daftar node.")
        return
    if ke_node not in graph.adj:
        print(f"  [!] Node tujuan '{ke_node}' tidak ditemukan.")
        return

    sukses, pesan = buat_pengiriman(
        pq_kirim, log_transaksi, bst_katalog,
        kirim_counter, dari_node, ke_node, kode, jumlah
    )

    if sukses:
        print(f"  [OK] {pesan}")
    else:
        print(f"  [!] {pesan}")


def _handle_proses_kirim(pq_kirim, log_transaksi, bst_katalog, buffer_gudang):
    """Handler perintah PROSES_KIRIM."""
    sukses, pesan = proses_pengiriman(
        pq_kirim, log_transaksi, bst_katalog, buffer_gudang
    )
    if sukses:
        print(f"  [OK] {pesan}")
    else:
        print(f"  [!] {pesan}")


def _handle_rute_murah(bagian, graph, log_transaksi):
    """Handler perintah RUTE_MURAH <dari> <ke>."""
    if len(bagian) < 3:
        print("  [!] Format: RUTE_MURAH <dari> <ke>")
        print("      Contoh: RUTE_MURAH PTN00 GDG02")
        return

    asal, tujuan = bagian[1], bagian[2]
    sukses, hasil = cari_rute_termurah(graph, log_transaksi, asal, tujuan)

    if sukses:
        _header(f"Jalur Termurah  {asal}  →  {tujuan}")
        tampilkan_rute(graph, hasil)
    else:
        print(f"  [!] {hasil}")


def _handle_cek_stok(bagian, bst_katalog):
    """Handler perintah CEK_STOK <kode>."""
    if len(bagian) < 2:
        print("  [!] Format: CEK_STOK <kode>")
        print("      Contoh: CEK_STOK PRD-003")
        return

    kode = bagian[1]
    sukses, hasil = cek_stok_produk(bst_katalog, kode)

    if sukses:
        _header(f"Info Produk  -  {hasil.nama}")
        tampilkan_produk(hasil)
        _garis()
    else:
        print(f"  [!] {hasil}")

def _handle_katalog(bst_katalog):
    """Handler perintah KATALOG."""
    _header("Katalog Produk")
    tampilkan_katalog(bst_katalog)
    _garis()

def _handle_kadaluarsa(bagian, bst_katalog):
    """Handler perintah KADALUARSA <maks_hari>."""
    if len(bagian) < 2:
        print("  [!] Format: KADALUARSA <maks_hari>")
        print("      Contoh: KADALUARSA 7")
        return

    try:
        maks = int(bagian[1])
        if maks < 0:
            print("  [!] maks_hari tidak boleh negatif.")
            return
    except ValueError:
        print("  [!] maks_hari harus berupa angka.")
        return

    hasil = daftar_kadaluarsa(bst_katalog, maks)
    _header(f"Produk Kadaluarsa  ≤  {maks} Hari")
    tampilkan_kadaluarsa(hasil, maks)


