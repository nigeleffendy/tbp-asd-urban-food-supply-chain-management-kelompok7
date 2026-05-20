# =============================================================================
#  dijkstra.py  –  Algoritma Dijkstra (Jalur Distribusi Termurah)
# =============================================================================
#  Mencari jalur distribusi dengan total biaya minimum dari satu sumber
#  ke semua node lain dalam graf rantai pasok.
#
#  Bobot edge: jarak_km × biaya_per_km  (total biaya perjalanan, bukan jarak)
#
#  Implementasi:
#    → Dijkstra klasik tanpa priority queue bawaan (sesuai ketentuan tugas).
#    → Setiap iterasi: cari node unvisited dengan dist terkecil secara linear (O(V)).
#    → Relaksasi semua tetangga node tersebut.
#
#  Big-O: O(V² + E)
#    - V² dari pemilihan node minimum di setiap dari V iterasi
#    - E  dari total relaksasi semua edge
#
#  Fungsi rekonstruksi_jalur:
#    → Menggunakan array parent untuk menelusuri jalur balik dari tujuan ke asal.
#    → Hasil di-reverse agar urutan benar: asal → ... → tujuan.
#    → Big-O: O(V) – panjang jalur maksimal = jumlah node.
# =============================================================================

from src.data_structures.graph import GraphRantaiPasok


def dijkstra_biaya(graph: GraphRantaiPasok, asal: str):
    """
    Hitung jalur berbiaya minimum dari node asal ke semua node lain.

    Parameter:
        graph : GraphRantaiPasok  - graf jaringan distribusi
        asal  : str               - node ID titik keberangkatan

    Kembalikan:
        dist   : dict[str, float]  - biaya minimum ke setiap node
        parent : dict[str, str]    - node sebelumnya pada jalur terpendek
    """
    INF = float('inf')

    # inisialisasi: semua jarak tak terhingga, asal = 0
    dist   = {v: INF  for v in graph.adj}
    parent = {v: None for v in graph.adj}
    dist[asal] = 0.0

    visited = set()   # himpunan node yang sudah difinalisasi

    for _ in range(len(graph.adj)):

        # ── Langkah 1: Pilih node unvisited dengan dist terkecil ──
        # (menggantikan fungsi heapq.heappop)
        u = None
        for node in graph.adj:
            if node not in visited:
                if u is None or dist[node] < dist[u]:
                    u = node

        # semua node yang bisa dicapai sudah diproses
        if u is None or dist[u] == INF:
            break

        visited.add(u)

        # ── Langkah 2: Relaksasi semua tetangga u ──
        for edge in graph.tetangga(u):
            v     = edge.dest
            # bobot = total biaya perjalanan pada edge ini
            bobot = edge.jarak_km * edge.biaya_per_km

            # jika jalur melalui u lebih murah dari yang diketahui sebelumnya
            if dist[u] + bobot < dist[v]:
                dist[v]   = dist[u] + bobot
                parent[v] = u   # catat u sebagai pendahulu v

    return dist, parent


def rekonstruksi_jalur(parent: dict, asal: str, tujuan: str) -> list:
    """
    Rekonstruksi urutan node dari asal ke tujuan menggunakan array parent.

    Cara kerja:
        → Mulai dari tujuan, telusuri parent[] ke belakang hingga asal.
        → Balik hasilnya agar urutan menjadi asal → ... → tujuan.

    Kembalikan list node. List kosong berarti tidak ada jalur.
    Big-O: O(V).
    """
    jalur = []
    cur   = tujuan

    # telusuri mundur dari tujuan ke asal
    while cur is not None:
        jalur.append(cur)
        cur = parent[cur]

    jalur.reverse()   # balik agar asal ada di depan

    # validasi: jalur valid jika node pertama adalah asal
    if jalur and jalur[0] == asal:
        return jalur
    return []   # tidak ada jalur yang menghubungkan asal ke tujuan