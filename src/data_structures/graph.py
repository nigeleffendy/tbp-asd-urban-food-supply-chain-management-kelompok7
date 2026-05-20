# =============================================================================
#  graph.py  –  Graf Rantai Pasok (Adjacency List berbasis Linked List)
# =============================================================================
#  Graf berbobot tidak berarah (undirected weighted graph).
#  Merepresentasikan jaringan distribusi makanan:
#    - Node  : PETANI, DISTRIBUTOR, PASAR, GUDANG
#    - Edge  : jalur distribusi dengan atribut jarak_km dan biaya_per_km
#
#  Representasi adjacency list menggunakan linked list (EdgeNode),
#  bukan dictionary/list bawaan Python untuk setiap baris adjacency-nya.
#
#  Mengapa adjacency list, bukan adjacency matrix?
#    → Graf bersifat sparse (sedikit edge dibanding V²).
#    → Hemat memori: O(V + E) vs O(V²) pada matrix.
#    → Traversal tetangga lebih efisien untuk graf jarang.
#
#  Big-O:
#    tambah_node  : O(1)
#    tambah_jalur : O(1)  – sisip di depan linked list
#    tetangga     : O(deg) – traversal linked list tetangga node u
# =============================================================================


class EdgeNode:
    """
    Node pada adjacency linked list.
    Merepresentasikan satu jalur distribusi menuju node tujuan (dest).
    """
    def __init__(self, dest: str, jarak_km: int, biaya_per_km: float):
        self.dest         = dest           # ID node tujuan
        self.jarak_km     = jarak_km       # jarak jalur dalam kilometer
        self.biaya_per_km = biaya_per_km   # biaya pengiriman per kilometer (Rp)
        self.next         = None           # pointer ke edge berikutnya (linked list)


class GraphRantaiPasok:
    """
    Graf rantai pasok berbasis adjacency list (linked list per node).
    Tidak berarah: setiap jalur ditambahkan dua arah (u→v dan v→u).
    """

    def __init__(self):
        # adj: mapping node_id → EdgeNode (kepala linked list tetangga)
        self.adj       = {}
        # tipe_node: mapping node_id → tipe ('PETANI', 'DISTRIBUTOR', dst.)
        self.tipe_node = {}

    # ─────────────────────────────────────────
    #  TAMBAH NODE
    # ─────────────────────────────────────────
    def tambah_node(self, node_id: str, tipe: str):
        """
        Daftarkan node baru ke dalam graf.
        Jika node sudah ada, tidak ada perubahan (idempotent).
        Big-O: O(1).
        """
        if node_id not in self.adj:
            self.adj[node_id]       = None   # linked list tetangga kosong
            self.tipe_node[node_id] = tipe

    # ─────────────────────────────────────────
    #  TAMBAH JALUR
    # ─────────────────────────────────────────
    def tambah_jalur(self, u: str, v: str, jarak: int, biaya_km: float):
        """
        Tambahkan jalur distribusi antara node u dan v (tidak berarah).
        Edge baru disisipkan di depan linked list (O(1), tanpa traversal).
        Big-O: O(1).
        """
        # arah u → v
        e_uv       = EdgeNode(v, jarak, biaya_km)
        e_uv.next  = self.adj[u]   # sisip di depan
        self.adj[u] = e_uv

        # arah v → u  (karena graf tidak berarah)
        e_vu       = EdgeNode(u, jarak, biaya_km)
        e_vu.next  = self.adj[v]
        self.adj[v] = e_vu

    # ─────────────────────────────────────────
    #  TETANGGA
    # ─────────────────────────────────────────
    def tetangga(self, u: str) -> list:
        """
        Kembalikan list semua EdgeNode tetangga dari node u.
        Big-O: O(deg(u)) - deg = jumlah edge yang terhubung ke u.
        """
        hasil = []
        cur   = self.adj[u]
        while cur is not None:
            hasil.append(cur)
            cur = cur.next
        return hasil