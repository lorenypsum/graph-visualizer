import networkx as nx
import random
from chuliu import find_optimum_arborescence, remove_edges_to_r0
from andrasfrank import phase1_find_minimum_arborescence, phase2_find_minimum_arborescence, phase2_find_minimum_arborescence_v2

def build_rooted_digraph(n=10, m=None, r0="r0", peso_min=1, peso_max=10):
    """
    Cria um grafo direcionado com n vértices, m arestas.
    """
    if m is None:
        m = 2 * n  # número de arestas default

    D = nx.DiGraph()
    D.add_node(r0)
    nodes = [f"v{i}" for i in range(n - 1)]
    all_nodes = [r0] + nodes

    # Conecta o vértice raiz a todos os outros vértices
    reached = {r0}
    remaining = set(nodes)

    while remaining:
        v = remaining.pop()
        u = random.choice(list(reached))
        D.add_edge(u, v, w=random.randint(peso_min, peso_max))
        reached.add(v)

    # Adiciona arestas extras aleatórias
    while D.number_of_edges() < m:
        u, v = random.sample(all_nodes, 2)
        if not D.has_edge(u, v) and u != v:
            D.add_edge(u, v, w=random.randint(peso_min, peso_max))

    return D

D1 = build_rooted_digraph(10, 20, "r0", 1, 10)

def remove_edges_to_r0(D, r0):
    """
    Remove todas as arestas que entram na raiz r0.
    """
    incoming_edges = list(D.in_edges(r0))
    D.remove_edges_from(incoming_edges)
    return D

def contains_arborescence(D, r0):
    """
    Verifica se G contém uma arborescência com raiz r0.
    """
    tree = nx.dfs_tree(D, source=r0)
    return tree.number_of_nodes() == D.number_of_nodes()

def get_total_digraph_cost(D_arborescencia):
    """
    Calcula o custo total de um grafo dirigido.
    """
    return sum(data["w"] for _, _, data in D_arborescencia.edges(data=True))

# Executa os testes se o grafo contiver uma arborescência
if contains_arborescence(D1, "r0"):
    print("\n🔍 Executando algoritmo de Chu-Liu/Edmonds...")
    D1_sem_entradas = remove_edges_to_r0(D1.copy(), "r0")
    arborescencia_chuliu = find_optimum_arborescence(D1_sem_entradas, "r0")
    custo_chuliu = get_total_digraph_cost(arborescencia_chuliu)
    print(f"Custo da arborescência de Chu-Liu/Edmonds: {custo_chuliu}")

    print("\n🔍 Executando algoritmo de András Frank...")
    A_zero = phase1_find_minimum_arborescence(D1.copy(), "r0")
    arborescencia_frank = phase2_find_minimum_arborescence(D1.copy(),"r0", A_zero)
    arborescencia_frank_v2 = phase2_find_minimum_arborescence_v2(D1.copy(), "r0", A_zero)
    custo_frank = get_total_digraph_cost(arborescencia_frank)
    custo_frank_v2 = get_total_digraph_cost(arborescencia_frank_v2)
    print(f"Custo da arborescência de András Frank: {custo_frank}")
    print(f"Custo da arborescência de András Frank (v2): {custo_frank_v2}")

    # Verificação final
    assert custo_chuliu == custo_frank, f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank: {custo_frank}"
    assert custo_chuliu == custo_frank_v2, f"❌ Custos diferentes! Chu-Liu: {custo_chuliu}, Frank v2: {custo_frank_v2}"
    print("\n ✅ Testes concluídos com sucesso!")
    print("\n Sucesso! Ambos algoritmos retornaram arborescências com o mesmo custo mínimo.")
else:
    print("\n O grafo não contém uma arborescência com raiz r0. Teste abortado.")

# TODO: Implementar testagem em quantidade automaticamente. (Família robusta de testes).      