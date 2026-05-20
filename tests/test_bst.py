# =============================================================================
#  test_bst.py  –  Unit Test: BST Katalog Produk
# =============================================================================
#
#  Menguji seluruh operasi BSTKatalog:
#    1. insert                  – tambah produk baru & upsert (kode duplikat)
#    2. search                  – cari produk ada & tidak ada
#    3. update_stok             – tambah/kurang stok, batas minimum 0
#    4. filter_kadaluarsa       – filter berdasarkan batas hari
#    5. inorder                 – hasil harus terurut menaik berdasarkan kode
#    6. edge case               – BST kosong, satu node
#
#  Cara jalankan (dari root project):
#      python -m pytest tests/test_bst.py -v
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.data_models import Produk
from src.data_structures.bst import BSTKatalog, BSTNodeProd


# ─────────────────────────────────────────────
#  FIXTURES  –  data produk siap pakai
# ─────────────────────────────────────────────

def buat_produk(kode, nama, kadaluarsa=10, stok=100, harga=5000.0):
    """Helper: buat objek Produk dengan nilai default yang bisa di-override."""
    return Produk(
        kode                 = kode,
        nama                 = nama,
        kategori             = 'SAYUR',
        harga_satuan         = harga,
        stok                 = stok,
        masa_kadaluarsa_hari = kadaluarsa
    )

@pytest.fixture
def bst_terisi():
    """
    BST dengan 5 produk yang sudah di-insert.
    Kode sengaja tidak berurutan untuk menguji penempatan node yang benar.
    """
    bst = BSTKatalog()
    bst.insert(buat_produk('PRD-003', 'Tomat',    kadaluarsa=5,  stok=80))
    bst.insert(buat_produk('PRD-001', 'Beras',    kadaluarsa=30, stok=200))
    bst.insert(buat_produk('PRD-005', 'Kangkung', kadaluarsa=2,  stok=50))
    bst.insert(buat_produk('PRD-002', 'Cabai',    kadaluarsa=7,  stok=120))
    bst.insert(buat_produk('PRD-004', 'Ayam',     kadaluarsa=3,  stok=60))
    return bst


# ─────────────────────────────────────────────
#  TEST INSERT
# ─────────────────────────────────────────────

class TestInsert:

    def test_insert_satu_produk(self):
        """BST awalnya kosong, setelah insert satu produk root tidak boleh None."""
        bst = BSTKatalog()
        assert bst.root is None, "Root harus None sebelum insert"

        bst.insert(buat_produk('PRD-001', 'Beras'))
        assert bst.root is not None,        "Root tidak boleh None setelah insert"
        assert bst.root.produk.kode == 'PRD-001'

    def test_insert_banyak_produk(self, bst_terisi):
        """Semua produk yang di-insert harus bisa ditemukan kembali."""
        for kode in ['PRD-001', 'PRD-002', 'PRD-003', 'PRD-004', 'PRD-005']:
            assert bst_terisi.search(kode) is not None, \
                f"Produk {kode} seharusnya ada setelah insert"

    def test_insert_upsert_kode_duplikat(self):
        """Insert dengan kode yang sama harus memperbarui data, bukan duplikat."""
        bst = BSTKatalog()
        bst.insert(buat_produk('PRD-001', 'Beras', stok=100))
        bst.insert(buat_produk('PRD-001', 'Beras Premium', stok=999))  # upsert

        hasil = bst.search('PRD-001')
        assert hasil is not None
        assert hasil.nama == 'Beras Premium', "Nama harus diperbarui setelah upsert"
        assert hasil.stok == 999,             "Stok harus diperbarui setelah upsert"

    def test_insert_urutan_kiri_kanan(self):
        """
        Node dengan kode lebih kecil dari root harus di kiri,
        node dengan kode lebih besar harus di kanan.
        """
        bst = BSTKatalog()
        bst.insert(buat_produk('PRD-003', 'Tengah'))   # root
        bst.insert(buat_produk('PRD-001', 'Kiri'))     # kiri root
        bst.insert(buat_produk('PRD-005', 'Kanan'))    # kanan root

        assert bst.root.produk.kode        == 'PRD-003'
        assert bst.root.left.produk.kode   == 'PRD-001'
        assert bst.root.right.produk.kode  == 'PRD-005'


# ─────────────────────────────────────────────
#  TEST SEARCH
# ─────────────────────────────────────────────

class TestSearch:

    def test_search_produk_ada(self, bst_terisi):
        """Search produk yang ada harus mengembalikan objek Produk yang benar."""
        hasil = bst_terisi.search('PRD-002')
        assert hasil is not None
        assert hasil.kode == 'PRD-002'
        assert hasil.nama == 'Cabai'

    def test_search_produk_tidak_ada(self, bst_terisi):
        """Search produk yang tidak ada harus mengembalikan None."""
        assert bst_terisi.search('PRD-999') is None
        assert bst_terisi.search('PRD-000') is None

    def test_search_bst_kosong(self):
        """Search pada BST kosong harus mengembalikan None tanpa error."""
        bst = BSTKatalog()
        assert bst.search('PRD-001') is None

    def test_search_root(self, bst_terisi):
        """Search node root (PRD-003, diinsert pertama) harus langsung ketemu."""
        hasil = bst_terisi.search('PRD-003')
        assert hasil is not None
        assert hasil.kode == 'PRD-003'


