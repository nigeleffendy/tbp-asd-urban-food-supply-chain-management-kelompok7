# =============================================================================
#  modul_5.py  –  Modul Dijkstra Biaya Minimum
# =============================================================================
#  Modul ini menangani pencarian JALUR DISTRIBUSI TERMURAH antar node
#  menggunakan algoritma Dijkstra yang sudah diimplementasi manual.
#
#  Bobot edge: jarak_km × biaya_per_km  (total ongkos kirim, bukan jarak)
#
#  Fungsi utama:
#    - cari_rute_termurah   : jalankan Dijkstra + rekonstruksi jalur
#    - tampilkan_rute       : cetak rute dengan breakdown biaya per segmen
#    - semua_rute_dari_node : hitung biaya ke semua node lain dari satu sumber
#    - bandingkan_rute      : bandingkan dua jalur berbeda secara berdampingan
# =============================================================================

from src.data_structures.graph    import GraphRantaiPasok
from src.data_structures.dijkstra import dijkstra_biaya, rekonstruksi_jalur
from src.data_structures.stack    import Stack


# ─────────────────────────────────────────────
#  OPERASI UTAMA
# ─────────────────────────────────────────────

def cari_rute_termurah(
    graph         : GraphRantaiPasok,
    log_transaksi : Stack,
    asal          : str,
    tujuan        : str
) -> tuple:
    """
    Cari jalur distribusi berbiaya minimum dari asal ke tujuan.

    Langkah:
      1. Validasi asal dan tujuan ada di graf.
      2. Jalankan Dijkstra dari asal (O(V² + E)).
      3. Rekonstruksi jalur menggunakan array parent.
      4. Catat ke log transaksi.

    Kembalikan:
        (True,  {'jalur': list, 'biaya': float, 'dist': dict, 'parent': dict})
        (False, pesan_error)
    """
    # ── validasi node ──
    if asal not in graph.adj:
        return False, f"Node asal '{asal}' tidak ditemukan dalam jaringan."
    if tujuan not in graph.adj:
        return False, f"Node tujuan '{tujuan}' tidak ditemukan dalam jaringan."

    # ── jalankan Dijkstra ──
    dist, parent = dijkstra_biaya(graph, asal)

    # ── cek apakah tujuan bisa dicapai ──
    if dist[tujuan] == float('inf'):
        return False, (f"Tidak ada jalur yang menghubungkan '{asal}' ke '{tujuan}'. "
                       f"Jaringan mungkin terputus.")

    # ── rekonstruksi jalur ──
    jalur = rekonstruksi_jalur(parent, asal, tujuan)

    # ── catat ke log ──
    log_transaksi.push(
        f"[RUTE] {asal}->{tujuan} | "
        f"{' -> '.join(jalur)} | biaya=Rp {dist[tujuan]:,.0f}"
    )

    return True, {
        'jalur'  : jalur,
        'biaya'  : dist[tujuan],
        'dist'   : dist,
        'parent' : parent
    }


# ─────────────────────────────────────────────
#  TAMPILAN RUTE
# ─────────────────────────────────────────────

def tampilkan_rute(
    graph  : GraphRantaiPasok,
    hasil  : dict
):
    """
    Cetak rute distribusi dengan breakdown biaya tiap segmen jalur.
    Format: Node A --(jarak km, Rp biaya/km)--> Node B  = Rp total_segmen
    """
    jalur = hasil['jalur']
    biaya = hasil['biaya']

    if len(jalur) < 2:
        # jalur asal ke diri sendiri
        print(f"\n  Rute  : {jalur[0]}")
        print(f"  Biaya : Rp 0  (asal = tujuan)")
        return

    print(f"\n  Rute Termurah: {jalur[0]}  →  {jalur[-1]}")
    print(f"  {'-'*62}")
    print(f"  {'Segmen':<30} {'Jarak':>8}  {'Biaya/km':>12}  {'Subtotal':>14}")
    print(f"  {'-'*62}")

    akumulasi = 0.0
    for i in range(len(jalur) - 1):
        u, v = jalur[i], jalur[i + 1]

        # cari edge u → v di adjacency list
        edge_info = None
        for edge in graph.tetangga(u):
            if edge.dest == v:
                edge_info = edge
                break

        if edge_info:
            subtotal   = edge_info.jarak_km * edge_info.biaya_per_km
            akumulasi += subtotal
            segmen     = f"{u}  →  {v}"
            print(f"  {segmen:<30} {edge_info.jarak_km:>6} km  "
                  f"Rp {edge_info.biaya_per_km:>9,.0f}  "
                  f"Rp {subtotal:>12,.0f}")
        else:
            print(f"  {u} → {v}  (detail edge tidak ditemukan)")

    print(f"  {'-'*62}")
    print(f"  {'TOTAL BIAYA':<30} {'':>8}  {'':>12}  Rp {biaya:>12,.0f}")
    print(f"  Jumlah Hop  : {len(jalur) - 1} segmen")
    print(f"  Urutan Node : {' -> '.join(jalur)}")


