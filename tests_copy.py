import networkx as nx
import random
from chuliu import find_optimum_arborescence, remove_edges_to_r0
from andrasfrank import (
    phase1_find_minimum_arborescence,
    phase2_find_minimum_arborescence,
)

def assert_arborescence_equal(result, expected):
    assert nx.is_arborescence(result), "O resultado não é uma arborescência"
    assert set(result.nodes) == set(expected.nodes), "Os vértices não coincidem"
    assert set(result.edges) == set(expected.edges), "As arestas não coincidem"
    for u, v in expected.edges:
        assert result[u][v]["w"] == expected[u][v]["w"], f"Peso errado em ({u} → {v})"

# === TESTE ORIGINAL ===
def build_test_graph():
    G = nx.DiGraph()
    G.add_edge("r0", "A", w=2)
    G.add_edge("r0", "B", w=10)
    G.add_edge("r0", "C", w=10)
    G.add_edge("A", "C", w=4)
    G.add_edge("B", "A", w=1)
    G.add_edge("C", "D", w=2)
    G.add_edge("D", "B", w=2)
    G.add_edge("B", "E", w=8)
    G.add_edge("C", "E", w=4)
    return G


def build_expected_arborescence():
    T = nx.DiGraph()
    T.add_edge("r0", "A", w=2)
    T.add_edge("A", "C", w=4)
    T.add_edge("C", "D", w=2)
    T.add_edge("D", "B", w=2)
    T.add_edge("C", "E", w=4)
    return T


def test_arborescence_structure():
    G = build_test_graph()
    expected = build_expected_arborescence()
    G_filtered = remove_edges_to_r0(G, r0="r0")
    result_chuliu = find_optimum_arborescence(G_filtered, r0="r0")
    assert_arborescence_equal(result_chuliu, expected)


# === TESTE SEM CICLO ===
def test_case_2_no_cycles():
    G = nx.DiGraph()
    G.add_edge("r0", "A", w=3)
    G.add_edge("A", "B", w=2)
    G.add_edge("B", "C", w=1)
    G.add_edge("C", "D", w=4)

    expected = G.copy()
    G_filtered = remove_edges_to_r0(G, r0="r0")
    result_chuliu = find_optimum_arborescence(G_filtered, r0="r0")
    assert_arborescence_equal(result_chuliu, expected)


# === TESTE COM CICLOS DESCONEXOS ===
def test_case_3_multiple_cycles():
    G = nx.DiGraph()
    G.add_edge("r0", "A", w=1)
    G.add_edge("A", "B", w=2)
    G.add_edge("B", "A", w=2)  # ciclo 1

    G.add_edge("A", "C", w=3)
    G.add_edge("C", "D", w=4)
    G.add_edge("D", "C", w=1)  # ciclo 2

    expected = nx.DiGraph()
    expected.add_edge("r0", "A", w=1)
    expected.add_edge("B", "A", w=2)
    expected.add_edge("A", "C", w=3)
    expected.add_edge("D", "C", w=1)

    G_filtered = remove_edges_to_r0(G, r0="r0")
    result_chuliu = find_optimum_arborescence(G_filtered, r0="r0")
    assert_arborescence_equal(result_chuliu, expected)


# === TESTE MAIOR COM CICLO ENCADEADO ===
def test_case_4_large_graph_with_cycle():
    G = nx.DiGraph()
    edges = [
        ("r0", "A", 5),
        ("A", "B", 3),
        ("B", "C", 2),
        ("C", "A", 1),  # ciclo
        ("C", "D", 4),
        ("D", "E", 6),
        ("E", "F", 2),
        ("F", "G", 1),
        ("G", "H", 3),
        ("H", "E", 1),  # segundo ciclo
        ("B", "I", 5),
        ("I", "J", 2),
        ("J", "K", 1),
    ]
    for u, v, w in edges:
        G.add_edge(u, v, w=w)

    # Espera-se que o ciclo A→B→C→A e E→F→G→H→E sejam contraídos
    result_chuliu = find_optimum_arborescence(remove_edges_to_r0(G, "r0"), "r0")
    assert nx.is_arborescence(result_chuliu), "O resultado não é uma arborescência"
    assert "r0" in result_chuliu
    assert "K" in result_chuliu
    assert len(result_chuliu.nodes) == len(G.nodes)  # todos devem estar incluídos


# === TESTE COM PESOS ALEATÓRIOS ===
def generate_random_graph(n_nodes: int, edge_density: float = 0.3, seed=42):
    random.seed(seed)
    G = nx.DiGraph()
    nodes = [f"v{i}" for i in range(n_nodes)]
    root = "r0"
    G.add_node(root)
    G.add_nodes_from(nodes)

    for u in [root] + nodes:
        for v in nodes:
            if u != v and random.random() < edge_density:
                G.add_edge(u, v, w=random.randint(1, 20))
    return G


