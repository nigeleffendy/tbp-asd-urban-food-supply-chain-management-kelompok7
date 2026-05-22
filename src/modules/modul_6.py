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


