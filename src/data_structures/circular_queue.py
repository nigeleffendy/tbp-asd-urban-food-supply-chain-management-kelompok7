# =============================================================================
#  circular_queue.py  –  Circular Queue (Buffer FIFO Gudang)
# =============================================================================
#
#  Circular Queue berbasis array dengan kapasitas tetap (fixed capacity).
#  Digunakan sebagai buffer stok setiap node (gudang, pasar, dll).
#
#  Prinsip FIFO (First-In First-Out):
#    → Produk yang masuk pertama, keluar pertama.
#    → Mencegah penumpukan produk lama yang berisiko kadaluarsa.
#
#  Cara kerja "circular":
#    → Pointer rear dan front bergerak maju dengan modulo kapasitas.
#    → Saat rear mencapai ujung array, ia "melingkar" kembali ke indeks 0.
#    → Ini menghindari pemindahan elemen (O(n)) seperti pada queue biasa.
#
#  Big-O:
#    enqueue : O(1)
#    dequeue : O(1)
#    is_full : O(1)
#    is_empty: O(1)
# =============================================================================


class CircularQueue:
    """
    Circular Queue berbasis array untuk mensimulasikan buffer FIFO stok gudang.
    Kapasitas tetap sejak inisialisasi (fixed capacity = 50 slot per node).
    """

    def __init__(self, kapasitas: int):
        self.kapasitas = kapasitas
        self.buffer    = [None] * kapasitas  # array statis berukuran kapasitas
        self.front     = 0    # indeks elemen paling depan (akan di-dequeue)
        self.rear      = 0    # indeks slot kosong berikutnya (tempat enqueue)
        self._size     = 0    # jumlah elemen yang sedang ada di buffer

    # ─────────────────────────────────────────
    #  ENQUEUE  –  Masukkan produk ke buffer
    # ─────────────────────────────────────────
    def enqueue(self, produk) -> bool:
        """
        Tambahkan produk ke belakang antrian.
        Kembalikan False jika buffer sudah penuh (tidak ada override).
        Big-O: O(1).
        """
        if self.is_full():
            return False  # tolak, buffer sudah penuh

        # simpan produk di slot rear saat ini
        self.buffer[self.rear] = produk

        # geser rear ke depan, melingkar kembali jika sudah di ujung
        self.rear  = (self.rear + 1) % self.kapasitas
        self._size += 1
        return True

    # ─────────────────────────────────────────
    #  DEQUEUE  –  Ambil produk paling lama
    # ─────────────────────────────────────────
    def dequeue(self):
        """
        Ambil dan hapus produk paling depan (paling lama masuk).
        Kembalikan None jika buffer kosong.
        Big-O: O(1).
        """
        if self.is_empty():
            return None

        item = self.buffer[self.front]
        self.buffer[self.front] = None          # bersihkan slot agar tidak ghost reference

        # geser front ke depan, melingkar kembali jika sudah di ujung
        self.front = (self.front + 1) % self.kapasitas
        self._size -= 1
        return item

    # ─────────────────────────────────────────
    #  STATUS HELPERS
    # ─────────────────────────────────────────
    def is_full(self) -> bool:
        """Buffer penuh jika jumlah elemen sama dengan kapasitas."""
        return self._size == self.kapasitas

    def is_empty(self) -> bool:
        """Buffer kosong jika tidak ada elemen di dalamnya."""
        return self._size == 0

    def __len__(self) -> int:
        return self._size

