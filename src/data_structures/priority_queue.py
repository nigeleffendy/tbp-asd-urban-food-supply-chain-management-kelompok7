# =============================================================================
#  priority_queue.py  –  Priority Queue Pengiriman (Linked List Terurut)
# =============================================================================
#  Priority Queue berbasis singly linked list yang selalu terurut menaik
#  berdasarkan nilai prioritas pengiriman.
#
#  Skema prioritas:
#    1 = MENDESAK  (kadaluarsa <= 3 hari)  → dikirim PALING dulu
#    2 = REGULER   (kadaluarsa 4–7 hari)
#    3 = NORMAL    (kadaluarsa > 7 hari)   → dikirim paling akhir
#
#  Mengapa linked list, bukan array?
#    → Insertion di tengah lebih efisien tanpa perlu menggeser elemen.
#    → Ukuran dinamis, tidak perlu menetapkan kapasitas di awal.
#
#  Mengapa TIDAK pakai heapq bawaan Python?
#    → Sesuai ketentuan tugas: struktur data diimplementasi manual.
#
#  Big-O:
#    enqueue : O(n)  – perlu menelusuri list untuk posisi yang tepat
#    dequeue : O(1)  – selalu ambil dari head (prioritas terkecil)
# =============================================================================


from data_structures.linked_list import LLNode

class PriorityQueueKirim:
    """
    Priority Queue berbasis linked list terurut untuk antrian pengiriman.
    Head selalu menunjuk ke pengiriman dengan prioritas tertinggi (nilai terkecil).
    """

    def __init__(self):
        self.head  = None   # node paling depan (prioritas tertinggi)
        self._size = 0

    # ─────────────────────────────────────────
    #  ENQUEUE  –  Sisipkan pengiriman di posisi yang tepat
    # ─────────────────────────────────────────
    def enqueue(self, pengiriman):
        """
        Sisipkan pengiriman ke posisi yang benar agar list tetap terurut naik.
        Pengiriman dengan prioritas lebih kecil (lebih mendesak) berada di depan.
        Big-O: O(n)  - traversal untuk menemukan posisi sisip.
        """
        baru = LLNode(pengiriman)

        # Kasus 1: antrian kosong ATAU pengiriman baru lebih mendesak dari head
        if self.head is None or pengiriman.prioritas < self.head.data.prioritas:
            baru.next = self.head
            self.head = baru

        else:
            # Kasus 2: telusuri sampai menemukan posisi sisip yang tepat
            # → berhenti saat node berikutnya memiliki prioritas LEBIH BESAR
            cur = self.head
            while cur.next is not None and cur.next.data.prioritas <= pengiriman.prioritas:
                cur = cur.next

            # sisipkan baru di antara cur dan cur.next
            baru.next = cur.next
            cur.next  = baru

        self._size += 1

    # ─────────────────────────────────────────
    #  DEQUEUE  –  Ambil pengiriman paling mendesak
    # ─────────────────────────────────────────
    def dequeue(self):
        """
        Ambil dan hapus pengiriman dari depan antrian (prioritas tertinggi).
        Kembalikan None jika antrian kosong.
        Big-O: O(1).
        """
        if self.head is None:
            return None

        item      = self.head.data
        self.head = self.head.next   # geser head ke node berikutnya
        self._size -= 1
        return item

    def __len__(self) -> int:
        return self._size