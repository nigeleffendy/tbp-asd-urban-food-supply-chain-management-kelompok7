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



def _handle_laporan(graph, bst_katalog, pq_kirim, log_transaksi, buffer_gudang):
    """Handler perintah LAPORAN_DISTRIBUSI."""
    _header("LAPORAN DISTRIBUSI  -  Urban Food Supply Chain Yogyakarta")

    # ── 1. ringkasan jaringan ──
    print("\n  [1] RINGKASAN JARINGAN")
    tampilkan_semua_node(graph)

    # ── 2. ringkasan katalog ──
    print("\n  [2] RINGKASAN KATALOG PRODUK")
    ringkasan_katalog(bst_katalog)

    # ── 3. antrian pengiriman ──
    print("\n  [3] ANTRIAN PENGIRIMAN")
    ringkasan_antrian(pq_kirim)

    # ── 4. utilisasi buffer ──
    print("\n  [4] UTILISASI BUFFER GUDANG")
    laporan_semua_buffer(buffer_gudang, graph.tipe_node)

    # ── 5. log transaksi (5 terakhir) ──
    print("\n  [5] LOG TRANSAKSI (5 terakhir)")
    _tampilkan_log(log_transaksi, n=5)

    _garis('═')


def _handle_buffer(bagian, buffer_gudang, graph):
    """Handler perintah BUFFER <node_id>."""
    if len(bagian) < 2:
        print("  [!] Format: BUFFER <node_id>")
        print("      Contoh: BUFFER GDG00")
        return

    nid = bagian[1]
    if nid not in buffer_gudang:
        print(f"  [!] Node '{nid}' tidak ditemukan.")
        return

    tipe = graph.tipe_node.get(nid, '')
    _header(f"Buffer Gudang  -  {nid}")
    cek_buffer_node(buffer_gudang, nid, tipe)
    _garis()

def _handle_audit_jaringan(graph):
    """Handler perintah AUDIT_JARINGAN."""
    _header("Audit Konektivitas Jaringan Distribusi")

    # BFS dari node pertama
    asal_bfs = next(iter(graph.adj))
    hasil_bfs = audit_konektivitas(graph, asal_bfs)

    print(f"\n  BFS dari '{asal_bfs}':")
    print(f"    Node dijangkau    : {len(hasil_bfs['dikunjungi'])}")
    print(f"    Total node        : {hasil_bfs['total_node']}")
    print(f"    Status jaringan   : "
          f"{'TERHUBUNG PENUH ✓' if hasil_bfs['terhubung'] else 'ADA NODE TERISOLASI ✗'}")

    if not hasil_bfs['terhubung']:
        print(f"    Node terisolasi   : {', '.join(hasil_bfs['tidak_terjangkau'])}")

    # DFS traversal
    urutan_dfs = audit_dfs(graph, asal_bfs)
    print(f"\n  DFS dari '{asal_bfs}' — urutan kunjungan ({len(urutan_dfs)} node):")
    # tampilkan per baris, 8 node per baris
    for i in range(0, len(urutan_dfs), 8):
        baris = urutan_dfs[i:i + 8]
        print(f"    {' -> '.join(baris)}")

    _garis()


def _handle_antrian(pq_kirim, bst_katalog):
    """Handler perintah ANTRIAN."""
    _header("Antrian Pengiriman")
    tampilkan_antrian(pq_kirim, bst_katalog)
    print()
    ringkasan_antrian(pq_kirim)

