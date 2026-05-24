# =============================================================================
#  modul_1.py  –  Modul Graph Rantai Pasok
# =============================================================================
#
#  Modul ini bertanggung jawab atas semua operasi yang berkaitan dengan
#  JARINGAN DISTRIBUSI (graf) rantai pasok kota Yogyakarta.
#
#  Fungsi utama:
#    - inisialisasi_graph  : membangun graf dari data nodes & edges generator
#    - audit_konektivitas  : BFS dari asal, cek apakah semua node terjangkau
#    - audit_dfs           : DFS traversal untuk memetakan jalur distribusi
#    - tampilkan_info_node : cetak tipe dan jumlah tetangga suatu node
#    - tampilkan_semua_node: ringkasan seluruh node di jaringan
#
#  Hubungan dengan data_structures:
#    Modul ini MENGGUNAKAN GraphRantaiPasok dari data_structures/graph.py.
#    Tidak ada logika struktur data di sini — hanya logika bisnis/domain.
# =============================================================================

from src.data_structures.graph import GraphRantaiPasok


# ─────────────────────────────────────────────
#  INISIALISASI
# ─────────────────────────────────────────────

def inisialisasi_graph(nodes: list, edges: list) -> GraphRantaiPasok:
    """
    Bangun objek GraphRantaiPasok dari data hasil generate_rantai_pasok().

    Parameter:
        nodes : list of (node_id, tipe)  - 26 node rantai pasok
        edges : list of (u, v, jarak, biaya_km) - jalur distribusi

    Kembalikan:
        graph : GraphRantaiPasok yang sudah terisi penuh
    """
    graph = GraphRantaiPasok()

    # daftarkan semua node ke dalam graf
    for node_id, tipe in nodes:
        graph.tambah_node(node_id, tipe)

    # tambahkan semua jalur distribusi (otomatis dua arah)
    for u, v, jarak, biaya_km in edges:
        graph.tambah_jalur(u, v, jarak, biaya_km)

    return graph


# ─────────────────────────────────────────────
#  BFS  –  Audit Konektivitas Jaringan
# ─────────────────────────────────────────────

def audit_konektivitas(graph: GraphRantaiPasok, asal: str) -> dict:
    """
    Lakukan BFS (Breadth-First Search) dari node asal untuk mengecek
    apakah seluruh jaringan distribusi terhubung (connected).

    BFS dipilih karena:
      → Menemukan semua node yang bisa dijangkau secara level per level.
      → Cocok untuk audit "apakah ada node terisolasi?" karena menjangkau
         node terdekat dulu sebelum yang jauh.

    Big-O: O(V + E)

    Kembalikan dict berisi:
      'dikunjungi'    : set node yang berhasil dijangkau dari asal
      'tidak_terjangkau' : set node yang TIDAK bisa dijangkau (terisolasi)
      'total_node'    : jumlah total node
      'terhubung'     : True jika semua node terjangkau
    """
    # ── BFS manual menggunakan list sebagai queue (tanpa collections.deque) ──
    dikunjungi = set()
    antrian    = [asal]         # queue BFS: mulai dari node asal
    dikunjungi.add(asal)

    while antrian:
        # ambil node paling depan (FIFO)
        node_saat_ini = antrian.pop(0)

        # kunjungi semua tetangga yang belum dikunjungi
        for edge in graph.tetangga(node_saat_ini):
            if edge.dest not in dikunjungi:
                dikunjungi.add(edge.dest)
                antrian.append(edge.dest)

    semua_node        = set(graph.adj.keys())
    tidak_terjangkau  = semua_node - dikunjungi

    return {
        'dikunjungi'        : dikunjungi,
        'tidak_terjangkau'  : tidak_terjangkau,
        'total_node'        : len(semua_node),
        'terhubung'         : len(tidak_terjangkau) == 0
    }


# ─────────────────────────────────────────────
#  DFS  –  Pemetaan Jalur Distribusi
# ─────────────────────────────────────────────

def audit_dfs(graph: GraphRantaiPasok, asal: str) -> list:
    """
    Lakukan DFS (Depth-First Search) dari node asal untuk memetakan
    urutan kunjungan seluruh jaringan distribusi.

    DFS dipilih karena:
      → Menelusuri satu jalur sampai ujung sebelum berpindah ke jalur lain.
      → Berguna untuk menemukan jalur distribusi potensial yang panjang.
      → Cocok untuk mendeteksi siklus dalam jaringan.

    Big-O: O(V + E)

    Kembalikan:
        urutan_kunjungan : list node dalam urutan DFS traversal
    """
    dikunjungi       = set()
    urutan_kunjungan = []

    def _dfs_rekursif(node):
        dikunjungi.add(node)
        urutan_kunjungan.append(node)

        # kunjungi semua tetangga yang belum dikunjungi (rekursif)
        for edge in graph.tetangga(node):
            if edge.dest not in dikunjungi:
                _dfs_rekursif(edge.dest)

    _dfs_rekursif(asal)
    return urutan_kunjungan


# ─────────────────────────────────────────────
#  TAMPILAN INFO
# ─────────────────────────────────────────────

def tampilkan_info_node(graph: GraphRantaiPasok, node_id: str):
    """
    Cetak informasi detail satu node: tipe, jumlah tetangga,
    dan daftar jalur distribusi yang terhubung beserta bobotnya.
    """
    if node_id not in graph.adj:
        print(f"  [!] Node '{node_id}' tidak ditemukan dalam jaringan.")
        return

    tipe      = graph.tipe_node.get(node_id, 'TIDAK DIKETAHUI')
    tetangga  = graph.tetangga(node_id)

    print(f"\n  Node   : {node_id}  ({tipe})")
    print(f"  Degree : {len(tetangga)} koneksi")

    if tetangga:
        print(f"  {'Tujuan':<10} {'Jarak':>8} km  {'Biaya/km':>12}  {'Total Biaya':>14}")
        print(f"  {'-'*52}")
        for edge in tetangga:
            total = edge.jarak_km * edge.biaya_per_km
            print(f"  {edge.dest:<10} {edge.jarak_km:>8}     "
                  f"Rp {edge.biaya_per_km:>9,.0f}  Rp {total:>12,.0f}")
    else:
        print("  (tidak ada jalur terhubung - node terisolasi)")


def tampilkan_semua_node(graph: GraphRantaiPasok):
    """
    Cetak ringkasan seluruh node dalam jaringan, dikelompokkan per tipe.
    """
    # kelompokkan node berdasarkan tipe
    kelompok: dict = {}
    for node_id, tipe in graph.tipe_node.items():
        kelompok.setdefault(tipe, []).append(node_id)

    total_edge = sum(len(graph.tetangga(n)) for n in graph.adj) // 2

    print(f"\n  {'Tipe':<15} {'Jumlah':>7}  Node")
    print(f"  {'-'*55}")
    for tipe, node_list in sorted(kelompok.items()):
        node_str = ', '.join(sorted(node_list))
        print(f"  {tipe:<15} {len(node_list):>7}  {node_str}")

    print(f"  {'-'*55}")
    print(f"  {'Total Node':<15} {len(graph.adj):>7}")
    print(f"  {'Total Edge':<15} {total_edge:>7}")