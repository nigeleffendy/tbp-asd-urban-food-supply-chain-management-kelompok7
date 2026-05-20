# =============================================================================
#  test_priority_queue.py  –  Unit Test: Priority Queue Pengiriman
# =============================================================================
#
#  Menguji seluruh perilaku PriorityQueueKirim:
#    1. enqueue  – item terurut menaik berdasarkan prioritas
#    2. dequeue  – selalu ambil item dengan prioritas terkecil (paling mendesak)
#    3. urutan   – MENDESAK (1) → REGULER (2) → NORMAL (3)
#    4. prioritas sama  – urutan relatif (FIFO antar prioritas setara)
#    5. edge case       – antrian kosong, satu item
#
#  Cara jalankan (dari root project):
#      python -m pytest tests/test_priority_queue.py -v
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import time
from src.data_models import Pengiriman
from src.data_structures.priority_queue import PriorityQueueKirim


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────

_id_counter = 0

def buat_pengiriman(prioritas: int, kode: str = 'PRD-001', jumlah: int = 10):
    """
    Helper: buat objek Pengiriman dengan prioritas tertentu.
    Prioritas: 1=MENDESAK, 2=REGULER, 3=NORMAL
    """
    global _id_counter
    _id_counter += 1
    return Pengiriman(
        pengiriman_id = _id_counter,
        dari_node     = 'PTN00',
        ke_node       = 'PSR00',
        kode_produk   = kode,
        jumlah        = jumlah,
        prioritas     = prioritas,
        waktu_kirim   = time.time()
    )


# ─────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_counter():
    """Reset global ID counter sebelum setiap test."""
    global _id_counter
    _id_counter = 0

@pytest.fixture
def pq_terisi():
    """
    Priority Queue dengan 3 pengiriman: satu tiap prioritas.
    Dimasukkan dengan urutan NORMAL → MENDESAK → REGULER
    untuk memastikan pengurutan tidak tergantung urutan insert.
    """
    pq = PriorityQueueKirim()
    pq.enqueue(buat_pengiriman(prioritas=3))   # NORMAL
    pq.enqueue(buat_pengiriman(prioritas=1))   # MENDESAK
    pq.enqueue(buat_pengiriman(prioritas=2))   # REGULER
    return pq


# ─────────────────────────────────────────────
#  TEST KONDISI AWAL
# ─────────────────────────────────────────────

class TestKondisiAwal:

    def test_awal_kosong(self):
        """Queue baru harus kosong."""
        pq = PriorityQueueKirim()
        assert len(pq) == 0
        assert pq.head is None

    def test_dequeue_saat_kosong(self):
        """Dequeue pada queue kosong harus mengembalikan None."""
        pq = PriorityQueueKirim()
        assert pq.dequeue() is None


# ─────────────────────────────────────────────
#  TEST ENQUEUE & ORDERING
# ─────────────────────────────────────────────

class TestEnqueue:

    def test_enqueue_satu_item(self):
        """Enqueue satu item: head harus menunjuk item tersebut."""
        pq = PriorityQueueKirim()
        kirim = buat_pengiriman(prioritas=2)
        pq.enqueue(kirim)
        assert len(pq)              == 1
        assert pq.head.data         == kirim
        assert pq.head.data.prioritas == 2

    def test_enqueue_mendesak_jadi_head(self):
        """
        Insert REGULER dulu, lalu MENDESAK.
        MENDESAK (prioritas=1) harus menjadi head karena lebih kecil.
        """
        pq = PriorityQueueKirim()
        pq.enqueue(buat_pengiriman(prioritas=2))   # REGULER dulu
        pq.enqueue(buat_pengiriman(prioritas=1))   # MENDESAK belakangan
        assert pq.head.data.prioritas == 1, \
            "Head harus selalu item dengan prioritas terkecil (paling mendesak)"

    def test_enqueue_urutan_linked_list(self, pq_terisi):
        """
        Setelah insert NORMAL(3), MENDESAK(1), REGULER(2),
        linked list harus terurut: 1 → 2 → 3.
        """
        cur = pq_terisi.head
        urutan = []
        while cur is not None:
            urutan.append(cur.data.prioritas)
            cur = cur.next
        assert urutan == [1, 2, 3], \
            f"Linked list harus terurut [1, 2, 3], dapat {urutan}"

    def test_enqueue_tambah_ukuran(self, pq_terisi):
        """Tiap enqueue harus menambah _size."""
        assert len(pq_terisi) == 3
        pq_terisi.enqueue(buat_pengiriman(prioritas=1))
        assert len(pq_terisi) == 4


# ─────────────────────────────────────────────
#  TEST DEQUEUE
# ─────────────────────────────────────────────

