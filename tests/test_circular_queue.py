# =============================================================================
#  test_circular_queue.py  –  Unit Test: Circular Queue Buffer Gudang
#  Tugas Besar ASD  |  Topik 10: Urban Food Supply Chain Management
# =============================================================================
#
#  Menguji seluruh perilaku CircularQueue:
#    1. enqueue        – masukkan item, tolak jika penuh
#    2. dequeue        – ambil item urutan FIFO, None jika kosong
#    3. is_full        – deteksi buffer penuh
#    4. is_empty       – deteksi buffer kosong
#    5. circular wrap  – pointer melingkar dengan benar setelah melewati batas array
#    6. edge case      – kapasitas 1, enqueue+dequeue berselang-seling
#
#  Cara jalankan (dari root project):
#      python -m pytest tests/test_circular_queue.py -v
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.data_structures.circular_queue import CircularQueue


# ─────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def cq_kecil():
    """CircularQueue berkapasitas 3, memudahkan pengujian kondisi penuh."""
    return CircularQueue(kapasitas=3)

@pytest.fixture
def cq_standar():
    """CircularQueue berkapasitas 50 seperti di sistem nyata."""
    return CircularQueue(kapasitas=50)


# ─────────────────────────────────────────────
#  TEST KONDISI AWAL
# ─────────────────────────────────────────────

class TestKondisiAwal:

    def test_awal_kosong(self, cq_standar):
        """Queue baru harus kosong."""
        assert cq_standar.is_empty() is True
        assert len(cq_standar)       == 0

    def test_awal_tidak_penuh(self, cq_standar):
        """Queue baru tidak boleh penuh."""
        assert cq_standar.is_full() is False

    def test_kapasitas_tersimpan(self, cq_kecil):
        """Kapasitas yang diberikan saat init harus tersimpan dengan benar."""
        assert cq_kecil.kapasitas == 3


# ─────────────────────────────────────────────
#  TEST ENQUEUE
# ─────────────────────────────────────────────

class TestEnqueue:

    def test_enqueue_berhasil(self, cq_kecil):
        """Enqueue pada queue tidak penuh harus mengembalikan True."""
        hasil = cq_kecil.enqueue('Beras')
        assert hasil is True
        assert len(cq_kecil) == 1

    def test_enqueue_beberapa_item(self, cq_kecil):
        """Ukuran queue harus bertambah tiap enqueue yang berhasil."""
        cq_kecil.enqueue('Beras')
        cq_kecil.enqueue('Cabai')
        assert len(cq_kecil) == 2
        assert cq_kecil.is_full() is False

    def test_enqueue_sampai_penuh(self, cq_kecil):
        """Setelah mengisi semua slot, is_full harus True."""
        cq_kecil.enqueue('A')
        cq_kecil.enqueue('B')
        cq_kecil.enqueue('C')
        assert cq_kecil.is_full() is True
        assert len(cq_kecil)      == 3

    def test_enqueue_saat_penuh_ditolak(self, cq_kecil):
        """Enqueue saat penuh harus mengembalikan False dan ukuran tidak berubah."""
        cq_kecil.enqueue('A')
        cq_kecil.enqueue('B')
        cq_kecil.enqueue('C')         # penuh
        hasil = cq_kecil.enqueue('D') # harus ditolak
        assert hasil     is False
        assert len(cq_kecil) == 3     # ukuran tetap

    def test_enqueue_berbagai_tipe_data(self, cq_standar):
        """Queue harus bisa menampung semua tipe data Python."""
        cq_standar.enqueue(42)
        cq_standar.enqueue('teks')
        cq_standar.enqueue({'kode': 'PRD-001'})
        assert len(cq_standar) == 3


# ─────────────────────────────────────────────
#  TEST DEQUEUE
# ─────────────────────────────────────────────

