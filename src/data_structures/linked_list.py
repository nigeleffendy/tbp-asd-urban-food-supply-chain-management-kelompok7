# =============================================================================
#  linked_list.py  –  Singly Linked List (Node Dasar)
# =============================================================================
#
#  Menyediakan LLNode sebagai blok pembangun (building block) untuk
#  struktur data lain yang membutuhkan linked list:
#    - Stack             : tumpukan log transaksi (LIFO)
#    - PriorityQueueKirim: antrian pengiriman terurut prioritas (FIFO berbobot)
#
#  Prinsip Singly Linked List:
#    → Setiap node menyimpan data dan satu pointer next ke node berikutnya.
#    → Traversal hanya satu arah: head → tail.
#    → Tidak ada pointer prev, sehingga hapus node tertentu memerlukan O(n).
#
#  Mengapa linked list, bukan array/list Python?
#    → Sisip dan hapus di ujung depan selalu O(1) tanpa menggeser elemen.
#    → Ukuran dinamis, tidak perlu menetapkan kapasitas di awal.
#    → Cocok untuk Stack (push/pop di head) dan Priority Queue (insert terurut).
#
#  Big-O operasi umum pada LLNode:
#    sisip di head    : O(1)
#    hapus head       : O(1)
#    sisip di posisi  : O(n)  – perlu traversal ke posisi yang tepat
#    cari node        : O(n)  – traversal linear dari head
# =============================================================================


class LLNode:
    """
    Node tunggal pada Singly Linked List.

    Digunakan bersama oleh:
      - Stack             → node.data berisi string log transaksi
      - PriorityQueueKirim → node.data berisi objek Pengiriman

    Atribut:
        data : payload node (tipe bebas: str, Pengiriman, Produk, dll.)
        next : pointer ke node berikutnya, None jika node terakhir
    """

    def __init__(self, data=None):
        self.data = data   # isi/payload node
        self.next = None   # pointer ke node berikutnya dalam rantai