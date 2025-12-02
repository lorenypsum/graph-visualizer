import csv
import os
import random
import time
import traceback
import tracemalloc
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Tuple

import networkx as nx

from andrasfrank import (
    phase1,
    phase2,
    phase2_v2,
    check_dual_optimality_condition,
)
from chuliu import chuliu_edmonds, remove_in_edges_to

# Default parameters
NUM_TESTS = 2000
MIN_VERTICES = 2000
MAX_VERTICES = 2000
PESO_MIN = 1
PESO_MAX = 10
LOG_CSV_PATH = "test_results.csv"
LOG_TXT_PATH = "test_log.txt"
ROOT = 0
LANG = "pt"  # Change to "en" for English logs

# Instance family configuration
FAMILY = "random"  # options: random | dense | sparse | layered

@dataclass
class TestMetrics:
    """Container for test execution metrics."""
    custo_chuliu: Optional[float] = None
    custo_frank_v1: Optional[float] = None
    custo_frank_v2: Optional[float] = None
    t_chuliu: float = 0.0
    t_phase1: float = 0.0
    t_phase2_v1: float = 0.0
    t_phase2_v2: float = 0.0
    dual_frank_v1: Optional[bool] = None
    dual_frank_v2: Optional[bool] = None
    chu_metrics: Dict = field(
        default_factory=lambda: {"contractions": 0, "max_depth": 0}
    )
    frank_metrics: Dict = field(
        default_factory=lambda: {
            "d0_edges": None,
            "d0_nodes": None,
            "dual_count": None,
            "phase1_iterations": None,
        }
    )
    peak_kb: Optional[int] = None  # pico de memória em KB
    success: bool = False
    erro: str = ""


@dataclass
class TestConfig:
    """Configuration for test execution."""

    num_tests: int = NUM_TESTS
    min_vertices: int = MIN_VERTICES
    max_vertices: int = MAX_VERTICES
    r: int = ROOT
    peso_min: int = PESO_MIN
    peso_max: int = PESO_MAX
    log_csv_path: str = LOG_CSV_PATH
    log_txt_path: str = LOG_TXT_PATH
    family: str = FAMILY  # tipo de grafo
    draw_fn: Optional[Callable] = None
    log: Optional[Callable] = None
    boilerplate: bool = True
    lang: str = LANG


def log_console_and_file(msg: str, log_txt_path: str = LOG_TXT_PATH) -> None:
    """Log message to both console and file."""
    print(msg)
    with open(log_txt_path, "a") as f:
        f.write(msg + "\n")

def get_edge_count_for_family(n: int, family: str, m: Optional[int] = None) -> int:
    """Calculate appropriate edge count based on graph family."""
    if m is not None:
        return m

    edge_counts = {
        "dense": min(n * (n - 1), 5 * n),
        "sparse": max(n, int(1.2 * n)),
        "layered": 2 * n,
        "random": 2 * n,
    }
    return edge_counts.get(family, 2 * n)


def build_rooted_digraph(
    n: int = MIN_VERTICES,
    m: Optional[int] = None,
    root: int = ROOT,
    peso_min: int = PESO_MIN,
    peso_max: int = PESO_MAX,
    family: str = "random",
) -> nx.DiGraph:
    """
    Create a directed graph with n vertices, m edges.

    Parameters:
        - n: number of vertices (default: MIN_VERTICES)
        - m: number of edges (default: computed based on family)
        - root: label of root vertex (default: ROOT)
        - peso_min: minimum edge weight (default: PESO_MIN)
        - peso_max: maximum edge weight (default: PESO_MAX)
        - family: graph family type (default: "random")

    Returns:
        - D: directed graph (DiGraph)
    """
    m = get_edge_count_for_family(n, family, m)

    D = nx.DiGraph()
    D.add_node(root)
    nodes = list(range(1, n))
    all_nodes = [root] + nodes

    # Ensure all nodes are reachable from root
    reached = {root}
    remaining = set(nodes)

    while remaining:
        v = remaining.pop()
        u = random.choice(list(reached))
        D.add_edge(u, v, w=random.randint(peso_min, peso_max))
        reached.add(v)

    # Add extra edges based on family type
    if family == "layered":
        _build_layered_graph(D, root, nodes, m, peso_min, peso_max, all_nodes)
    elif family == "dense":
        _build_dense_graph(D, m, peso_min, peso_max, all_nodes)
    else:  # random or sparse
        _build_random_graph(D, m, peso_min, peso_max, all_nodes)

    return D