def test_random_graph_structure():
    G = generate_random_graph(10, edge_density=0.4)
    r0 = "r0"
    G_filtered = remove_edges_to_r0(G, r0)

    result_chuliu = find_optimum_arborescence(G_filtered, r0)

    assert nx.is_arborescence(result_chuliu), "O resultado não é uma arborescência"
    assert r0 in result_chuliu, "A raiz não está presente"
    assert len(result_chuliu.nodes) == len(
        G.nodes
    ), "Nem todos os vértices estão na arborescência"
    assert nx.is_weakly_connected(
        result_chuliu
    ), "A arborescência não conecta todos os nós"


def test_multiple_random_graphs():
    for i in range(5):  # Executa 5 grafos diferentes
        G = generate_random_graph(15, edge_density=0.2, seed=100 + i)
        r0 = "r0"
        G_filtered = remove_edges_to_r0(G, r0)

        result_chuliu = find_optimum_arborescence(G_filtered, r0)

        assert nx.is_arborescence(result_chuliu), f"[{i}] Resultado não é arborescência"
        assert r0 in result_chuliu, f"[{i}] Raiz ausente"
        assert len(result_chuliu.nodes) == len(
            G.nodes
        ), f"[{i}] Número de vértices incorreto"


# TODO: Encontrar repositório c/ Dígrafos maiores.
# TODO: Verificar se ambos os algoritmos estão retornando o mesmo resultado:
# Verificar se o custo total da arborescência das arborescências encontradas é o mesmo para ambos os algoritmos.


def calculate_arborescence_cost(arborescence: nx.DiGraph):
    """Calcula o custo total de uma arborescência."""
    total_cost = 0
    for u, v, data in arborescence.edges(data=True):
        total_cost += data.get("w", 0)  # Assume 'w' como atributo de peso
    return total_cost


def test_compare_algorithm_costs():
    """
    Testa se os algoritmos de Chu-Liu e Andras Frank encontram arborescências
    com o mesmo custo total.
    """
    # Usar um grafo um pouco maior para o teste
    G = generate_random_graph(15, edge_density=0.3, seed=2024)
    r0 = "r0"

    # Executar Algoritmo de Chu-Liu/Edmonds
    G_chuliu = G.copy()  # Criar cópia para não modificar o original
    G_chuliu_filtered = remove_edges_to_r0(G_chuliu, r0)
    arborescence_chuliu = find_optimum_arborescence(G_chuliu_filtered, r0)
    cost_chuliu = calculate_arborescence_cost(arborescence_chuliu)

    # Executar Algoritmo de Andras Frank
    G_andras = G.copy()  # Criar cópia para não modificar o original
    # O algoritmo de Andras Frank não requer a remoção de arestas para r0 explicitamente antes
    # A_zero_frank = phase1_find_minimum_arborescence(G_andras, r0)
    # arborescence_andras_frank = phase2_find_minimum_arborescence(G_andras, r0, A_zero_frank)

    # Corrigindo a chamada para o algoritmo de Andras Frank conforme a estrutura em andrasfrank.py
    # Primeiro, a fase 1 para obter A_zero
    A_zero_frank = phase1_find_minimum_arborescence(G_andras, r0)
    # Depois, a fase 2 para construir a arborescência
    arborescence_andras_frank = phase2_find_minimum_arborescence(
        G_andras, r0, A_zero_frank
    )
    cost_andras_frank = calculate_arborescence_cost(arborescence_andras_frank)

    assert nx.is_arborescence(
        arborescence_chuliu
    ), "Resultado de Chu-Liu não é uma arborescência."
    assert nx.is_arborescence(
        arborescence_andras_frank
    ), "Resultado de Andras Frank não é uma arborescência."

    print(f"Custo Chu-Liu: {cost_chuliu}")
    print(f"Custo Andras Frank: {cost_andras_frank}")

    # Verificar se os custos são iguais
    assert cost_chuliu == cost_andras_frank, (
        f"Os custos das arborescências são diferentes. "
        f"Chu-Liu: {cost_chuliu}, Andras Frank: {cost_andras_frank}"
    )

    # Opcional: Verificar se as estruturas das arborescências são as mesmas (pode não ser sempre o caso se houver múltiplas arborescências ótimas)
    # No entanto, para este teste, focamos apenas no custo.
    # Se os custos forem iguais, mas as arestas diferentes, ainda é um resultado válido se ambas forem arborescências ótimas.
