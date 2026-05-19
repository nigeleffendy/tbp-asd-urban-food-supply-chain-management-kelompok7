# =============================================================================
#  bst.py  –  Binary Search Tree (BST) untuk Katalog Produk
# =============================================================================
#  BST digunakan sebagai katalog produk dengan kunci = kode produk (string).
#  Operasi utama:
#    - insert               : O(log n)  – tambah / perbarui produk
#    - search               : O(log n)  – cari produk berdasarkan kode
#    - update_stok          : O(log n)  – ubah jumlah stok
#    - filter_kadaluarsa    : O(n)      – inorder traversal dengan filter
#    - inorder              : O(n)      – kembalikan semua produk urut kode
#
#  Karena menggunakan binary search(banyak data yang ada di sistemnya di bagi
#  menjadi dua bagian), pencarian produk berdasarkan kode sangat efisien (O(log n)), 
#  pencarian jauh lebih cepat
#  dibandingkan linear search pada list (O(n)).
# =============================================================================
 
from src.data_models import Produk
 
 
class BSTNodeProd:
    """
    Node tunggal pada BST Katalog.
    Setiap node menyimpan satu objek Produk beserta pointer kiri dan kanan.
    """
    def __init__(self, produk: Produk):
        self.produk = produk
        self.left   = None   # subtree produk dengan kode < kode node ini
        self.right  = None   # subtree produk dengan kode > kode node ini
 
 
class BSTKatalog:
    """
    Binary Search Tree untuk menyimpan dan mengelola katalog produk.
    Kunci pencarian: produk.kode  (string, dibandingkan secara leksikografis(membandingkan 
    atau mengurutkan data berdasarkan urutan seperti di kamus)).
    """
 
    def __init__(self):
        self.root = None   # akar BST, None berarti katalog masih kosong
 
    # ─────────────────────────────────────────
    #  INSERT
    # ─────────────────────────────────────────
    def insert(self, produk: Produk):
        """
        Tambahkan produk ke BST.
        Jika kode sudah ada, data produk diperbarui (upsert).
        Big-O: O(log n) rata-rata, O(n) worst-case (pohon tidak seimbang).
        """
        self.root = self._insert_rekursif(self.root, produk)
 
    def _insert_rekursif(self, node, produk):
        # basis: posisi kosong ditemukan, lalu buat node baru
        if node is None:
            return BSTNodeProd(produk)
 
        if produk.kode < node.produk.kode:
            # kode lebih kecil → masuk ke subtree kiri
            node.left  = self._insert_rekursif(node.left, produk)
        elif produk.kode > node.produk.kode:
            # kode lebih besar → masuk ke subtree kanan
            node.right = self._insert_rekursif(node.right, produk)
        else:
            # kode sama → perbarui data produk (upsert)
            node.produk = produk
 
        return node
 
    # ─────────────────────────────────────────
    #  SEARCH
    # ─────────────────────────────────────────
    def search(self, kode: str):
        """
        Cari produk berdasarkan kode.
        Kembalikan objek Produk jika ditemukan, None jika tidak ada.
        Big-O: O(log n) rata-rata.
        """
        return self._search_rekursif(self.root, kode)
 
    def _search_rekursif(self, node, kode):
        # basis: node kosong = tidak ditemukan
        if node is None:
            return None
 
        if kode == node.produk.kode:
            return node.produk               # ketemu!
        elif kode < node.produk.kode:
            return self._search_rekursif(node.left, kode)   # cari ke kiri
        else:
            return self._search_rekursif(node.right, kode)  # cari ke kanan
 
    # ─────────────────────────────────────────
    #  UPDATE STOK
    # ─────────────────────────────────────────
    def update_stok(self, kode: str, delta: int) -> bool:
        """
        Ubah stok produk sebesar delta (bisa positif/negatif).
        Stok tidak akan turun di bawah 0.
        Kembalikan True jika berhasil, False jika produk tidak ditemukan.
        Big-O: O(log n).
        """
        produk = self.search(kode)
        if produk is None:
            return False
 
        # pastikan stok tidak negatif
        produk.stok = max(0, produk.stok + delta)
        return True
 