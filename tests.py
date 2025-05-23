import networkx as nx
import random
from chuliu import find_optimum_arborescence, remove_edges_to_r0
from andrasfrank import (
    phase1_find_minimum_arborescence,
    phase2_find_minimum_arborescence,
)

def criar_grafo_com_arborescencia(n=10, m=None, r0="r0", peso_min=1, peso_max=10):
    """
    Cria um grafo direcionado com n vértices, m arestas, e garante que há uma arborescência com raiz r0.
    """
    if m is None:
        m = 2 * n  # número de arestas default

    G = nx.DiGraph()
    G.add_node(r0)
    nodes = [f"v{i}" for i in range(n - 1)]
    all_nodes = [r0] + nodes

    # Garante conectividade da arborescência (cada nó tem exatamente um pai)
    for v in nodes:
        u = random.choice(all_nodes)
        while u == v or G.has_edge(u, v):
            u = random.choice(all_nodes)
        G.add_edge(u, v, w=random.randint(peso_min, peso_max))

    # Adiciona arestas extras aleatórias
    while G.number_of_edges() < m:
        u, v = random.sample(all_nodes, 2)
        if not G.has_edge(u, v) and u != v:
            G.add_edge(u, v, w=random.randint(peso_min, peso_max))

    return G

G1 = criar_grafo_com_arborescencia(10, 20, "r0", 1, 10)

# Imprime o grafo
print("Grafo G1:")
print(G1.edges(data=True))
