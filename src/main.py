# =============================================================================
#  main.py  –  Entry Point Sistem Urban Food Supply Chain Management
# =============================================================================
#
#  File ini adalah titik masuk program. Tugasnya hanya:
#    1. Generate data awal (nodes, edges, produk) via data_generator
#    2. Inisialisasi semua struktur data via modul 1–4
#    3. Serahkan semua state ke modul_6 (CLI loop)
#
#  Tidak ada logika bisnis di sini — semuanya didelegasikan ke modul yang tepat.
# =============================================================================

from src.data_generator          import generate_rantai_pasok
from src.data_structures.priority_queue import PriorityQueueKirim
from src.data_structures.stack          import Stack

from src.modules.modul_1 import inisialisasi_graph
from src.modules.modul_2 import inisialisasi_buffer
from src.modules.modul_4 import inisialisasi_katalog
from src.modules.modul_6 import jalankan_cli


def main():
    # ── 1. Generate data awal (seed=61, deterministik sesuai ketentuan dosen) ──
    nodes, edges, produk_list = generate_rantai_pasok(seed=61)

    # ── 2. Inisialisasi struktur data ──
    graph         = inisialisasi_graph(nodes, edges)            # Modul 1
    buffer_gudang = inisialisasi_buffer(                        # Modul 2
                        [nid for nid, _ in nodes], kapasitas=50
                    )
    bst_katalog   = inisialisasi_katalog(produk_list)           # Modul 4
    pq_kirim      = PriorityQueueKirim()                        # Modul 3
    log_transaksi = Stack()                                     # log global
    kirim_counter = [0]   # list agar bisa dimodifikasi di dalam fungsi

    # ── 3. Jalankan CLI loop (Modul 6) ──
    jalankan_cli(
        graph         = graph,
        bst_katalog   = bst_katalog,
        pq_kirim      = pq_kirim,
        log_transaksi = log_transaksi,
        buffer_gudang = buffer_gudang,
        kirim_counter = kirim_counter
    )


if __name__ == '__main__':
    main()