def _build_layered_graph(
    D: nx.DiGraph,
    root: int,
    nodes: list,
    m: int,
    peso_min: int,
    peso_max: int,
    all_nodes: list,
) -> None:
    """Build a layered graph structure with 3 layers."""
    layers = [[], [], []]
    for i, v in enumerate(nodes):
        layers[i % 3].append(v)

    # Ensure edges from root to first layer
    for v in layers[0]:
        if not D.has_edge(root, v):
            D.add_edge(root, v, w=random.randint(peso_min, peso_max))

    # Add edges from layer k to k+1
    for k in range(2):
        for u in layers[k]:
            for v in layers[k + 1]:
                if D.number_of_edges() >= m:
                    return
                if u != v and not D.has_edge(u, v) and random.random() < 0.5:
                    D.add_edge(u, v, w=random.randint(peso_min, peso_max))

    # Fill with random edges if needed
    _build_random_graph(D, m, peso_min, peso_max, all_nodes)


def _build_dense_graph(
    D: nx.DiGraph,
    m: int,
    peso_min: int,
    peso_max: int,
    all_nodes: list,
) -> None:
    """Build a dense graph by adding many edges uniformly at random."""
    n = len(all_nodes)
    target = min(m, n * (n - 1))

    while D.number_of_edges() < target:
        u, v = random.sample(all_nodes, 2)
        if not D.has_edge(u, v):
            D.add_edge(u, v, w=random.randint(peso_min, peso_max))


def _build_random_graph(
    D: nx.DiGraph,
    m: int,
    peso_min: int,
    peso_max: int,
    all_nodes: list,
) -> None:
    """Build a random graph by adding edges uniformly at random."""
    while D.number_of_edges() < m:
        u, v = random.sample(all_nodes, 2)
        if not D.has_edge(u, v) and u != v:
            D.add_edge(u, v, w=random.randint(peso_min, peso_max))


def contains_arborescence(D: nx.DiGraph, r: int) -> Tuple[bool, nx.DiGraph]:
    """Check if graph contains an arborescence with root r."""
    tree = nx.dfs_tree(D, source=r)
    return tree.number_of_nodes() == D.number_of_nodes(), tree


def get_total_digraph_cost(D_arbo: nx.DiGraph) -> float:
    """Calculate the total cost of a directed graph."""
    return sum(data["w"] for _, _, data in D_arbo.edges(data=True))


def get_edge_count_range(n: int, family: str) -> Tuple[int, int]:
    """Get the range of edge counts for a given family."""
    ranges = {
        "dense": (3 * n, min(n * (n - 1), 6 * n)),
        "sparse": (n - 1, int(1.5 * n)),
        "layered": (2 * n, 3 * n),
    }
    return ranges.get(family, (n, 3 * n))


def initialize_csv_log(log_csv_path: str) -> None:
    """Initialize CSV log file with headers."""
    with open(log_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Teste",
                "Familia",
                "Vertices",
                "Arestas",
                "Custo_ChuLiu",
                "Custo_Frank_v1",
                "Custo_Frank_v2",
                "Tempo_total_s",
                "Tempo_ChuLiu_s",
                "Tempo_Fase1_s",
                "Tempo_Fase2_v1_s",
                "Tempo_Fase2_v2_s",
                "Dual_Frank_v1",
                "Dual_Frank_v2",
                "Contractions",
                "MaxDepth",
                "D0_edges",
                "D0_nodes",
                "Dual_count",
                "Fase1_iter",
                "PeakMem_kB",
                "Sucesso",
                "Erro",
                "Total_sucessos",
                "Total_falhas",
                "ChuLiu_maior_que_Frank",
                "Frank_maior_que_ChuLiu",
            ]
        )