class TestDequeue:

    def test_dequeue_urutan_fifo(self, cq_kecil):
        """
        FIFO: item yang masuk pertama harus keluar pertama.
        Ini prinsip utama yang mencegah penumpukan produk lama di gudang.
        """
        cq_kecil.enqueue('Pertama')
        cq_kecil.enqueue('Kedua')
        cq_kecil.enqueue('Ketiga')

        assert cq_kecil.dequeue() == 'Pertama'
        assert cq_kecil.dequeue() == 'Kedua'
        assert cq_kecil.dequeue() == 'Ketiga'

    def test_dequeue_kurangi_ukuran(self, cq_kecil):
        """Ukuran queue harus berkurang satu setelah setiap dequeue."""
        cq_kecil.enqueue('A')
        cq_kecil.enqueue('B')
        assert len(cq_kecil) == 2

        cq_kecil.dequeue()
        assert len(cq_kecil) == 1

        cq_kecil.dequeue()
        assert len(cq_kecil) == 0

    def test_dequeue_queue_kosong(self, cq_kecil):
        """Dequeue pada queue kosong harus mengembalikan None tanpa error."""
        assert cq_kecil.dequeue() is None

    def test_dequeue_sampai_kosong(self, cq_kecil):
        """Setelah semua item diambil, is_empty harus True."""
        cq_kecil.enqueue('X')
        cq_kecil.dequeue()
        assert cq_kecil.is_empty() is True

    def test_dequeue_bersihkan_slot(self, cq_kecil):
        """
        Slot yang sudah di-dequeue harus None (tidak ghost reference).
        Ini penting untuk mencegah memory leak pada simulasi jangka panjang.
        """
        cq_kecil.enqueue('Beras')
        slot_front = cq_kecil.front   # catat posisi front sebelum dequeue
        cq_kecil.dequeue()
        assert cq_kecil.buffer[slot_front] is None


# ─────────────────────────────────────────────
#  TEST CIRCULAR WRAP  –  Inti dari Circular Queue
# ─────────────────────────────────────────────

class TestCircularWrap:

    def test_rear_melingkar(self, cq_kecil):
        """
        Setelah isi penuh lalu kosongkan lalu isi lagi,
        pointer rear harus melingkar kembali ke indeks 0.
        Ini yang membedakan Circular Queue dari queue biasa.
        """
        # isi penuh (kapasitas=3)
        cq_kecil.enqueue('A')
        cq_kecil.enqueue('B')
        cq_kecil.enqueue('C')
        # kosongkan semua
        cq_kecil.dequeue()  # front maju ke 1
        cq_kecil.dequeue()  # front maju ke 2
        cq_kecil.dequeue()  # front maju ke 0 (wrap)
        # isi lagi, rear harusnya melingkar ke 0
        cq_kecil.enqueue('D')
        assert cq_kecil.buffer[0] == 'D', \
            "Setelah wrap, slot 0 harus terisi dengan item baru"

    def test_fifo_setelah_wrap(self, cq_kecil):
        """
        Urutan FIFO harus tetap terjaga meskipun pointer sudah melingkar.
        Ini skenario realistis: gudang terus-menerus menerima dan mengeluarkan stok.
        """
        cq_kecil.enqueue('A')   # indeks 0
        cq_kecil.enqueue('B')   # indeks 1
        cq_kecil.dequeue()      # ambil A, front → 1
        cq_kecil.enqueue('C')   # indeks 2
        cq_kecil.enqueue('D')   # rear melingkar → indeks 0

        # urutan seharusnya: B (masuk ke-2), C (ke-3), D (ke-4)
        assert cq_kecil.dequeue() == 'B'
        assert cq_kecil.dequeue() == 'C'
        assert cq_kecil.dequeue() == 'D'

    def test_berselang_seling_enqueue_dequeue(self, cq_kecil):
        """
        Simulasi operasi berselang-seling (seperti di sistem nyata).
        Queue harus tetap konsisten sepanjang operasi.
        """
        cq_kecil.enqueue(1)
        cq_kecil.enqueue(2)
        assert cq_kecil.dequeue() == 1

        cq_kecil.enqueue(3)
        cq_kecil.enqueue(4)   # penuh: [2, 3, 4]
        assert cq_kecil.dequeue() == 2
        assert cq_kecil.dequeue() == 3
        assert cq_kecil.dequeue() == 4
        assert cq_kecil.is_empty() is True


# ─────────────────────────────────────────────
#  TEST EDGE CASE
# ─────────────────────────────────────────────

class TestEdgeCase:

    def test_kapasitas_satu(self):
        """Queue dengan kapasitas 1 harus berfungsi benar."""
        cq = CircularQueue(kapasitas=1)
        assert cq.enqueue('X') is True
        assert cq.is_full()    is True
        assert cq.enqueue('Y') is False   # tolak, sudah penuh
        assert cq.dequeue()    == 'X'
        assert cq.is_empty()   is True

    def test_len_akurat(self, cq_kecil):
        """__len__ harus selalu mencerminkan jumlah item aktual."""
        assert len(cq_kecil) == 0
        cq_kecil.enqueue('A')
        assert len(cq_kecil) == 1
        cq_kecil.enqueue('B')
        assert len(cq_kecil) == 2
        cq_kecil.dequeue()
        assert len(cq_kecil) == 1
