# =============================================================================
#  test_stack.py  –  Unit Test: Stack Log Transaksi
# =============================================================================
#
#  Menguji seluruh perilaku Stack:
#    1. push   – tambah elemen ke puncak, ukuran bertambah
#    2. pop    – ambil elemen dari puncak (LIFO), ukuran berkurang
#    3. LIFO   – elemen terakhir masuk harus keluar pertama
#    4. edge case – stack kosong, satu elemen, berbagai tipe data
#
#  Cara jalankan (dari root project):
#      python -m pytest tests/test_stack.py -v
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.data_structures.stack import Stack


# ─────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def stack_terisi():
    """Stack dengan 4 entri log transaksi."""
    s = Stack()
    s.push('[KIRIM] #1 PTN00->PSR00 PRD-001 x10 [MENDESAK]')
    s.push('[KIRIM] #2 PTN01->PSR01 PRD-002 x20 [REGULER]')
    s.push('[PROSES] #1 PTN00->PSR00 selesai')
    s.push('[RUTE] PTN00->GDG00 biaya=150000')
    return s


# ─────────────────────────────────────────────
#  TEST KONDISI AWAL
# ─────────────────────────────────────────────

class TestKondisiAwal:

    def test_awal_kosong(self):
        """Stack baru harus kosong."""
        s = Stack()
        assert s.is_empty() is True
        assert len(s)       == 0
        assert s.top        is None

    def test_pop_saat_kosong(self):
        """Pop pada stack kosong harus mengembalikan None tanpa error."""
        s = Stack()
        assert s.pop() is None


# ─────────────────────────────────────────────
#  TEST PUSH
# ─────────────────────────────────────────────

class TestPush:

    def test_push_satu_item(self):
        """Push satu item: top harus menunjuk item tersebut."""
        s = Stack()
        s.push('log pertama')
        assert s.top is not None
        assert s.top.data == 'log pertama'
        assert len(s)     == 1

    def test_push_ganti_top(self):
        """
        Setelah push kedua, top harus berpindah ke item yang baru.
        Item lama masih ada di bawahnya (top.next).
        """
        s = Stack()
        s.push('log A')
        s.push('log B')
        assert s.top.data      == 'log B'   # top terbaru
        assert s.top.next.data == 'log A'   # item sebelumnya ada di bawah

    def test_push_tambah_ukuran(self, stack_terisi):
        """Tiap push harus menambah _size satu."""
        ukuran_awal = len(stack_terisi)
        stack_terisi.push('log baru')
        assert len(stack_terisi) == ukuran_awal + 1

    def test_push_berbagai_tipe_data(self):
        """Stack harus bisa menampung berbagai tipe data."""
        s = Stack()
        s.push(42)
        s.push('string')
        s.push({'key': 'val'})
        s.push([1, 2, 3])
        assert len(s) == 4


# ─────────────────────────────────────────────
#  TEST POP  –  LIFO
# ─────────────────────────────────────────────

class TestPop:

    def test_pop_urutan_lifo(self, stack_terisi):
        """
        LIFO: elemen yang terakhir di-push harus keluar pertama.
        Urutan push: log1, log2, log3, log4
        Urutan pop : log4, log3, log2, log1
        """
        assert stack_terisi.pop() == '[RUTE] PTN00->GDG00 biaya=150000'
        assert stack_terisi.pop() == '[PROSES] #1 PTN00->PSR00 selesai'
        assert stack_terisi.pop() == '[KIRIM] #2 PTN01->PSR01 PRD-002 x20 [REGULER]'
        assert stack_terisi.pop() == '[KIRIM] #1 PTN00->PSR00 PRD-001 x10 [MENDESAK]'

    def test_pop_kurangi_ukuran(self, stack_terisi):
        """Tiap pop harus mengurangi _size satu."""
        ukuran_awal = len(stack_terisi)   # 4
        stack_terisi.pop()
        assert len(stack_terisi) == ukuran_awal - 1

    def test_pop_sampai_kosong(self, stack_terisi):
        """Setelah semua item diambil, is_empty harus True."""
        for _ in range(len(stack_terisi)):
            stack_terisi.pop()
        assert stack_terisi.is_empty() is True
        assert stack_terisi.top        is None

    def test_pop_setelah_kosong_kembalikan_none(self, stack_terisi):
        """Pop pada stack yang baru saja dikosongkan harus None."""
        for _ in range(len(stack_terisi)):
            stack_terisi.pop()
        assert stack_terisi.pop() is None

    def test_pop_update_top(self):
        """
        Setelah pop, top harus berpindah ke item di bawahnya.
        Simulasi: push A, push B → pop → top harus kembali ke A.
        """
        s = Stack()
        s.push('A')
        s.push('B')
        s.pop()                     # hapus B
        assert s.top.data == 'A'   # top kembali ke A


# ─────────────────────────────────────────────
#  TEST EDGE CASE
# ─────────────────────────────────────────────

class TestEdgeCase:

    def test_push_pop_berselang(self):
        """
        Push dan pop berselang-seling harus tetap konsisten.
        Ini mensimulasikan log transaksi yang aktif sepanjang sesi CLI.
        """
        s = Stack()
        s.push('T1')
        s.push('T2')
        assert s.pop() == 'T2'

        s.push('T3')
        assert s.pop() == 'T3'
        assert s.pop() == 'T1'
        assert s.pop() is None

    def test_is_empty_akurat(self):
        """is_empty harus akurat di setiap tahap."""
        s = Stack()
        assert s.is_empty() is True
        s.push('X')
        assert s.is_empty() is False
        s.pop()
        assert s.is_empty() is True

    def test_len_akurat(self):
        """__len__ harus selalu mencerminkan jumlah item aktual."""
        s = Stack()
        for i in range(5):
            s.push(f'item-{i}')
            assert len(s) == i + 1
        for i in range(5, 0, -1):
            s.pop()
            assert len(s) == i - 1

    def test_stack_tidak_rusak_setelah_pop_berulang(self):
        """
        Stress test: push banyak item lalu pop semua.
        Stack harus tetap bisa digunakan kembali setelahnya.
        """
        s = Stack()
        for i in range(100):
            s.push(f'log-{i}')
        for _ in range(100):
            s.pop()

        # stack harus kosong dan siap dipakai lagi
        assert s.is_empty() is True
        s.push('log baru setelah reset')
        assert len(s) == 1
        assert s.pop() == 'log baru setelah reset'