def write_test_result(
    log_csv_path: str,
    test_num: int,
    family: str,
    n: int,
    m: int,
    metrics: TestMetrics,
    elapsed: float,
    success_count: int,
    failure_count: int,
    chuliu_greater: int,
    frank_greater: int,
) -> None:
    """Write test results to CSV file."""
    with open(log_csv_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                test_num,
                family,
                n,
                m,
                metrics.custo_chuliu if metrics.custo_chuliu is not None else "-",
                metrics.custo_frank_v1 if metrics.custo_frank_v1 is not None else "-",
                metrics.custo_frank_v2 if metrics.custo_frank_v2 is not None else "-",
                elapsed,
                round(metrics.t_chuliu, 6),
                round(metrics.t_phase1, 6),
                round(metrics.t_phase2_v1, 6),
                round(metrics.t_phase2_v2, 6),
                metrics.dual_frank_v1,
                metrics.dual_frank_v2,
                metrics.chu_metrics.get("contractions"),
                metrics.chu_metrics.get("max_depth"),
                metrics.frank_metrics.get("d0_edges"),
                metrics.frank_metrics.get("d0_nodes"),
                metrics.frank_metrics.get("dual_count"),
                metrics.frank_metrics.get("phase1_iterations"),
                metrics.peak_kb,
                "OK" if metrics.success else "FAIL",
                metrics.erro,
                success_count,
                failure_count,
                chuliu_greater,
                frank_greater,
            ]
        )


def run_chuliu_algorithm(
    D: nx.DiGraph,
    r: int,
    config: TestConfig,
    chu_metrics: Dict,
) -> Tuple[nx.DiGraph, float]:
    """Run Chu-Liu/Edmonds algorithm and return arborescence and execution time."""
    t1 = time.perf_counter()
    arbo = chuliu_edmonds(
        D,
        r,
        draw_fn=config.draw_fn,
        log=config.log,
        boilerplate=config.boilerplate,
        metrics=chu_metrics,
        lang=config.lang,
    )
    t_elapsed = time.perf_counter() - t1
    return arbo, t_elapsed


def run_frank_phase1(
    D: nx.DiGraph,
    r: int,
    config: TestConfig,
    frank_metrics: Dict,
) -> Tuple[list, list, float, int]:
    """Run András Frank Phase 1 with memory tracking."""
    tracemalloc.start()
    t1 = time.perf_counter()
    sigma = phase1(
        D,
        r,
        draw_fn=None,
        log=config.log,
        boilerplate=config.boilerplate,
        lang=config.lang,
        metrics=frank_metrics,
    )
    F = [a for a, _, _ in sigma]
    t_elapsed = time.perf_counter() - t1
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = int(peak / 1024)
    return F, sigma, t_elapsed, peak_kb


def run_frank_phase2(
    D: nx.DiGraph,
    r: int,
    F: list,
    config: TestConfig,
    use_v2: bool = False,
) -> Tuple[nx.DiGraph, float]:
    """Run András Frank Phase 2 (v1 or v2)."""
    phase_func = phase2_v2 if use_v2 else phase2
    t1 = time.perf_counter()
    arbo = phase_func(
        D,
        r,
        F,
        draw_fn=None,
        log=None,
        boilerplate=config.boilerplate,
        lang=config.lang,
    )
    t_elapsed = time.perf_counter() - t1
    return arbo, t_elapsed


def verify_algorithms(
    arbo_chuliu: nx.DiGraph,
    arbo_frank_v1: nx.DiGraph,
    arbo_frank_v2: nx.DiGraph,
    sigma: list,
    config: TestConfig,
) -> Tuple[float, float, float, bool, bool]:
    """Verify both algorithms and check dual conditions."""
    custo_chuliu = get_total_digraph_cost(arbo_chuliu)
    custo_frank_v1 = get_total_digraph_cost(arbo_frank_v1)
    custo_frank_v2 = get_total_digraph_cost(arbo_frank_v2)

    # Verify costs match
    assert (
        custo_chuliu == custo_frank_v1
    ), f"\n x Custos diferentes! Chu-Liu: {custo_chuliu}, Frank: {custo_frank_v1}"
    assert (
        custo_chuliu == custo_frank_v2
    ), f"\n x Custos diferentes! Chu-Liu: {custo_chuliu}, Frank v2: {custo_frank_v2}"

    # Check dual conditions
    dual_v1 = check_dual_optimality_condition(
        arbo_frank_v1,
        sigma,
        log=config.log,
        boilerplate=config.boilerplate,
        lang=config.lang,
    )
    dual_v2 = check_dual_optimality_condition(
        arbo_frank_v2,
        sigma,
        log=config.log,
        boilerplate=config.boilerplate,
        lang=config.lang,
    )

    if config.lang == "en":
        assert dual_v1, "\n x Dual condition failed for Andras Frank."
        assert dual_v2, "\n x Dual condition failed for Andras Frank v2."
    else:
        assert dual_v1, "\n x Falha na condição dual para Andras Frank."
        assert dual_v2, "\n x Falha na condição dual para Andras Frank v2."

    return custo_chuliu, custo_frank_v1, custo_frank_v2, dual_v1, dual_v2