# ─────────────────────────────────────────────
#  TEST UPDATE STOK
# ─────────────────────────────────────────────

class TestUpdateStok:

    def test_update_stok_tambah(self, bst_terisi):
        """Stok harus bertambah sesuai delta positif."""
        stok_awal = bst_terisi.search('PRD-001').stok   # 200
        bst_terisi.update_stok('PRD-001', +50)
        assert bst_terisi.search('PRD-001').stok == stok_awal + 50

    def test_update_stok_kurang(self, bst_terisi):
        """Stok harus berkurang sesuai delta negatif."""
        stok_awal = bst_terisi.search('PRD-001').stok   # 200
        bst_terisi.update_stok('PRD-001', -30)
        assert bst_terisi.search('PRD-001').stok == stok_awal - 30

    def test_update_stok_tidak_negatif(self, bst_terisi):
        """Stok tidak boleh turun di bawah 0 meski delta sangat besar."""
        bst_terisi.update_stok('PRD-005', -9999)   # stok awal 50
        assert bst_terisi.search('PRD-005').stok == 0

    def test_update_stok_produk_tidak_ada(self, bst_terisi):
        """Update stok produk yang tidak ada harus mengembalikan False."""
        hasil = bst_terisi.update_stok('PRD-999', +10)
        assert hasil is False

    def test_update_stok_produk_ada_return_true(self, bst_terisi):
        """Update stok produk yang ada harus mengembalikan True."""
        hasil = bst_terisi.update_stok('PRD-001', +10)
        assert hasil is True


# ─────────────────────────────────────────────
#  TEST FILTER KADALUARSA
# ─────────────────────────────────────────────

class TestFilterKadaluarsa:
    """
    Data fixture (bst_terisi):
      PRD-001 Beras    → 30 hari
      PRD-002 Cabai    →  7 hari
      PRD-003 Tomat    →  5 hari
      PRD-004 Ayam     →  3 hari
      PRD-005 Kangkung →  2 hari
    """

    def test_filter_mendesak(self, bst_terisi):
        """Filter <= 3 hari: hanya Ayam (3) dan Kangkung (2) yang lolos."""
        hasil = bst_terisi.filter_kadaluarsa(3)
        kode_hasil = [p.kode for p in hasil]
        assert 'PRD-004' in kode_hasil   # Ayam 3 hari
        assert 'PRD-005' in kode_hasil   # Kangkung 2 hari
        assert len(hasil) == 2

    def test_filter_seminggu(self, bst_terisi):
        """Filter <= 7 hari: Cabai, Tomat, Ayam, Kangkung (4 produk)."""
        hasil = bst_terisi.filter_kadaluarsa(7)
        assert len(hasil) == 4
        assert all(p.masa_kadaluarsa_hari <= 7 for p in hasil)

    def test_filter_semua(self, bst_terisi):
        """Filter <= 30 hari: semua 5 produk harus masuk."""
        hasil = bst_terisi.filter_kadaluarsa(30)
        assert len(hasil) == 5

    def test_filter_tidak_ada_yang_lolos(self, bst_terisi):
        """Filter <= 1 hari: tidak ada produk yang lolos, kembalikan list kosong."""
        hasil = bst_terisi.filter_kadaluarsa(1)
        assert hasil == []

    def test_filter_hasil_terurut_kode(self, bst_terisi):
        """Hasil filter harus terurut menaik berdasarkan kode (inorder)."""
        hasil = bst_terisi.filter_kadaluarsa(10)
        kode_list = [p.kode for p in hasil]
        assert kode_list == sorted(kode_list), "Hasil filter harus terurut berdasarkan kode"


# ─────────────────────────────────────────────
#  TEST INORDER
# ─────────────────────────────────────────────

class TestInorder:

    def test_inorder_terurut(self, bst_terisi):
        """Hasil inorder harus terurut menaik berdasarkan kode produk."""
        hasil = bst_terisi.inorder()
        kode_list = [p.kode for p in hasil]
        assert kode_list == sorted(kode_list)

    def test_inorder_jumlah_node(self, bst_terisi):
        """Jumlah elemen inorder harus sama dengan jumlah produk yang di-insert."""
        hasil = bst_terisi.inorder()
        assert len(hasil) == 5

    def test_inorder_bst_kosong(self):
        """Inorder pada BST kosong harus mengembalikan list kosong."""
        bst = BSTKatalog()
        assert bst.inorder() == []

    def test_inorder_satu_node(self):
        """Inorder dengan satu node harus mengembalikan list dengan satu elemen."""
        bst = BSTKatalog()
        bst.insert(buat_produk('PRD-001', 'Beras'))
        hasil = bst.inorder()
        assert len(hasil) == 1
        assert hasil[0].kode == 'PRD-001'

    def test_inorder_insert_acak_tetap_terurut(self):
        """Meski di-insert secara acak, inorder harus selalu terurut."""
        bst = BSTKatalog()
        kode_acak = ['PRD-007', 'PRD-002', 'PRD-009', 'PRD-001', 'PRD-005']
        for kode in kode_acak:
            bst.insert(buat_produk(kode, f'Produk {kode}'))
        hasil = bst.inorder()
        kode_list = [p.kode for p in hasil]
        assert kode_list == sorted(kode_acak)