def semua_rute_dari_node(
    graph    : GraphRantaiPasok,
    asal     : str,
    tipe_node: dict = None,
    top_n    : int  = 10
):
    """
    Hitung dan tampilkan biaya minimum dari node asal ke semua node lain.
    Urutkan dari yang termurah ke termahal. Tampilkan top_n terjangkau.

    Berguna untuk memilih distributor atau pasar tujuan pengiriman terbaik.
    """
    if asal not in graph.adj:
        print(f"  [!] Node '{asal}' tidak ditemukan.")
        return

    dist, _ = dijkstra_biaya(graph, asal)

    # kumpulkan node yang bisa dijangkau (dist < INF), kecuali asal sendiri
    terjangkau = [
        (node, d)
        for node, d in dist.items()
        if d < float('inf') and node != asal
    ]
    # urutkan dari biaya terkecil
    terjangkau.sort(key=lambda x: x[1])

    print(f"\n  Biaya Distribusi dari '{asal}' ke seluruh jaringan")
    print(f"  (menampilkan {min(top_n, len(terjangkau))} termurah dari "
          f"{len(terjangkau)} node terjangkau)")
    print(f"\n  {'No':<4} {'Node':<10} {'Tipe':<14} {'Biaya Minimum':>18}")
    print(f"  {'-'*50}")

    for i, (node, biaya) in enumerate(terjangkau[:top_n], start=1):
        tipe = tipe_node.get(node, '-') if tipe_node else '-'
        print(f"  {i:<4} {node:<10} {tipe:<14} Rp {biaya:>14,.0f}")

    tidak_terjangkau = [n for n, d in dist.items() if d == float('inf') and n != asal]
    if tidak_terjangkau:
        print(f"\n  Node tidak terjangkau ({len(tidak_terjangkau)}): "
              f"{', '.join(tidak_terjangkau)}")


def bandingkan_rute(
    graph  : GraphRantaiPasok,
    asal   : str,
    tujuan : str
):
    """
    Bandingkan jalur terpendek (biaya minimum via Dijkstra) vs
    jalur langsung (jika ada edge langsung antara asal dan tujuan).

    Membantu pengambil keputusan menilai apakah jalur langsung
    lebih mahal dibandingkan melewati distributor perantara.
    """
    if asal not in graph.adj or tujuan not in graph.adj:
        print("  [!] Asal atau tujuan tidak valid.")
        return

    # jalur optimal via Dijkstra
    dist, parent = dijkstra_biaya(graph, asal)
    jalur_opt    = rekonstruksi_jalur(parent, asal, tujuan)
    biaya_opt    = dist[tujuan]

    # cek apakah ada edge langsung asal → tujuan
    biaya_langsung = None
    for edge in graph.tetangga(asal):
        if edge.dest == tujuan:
            biaya_langsung = edge.jarak_km * edge.biaya_per_km
            break

    print(f"\n  Perbandingan Rute: {asal}  →  {tujuan}")
    print(f"  {'-'*55}")

    if biaya_opt < float('inf'):
        print(f"  Jalur Optimal (Dijkstra):")
        print(f"    Rute  : {' -> '.join(jalur_opt)}")
        print(f"    Biaya : Rp {biaya_opt:,.0f}")
        print(f"    Hop   : {len(jalur_opt) - 1} segmen")
    else:
        print(f"  Jalur Optimal : TIDAK ADA jalur yang menghubungkan.")

    if biaya_langsung is not None:
        print(f"\n  Jalur Langsung (1 hop):")
        print(f"    Rute  : {asal} -> {tujuan}")
        print(f"    Biaya : Rp {biaya_langsung:,.0f}")
        if biaya_opt < float('inf'):
            selisih = biaya_langsung - biaya_opt
            if selisih > 0:
                print(f"    Jalur langsung lebih MAHAL Rp {selisih:,.0f} "
                      f"({selisih / biaya_opt * 100:.1f}%) dari jalur optimal.")
            elif selisih < 0:
                print(f"    Jalur langsung lebih MURAH Rp {abs(selisih):,.0f} "
                      f"(ini adalah jalur optimal).")
            else:
                print(f"    Biaya sama dengan jalur optimal.")
    else:
        print(f"\n  Jalur Langsung : Tidak ada edge langsung {asal} → {tujuan}.")

    print(f"  {'-'*55}")