def log_test_start(test_num: int, n: int, m: int, config: TestConfig) -> None:
    """Log the start of a test."""
    if not (config.boilerplate and config.log):
        return

    if config.lang == "en":
        log_console_and_file(f"\n=== Test #{test_num} - Vertices: {n}, Edges: {m} ===")
    else:
        log_console_and_file(
            f"\n=== Teste #{test_num} - Vértices: {n}, Arestas: {m} ==="
        )


def log_test_success(config: TestConfig) -> None:
    """Log successful test completion."""
    if not (config.boilerplate and config.log):
        return

    if config.lang == "en":
        config.log(
            "\n✓ Tests completed successfully! Both algorithms returned "
            "arborescences with the same minimum cost."
        )
    else:
        config.log(
            "\n✓ Testes concluídos com sucesso! Ambos algoritmos retornaram "
            "arborescências com o mesmo custo mínimo."
        )


def run_single_test(
    test_num: int,
    config: TestConfig,
) -> Tuple[TestMetrics, int, int, float]:
    """Run a single test iteration."""
    metrics = TestMetrics()

    # Generate graph parameters
    n = random.randint(config.min_vertices, config.max_vertices)
    min_edges, max_edges = get_edge_count_range(n, config.family)
    m = random.randint(min_edges, max_edges)

    log_test_start(test_num, n, m, config)

    t0_total = time.perf_counter()

    try:
        # Build graph
        D = build_rooted_digraph(
            n=n,
            m=m,
            root=config.r,
            peso_min=config.peso_min,
            peso_max=config.peso_max,
            family=config.family,
        )
        D_copy = nx.DiGraph(D)

        # Check if graph contains arborescence
        has_arbo, tree = contains_arborescence(D_copy, config.r)
        if not has_arbo:
            if config.boilerplate and config.log:
                msg = (
                    "\n The graph does not contain an arborescence with root r. Test aborted."
                    if config.lang == "en"
                    else "\n O grafo não contém uma arborescência com raiz r. Teste abortado."
                )
                config.log(msg)
            return metrics, n, m, time.perf_counter() - t0_total

        # Remove edges to root
        remove_in_edges_to(D_copy, config.r)

        # Run Chu-Liu/Edmonds
        arbo_chuliu, metrics.t_chuliu = run_chuliu_algorithm(
            D_copy, config.r, config, metrics.chu_metrics
        )

        # Run András Frank Phase 1
        F, sigma, metrics.t_phase1, metrics.peak_kb = run_frank_phase1(
            D_copy, config.r, config, metrics.frank_metrics
        )

        # Run András Frank Phase 2 (both versions)
        arbo_frank_v1, metrics.t_phase2_v1 = run_frank_phase2(
            D_copy, config.r, F, config, use_v2=False
        )
        arbo_frank_v2, metrics.t_phase2_v2 = run_frank_phase2(
            D_copy, config.r, F, config, use_v2=True
        )

        # Verify results
        (
            metrics.custo_chuliu,
            metrics.custo_frank_v1,
            metrics.custo_frank_v2,
            metrics.dual_frank_v1,
            metrics.dual_frank_v2,
        ) = verify_algorithms(
            arbo_chuliu, arbo_frank_v1, arbo_frank_v2, sigma, config
        )

        metrics.success = True
        log_test_success(config)

    except Exception as e:
        metrics.erro = str(e)
        log_console_and_file(f"x Erro: {metrics.erro}")
        print(e)
        traceback.print_exc(file=open(config.log_txt_path, "a"))

    elapsed = time.perf_counter() - t0_total
    return metrics, n, m, elapsed


