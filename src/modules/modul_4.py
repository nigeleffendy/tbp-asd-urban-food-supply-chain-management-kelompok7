# =============================================================================
#  modul_4.py  –  Modul BST Katalog Produk
# =============================================================================
#
#  Modul ini mengelola KATALOG PRODUK menggunakan Binary Search Tree.
#  Setiap produk diidentifikasi dengan kode unik (PRD-000 s.d. PRD-011).
#
#  Fungsi utama:
#    - inisialisasi_katalog   : isi BST dari list produk generator
#    - cek_stok_produk        : cari & tampilkan info produk (search BST)
#    - perbarui_stok          : tambah/kurangi stok (update BST)
#    - daftar_kadaluarsa      : filter produk mendekati kadaluarsa
#    - tampilkan_katalog      : cetak semua produk terurut kode (inorder)
#    - ringkasan_katalog      : statistik total stok, harga rata-rata, dll.
#
#  Big-O operasi BST:
#    insert / search / update : O(log n) rata-rata
#    filter / inorder         : O(n)
# =============================================================================

from src.data_structures.bst import BSTKatalog
from src.data_models import Produk


# Label status berdasarkan masa kadaluarsa
def _label_status(hari: int) -> str:
    if hari <= 3:
        return 'MENDESAK'
    elif hari <= 7:
        return 'REGULER'
    return 'NORMAL'


# ─────────────────────────────────────────────
#  INISIALISASI
# ─────────────────────────────────────────────

def inisialisasi_katalog(produk_list: list) -> BSTKatalog:
    """
    Bangun BST katalog dari list produk hasil generate_rantai_pasok().

    Produk di-insert satu per satu ke BST dengan kode sebagai kunci.
    Urutan insert tidak mempengaruhi hasil pencarian karena BST
    menjamin posisi node berdasarkan perbandingan kunci.

    Kembalikan:
        bst_katalog : BSTKatalog yang sudah terisi 12 produk
    """
    bst_katalog = BSTKatalog()
    for produk in produk_list:
        bst_katalog.insert(produk)
    return bst_katalog


# ─────────────────────────────────────────────
#  OPERASI KATALOG
# ─────────────────────────────────────────────

def cek_stok_produk(bst_katalog: BSTKatalog, kode: str) -> tuple:
    """
    Cari produk di katalog BST dan kembalikan info lengkapnya.

    Kembalikan:
        (True,  produk)       jika ditemukan
        (False, pesan_error)  jika tidak ada
    """
    produk = bst_katalog.search(kode)
    if produk is None:
        return False, f"Produk dengan kode '{kode}' tidak ditemukan di katalog."
    return True, produk


def perbarui_stok(
    bst_katalog   : BSTKatalog,
    log_transaksi,              # Stack
    kode          : str,
    delta         : int,
    keterangan    : str = ''
) -> tuple:
    """
    Perbarui stok produk sebesar delta (positif = tambah, negatif = kurang).
    Stok tidak akan turun di bawah 0.

    Kembalikan:
        (True,  pesan_sukses)  jika berhasil
        (False, pesan_error)   jika produk tidak ditemukan
    """
    produk = bst_katalog.search(kode)
    if produk is None:
        return False, f"Produk '{kode}' tidak ditemukan, stok tidak diperbarui."

    stok_lama = produk.stok
    bst_katalog.update_stok(kode, delta)
    stok_baru = produk.stok   # sudah diubah langsung pada objek

    arah = f"+{delta}" if delta >= 0 else str(delta)
    log_transaksi.push(
        f"[STOK] {kode} {arah} | {stok_lama} -> {stok_baru}"
        + (f" | {keterangan}" if keterangan else "")
    )

    pesan = (f"Stok '{produk.nama}' ({kode}) diperbarui: "
             f"{stok_lama} -> {stok_baru}  (delta: {arah})")
    return True, pesan


def daftar_kadaluarsa(bst_katalog: BSTKatalog, maks_hari: int) -> list:
    """
    Ambil semua produk dengan masa kadaluarsa <= maks_hari dari BST.
    Hasil sudah terurut berdasarkan kode (karena inorder traversal).

    Kembalikan list Produk. List kosong jika tidak ada yang lolos filter.
    """
    return bst_katalog.filter_kadaluarsa(maks_hari)


