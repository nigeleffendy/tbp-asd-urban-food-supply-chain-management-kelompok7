# =============================================================================
#  test_dijkstra.py  –  Unit Test: Algoritma Dijkstra Biaya Minimum
# =============================================================================
#  Menguji seluruh perilaku dijkstra_biaya & rekonstruksi_jalur:
#    1. dist asal = 0, dist node tak terjangkau = INF
#    2. bobot    = jarak_km × biaya_per_km (bukan jarak saja)
#    3. jalur terpendek pada graf sederhana (verifiable manual)
#    4. rekonstruksi jalur benar dari parent[]
#    5. graf tidak terhubung → dist INF, jalur kosong []
#    6. smoke test pada data generator dosen (seed=61)
#
#  Cara jalankan (dari root project):
#      python -m pytest tests/test_dijkstra.py -v
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.data_structures.graph    import GraphRantaiPasok
from src.data_structures.dijkstra import dijkstra_biaya, rekonstruksi_jalur


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────

def buat_graph(node_list, edge_list):
    """
    Helper: buat GraphRantaiPasok dari list node dan edge.
    edge_list format: [(u, v, jarak_km, biaya_per_km), ...]
    """
    g = GraphRantaiPasok()
    for nid in node_list:
        g.tambah_node(nid, 'TEST')
    for u, v, j, b in edge_list:
        g.tambah_jalur(u, v, j, b)
    return g


# ─────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def graph_lurus():
    """
    Graf lurus: A ─── B ─── C ─── D
    Bobot:
      A→B : 10km x 1000/km = 10_000
      B→C : 5km  x 2000/km = 10_000
      C→D : 20km x 500/km  = 10_000
    Jalur terpendek A→D = 30_000 melalui A→B→C→D.
    """
    return buat_graph(
        ['A', 'B', 'C', 'D'],
        [
            ('A', 'B', 10, 1000.0),
            ('B', 'C', 5,  2000.0),
            ('C', 'D', 20, 500.0),
        ]
    )

@pytest.fixture
def graph_alternatif():
    """
    Graf dengan dua jalur dari A ke C:
      Jalur 1: A → B → C  (bobot: 5000 + 5000 = 10_000)
      Jalur 2: A → C      (bobot: 15_000)
    Dijkstra harus memilih Jalur 1 (lebih murah).
    """
    return buat_graph(
        ['A', 'B', 'C'],
        [
            ('A', 'B', 5,  1000.0),   # 5_000
            ('B', 'C', 5,  1000.0),   # 5_000  → total A→B→C = 10_000
            ('A', 'C', 15, 1000.0),   # 15_000 → total A→C langsung = 15_000
        ]
    )

@pytest.fixture
def graph_tidak_terhubung():
    """
    Graf dengan dua komponen terpisah:
      Komponen 1: A ─── B
      Komponen 2: C ─── D  (tidak terhubung ke A/B)
    """
    return buat_graph(
        ['A', 'B', 'C', 'D'],
        [
            ('A', 'B', 10, 1000.0),
            ('C', 'D', 10, 1000.0),
        ]
    )


# ─────────────────────────────────────────────
#  TEST INISIALISASI DIJKSTRA
# ─────────────────────────────────────────────

class TestInisialisasi:

    def test_dist_asal_nol(self, graph_lurus):
        """Jarak dari asal ke dirinya sendiri harus 0."""
        dist, _ = dijkstra_biaya(graph_lurus, 'A')
        assert dist['A'] == 0.0

    def test_dist_tidak_terjangkau_inf(self, graph_tidak_terhubung):
        """Node yang tidak terhubung ke asal harus punya dist = INF."""
        dist, _ = dijkstra_biaya(graph_tidak_terhubung, 'A')
        assert dist['C'] == float('inf')
        assert dist['D'] == float('inf')

    def test_semua_node_ada_di_hasil(self, graph_lurus):
        """Dict dist harus berisi semua node dalam graf."""
        dist, parent = dijkstra_biaya(graph_lurus, 'A')
        for node in ['A', 'B', 'C', 'D']:
            assert node in dist
            assert node in parent


# ─────────────────────────────────────────────
#  TEST PERHITUNGAN BOBOT
# ─────────────────────────────────────────────

class TestBobot:

    def test_bobot_adalah_jarak_kali_biaya(self, graph_lurus):
        """
        Bobot harus dihitung sebagai jarak_km x biaya_per_km,
        bukan hanya jarak_km.
        A→B: 10km x 1000 = 10_000
        """
        dist, _ = dijkstra_biaya(graph_lurus, 'A')
        assert dist['B'] == 10 * 1000.0   # 10_000

    def test_bobot_jalur_dua_hop(self, graph_lurus):
        """
        A→C melalui B:
        dist[B] = 10_000
        dist[C] = dist[B] + (5 x 2000) = 10_000 + 10_000 = 20_000
        """
        dist, _ = dijkstra_biaya(graph_lurus, 'A')
        assert dist['C'] == 20_000.0

    def test_bobot_jalur_tiga_hop(self, graph_lurus):
        """
        A→D melalui B→C:
        dist[D] = 20_000 + (20 x 500) = 20_000 + 10_000 = 30_000
        """
        dist, _ = dijkstra_biaya(graph_lurus, 'A')
        assert dist['D'] == 30_000.0


# ─────────────────────────────────────────────
#  TEST JALUR TERPENDEK (PILIHAN OPTIMAL)
# ─────────────────────────────────────────────