def volume_tester(
    num_tests: int = NUM_TESTS,
    min_vertices: int = MIN_VERTICES,
    max_vertices: int = MAX_VERTICES,
    r: int = ROOT,
    peso_min: int = PESO_MIN,
    peso_max: int = PESO_MAX,
    log_csv_path: str = LOG_CSV_PATH,
    log_txt_path: str = LOG_TXT_PATH,
    family: str = FAMILY,
    **kwargs,
) -> None:
    """
    Run volume tests comparing Chu-Liu/Edmonds and András Frank algorithms.

    Parameters:
        - num_tests: Number of tests to run
        - min_vertices: Minimum number of vertices
        - max_vertices: Maximum number of vertices
        - r: Root vertex
        - peso_min: Minimum edge weight
        - peso_max: Maximum edge weight
        - log_csv_path: Path to CSV log file
        - log_txt_path: Path to text log file
        - family: Instance family ("random", "dense", "sparse", "layered")
        - **kwargs: Additional parameters:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")
    """
    # Create configuration
    config = TestConfig(
        num_tests=num_tests,
        min_vertices=min_vertices,
        max_vertices=max_vertices,
        r=r,
        peso_min=peso_min,
        peso_max=peso_max,
        log_csv_path=log_csv_path,
        log_txt_path=log_txt_path,
        family=family,
        draw_fn=kwargs.get("draw_fn", None),
        log=kwargs.get("log", None),
        boilerplate=kwargs.get("boilerplate", True),
        lang=kwargs.get("lang", LANG),
    )

    # Initialize counters
    success_count = 0
    failure_count = 0
    chuliu_greater_than_frank = 0
    frank_greater_than_chuliu = 0

    # Clean up old logs
    for path in [config.log_csv_path, config.log_txt_path]:
        if os.path.exists(path):
            os.remove(path)

    # Initialize CSV
    initialize_csv_log(config.log_csv_path)

    # Run tests
    for i in range(1, config.num_tests + 1):
        metrics, n, m, elapsed = run_single_test(i, config)

        # Update counters
        if metrics.success:
            success_count += 1
        else:
            failure_count += 1
            if metrics.custo_chuliu is not None and metrics.custo_frank_v1 is not None:
                if metrics.custo_chuliu > metrics.custo_frank_v1:
                    chuliu_greater_than_frank += 1
                elif metrics.custo_frank_v1 > metrics.custo_chuliu:
                    frank_greater_than_chuliu += 1

        # Write results to CSV
        write_test_result(
            config.log_csv_path,
            i,
            config.family,
            n,
            m,
            metrics,
            elapsed,
            success_count,
            failure_count,
            chuliu_greater_than_frank,
            frank_greater_than_chuliu,
        )

        # Break on failure
        if not metrics.success:
            if config.boilerplate and config.log:
                msg = (
                    f"\nx Test #{i} failed. Stopping test execution."
                    if config.lang == "en"
                    else f"\nx Teste #{i} falhou. Interrompendo execução dos testes."
                )
                log_console_and_file(msg, config.log_txt_path)
            break

    # Log summary
    if config.boilerplate and config.log:
        log_console_and_file("\n=== Resumo dos Testes ===")
        log_console_and_file(f"\n Total de testes: {config.num_tests}")
        log_console_and_file(f"\n Testes bem-sucedidos: {success_count}")
        log_console_and_file(f"\n Testes com falha: {failure_count}")
        log_console_and_file(f"\n Custo ChuLiu > Frank: {chuliu_greater_than_frank}")
        log_console_and_file(f"\n Custo Frank > ChuLiu: {frank_greater_than_chuliu}")


if __name__ == "__main__":
    volume_tester(
        num_tests=NUM_TESTS,
        min_vertices=MIN_VERTICES,
        max_vertices=MAX_VERTICES,
        r=ROOT,
        peso_min=PESO_MIN,
        peso_max=PESO_MAX,
        log_csv_path=LOG_CSV_PATH,
        log_txt_path=LOG_TXT_PATH,
        family=FAMILY,
        draw_fn=None,
        log=log_console_and_file,
        boilerplate=True,
        lang="pt",
    )