# ─────────────────────────────────────────────
#  TAMPILAN KATALOG
# ─────────────────────────────────────────────

def tampilkan_katalog(bst_katalog: BSTKatalog):
    """
    Tampilkan semua produk dalam katalog, terurut kode (inorder BST).
    Sertakan info kode, nama, kategori, harga, stok, kadaluarsa, dan status.
    """
    semua = bst_katalog.inorder()
    if not semua:
        print("  (katalog kosong)")
        return

    print(f"\n  {'Kode':<10} {'Nama':<14} {'Kategori':<14} "
          f"{'Harga':>12} {'Stok':>6} {'Kadaluarsa':>12}  Status")
    print(f"  {'-'*78}")

    for p in semua:
        status = _label_status(p.masa_kadaluarsa_hari)
        print(f"  {p.kode:<10} {p.nama:<14} {p.kategori:<14} "
              f"Rp {p.harga_satuan:>9,.0f} {p.stok:>6} "
              f"{p.masa_kadaluarsa_hari:>9} hari  {status}")

    print(f"  {'-'*78}")
    print(f"  Total: {len(semua)} produk terdaftar")


def tampilkan_produk(produk: Produk):
    """Cetak detail satu produk secara terformat."""
    status = _label_status(produk.masa_kadaluarsa_hari)
    print(f"\n  Kode          : {produk.kode}")
    print(f"  Nama          : {produk.nama}")
    print(f"  Kategori      : {produk.kategori}")
    print(f"  Harga Satuan  : Rp {produk.harga_satuan:,.0f}")
    print(f"  Stok          : {produk.stok} unit")
    print(f"  Kadaluarsa    : {produk.masa_kadaluarsa_hari} hari")
    print(f"  Status        : {status}")


def tampilkan_kadaluarsa(produk_list: list, maks_hari: int):
    """
    Cetak daftar produk hasil filter kadaluarsa dengan tampilan ringkas
    + peringatan untuk yang berstatus MENDESAK.
    """
    if not produk_list:
        print(f"  Tidak ada produk dengan kadaluarsa <= {maks_hari} hari.")
        return

    print(f"\n  {'Status':<10} {'Kode':<10} {'Nama':<14} "
          f"{'Stok':>6}  {'Kadaluarsa':>12}")
    print(f"  {'-'*58}")

    for p in produk_list:
        status = _label_status(p.masa_kadaluarsa_hari)
        tanda  = ' ⚠' if status == 'MENDESAK' else ''
        print(f"  {status:<10} {p.kode:<10} {p.nama:<14} "
              f"{p.stok:>6}  {p.masa_kadaluarsa_hari:>9} hari{tanda}")

    print(f"  {'-'*58}")
    mendesak = sum(1 for p in produk_list if p.masa_kadaluarsa_hari <= 3)
    print(f"  Total: {len(produk_list)} produk  |  MENDESAK: {mendesak}")


def ringkasan_katalog(bst_katalog: BSTKatalog):
    """
    Cetak statistik ringkas katalog:
    total produk, total stok, rata-rata harga, distribusi status kadaluarsa.
    """
    semua = bst_katalog.inorder()
    if not semua:
        print("  Katalog kosong.")
        return

    total_stok    = sum(p.stok           for p in semua)
    total_harga   = sum(p.harga_satuan   for p in semua)
    rata_harga    = total_harga / len(semua)

    # hitung distribusi per status
    distribusi = {'MENDESAK': 0, 'REGULER': 0, 'NORMAL': 0}
    for p in semua:
        distribusi[_label_status(p.masa_kadaluarsa_hari)] += 1

    # hitung distribusi per kategori
    per_kategori: dict = {}
    for p in semua:
        per_kategori[p.kategori] = per_kategori.get(p.kategori, 0) + 1

    print(f"\n  Jumlah Produk  : {len(semua)}")
    print(f"  Total Stok     : {total_stok} unit")
    print(f"  Rata-rata Harga: Rp {rata_harga:,.0f}")
    print(f"\n  Distribusi Status Kadaluarsa:")
    for status, jml in distribusi.items():
        bar = '▮' * jml
        print(f"    {status:<10} : {jml:>3}  {bar}")
    print(f"\n  Distribusi Kategori:")
    for kat, jml in sorted(per_kategori.items()):
        print(f"    {kat:<15}: {jml:>3}")
        
