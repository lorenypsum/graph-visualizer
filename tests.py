import csv
import os
import random
import time
import traceback

import networkx as nx

from andrasfrank import andras_frank_algorithm
from chuliu import find_optimum_arborescence_chuliu, remove_edges_to_r0

# Deafult parameters
NUM_TESTS = 2000
MIN_VERTICES = 100
MAX_VERTICES = 200
PESO_MIN = 1
PESO_MAX = 20
LOG_CSV_PATH = "test_results.csv"
LOG_TXT_PATH = "test_log.txt"
ROOT = "r0"
LANG = "pt"  # Change to "en" for English logs

def log_console_and_file(msg, log_txt_path=LOG_TXT_PATH):
    print(msg)
    with open(log_txt_path, "a") as f:
        f.write(msg + "\n")

def build_rooted_digraph(n=10, m=None, root="r0", peso_min=1, peso_max=10):
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
        # default to 2*n edges
        m = 2 * n

    D = nx.DiGraph()
    D.add_node(root)
    nodes = [f"v{i}" for i in range(n - 1)]
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

    # Add random edges until we reach m edges
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
    draw_fn=None,
    log=None,
    boilerplate=True,
    lang=LANG,
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
                "Vértices",
                "Arestas",
                "Custo_ChuLiu",
                "Custo_Frank1",
                "Custo_Frank2",
                "Sucesso",
                "Erro",
                "Tempo_execucao_seg",
                "Condicao_dual_Frank1",
                "Condicao_dual_Frank2",
                "Total_sucessos",
                "Total_falhas",
                "ChuLiu_maior_que_Frank",
                "Frank_maior_que_ChuLiu",
            ]
        )

    for i in range(1, num_tests + 1):
        n = random.randint(min_vertices, max_vertices)
        m = random.randint(n, 3 * n)

        if boilerplate and log:
            if lang == "en":
                log_console_and_file(f"\n=== Test #{i} - Vertices: {n}, Edges: {m} ===")
            elif lang == "pt":
                log_console_and_file(f"\n=== Teste #{i} - Vértices: {n}, Arestas: {m} ===")

        success = False
        erro = ""
        custo1 = custo2 = custo3 = "-"
        start_time = time.time()

        try:
            D = build_rooted_digraph(
                n=n, m=m, root=root, peso_min=peso_min, peso_max=peso_max
            )

            D1_copy = D.copy()

            contains_arborescence_result, tree_result = contains_arborescence(D1_copy, root)

            if contains_arborescence_result:
                if boilerplate and log:
                    if lang == "en":
                        log(
                         f"\n The original graph contains an arborescence with root {root}. Starting tests..."
                        )
                        if draw_fn:
                            draw_fn(tree_result, title=f"Original Arborescence with root {root}")
                    elif lang == "pt":
                        log(
                            f"\n O grafo original contém uma arborescência com raiz {root}. Iniciando os testes..."
                            )
                        if draw_fn:
                            draw_fn(tree_result, title=f"Arborescência Original com raiz {root}")

            if lang == "en":
                D1_filtered = remove_edges_to_r0(D1_copy, root, log=log, boilerplate=boilerplate, lang="en")
            elif lang == "pt":
                D1_filtered = remove_edges_to_r0(D1_copy, root, log=log, boilerplate=boilerplate, lang="pt")

            # Chu-Liu/Edmonds Algorithm
            arbo_chuliu = find_optimum_arborescence_chuliu(D1_filtered, root, draw_fn=draw_fn, log=log, boilerplate=boilerplate)
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
            

            if lang == "en":
                # Frank's Algorithm
                arbo_frank_v1, arbo_frank_v2, b1, b2 = andras_frank_algorithm(
                    D1_filtered, draw_fn=None, log=log, boilerplate=boilerplate, lang="en"
                )
            elif lang == "pt":
                # Algoritmo de Frank
                arbo_frank_v1, arbo_frank_v2, b1, b2 = andras_frank_algorithm(
                    D1_filtered, draw_fn=None, log=log, boilerplate=boilerplate, lang="pt"
                )    

            custo_frank = get_total_digraph_cost(arbo_frank_v1)
            custo_frank_v2 = get_total_digraph_cost(arbo_frank_v2)

                        # Verifying that both algorithms yield the same cost
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
                    log(f"\n Custo da arborescência de Andras Frank (v2): {custo_frank_v2}")
                    if draw_fn:
                        draw_fn(arbo_frank_v1, title="Arborescência de Andras Frank")
                        draw_fn(arbo_frank_v2, title="Arborescência de Andras Frank (v2)")
                    
                if lang == "en":
                    assert b1, "\n ❌ Dual condition failed for Andras Frank."
                    assert b2, "\n ❌ Dual condition failed for Andras Frank v2."
                elif lang == "pt":
                    assert b1, "\n ❌ Falha na condição dual para Andras Frank."
                    assert b2, "\n ❌ Falha na condição dual para Andras Frank v2."

                success = True
        
                if boilerplate and log:
                    if lang == "en":
                        log("\n✅ Tests completed successfully! Both algorithms returned arborescences with the same minimum cost.")
                    elif lang == "pt":
                        log("\n✅ Testes concluídos com sucesso! Ambos algoritmos retornaram arborescências com o mesmo custo mínimo.")

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
                    draw_fn(D1_filtered)

        except Exception as e:
            erro = str(e)
            log_console_and_file(f"❌ Erro: {erro}")
            print(e)
            traceback.print_exc(file=open(LOG_TXT_PATH, "a"))

        elapsed = round(time.time() - start_time, 4)

        # Update counters
        if success:
            success_count += 1
        else:
            failure_count += 1
            if custo1 > custo2:
                chuliu_greater_than_frank += 1
            else:
                frank_greater_than_chuliu += 1

        # Write to CSV
        with open(LOG_CSV_PATH, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    i,
                    n,
                    m,
                    custo1,
                    custo2,
                    custo3,
                    "OK" if success else "FAIL",
                    erro,
                    elapsed,
                    b1,
                    b2,
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
    lang="pt"
)