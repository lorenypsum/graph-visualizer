import csv
import os
import random
import time
import traceback

import networkx as nx

from andrasfrank import andras_frank_algorithm
from chuliu import find_optimum_arborescence_chuliu, remove_edges_to_r0


def logger(message: str):
    print(f"[LOG] {message}")


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


def remove_edges_to_r0(D, r0):
    """
    Remove all incoming edges to the root node r0 in the directed graph D.
    """
    incoming_edges = list(D.in_edges(r0))
    D.remove_edges_from(incoming_edges)
    return D


def contains_arborescence(D, r0):
    """
    Check if G contains an arborescence with root r0.
    """
    tree = nx.dfs_tree(D, source=r0)
    return tree.number_of_nodes() == D.number_of_nodes(), tree


def get_total_digraph_cost(D_arborescencia):
    """
    Calculate the total cost of a directed graph.
    """
    return sum(data["w"] for _, _, data in D_arborescencia.edges(data=True))


# def testar_algoritmos_arborescencia(draw_fn=None, log=None, boilerplate: bool = True):

#     D1 = build_rooted_digraph(10, 20, "r0", 1, 10)
#     r0 = "r0"

#     contains_arborescence_result, tree_result = contains_arborescence(D1, r0)

#     if contains_arborescence_result:
#         if boilerplate:
#             if log:
#                 log(
#                     f"\n✅ O grafo contém uma arborescência com raiz {r0}. Iniciando os testes..."
#                 )
#             if draw_fn:
#                 draw_fn(tree_result)

#         D1_sem_entradas = remove_edges_to_r0(D1.copy(), r0)
#         arborescencia_chuliu = find_optimum_arborescence_chuliu(
#             D1_sem_entradas,
#             r0,
#             level=0,
#             draw_fn=None,
#             log=log,
#             boilerplate=boilerplate,
#         )

#         custo_chuliu = get_total_digraph_cost(arborescencia_chuliu)

#         if boilerplate:
#             if log:
#                 log("\n🔍 Executando algoritmo de Chu-Liu/Edmonds...")
#                 log(f"Custo da arborescência de Chu-Liu/Edmonds: {custo_chuliu}")
#             if draw_fn:
#                 draw_fn(arborescencia_chuliu)

#         arborescencia_frank, arborescencia_frank_v2, b1, b2 = andras_frank_algorithm(
#             D1.copy(), draw_fn=None, log=log, boilerplate=boilerplate
#         )
#         custo_frank = get_total_digraph_cost(arborescencia_frank)
#         custo_frank_v2 = get_total_digraph_cost(arborescencia_frank_v2)

#         if boilerplate:
#             if log:
#                 log(f"Custo da arborescência de András Frank: {custo_frank}")
#                 log(f"Custo da arborescência de András Frank (v2): {custo_frank_v2}")

#         # Verifying that both algorithms yield the same cost
#         assert (
#             custo_chuliu == custo_frank
#         ), f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank: {custo_frank}"

#         assert (
#             custo_chuliu == custo_frank_v2
#         ), f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank v2: {custo_frank_v2}"

#         assert b1, "❌ Condição dual falhou para András Frank."
#         assert b2, "❌ Condição dual falhou para András Frank v2."

#         if boilerplate:
#             if log:
#                 log("\n ✅ Testes concluídos com sucesso!")
#                 log(
#                     "\n Sucesso! Ambos algoritmos retornaram arborescências com o mesmo custo mínimo."
#                 )
#     else:
#         if boilerplate:
#             if log:
#                 log(
#                     "\n O grafo não contém uma arborescência com raiz r0. Teste abortado."
#                 )
#             if draw_fn:
#                 draw_fn(D1)


# # Exemplo de uso:
# testar_algoritmos_arborescencia(log=logger, boilerplate=True)

