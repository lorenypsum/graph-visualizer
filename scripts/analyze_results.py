import csv
import os
import statistics as stats
from collections import defaultdict

import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(ROOT, "test_results.csv")
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
    ax.scatter(edges, t_chuliu, s=12, alpha=0.6, label="Chu–Liu")
    ax.set_xlabel("|A| (arestas)")
    ax.set_ylabel("tempo (s)")
    ax.set_title("Escalonamento em função de |A|")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_time_vs_edges_scatter.png"), dpi=180)
    plt.close(fig)

    # 3) Speedup hist
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(speedups, bins=20, alpha=0.8)
    ax.set_xlabel("aceleramento (speedup) (Fase II v1 / v2)")
    ax.set_ylabel("contagem")
    ax.set_title("Distribuição de aceleramento na Fase II (heap vs sem heap)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_speedup_hist.png"), dpi=180)
    plt.close(fig)

    # 4) Contractions and depth hist
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].hist(
        [c for c in contractions if c is not None],
        bins=range(0, max(contractions + [1]) + 1),
        alpha=0.8,
    )
    ax[0].set_title("Contrações (Chu–Liu)")
    ax[0].set_xlabel("nº de contrações")
    ax[0].set_ylabel("contagem")
    ax[1].hist(
        [d for d in depth if d is not None],
        bins=range(0, max(depth + [1]) + 1),
        alpha=0.8,
    )
    ax[1].set_title("Profundidade de recursão (Chu–Liu)")
    ax[1].set_xlabel("profundidade")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig_contractions_depth.png"), dpi=180)
    plt.close(fig)

    # 5) Peak memory
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(peak_kb, bins=20, alpha=0.8)
    ax.set_xlabel("pico de memória na Fase I (kB)")
    ax.set_ylabel("contagem")
    ax.set_title("Uso de memória — Fase I")
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