class TestJalurTerpendek:

    def test_pilih_jalur_lebih_murah(self, graph_alternatif):
        """
        Dijkstra harus memilih A→B→C (10_000) bukan A→C langsung (15_000).
        """
        dist, _ = dijkstra_biaya(graph_alternatif, 'A')
        assert dist['C'] == 10_000.0, \
            f"Seharusnya 10_000 (lewat B), dapat {dist['C']}"

    def test_parent_menunjuk_jalur_optimal(self, graph_alternatif):
        """
        Karena jalur optimal A→C adalah melalui B,
        parent[C] harus B, bukan A.
        """
        _, parent = dijkstra_biaya(graph_alternatif, 'A')
        assert parent['C'] == 'B', \
            f"Parent C seharusnya B (jalur murah), dapat {parent['C']}"

    def test_dist_simetris_tidak_berarah(self, graph_lurus):
        """
        Karena graf tidak berarah, dist dari D ke A harus sama
        dengan dist dari A ke D.
        """
        dist_dari_a, _ = dijkstra_biaya(graph_lurus, 'A')
        dist_dari_d, _ = dijkstra_biaya(graph_lurus, 'D')
        assert dist_dari_a['D'] == dist_dari_d['A']


# ─────────────────────────────────────────────
#  TEST REKONSTRUKSI JALUR
# ─────────────────────────────────────────────

class TestRekonstruksiJalur:

    def test_rekonstruksi_jalur_lurus(self, graph_lurus):
        """
        Pada graf lurus A→B→C→D, rekonstruksi dari A ke D
        harus menghasilkan ['A', 'B', 'C', 'D'].
        """
        _, parent = dijkstra_biaya(graph_lurus, 'A')
        jalur = rekonstruksi_jalur(parent, 'A', 'D')
        assert jalur == ['A', 'B', 'C', 'D']

    def test_rekonstruksi_jalur_asal_ke_diri_sendiri(self, graph_lurus):
        """Jalur dari A ke A harus ['A']."""
        _, parent = dijkstra_biaya(graph_lurus, 'A')
        jalur = rekonstruksi_jalur(parent, 'A', 'A')
        assert jalur == ['A']

    def test_rekonstruksi_jalur_dua_hop(self, graph_alternatif):
        """
        Pada graph_alternatif, jalur A ke C seharusnya ['A', 'B', 'C']
        bukan ['A', 'C'] (karena lewat B lebih murah).
        """
        _, parent = dijkstra_biaya(graph_alternatif, 'A')
        jalur = rekonstruksi_jalur(parent, 'A', 'C')
        assert jalur == ['A', 'B', 'C']

    def test_rekonstruksi_tidak_terhubung(self, graph_tidak_terhubung):
        """
        Jika tidak ada jalur dari A ke C,
        rekonstruksi harus mengembalikan list kosong [].
        """
        _, parent = dijkstra_biaya(graph_tidak_terhubung, 'A')
        jalur = rekonstruksi_jalur(parent, 'A', 'C')
        assert jalur == []

    def test_rekonstruksi_awal_adalah_asal(self, graph_lurus):
        """Elemen pertama jalur hasil rekonstruksi harus selalu asal."""
        _, parent = dijkstra_biaya(graph_lurus, 'A')
        for tujuan in ['B', 'C', 'D']:
            jalur = rekonstruksi_jalur(parent, 'A', tujuan)
            assert jalur[0] == 'A', f"Jalur ke {tujuan} harus dimulai dari A"

    def test_rekonstruksi_akhir_adalah_tujuan(self, graph_lurus):
        """Elemen terakhir jalur hasil rekonstruksi harus selalu tujuan."""
        _, parent = dijkstra_biaya(graph_lurus, 'A')
        for tujuan in ['B', 'C', 'D']:
            jalur = rekonstruksi_jalur(parent, 'A', tujuan)
            assert jalur[-1] == tujuan, f"Jalur ke {tujuan} harus diakhiri {tujuan}"


# ─────────────────────────────────────────────
#  SMOKE TEST – Data Generator Dosen (seed=61)
# ─────────────────────────────────────────────

class TestSmokeGeneratorDosen:

    @pytest.fixture
    def graph_dosen(self):
        from src.data_generator import generate_rantai_pasok
        nodes, edges, _ = generate_rantai_pasok(seed=61)
        g = GraphRantaiPasok()
        for nid, tipe in nodes:
            g.tambah_node(nid, tipe)
        for u, v, j, b in edges:
            g.tambah_jalur(u, v, j, b)
        return g

    def test_dijkstra_jalan_tanpa_error(self, graph_dosen):
        """Dijkstra pada graf dosen harus berjalan tanpa exception."""
        dist, parent = dijkstra_biaya(graph_dosen, 'PTN00')
        assert dist   is not None
        assert parent is not None

    def test_dist_asal_nol_pada_graf_dosen(self, graph_dosen):
        """dist[PTN00] = 0 pada graf dosen."""
        dist, _ = dijkstra_biaya(graph_dosen, 'PTN00')
        assert dist['PTN00'] == 0.0

    def test_sebagian_besar_node_terjangkau(self, graph_dosen):
        """
        Karena generator menggunakan spanning tree, hampir semua node
        harus terjangkau dari PTN00 (dist < INF).
        """
        dist, _ = dijkstra_biaya(graph_dosen, 'PTN00')
        terjangkau = [v for v, d in dist.items() if d < float('inf')]
        # minimal harus lebih dari separuh node yang terjangkau
        assert len(terjangkau) > len(graph_dosen.adj) // 2