# Parâmetros gerais
NUM_TESTS = 2000
MIN_VERTICES = 100
MAX_VERTICES = 200
PESO_MIN = 1
PESO_MAX = 20
LOG_CSV_PATH = "test_results.csv"
LOG_TXT_PATH = "test_log.txt"
ROOT = "r0"


def log_console_and_file(msg, log_txt_path=LOG_TXT_PATH):
    print(msg)
    with open(log_txt_path, "a") as f:
        f.write(msg + "\n")

def volume_tester(
    num_tests,
    min_vertices,
    max_vertices,
    root,
    peso_min,
    peso_max,
    log_csv_path,
    log_txt_path,
    draw_fn=None,
    log=None,
    boilerplate=True,
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

    for i in range(1, NUM_TESTS + 1):
        n = random.randint(MIN_VERTICES, MAX_VERTICES)
        m = random.randint(n, 3 * n)

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
            # Remover arestas que entram em ROOT para uniformizar a entrada

            if contains_arborescence_result:
                if boilerplate:
                    if log:
                        log(
                            f"\n✅ O grafo original contém uma arborescência com raiz {root}. Iniciando os testes..."
                        )
                    if draw_fn:
                        draw_fn(tree_result)

            D1_filtered = remove_edges_to_r0(D1_copy, root)

            # Algoritmo de Chu-Liu/Edmonds
            arbo_chuliu = find_optimum_arborescence_chuliu(D1_filtered, root)
            custo_chuliu = get_total_digraph_cost(arbo_chuliu)
            
            if boilerplate:
                if log:
                    log("\n🔍 Executando algoritmo de Chu-Liu/Edmonds...")
                    log(f"Custo da arborescência de Chu-Liu/Edmonds: {custo_chuliu}")
                if draw_fn:
                    draw_fn(arbo_chuliu)

            # Algoritmo de Frank - Fase 1
            arbo_frank_v1, arbo_frank_v2, b1, b2 = andras_frank_algorithm(
                D1_filtered, draw_fn=None, log=log, boilerplate=boilerplate
            )

            custo_frank = get_total_digraph_cost(arbo_frank_v1)
            custo_frank_v2 = get_total_digraph_cost(arbo_frank_v2)

            # Verifying that both algorithms yield the same cost
            assert (
                custo_chuliu == custo_frank
            ), f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank: {custo_frank}"

            assert (
                custo_chuliu == custo_frank_v2
            ), f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank v2: {custo_frank_v2}"

            if boilerplate:
                if log:
                    log(f"Custo da arborescência de Chu-Liu/Edmonds: {custo_chuliu}")
                    log(f"Custo da arborescência de András Frank: {custo_frank}")
                    log(f"Custo da arborescência de András Frank (v2): {custo_frank_v2}")
                    

            assert b1, "❌ Condição dual falhou para András Frank."
            assert b2, "❌ Condição dual falhou para András Frank v2."

            success = True

            if boilerplate:
                if log:
                    log("\n ✅ Testes concluídos com sucesso!")
                    log(
                        "\n Sucesso! Ambos algoritmos retornaram arborescências com o mesmo custo mínimo."
                    )
            else:
                if boilerplate:
                    if log:
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

        # Atualiza contadores
        if success:
            success_count += 1
        else:
            failure_count += 1
            if custo1 > custo2:
                chuliu_greater_than_frank += 1
            else:
                frank_greater_than_chuliu += 1

        # Escreve no CSV
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


    if boilerplate:
        if log:
            log_console_and_file("\n=== Resumo dos Testes ===")
            log_console_and_file(f"Total de testes: {NUM_TESTS}")
            log_console_and_file(f"Testes bem-sucedidos: {success_count}")
            log_console_and_file(f"Testes com falha: {failure_count}")
            log_console_and_file(f"Custo ChuLiu > Frank: {chuliu_greater_than_frank}")
            log_console_and_file(f"Custo Frank > ChuLiu: {frank_greater_than_chuliu}")

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
)