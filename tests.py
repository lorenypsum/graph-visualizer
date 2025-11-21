import csv
import os
import random
import time
import traceback
import tracemalloc

import networkx as nx
from typing import Optional, Callable

from andrasfrank import (
    phase1,
    phase2,
    phase2_v2,
    check_dual_optimality_condition,
)
from chuliu import chuliu_edmonds, remove_in_edges_to

# Deafult parameters
NUM_TESTS = 10 
MIN_VERTICES = 100
MAX_VERTICES = 300
PESO_MIN = 1
PESO_MAX = 20
LOG_CSV_PATH = "test_results.csv"
LOG_TXT_PATH = "test_log.txt"
ROOT = "r0"
LANG = "pt"  # Change to "en" for English logs

# Instance family configuration
FAMILY = "random"  # options: random | dense | sparse | layered


def log_console_and_file(msg, log_txt_path=LOG_TXT_PATH):
    print(msg)
    with open(log_txt_path, "a") as f:
        f.write(msg + "\n")


def build_rooted_digraph(
    n=10, m=None, root="r0", peso_min=1, peso_max=10, family: str = "random"
):
    """
    Create a directed graph with n vertices, m edges.
    Parameters:
        - n: número de vértices (default: 10)
        - m: número de arestas (default: 2*n)
        - r0: rótulo do vértice raiz (default: "r0")
        - peso_min: peso mínimo das arestas (default: 1)
        - peso_max: peso máximo das arestas (default: 10)
    Returns:
        - D: grafo direcionado (DiGraph) criado
    """
    if m is None:
        # default edge count varies by family
        if family == "dense":
            m = min(n * (n - 1), 5 * n)
        elif family == "sparse":
            m = max(n, int(1.2 * n))
        elif family == "layered":
            m = 2 * n
        else:
            m = 2 * n

    D = nx.DiGraph()
    D.add_node(root)
    nodes = [i for i in range(n - 1)]
    all_nodes = [root] + nodes

    # Connect the root to at least one other node to ensure connectivity
    reached = {root}
    remaining = set(nodes)

    # Ensure all nodes are reachable from r0
    while remaining:
        v = remaining.pop()
        u = random.choice(list(reached))
        D.add_edge(u, v, w=random.randint(peso_min, peso_max))
        reached.add(v)

    # Add extra edges guided by family until we reach m edges
    if family == "layered":
        # Create 3 layers (root -> L1 -> L2), then add forward edges preferentially
        layers = [[], [], []]
        for i, v in enumerate(nodes):
            layers[i % 3].append(v)
        # ensure edges from root to first layer
        for v in layers[0]:
            if not D.has_edge(root, v):
                D.add_edge(root, v, w=random.randint(peso_min, peso_max))
        # edges from layer k to k+1
        for k in range(2):
            for u in layers[k]:
                for v in layers[k + 1]:
                    if D.number_of_edges() >= m:
                        break
                    if u != v and not D.has_edge(u, v):
                        if random.random() < 0.5:
                            D.add_edge(u, v, w=random.randint(peso_min, peso_max))
        # fill random if still under m
        while D.number_of_edges() < m:
            u, v = random.sample(all_nodes, 2)
            if not D.has_edge(u, v) and u != v:
                D.add_edge(u, v, w=random.randint(peso_min, peso_max))
    elif family == "dense":
        # Prefer adding many edges uniformly at random
        target = min(m, n * (n - 1))
        while D.number_of_edges() < target:
            u, v = random.sample(all_nodes, 2)
            if not D.has_edge(u, v):
                D.add_edge(u, v, w=random.randint(peso_min, peso_max))
    else:  # random or sparse
        while D.number_of_edges() < m:
            u, v = random.sample(all_nodes, 2)
            if not D.has_edge(u, v) and u != v:
                D.add_edge(u, v, w=random.randint(peso_min, peso_max))
    return D

def contains_arborescence(D, r0):
    """
    Check if G contains an arborescence with root r0.
    """
    tree = nx.dfs_tree(D, source=r0)
    return tree.number_of_nodes() == D.number_of_nodes(), tree

def get_total_digraph_cost(D_arbo):
    """
    Calculate the total cost of a directed graph.
    """
    return sum(data["w"] for _, _, data in D_arbo.edges(data=True))