class TestDequeue:

    def test_dequeue_urutan_prioritas(self, pq_terisi):
        """
        Dequeue harus selalu mengeluarkan item dengan prioritas terkecil dulu.
        Urutan yang benar: MENDESAK(1) → REGULER(2) → NORMAL(3).
        """
        assert pq_terisi.dequeue().prioritas == 1   # MENDESAK keluar dulu
        assert pq_terisi.dequeue().prioritas == 2   # REGULER
        assert pq_terisi.dequeue().prioritas == 3   # NORMAL

    def test_dequeue_kurangi_ukuran(self, pq_terisi):
        """Tiap dequeue harus mengurangi _size satu."""
        assert len(pq_terisi) == 3
        pq_terisi.dequeue()
        assert len(pq_terisi) == 2
        pq_terisi.dequeue()
        assert len(pq_terisi) == 1
        pq_terisi.dequeue()
        assert len(pq_terisi) == 0

    def test_dequeue_sampai_kosong_lalu_none(self, pq_terisi):
        """Setelah semua item diambil, dequeue berikutnya harus None."""
        pq_terisi.dequeue()
        pq_terisi.dequeue()
        pq_terisi.dequeue()
        assert pq_terisi.dequeue() is None
        assert len(pq_terisi)      == 0

    def test_dequeue_kembalikan_objek_pengiriman(self, pq_terisi):
        """Objek yang dikembalikan harus berupa Pengiriman yang valid."""
        hasil = pq_terisi.dequeue()
        assert isinstance(hasil, Pengiriman)
        assert hasattr(hasil, 'pengiriman_id')
        assert hasattr(hasil, 'prioritas')


# ─────────────────────────────────────────────
#  TEST PRIORITAS SAMA
# ─────────────────────────────────────────────

class TestPrioritasSama:

    def test_prioritas_sama_masuk_urutan_insert(self):
        """
        Jika dua item memiliki prioritas yang sama,
        item yang diinsert lebih dulu harus keluar lebih dulu (FIFO dalam tier).
        """
        pq = PriorityQueueKirim()
        k1 = buat_pengiriman(prioritas=1)
        k2 = buat_pengiriman(prioritas=1)
        k3 = buat_pengiriman(prioritas=1)
        pq.enqueue(k1)
        pq.enqueue(k2)
        pq.enqueue(k3)

        assert pq.dequeue().pengiriman_id == k1.pengiriman_id
        assert pq.dequeue().pengiriman_id == k2.pengiriman_id
        assert pq.dequeue().pengiriman_id == k3.pengiriman_id

    def test_campuran_prioritas_sama_dan_berbeda(self):
        """
        Skenario realistis: beberapa item MENDESAK dan beberapa NORMAL.
        MENDESAK harus habis dulu sebelum NORMAL diproses.
        """
        pq = PriorityQueueKirim()
        pq.enqueue(buat_pengiriman(prioritas=3))   # NORMAL
        pq.enqueue(buat_pengiriman(prioritas=1))   # MENDESAK
        pq.enqueue(buat_pengiriman(prioritas=1))   # MENDESAK
        pq.enqueue(buat_pengiriman(prioritas=3))   # NORMAL

        assert pq.dequeue().prioritas == 1   # MENDESAK ke-1
        assert pq.dequeue().prioritas == 1   # MENDESAK ke-2
        assert pq.dequeue().prioritas == 3   # NORMAL ke-1
        assert pq.dequeue().prioritas == 3   # NORMAL ke-2


# ─────────────────────────────────────────────
#  TEST EDGE CASE
# ─────────────────────────────────────────────

class TestEdgeCase:

    def test_satu_item_enqueue_dequeue(self):
        """Queue dengan satu item harus bisa enqueue dan dequeue dengan benar."""
        pq    = PriorityQueueKirim()
        kirim = buat_pengiriman(prioritas=2)
        pq.enqueue(kirim)
        hasil = pq.dequeue()
        assert hasil         == kirim
        assert len(pq)       == 0
        assert pq.head       is None

    def test_banyak_insert_lalu_dequeue_semua(self):
        """Stress test: insert 10 item acak, pastikan dequeue selalu terurut prioritas."""
        import random
        random.seed(42)
        pq = PriorityQueueKirim()

        prioritas_list = [random.randint(1, 3) for _ in range(10)]
        for p in prioritas_list:
            pq.enqueue(buat_pengiriman(prioritas=p))

        hasil_prioritas = []
        while len(pq) > 0:
            hasil_prioritas.append(pq.dequeue().prioritas)

        # hasil dequeue harus terurut menaik (1 dulu, lalu 2, lalu 3)
        assert hasil_prioritas == sorted(hasil_prioritas), \
            f"Urutan prioritas tidak konsisten: {hasil_prioritas}"