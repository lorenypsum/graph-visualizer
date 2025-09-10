import random

import networkx as nx

from andrasfrank import andras_frank_algorithm
from chuliu import find_optimum_arborescence_chuliu, remove_edges_to_r0

def logger(message: str):
    print(f"[LOG] {message}")

def build_rooted_digraph(n=10, m=None, r0="r0", peso_min=1, peso_max=10):
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
    D.add_node(r0)
    nodes = [f"v{i}" for i in range(n - 1)]
    all_nodes = [r0] + nodes

    # Connect the root to at least one other node to ensure connectivity
    reached = {r0}
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


def testar_algoritmos_arborescencia(draw_fn=None, log=None, boilerplate: bool = True):

    D1 = build_rooted_digraph(10, 20, "r0", 1, 10)
    r0 = "r0"

    contains_arborescence_result, tree_result = contains_arborescence(D1, r0)

    if contains_arborescence_result:
        if boilerplate:
            if log:
                log(
                    f"\n✅ O grafo contém uma arborescência com raiz {r0}. Iniciando os testes..."
                )
            if draw_fn:
                draw_fn(tree_result)

        D1_sem_entradas = remove_edges_to_r0(D1.copy(), r0)
        arborescencia_chuliu = find_optimum_arborescence_chuliu(
            D1_sem_entradas,
            r0,
            level=0,
            draw_fn=None,
            log=log,
            boilerplate=boilerplate,
        )

        custo_chuliu = get_total_digraph_cost(arborescencia_chuliu)

        if boilerplate:
            if log:
                log("\n🔍 Executando algoritmo de Chu-Liu/Edmonds...")
                log(f"Custo da arborescência de Chu-Liu/Edmonds: {custo_chuliu}")
            if draw_fn:
                draw_fn(arborescencia_chuliu)

        arborescencia_frank, arborescencia_frank_v2, b1, b2 = andras_frank_algorithm(
            D1.copy(), draw_fn=None, log=log, boilerplate=boilerplate
        )
        custo_frank = get_total_digraph_cost(arborescencia_frank)
        custo_frank_v2 = get_total_digraph_cost(arborescencia_frank_v2)

        if boilerplate:
            if log:
                log(f"Custo da arborescência de András Frank: {custo_frank}")
                log(f"Custo da arborescência de András Frank (v2): {custo_frank_v2}")

        # Verifying that both algorithms yield the same cost
        assert (
            custo_chuliu == custo_frank
        ), f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank: {custo_frank}"

        assert (
            custo_chuliu == custo_frank_v2
        ), f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank v2: {custo_frank_v2}"

        assert b1, "❌ Condição dual falhou para András Frank."
        assert b2, "❌ Condição dual falhou para András Frank v2."

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
                draw_fn(D1)


# Exemplo de uso:
testar_algoritmos_arborescencia(log=logger, boilerplate=True)