def volume_tester(
    num_tests=NUM_TESTS,
    min_vertices=MIN_VERTICES,
    max_vertices=MAX_VERTICES,
    root=ROOT,
    peso_min=PESO_MIN,
    peso_max=PESO_MAX,
    log_csv_path=LOG_CSV_PATH,
    log_txt_path=LOG_TXT_PATH,
    draw_fn: Optional[Callable] = None,
    log: Optional[Callable[[str], None]] = None,
    boilerplate: bool = True,
    lang=LANG,
    family: str = FAMILY,
):
    success_count = 0
    failure_count = 0
    chuliu_greater_than_frank = 0
    frank_greater_than_chuliu = 0
    b1 = b2 = None

    # Garante saída limpa
    if os.path.exists(log_csv_path):
        os.remove(log_csv_path)
    if os.path.exists(log_txt_path):
        os.remove(log_txt_path)

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

    for i in range(1, num_tests + 1):
        n = random.randint(min_vertices, max_vertices)
        # choose edges range per family
        if family == "dense":
            m = random.randint(3 * n, min(n * (n - 1), 6 * n))
        elif family == "sparse":
            m = random.randint(n - 1, int(1.5 * n))
        elif family == "layered":
            m = random.randint(2 * n, 3 * n)
        else:
            m = random.randint(n, 3 * n)

        if boilerplate and log:
            if lang == "en":
                log_console_and_file(f"\n=== Test #{i} - Vertices: {n}, Edges: {m} ===")
            elif lang == "pt":
                log_console_and_file(
                    f"\n=== Teste #{i} - Vértices: {n}, Arestas: {m} ==="
                )

        success = False
        erro = ""
        custo_chuliu = custo_frank = custo_frank_v2 = None
        t0_total = time.perf_counter()
        t_chuliu = t_phase1 = t_phase2_v1 = t_phase2_v2 = 0.0
        # metrics
        chu_metrics = {"contractions": 0, "max_depth": 0}
        frank_metrics = {
            "d0_edges": None,
            "d0_nodes": None,
            "dual_count": None,
            "phase1_iterations": None,
        }
        peak_kb = None
        try:
            D = build_rooted_digraph(
                n=n, m=m, root=root, peso_min=peso_min, peso_max=peso_max, family=family
            )

            D1_copy = nx.DiGraph(D)

            contains_arborescence_result, tree_result = contains_arborescence(
                D1_copy, root
            )

            if contains_arborescence_result:
                if boilerplate and log:
                    if lang == "en":
                        log(
                            f"\n The original graph contains an arborescence with root {root}. Starting tests..."
                        )
                        if draw_fn:
                            draw_fn(
                                tree_result,
                                title=f"Original Arborescence with root {root}",
                            )
                    elif lang == "pt":
                        log(
                            f"\n O grafo original contém uma arborescência com raiz {root}. Iniciando os testes..."
                        )
                        if draw_fn:
                            draw_fn(
                                tree_result,
                                title=f"Arborescência Original com raiz {root}",
                            )

            if lang == "en":
                remove_in_edges_to(
                    D1_copy, root, log=log, boilerplate=boilerplate, lang="en"
                )
            elif lang == "pt":
                remove_in_edges_to(
                    D1_copy, root, log=log, boilerplate=boilerplate, lang="pt"
                )

            # Chu-Liu/Edmonds Algorithm (timed)
            t1 = time.perf_counter()
            arbo_chuliu = chuliu_edmonds(
                D1_copy,
                root,
                draw_fn=draw_fn,
                log=log,
                boilerplate=boilerplate,
                metrics=chu_metrics,
            )
            t_chuliu = time.perf_counter() - t1
            custo_chuliu = get_total_digraph_cost(arbo_chuliu)

            if boilerplate and log:
                if lang == "en":
                    log("\n Executing Chu-Liu/Edmonds algorithm...")
                    log(f"\n Cost of Chu-Liu/Edmonds arborescence: {custo_chuliu}")
                    if draw_fn:
                        draw_fn(arbo_chuliu, title="Chu-Liu/Edmonds Arborescence")
                elif lang == "pt":
                    log("\n Executando algoritmo de Chu-Liu/Edmonds...")
                    log(f"\n Custo da arborescência de Chu-Liu/Edmonds: {custo_chuliu}")
                    if draw_fn:
                        draw_fn(arbo_chuliu, title="Arborescência de Chu-Liu/Edmonds")

            # András Frank Algorithm phases (timed individually)
            # Phase I with metrics and peak memory
            tracemalloc.start()
            t1 = time.perf_counter()
            A_zero, Dual_list = phase1(
                D1_copy,
                root,
                draw_fn=None,
                log=log,
                boilerplate=boilerplate,
                lang=lang,
                metrics=frank_metrics,
            )
            t_phase1 = time.perf_counter() - t1
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_kb = int(peak / 1024)

            # Phase II v1
            t1 = time.perf_counter()
            arbo_frank_v1 = phase2(
                D1_copy,
                root,
                A_zero,
                draw_fn=None,
                log=None,
                boilerplate=boilerplate,
                lang=lang,
            )
            t_phase2_v1 = time.perf_counter() - t1

            # Phase II v2
            t1 = time.perf_counter()
            arbo_frank_v2 = phase2_v2(
                D1_copy,
                root,
                A_zero,
                draw_fn=None,
                log=None,
                boilerplate=boilerplate,
                lang=lang,
            )
            t_phase2_v2 = time.perf_counter() - t1

            custo_frank = get_total_digraph_cost(arbo_frank_v1)
            custo_frank_v2 = get_total_digraph_cost(arbo_frank_v2)

            # Verify both algorithms yield the same cost
            assert (
                custo_chuliu == custo_frank
            ), f"\n ❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank: {custo_frank}"

            assert (
                custo_chuliu == custo_frank_v2
            ), f"\n ❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank v2: {custo_frank_v2}"

            if boilerplate and log:
                if lang == "en":
                    log(f"\n Cost of Andras Frank arborescence: {custo_frank}")
                    log(f"\n Cost of Andras Frank arborescence (v2): {custo_frank_v2}")
                    if draw_fn:
                        draw_fn(arbo_frank_v1, title="Andras Frank Arborescence")
                        draw_fn(arbo_frank_v2, title="Andras Frank Arborescence (v2)")
                elif lang == "pt":
                    log(f"\n Custo da arborescência de Andras Frank: {custo_frank}")
                    log(
                        f"\n Custo da arborescência de Andras Frank (v2): {custo_frank_v2}"
                    )
                    if draw_fn:
                        draw_fn(arbo_frank_v1, title="Arborescência de Andras Frank")
                        draw_fn(
                            arbo_frank_v2, title="Arborescência de Andras Frank (v2)"
                        )

                # Dual checks
                b1 = check_dual_optimality_condition(
                    arbo_frank_v1,
                    Dual_list,
                    log=log,
                    boilerplate=boilerplate,
                    lang=lang,
                )
                b2 = check_dual_optimality_condition(
                    arbo_frank_v2,
                    Dual_list,
                    log=log,
                    boilerplate=boilerplate,
                    lang=lang,
                )
                if lang == "en":
                    assert b1, "\n ❌ Dual condition failed for Andras Frank."
                    assert b2, "\n ❌ Dual condition failed for Andras Frank v2."
                elif lang == "pt":
                    assert b1, "\n ❌ Falha na condição dual para Andras Frank."
                    assert b2, "\n ❌ Falha na condição dual para Andras Frank v2."

                success = True

                if boilerplate and log:
                    if lang == "en":
                        log(
                            "\n✅ Tests completed successfully! Both algorithms returned arborescences with the same minimum cost."
                        )
                    elif lang == "pt":
                        log(
                            "\n✅ Testes concluídos com sucesso! Ambos algoritmos retornaram arborescências com o mesmo custo mínimo."
                        )

            else:
                if boilerplate and log:
                    if lang == "en":
                        log(
                            "\n The graph does not contain an arborescence with root r0. Test aborted."
                        )
                    elif lang == "pt":
                        log(
                            "\n O grafo não contém uma arborescência com raiz r0. Teste abortado."
                        )
                if draw_fn:
                    draw_fn(D1_copy)

        except Exception as e:
            erro = str(e)
            log_console_and_file(f"❌ Erro: {erro}")
            print(e)
            traceback.print_exc(file=open(LOG_TXT_PATH, "a"))

        elapsed = round(time.perf_counter() - t0_total, 6)

        # Update counters
        if success:
            success_count += 1
        else:
            failure_count += 1
            if custo_chuliu is not None and custo_frank is not None:
                if custo_chuliu > custo_frank:
                    chuliu_greater_than_frank += 1
                elif custo_frank > custo_chuliu:
                    frank_greater_than_chuliu += 1

        # Write to CSV
        with open(LOG_CSV_PATH, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    i,
                    family,
                    n,
                    m,
                    custo_chuliu if custo_chuliu is not None else "-",
                    custo_frank if custo_frank is not None else "-",
                    custo_frank_v2 if custo_frank_v2 is not None else "-",
                    elapsed,
                    round(t_chuliu, 6),
                    round(t_phase1, 6),
                    round(t_phase2_v1, 6),
                    round(t_phase2_v2, 6),
                    b1,
                    b2,
                    chu_metrics.get("contractions"),
                    chu_metrics.get("max_depth"),
                    frank_metrics.get("d0_edges"),
                    frank_metrics.get("d0_nodes"),
                    frank_metrics.get("dual_count"),
                    frank_metrics.get("phase1_iterations"),
                    peak_kb,
                    "OK" if success else "FAIL",
                    erro,
                    success_count,
                    failure_count,
                    chuliu_greater_than_frank,
                    frank_greater_than_chuliu,
                ]
            )

    if boilerplate and log:
        log_console_and_file("\n=== Resumo dos Testes ===")
        log_console_and_file(f"\n Total de testes: {NUM_TESTS}")
        log_console_and_file(f"\n Testes bem-sucedidos: {success_count}")
        log_console_and_file(f"\n Testes com falha: {failure_count}")
        log_console_and_file(f"\n Custo ChuLiu > Frank: {chuliu_greater_than_frank}")
        log_console_and_file(f"\n Custo Frank > ChuLiu: {frank_greater_than_chuliu}")


volume_tester(
    num_tests=NUM_TESTS,
    min_vertices=MIN_VERTICES,
    max_vertices=MAX_VERTICES,
    root=ROOT,
    peso_min=PESO_MIN,
    peso_max=PESO_MAX,
    log_csv_path=LOG_CSV_PATH,
    log_txt_path=LOG_TXT_PATH,
    draw_fn=None,
    log=log_console_and_file,
    boilerplate=True,
    lang="pt",
    family=FAMILY,
)
