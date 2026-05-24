# =============================================================================
#  test_graph.py  –  Unit Test: Graph Rantai Pasok
# =============================================================================
#
#  Menguji seluruh perilaku GraphRantaiPasok:
#    1. tambah_node   – daftarkan node baru, idempotent jika sudah ada
#    2. tambah_jalur  – tambah edge dua arah, bobot tersimpan benar
#    3. tetangga      – kembalikan semua EdgeNode tetangga
#    4. konektivitas  – node terhubung setelah tambah_jalur
#    5. edge case     – node terisolasi, self-loop tidak relevan
#
#  Cara jalankan (dari root project):
#      python -m pytest tests/test_graph.py -v
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.data_structures.graph import GraphRantaiPasok, EdgeNode


# ─────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def graph_kecil():
    """
    Graf kecil 4 node untuk pengujian dasar:
      PTN00 ──(10km, 1000/km)── DST00
      DST00 ──(20km, 2000/km)── PSR00
      PSR00 ──(5km,  500/km)──  GDG00
    """
    g = GraphRantaiPasok()
    g.tambah_node('PTN00', 'PETANI')
    g.tambah_node('DST00', 'DISTRIBUTOR')
    g.tambah_node('PSR00', 'PASAR')
    g.tambah_node('GDG00', 'GUDANG')
    g.tambah_jalur('PTN00', 'DST00', jarak=10, biaya_km=1000.0)
    g.tambah_jalur('DST00', 'PSR00', jarak=20, biaya_km=2000.0)
    g.tambah_jalur('PSR00', 'GDG00', jarak=5,  biaya_km=500.0)
    return g

@pytest.fixture
def graph_lengkap():
    """Graf dengan semua node dari generate_rantai_pasok untuk smoke test."""
    from src.data_generator import generate_rantai_pasok
    nodes, edges, _ = generate_rantai_pasok(seed=61)
    g = GraphRantaiPasok()
    for nid, tipe in nodes:
        g.tambah_node(nid, tipe)
    for u, v, j, b in edges:
        g.tambah_jalur(u, v, j, b)
    return g


# ─────────────────────────────────────────────
#  TEST TAMBAH NODE
# ─────────────────────────────────────────────

class TestTambahNode:

    def test_tambah_node_baru(self):
        """Node yang baru ditambahkan harus ada di adj dan tipe_node."""
        g = GraphRantaiPasok()
        g.tambah_node('PTN00', 'PETANI')
        assert 'PTN00' in g.adj
        assert 'PTN00' in g.tipe_node
        assert g.tipe_node['PTN00'] == 'PETANI'

    def test_tambah_node_inisialisasi_adj_none(self):
        """Adjacency list node baru harus None (linked list kosong)."""
        g = GraphRantaiPasok()
        g.tambah_node('PTN00', 'PETANI')
        assert g.adj['PTN00'] is None

    def test_tambah_node_idempotent(self):
        """Menambahkan node yang sudah ada tidak boleh mengubah state."""
        g = GraphRantaiPasok()
        g.tambah_node('PTN00', 'PETANI')
        g.tambah_node('PTN00', 'DISTRIBUTOR')   # tidak boleh mengubah tipe

        # tipe pertama yang terdaftar harus tetap
        assert g.tipe_node['PTN00'] == 'PETANI'
        # adj tidak rusak (tetap None karena belum ada jalur)
        assert g.adj['PTN00'] is None

    def test_tambah_banyak_node(self, graph_kecil):
        """Semua 4 node harus terdaftar."""
        for nid in ['PTN00', 'DST00', 'PSR00', 'GDG00']:
            assert nid in graph_kecil.adj


# ─────────────────────────────────────────────
#  TEST TAMBAH JALUR
# ─────────────────────────────────────────────

