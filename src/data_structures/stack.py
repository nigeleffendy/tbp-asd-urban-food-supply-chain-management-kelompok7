# =============================================================================
#  stack.py  –  Stack (Tumpukan) untuk Log Transaksi
# =============================================================================
#
#  Stack berbasis singly linked list.
#  Digunakan untuk menyimpan log/riwayat transaksi pengiriman.
#
#  Prinsip LIFO (Last-In First-Out):
#    → Transaksi terakhir yang masuk, pertama kali keluar.
#    → Cocok untuk menampilkan "log terbaru" dengan pop berurutan.
#
#  Mengapa linked list, bukan array/list Python?
#    → Tidak ada batas kapasitas (dinamis).
#    → push dan pop di ujung depan selalu O(1) tanpa geser elemen.
#
#  Big-O:
#    push : O(1)
#    pop  : O(1)
# =============================================================================


from src.data_structures.linked_list import LLNode

class Stack:
    """
    Stack berbasis linked list untuk menyimpan log transaksi sistem.
    Elemen paling atas (top) adalah transaksi yang paling baru ditambahkan.
    """

    def __init__(self):
        self.top   = None   # pointer ke node paling atas (paling baru)
        self._size = 0

    # ─────────────────────────────────────────
    #  PUSH  –  Tambahkan log ke atas tumpukan
    # ─────────────────────────────────────────
    def push(self, data):
        """
        Tambahkan data baru ke puncak stack.
        Node baru menjadi top baru, menunjuk ke top sebelumnya.
        Big-O: O(1).
        """
        node      = LLNode(data)
        node.next = self.top   # tumpuk di atas top saat ini
        self.top  = node
        self._size += 1

    # ─────────────────────────────────────────
    #  POP  –  Ambil log teratas
    # ─────────────────────────────────────────
    def pop(self):
        """
        Ambil dan hapus elemen dari puncak stack.
        Kembalikan None jika stack kosong.
        Big-O: O(1).
        """
        if self.top is None:
            return None

        item     = self.top.data
        self.top = self.top.next   # turunkan top ke node di bawahnya
        self._size -= 1
        return item

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size
