# =============================================================================
#  modul_2.py  –  Modul Circular Queue Buffer Gudang
# =============================================================================
#
#  Modul ini mengelola BUFFER STOK setiap node dalam jaringan distribusi.
#  Setiap node (petani, distributor, pasar, gudang) memiliki satu CircularQueue
#  berkapasitas 50 slot sebagai simulasi tempat penyimpanan stok fisik.
#
#  Prinsip FIFO sangat penting di sini:
#    → Produk yang PERTAMA masuk, PERTAMA keluar.
#    → Mencegah produk lama tertimbun di belakang stok baru (risiko kadaluarsa).
#
#  Fungsi utama:
#    - inisialisasi_buffer    : buat CircularQueue untuk setiap node
#    - masukkan_stok          : enqueue produk ke buffer node tujuan
#    - ambil_stok             : dequeue produk dari buffer node
#    - cek_buffer_node        : tampilkan status & isi buffer suatu node
#    - laporan_semua_buffer   : ringkasan utilisasi buffer seluruh jaringan
# =============================================================================

from src.data_structures.circular_queue import CircularQueue
from src.data_models import Produk


# ─────────────────────────────────────────────
#  INISIALISASI
# ─────────────────────────────────────────────

def inisialisasi_buffer(node_ids: list, kapasitas: int = 50) -> dict:
    """
    Buat satu CircularQueue per node sebagai buffer penyimpanan stok.

    Parameter:
        node_ids  : list node_id yang akan diberi buffer
        kapasitas : ukuran buffer tiap node (default 50 sesuai spesifikasi)

    Kembalikan:
        buffer_gudang : dict { node_id -> CircularQueue }
    """
    buffer_gudang = {}
    for node_id in node_ids:
        buffer_gudang[node_id] = CircularQueue(kapasitas=kapasitas)
    return buffer_gudang


# ─────────────────────────────────────────────
#  OPERASI BUFFER
# ─────────────────────────────────────────────

def masukkan_stok(buffer_gudang: dict, node_id: str, produk: Produk) -> bool:
    """
    Masukkan produk ke buffer node tujuan (enqueue).

    Produk akan menempati slot berikutnya di buffer (FIFO).
    Jika buffer penuh, produk ditolak dan fungsi mengembalikan False.

    Kembalikan True jika berhasil, False jika buffer penuh.
    """
    if node_id not in buffer_gudang:
        print(f"  [!] Node '{node_id}' tidak memiliki buffer.")
        return False

    cq = buffer_gudang[node_id]

    if cq.is_full():
        print(f"  [!] Buffer {node_id} penuh ({cq.kapasitas} slot). "
              f"Produk '{produk.nama}' tidak bisa disimpan.")
        return False

    cq.enqueue(produk)
    return True


def ambil_stok(buffer_gudang: dict, node_id: str):
    """
    Ambil produk paling lama dari buffer node (dequeue, FIFO).

    Kembalikan objek Produk jika berhasil, None jika buffer kosong.
    """
    if node_id not in buffer_gudang:
        print(f"  [!] Node '{node_id}' tidak memiliki buffer.")
        return None

    cq   = buffer_gudang[node_id]
    item = cq.dequeue()

    if item is None:
        print(f"  [!] Buffer {node_id} kosong, tidak ada stok untuk diambil.")

    return item


# ─────────────────────────────────────────────
#  TAMPILAN INFO BUFFER
# ─────────────────────────────────────────────

def cek_buffer_node(buffer_gudang: dict, node_id: str, tipe_node: str = ''):
    """
    Tampilkan status lengkap buffer suatu node:
    kapasitas, jumlah terisi, persentase utilisasi, dan isi buffer (urutan FIFO).
    """
    if node_id not in buffer_gudang:
        print(f"  [!] Node '{node_id}' tidak ditemukan.")
        return

    cq          = buffer_gudang[node_id]
    utilisasi   = (len(cq) / cq.kapasitas * 100) if cq.kapasitas > 0 else 0
    label_tipe  = f"  ({tipe_node})" if tipe_node else ""

    print(f"\n  Buffer  : {node_id}{label_tipe}")
    print(f"  Status  : {'PENUH' if cq.is_full() else 'KOSONG' if cq.is_empty() else 'ADA ISI'}")
    print(f"  Terisi  : {len(cq)}/{cq.kapasitas} slot  ({utilisasi:.1f}%)")

    # tampilkan isi buffer secara non-destructive (jangan dequeue)
    if not cq.is_empty():
        print(f"  Isi (urutan FIFO – terlama di kiri):")
        isi = _intip_buffer(cq)
        # cetak maksimal 10 item agar tidak terlalu panjang
        tampil  = isi[:10]
        sisa    = len(isi) - len(tampil)
        baris   = ', '.join(
            f"{p.nama}({p.kode})" if hasattr(p, 'nama') else str(p)
            for p in tampil
        )
        print(f"    [{baris}{'...' if sisa > 0 else ''}]")
        if sisa > 0:
            print(f"    ... dan {sisa} item lainnya")
    else:
        print(f"  Isi     : (kosong)")


def laporan_semua_buffer(buffer_gudang: dict, tipe_node: dict = None):
    """
    Cetak ringkasan utilisasi buffer seluruh node dalam jaringan.
    Urutkan dari yang paling padat ke paling kosong.
    """
    # hitung utilisasi tiap node
    data = []
    for node_id, cq in buffer_gudang.items():
        tipe   = tipe_node.get(node_id, '-') if tipe_node else '-'
        persen = (len(cq) / cq.kapasitas * 100) if cq.kapasitas > 0 else 0
        data.append((node_id, tipe, len(cq), cq.kapasitas, persen))

    # urutkan dari utilisasi terbesar
    data.sort(key=lambda x: x[4], reverse=True)

    print(f"\n  {'Node':<10} {'Tipe':<14} {'Terisi':>8} {'Kapasitas':>10} {'Utilisasi':>10}")
    print(f"  {'-'*56}")
    for node_id, tipe, terisi, kapasitas, persen in data:
        bar = '█' * int(persen / 10) + '░' * (10 - int(persen / 10))
        print(f"  {node_id:<10} {tipe:<14} {terisi:>8} {kapasitas:>10} "
              f"  {bar} {persen:>5.1f}%")

    total_terisi    = sum(len(cq)         for cq in buffer_gudang.values())
    total_kapasitas = sum(cq.kapasitas    for cq in buffer_gudang.values())
    total_persen    = (total_terisi / total_kapasitas * 100) if total_kapasitas > 0 else 0

    print(f"  {'-'*56}")
    print(f"  {'TOTAL':<10} {'':<14} {total_terisi:>8} {total_kapasitas:>10}  "
          f"{'':10} {total_persen:>5.1f}%")


# ─────────────────────────────────────────────
#  HELPER INTERNAL
# ─────────────────────────────────────────────

def _intip_buffer(cq: CircularQueue) -> list:
    """
    Baca isi buffer tanpa mengubah state (non-destructive).
    Telusuri dari front hingga sebanyak _size elemen.
    """
    hasil = []
    idx   = cq.front
    for _ in range(len(cq)):
        slot = cq.buffer[idx]
        if slot is not None:
            hasil.append(slot)
        idx = (idx + 1) % cq.kapasitas
    return hasil