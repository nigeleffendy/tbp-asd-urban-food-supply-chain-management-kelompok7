# =============================================================================
#  modul_3.py  –  Modul Priority Queue Pengiriman
# =============================================================================
#
#  Modul ini mengelola ANTRIAN PENGIRIMAN dengan sistem prioritas.
#  Produk yang mendekati kadaluarsa harus dikirim lebih dahulu agar tidak
#  terbuang sia-sia sebelum sampai ke konsumen.
#
#  Skema prioritas:
#    1 = MENDESAK  (kadaluarsa <= 3 hari)   → kirim PALING dulu
#    2 = REGULER   (kadaluarsa 4–7 hari)    → kirim setelah MENDESAK
#    3 = NORMAL    (kadaluarsa > 7 hari)    → kirim terakhir
#
#  Fungsi utama:
#    - tentukan_prioritas   : hitung prioritas berdasarkan masa kadaluarsa
#    - buat_pengiriman      : buat objek Pengiriman dan masukkan ke antrian
#    - proses_pengiriman    : dequeue satu pengiriman paling prioritas
#    - tampilkan_antrian    : cetak semua pengiriman yang menunggu
#    - ringkasan_antrian    : statistik antrian (jumlah per prioritas)
# =============================================================================

import time
from src.data_structures.priority_queue import PriorityQueueKirim
from src.data_structures.stack          import Stack
from src.data_structures.bst            import BSTKatalog
from src.data_models                    import Pengiriman, Produk


# Label teks untuk tiap level prioritas
LABEL_PRIORITAS = {1: 'MENDESAK', 2: 'REGULER', 3: 'NORMAL'}


# ─────────────────────────────────────────────
#  LOGIKA PRIORITAS
# ─────────────────────────────────────────────

def tentukan_prioritas(produk: Produk) -> int:
    """
    Tentukan level prioritas pengiriman berdasarkan masa kadaluarsa produk.

    Semakin dekat kadaluarsa, semakin tinggi prioritas (nilai lebih kecil).
    Ini memastikan produk berisiko kadaluarsa selalu dikirim duluan.

    Kembalikan: 1 (MENDESAK), 2 (REGULER), atau 3 (NORMAL)
    """
    hari = produk.masa_kadaluarsa_hari
    if hari <= 3:
        return 1   # MENDESAK – harus segera dikirim hari ini
    elif hari <= 7:
        return 2   # REGULER  – kirim dalam minggu ini
    else:
        return 3   # NORMAL   – tidak terburu-buru


# ─────────────────────────────────────────────
#  OPERASI ANTRIAN
# ─────────────────────────────────────────────

def buat_pengiriman(
    pq_kirim      : PriorityQueueKirim,
    log_transaksi : Stack,
    bst_katalog   : BSTKatalog,
    kirim_counter : list,          # [int] – wrapper agar bisa dimodifikasi
    dari_node     : str,
    ke_node       : str,
    kode_produk   : str,
    jumlah        : int
) -> tuple:
    """
    Validasi input lalu buat dan masukkan objek Pengiriman ke antrian prioritas.

    Validasi yang dilakukan:
      1. Produk harus ada di katalog BST.
      2. Stok harus mencukupi jumlah yang diminta.

    Kembalikan:
        (True, pesan_sukses)  jika pengiriman berhasil dibuat
        (False, pesan_error)  jika validasi gagal
    """
    # ── 1. validasi produk di katalog ──
    produk = bst_katalog.search(kode_produk)
    if produk is None:
        return False, f"Produk '{kode_produk}' tidak ditemukan di katalog."

    # ── 2. validasi stok mencukupi ──
    if produk.stok < jumlah:
        return False, (f"Stok '{produk.nama}' tidak cukup. "
                       f"Diminta: {jumlah}, tersedia: {produk.stok}.")

    # ── 3. tentukan prioritas berdasarkan kadaluarsa ──
    prioritas = tentukan_prioritas(produk)

    # ── 4. buat dan enqueue objek Pengiriman ──
    kirim_counter[0] += 1
    kiriman = Pengiriman(
        pengiriman_id = kirim_counter[0],
        dari_node     = dari_node,
        ke_node       = ke_node,
        kode_produk   = kode_produk,
        jumlah        = jumlah,
        prioritas     = prioritas,
        waktu_kirim   = time.time()
    )
    pq_kirim.enqueue(kiriman)

    # ── 5. catat ke log transaksi ──
    label = LABEL_PRIORITAS[prioritas]
    log_transaksi.push(
        f"[KIRIM] ID#{kiriman.pengiriman_id} "
        f"{dari_node}->{ke_node} {kode_produk} x{jumlah} [{label}]"
    )

    pesan = (f"Pengiriman #{kiriman.pengiriman_id} ditambahkan ke antrian.\n"
             f"       Produk   : {produk.nama} ({kode_produk})\n"
             f"       Rute     : {dari_node} -> {ke_node}\n"
             f"       Jumlah   : {jumlah}  |  Prioritas: {label} "
             f"(kadaluarsa {produk.masa_kadaluarsa_hari} hari)\n"
             f"       Antrian  : {len(pq_kirim)} kiriman menunggu")
    return True, pesan


