import csv
import os
import statistics as stats
from collections import defaultdict

import matplotlib

matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(ROOT, "test_results copy.csv")
OUT_DIR = os.path.join(ROOT, "Latex", "figures")
os.makedirs(OUT_DIR, exist_ok=True)


def read_rows(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def to_float(v, default=None):
    try:
        return float(v)
    except Exception:
        return default


def to_int(v, default=None):
    try:
        return int(float(v))
    except Exception:
        return default


def summarize(rows):
    n = len(rows)
    ok = sum(1 for r in rows if r.get("Sucesso") == "OK")
    # cost equality checks (available implicitly via Sucesso)
    dual_ok_v1 = sum(1 for r in rows if r.get("Dual_Frank_v1") in ("True", True))
    dual_ok_v2 = sum(1 for r in rows if r.get("Dual_Frank_v2") in ("True", True))

    # times
    t_chuliu = [to_float(r.get("Tempo_ChuLiu_s"), 0.0) for r in rows]
    t_f1 = [to_float(r.get("Tempo_Fase1_s"), 0.0) for r in rows]
    t_f2v1 = [to_float(r.get("Tempo_Fase2_v1_s"), 0.0) for r in rows]
    t_f2v2 = [to_float(r.get("Tempo_Fase2_v2_s"), 0.0) for r in rows]

    # speedup v1 vs v2
    speedups = []
    for a, b in zip(t_f2v1, t_f2v2):
        if b and b > 0:
            speedups.append(a / b)

    # structural metrics
    contractions = [to_int(r.get("Contractions"), 0) for r in rows]
    depth = [to_int(r.get("MaxDepth"), 0) for r in rows]
    d0_edges = [to_int(r.get("D0_edges"), 0) for r in rows]
    d0_nodes = [to_int(r.get("D0_nodes"), 0) for r in rows]
    peak_kb = [to_int(r.get("PeakMem_kB"), 0) for r in rows]
    vertices = [to_int(r.get("Vertices"), 0) for r in rows]
    edges = [to_int(r.get("Arestas"), 0) for r in rows]

    def m(x):
        return (stats.mean(x), stats.median(x)) if x else (0.0, 0.0)

    summary = {
        "n": n,
        "ok": ok,
        "dual_ok_v1": dual_ok_v1,
        "dual_ok_v2": dual_ok_v2,
        "t_chuliu_mean_median": m(t_chuliu),
        "t_f1_mean_median": m(t_f1),
        "t_f2v1_mean_median": m(t_f2v1),
        "t_f2v2_mean_median": m(t_f2v2),
        "speedup_count": len(speedups),
        "speedup_mean_median": m(speedups),
        "contractions_mean_median": m(contractions),
        "depth_mean_median": m(depth),
        "peak_kb_mean_median": m(peak_kb),
        "d0_edges_mean_median": m(d0_edges),
        "d0_nodes_mean_median": m(d0_nodes),
    }

    # plots
    # 1) Boxplots of times
    fig, ax = plt.subplots(figsize=(8, 4))
    bp = ax.boxplot(
        [t_chuliu, t_f1, t_f2v1, t_f2v2],
    )
    ax.set_xticklabels(["Chu–Liu", "Fase I", "Fase II v1", "Fase II v2"])
    ax.set_ylabel("tempo (s)")
    ax.set_title("Distribuição de tempos por etapa")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_times_boxplot.png"), dpi=180)
    plt.close(fig)

    # 2) Scatter: tempo vs arestas
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(edges, t_f1, s=12, alpha=0.6, label="Fase I")
    ax.scatter(edges, t_chuliu, s=12, alpha=0.6, label="Chu-Liu")
    ax.set_xlabel("|A| (arestas)")
    ax.set_ylabel("tempo (s)")
    ax.set_title("Escalonamento em funcao de |A|")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_time_vs_edges_scatter.png"), dpi=180)
    plt.close(fig)

    # 3) Fase II comparison: v1 vs v2 - REDESIGNED FOR CLARITY
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Direct time comparison with clear labels
    positions = [1, 2]
    bp = ax[0].boxplot(
        [t_f2v1, t_f2v2], positions=positions, patch_artist=True, widths=0.6
    )

    # Color boxes differently
    colors = ["#ff9999", "#66b3ff"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    ax[0].set_xticks(positions)
    ax[0].set_xticklabels(["v1\n(lista)", "v2\n(heap)"], fontsize=11, fontweight="bold")
    ax[0].set_ylabel("Tempo de execucao (segundos)", fontsize=11)
    ax[0].set_title("Fase II: Comparacao de Desempenho", fontsize=12, fontweight="bold")
    ax[0].grid(axis="y", alpha=0.3, linestyle="--")

    # Add median values as text
    med_v1, med_v2 = stats.median(t_f2v1), stats.median(t_f2v2)
    ax[0].text(
        1,
        med_v1,
        f" {med_v1:.2f}s",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="darkred",
    )
    ax[0].text(
        2,
        med_v2,
        f" {med_v2:.3f}s",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="darkblue",
    )

    # Right: Speedup histogram with better annotations
    n, bins, patches = ax[1].hist(
        speedups, bins=35, alpha=0.75, color="#66b3ff", edgecolor="black", linewidth=0.8
    )

    med_speedup = stats.median(speedups)
    mean_speedup = stats.mean(speedups)

    ax[1].axvline(
        x=med_speedup,
        color="red",
        linestyle="--",
        linewidth=2.5,
        label=f"Mediana: {med_speedup:.1f}x",
        zorder=5,
    )
    ax[1].axvline(
        x=mean_speedup,
        color="orange",
        linestyle=":",
        linewidth=2.5,
        label=f"Media: {mean_speedup:.1f}x",
        zorder=5,
    )

    ax[1].set_xlabel(
        "Fator de Aceleracao (tempo v1 / tempo v2)", fontsize=11, fontweight="bold"
    )
    ax[1].set_ylabel("Numero de Instancias", fontsize=11)
    ax[1].set_title("Distribuicao do Speedup", fontsize=12, fontweight="bold")
    ax[1].legend(fontsize=10, loc="upper right")
    ax[1].grid(axis="y", alpha=0.3, linestyle="--")

    # Add explanatory text box with formula
    text_box = "Speedup = Tempo v1 / Tempo v2\n"
    text_box += f"Total: {len(speedups)} testes\n"
    text_box += f"v2 e {med_speedup:.0f}x mais rapida"
    ax[1].text(
        0.02,
        0.98,
        text_box,
        transform=ax[1].transAxes,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_speedup_hist.png"), dpi=180)
    plt.close(fig)

    # 4) Contractions and depth hist - REDESIGNED FOR CLARITY
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Contractions histogram with clear labels
    contr_clean = [c for c in contractions if c is not None]
    max_contr = max(contr_clean)

    # Limit bins to reasonable range for better visualization
    bin_limit = min(50, max_contr + 1)
    n, bins, patches = ax[0].hist(
        contr_clean,
        bins=range(0, bin_limit),
        alpha=0.75,
        color="#ff9999",
        edgecolor="black",
        linewidth=0.8,
    )

    med_contr = int(stats.median(contr_clean))
    mean_contr = stats.mean(contr_clean)

    ax[0].axvline(
        x=med_contr,
        color="red",
        linestyle="--",
        linewidth=2.5,
        label=f"Mediana: {med_contr}",
        zorder=5,
    )
    ax[0].axvline(
        x=mean_contr,
        color="orange",
        linestyle=":",
        linewidth=2.5,
        label=f"Media: {mean_contr:.1f}",
        zorder=5,
    )

    ax[0].set_xlabel("Numero de Contracoes de Ciclos", fontsize=11)
    ax[0].set_ylabel("Numero de Instancias", fontsize=11)
    ax[0].set_title("Contracoes em Chu-Liu/Edmonds", fontsize=12, fontweight="bold")
    ax[0].legend(fontsize=10)
    ax[0].grid(axis="y", alpha=0.3, linestyle="--")

    # Add statistics box
    stats_text = f"Min: {min(contr_clean)}\nMax: {max_contr}\n2000 testes"
    ax[0].text(
        0.98,
        0.98,
        stats_text,
        transform=ax[0].transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
    )

    # Right: Depth histogram
    depth_clean = [d for d in depth if d is not None]
    max_depth = max(depth_clean)

    bin_limit_depth = min(50, max_depth + 1)
    n, bins, patches = ax[1].hist(
        depth_clean,
        bins=range(0, bin_limit_depth),
        alpha=0.75,
        color="#66b3ff",
        edgecolor="black",
        linewidth=0.8,
    )

    med_depth = int(stats.median(depth_clean))
    mean_depth = stats.mean(depth_clean)

    ax[1].axvline(
        x=med_depth,
        color="red",
        linestyle="--",
        linewidth=2.5,
        label=f"Mediana: {med_depth}",
        zorder=5,
    )
    ax[1].axvline(
        x=mean_depth,
        color="orange",
        linestyle=":",
        linewidth=2.5,
        label=f"Media: {mean_depth:.1f}",
        zorder=5,
    )

    ax[1].set_xlabel("Profundidade de Recursao", fontsize=11)
    ax[1].set_ylabel("Numero de Instancias", fontsize=11)
    ax[1].set_title("Profundidade em Chu-Liu/Edmonds", fontsize=12, fontweight="bold")
    ax[1].legend(fontsize=10)
    ax[1].grid(axis="y", alpha=0.3, linestyle="--")

    # Add statistics box
    stats_text_depth = f"Min: {min(depth_clean)}\nMax: {max_depth}\n2000 testes"
    ax[1].text(
        0.98,
        0.98,
        stats_text_depth,
        transform=ax[1].transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
    )

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_contractions_depth.png"), dpi=180)
    plt.close(fig)

    # 5) Peak memory
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(peak_kb, bins=20, alpha=0.8)
    ax.set_xlabel("Pico de memória na Fase I (kB)")
    ax.set_ylabel("Contagem")
    ax.set_title("Uso de memória - Fase I")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_peakmem_hist.png"), dpi=180)
    plt.close(fig)

    # 6) D0 edges vs vertices
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(vertices, d0_edges, s=12, alpha=0.6)
    ax.set_xlabel("|V|")
    ax.set_ylabel("|A(D0)|")
    ax.set_title("Tamanho de D0 vs |V|")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_d0_edges_vs_vertices.png"), dpi=180)
    plt.close(fig)

    return summary


def main():
    if not os.path.exists(CSV_PATH):
        print(f"CSV não encontrado em {CSV_PATH}")
        return
    rows = read_rows(CSV_PATH)
    summary = summarize(rows)
    print("Resumo dos resultados:")
    print(f"  instâncias: {summary['n']}")
    print(f"  sucesso (custos iguais): {summary['ok']} / {summary['n']}")
    print(f"  dual ok v1: {summary['dual_ok_v1']} / {summary['n']}")
    print(f"  dual ok v2: {summary['dual_ok_v2']} / {summary['n']}")
    m_chu, md_chu = summary["t_chuliu_mean_median"]
    m_f1, md_f1 = summary["t_f1_mean_median"]
    m_v1, md_v1 = summary["t_f2v1_mean_median"]
    m_v2, md_v2 = summary["t_f2v2_mean_median"]
    print(
        f"  tempo médio/mediano (s): Chu–Liu {m_chu:.4f}/{md_chu:.4f}, Fase I {m_f1:.4f}/{md_f1:.4f}, Fase II v1 {m_v1:.4f}/{md_v1:.4f}, v2 {m_v2:.4f}/{md_v2:.4f}"
    )
    if summary["speedup_count"]:
        m_sp, md_sp = summary["speedup_mean_median"]
        print(f"  speedup Fase II (v1/v2) médio/mediano: {m_sp:.2f}/{md_sp:.2f}×")
    m_contr, md_contr = summary["contractions_mean_median"]
    m_depth, md_depth = summary["depth_mean_median"]
    print(
        f"  contrações (médio/mediano): {m_contr:.2f}/{md_contr:.2f}, profundidade: {m_depth:.2f}/{md_depth:.2f}"
    )
    m_pk, md_pk = summary["peak_kb_mean_median"]
    print(f"  pico de memória Fase I (kB) médio/mediano: {m_pk:.0f}/{md_pk:.0f}")


if __name__ == "__main__":
    main()