class TestTambahJalur:

    def test_jalur_tidak_berarah(self, graph_kecil):
        """
        Karena graf tidak berarah, tambah_jalur harus membuat edge di dua arah:
        PTN00 → DST00  DAN  DST00 → PTN00.
        """
        tetangga_ptn = [e.dest for e in graph_kecil.tetangga('PTN00')]
        tetangga_dst = [e.dest for e in graph_kecil.tetangga('DST00')]

        assert 'DST00' in tetangga_ptn, "PTN00 harus punya tetangga DST00"
        assert 'PTN00' in tetangga_dst, "DST00 harus punya tetangga PTN00 (arah balik)"

    def test_bobot_jalur_tersimpan_benar(self, graph_kecil):
        """Jarak dan biaya per km harus tersimpan sesuai yang diinputkan."""
        # cari edge PTN00 → DST00
        for edge in graph_kecil.tetangga('PTN00'):
            if edge.dest == 'DST00':
                assert edge.jarak_km     == 10
                assert edge.biaya_per_km == 1000.0
                break
        else:
            pytest.fail("Edge PTN00 → DST00 tidak ditemukan")

    def test_bobot_arah_balik_sama(self, graph_kecil):
        """Bobot edge pada arah balik harus sama (karena tidak berarah)."""
        bobot_maju  = None
        bobot_balik = None

        for edge in graph_kecil.tetangga('PTN00'):
            if edge.dest == 'DST00':
                bobot_maju = (edge.jarak_km, edge.biaya_per_km)

        for edge in graph_kecil.tetangga('DST00'):
            if edge.dest == 'PTN00':
                bobot_balik = (edge.jarak_km, edge.biaya_per_km)

        assert bobot_maju  is not None, "Edge maju tidak ditemukan"
        assert bobot_balik is not None, "Edge balik tidak ditemukan"
        assert bobot_maju  == bobot_balik, "Bobot maju dan balik harus sama"

    def test_tambah_beberapa_jalur_ke_satu_node(self):
        """Node DST00 harus punya beberapa tetangga setelah beberapa tambah_jalur."""
        g = GraphRantaiPasok()
        for nid in ['DST00', 'PTN00', 'PTN01', 'PSR00']:
            g.tambah_node(nid, 'TEST')
        g.tambah_jalur('DST00', 'PTN00', 15, 1000.0)
        g.tambah_jalur('DST00', 'PTN01', 25, 1500.0)
        g.tambah_jalur('DST00', 'PSR00', 10, 800.0)

        tetangga = [e.dest for e in g.tetangga('DST00')]
        assert len(tetangga) == 3
        assert 'PTN00' in tetangga
        assert 'PTN01' in tetangga
        assert 'PSR00' in tetangga


# ─────────────────────────────────────────────
#  TEST TETANGGA
# ─────────────────────────────────────────────

class TestTetangga:

    def test_tetangga_kembalikan_list_edge_node(self, graph_kecil):
        """Setiap elemen yang dikembalikan tetangga() harus bertipe EdgeNode."""
        hasil = graph_kecil.tetangga('DST00')
        assert isinstance(hasil, list)
        for edge in hasil:
            assert isinstance(edge, EdgeNode)

    def test_tetangga_node_terisolasi_benar(self):
        """Node tanpa jalur (terisolasi) harus punya tetangga kosong."""
        g = GraphRantaiPasok()
        g.tambah_node('TERISOLASI', 'PETANI')
        hasil = g.tetangga('TERISOLASI')
        assert hasil == []

    def test_tetangga_dst00_punya_dua_tetangga(self, graph_kecil):
        """
        DST00 terhubung ke PTN00 dan PSR00,
        maka tetangga DST00 harus punya tepat 2 elemen.
        """
        hasil = graph_kecil.tetangga('DST00')
        dest_list = [e.dest for e in hasil]
        assert len(dest_list) == 2
        assert 'PTN00' in dest_list
        assert 'PSR00' in dest_list


# ─────────────────────────────────────────────
#  TEST GRAPH LENGKAP (Smoke Test)
# ─────────────────────────────────────────────

class TestGraphLengkap:

    def test_jumlah_node_sesuai_spesifikasi(self, graph_lengkap):
        """Graf harus memiliki tepat 26 node (10+5+8+3)."""
        assert len(graph_lengkap.adj) == 26

    def test_semua_tipe_node_ada(self, graph_lengkap):
        """Semua tipe node (PETANI, DISTRIBUTOR, PASAR, GUDANG) harus ada."""
        tipe_ada = set(graph_lengkap.tipe_node.values())
        assert 'PETANI'      in tipe_ada
        assert 'DISTRIBUTOR' in tipe_ada
        assert 'PASAR'       in tipe_ada
        assert 'GUDANG'      in tipe_ada

    def test_semua_node_punya_setidaknya_satu_tetangga(self, graph_lengkap):
        """
        Karena generate menggunakan spanning tree, setiap node dijamin
        terhubung dan punya minimal 1 tetangga.
        """
        for nid in graph_lengkap.adj:
            tetangga = graph_lengkap.tetangga(nid)
            assert len(tetangga) >= 1, \
                f"Node {nid} tidak punya tetangga (terisolasi), ini tidak valid"