def proses_pengiriman(
    pq_kirim      : PriorityQueueKirim,
    log_transaksi : Stack,
    bst_katalog   : BSTKatalog,
    buffer_gudang : dict
) -> tuple:
    """
    Proses satu pengiriman dari antrian — selalu yang paling mendesak duluan.

    Efek samping:
      - Stok produk dikurangi di katalog BST.
      - Produk dimasukkan ke buffer CircularQueue node tujuan.
      - Log transaksi diperbarui.

    Kembalikan:
        (True, pesan_sukses)   jika ada pengiriman yang diproses
        (False, pesan_error)   jika antrian kosong
    """
    if len(pq_kirim) == 0:
        return False, "Antrian pengiriman kosong. Tidak ada yang bisa diproses."

    kiriman = pq_kirim.dequeue()
    produk  = bst_katalog.search(kiriman.kode_produk)

    # kurangi stok di katalog
    if produk:
        bst_katalog.update_stok(kiriman.kode_produk, -kiriman.jumlah)

    # masukkan produk ke buffer node tujuan
    if kiriman.ke_node in buffer_gudang and produk:
        cq = buffer_gudang[kiriman.ke_node]
        if not cq.is_full():
            cq.enqueue(produk)

    # catat ke log
    log_transaksi.push(
        f"[PROSES] ID#{kiriman.pengiriman_id} "
        f"{kiriman.dari_node}->{kiriman.ke_node} selesai dikirim"
    )

    stok_info = f"Stok sisa: {produk.stok}" if produk else "Produk tidak ditemukan di BST"
    pesan = (f"Pengiriman #{kiriman.pengiriman_id} berhasil diproses.\n"
             f"       Rute     : {kiriman.dari_node} -> {kiriman.ke_node}\n"
             f"       Produk   : {kiriman.kode_produk}  x{kiriman.jumlah}\n"
             f"       {stok_info}\n"
             f"       Sisa antrian: {len(pq_kirim)} kiriman")
    return True, pesan


# ─────────────────────────────────────────────
#  TAMPILAN ANTRIAN
# ─────────────────────────────────────────────

def tampilkan_antrian(pq_kirim: PriorityQueueKirim, bst_katalog: BSTKatalog):
    """
    Cetak semua pengiriman dalam antrian secara non-destructive.
    Urutan tampil mencerminkan urutan pemrosesan (prioritas terkecil dulu).
    """
    if len(pq_kirim) == 0:
        print("  (antrian pengiriman kosong)")
        return

    print(f"\n  {'No':<4} {'ID':>5} {'Prioritas':<12} {'Dari':<8} {'Ke':<8} "
          f"{'Produk':<10} {'Jumlah':>8}")
    print(f"  {'-'*65}")

    cur = pq_kirim.head
    no  = 1
    while cur is not None:
        k     = cur.data
        label = LABEL_PRIORITAS.get(k.prioritas, str(k.prioritas))
        print(f"  {no:<4} #{k.pengiriman_id:>4}  {label:<12} {k.dari_node:<8} "
              f"{k.ke_node:<8} {k.kode_produk:<10} {k.jumlah:>8}")
        cur = cur.next
        no += 1

    print(f"  {'-'*65}")
    print(f"  Total: {len(pq_kirim)} pengiriman menunggu")


def ringkasan_antrian(pq_kirim: PriorityQueueKirim):
    """
    Hitung dan tampilkan jumlah pengiriman per level prioritas.
    Berguna untuk monitoring beban antrian secara cepat.
    """
    hitung = {1: 0, 2: 0, 3: 0}
    cur    = pq_kirim.head
    while cur is not None:
        p = cur.data.prioritas
        if p in hitung:
            hitung[p] += 1
        cur = cur.next

    print(f"\n  Ringkasan Antrian Pengiriman:")
    for level, label in LABEL_PRIORITAS.items():
        bar = '▮' * hitung[level]
        print(f"    [{level}] {label:<10} : {hitung[level]:>4} kiriman  {bar}")
    print(f"    {'─'*35}")
    print(f"    {'TOTAL':<16} : {len(pq_kirim):>4} kiriman")