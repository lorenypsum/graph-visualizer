import networkx as nx
from chuliu import find_optimum_arborescence, remove_edge_in_r0

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

    G_filtered = remove_edge_in_r0(G, r0="r0")
    result = find_optimum_arborescence(G_filtered, r0="r0")

    assert nx.is_arborescence(result), "O resultado não é uma arborescência"
    assert nx.is_isomorphic(result, expected), "A estrutura não é isomorfa à esperada"
    assert set(result.nodes) == set(expected.nodes), "Os vértices não coincidem"
    assert set(result.edges) == set(expected.edges), "As arestas não coincidem"

    for u, v in expected.edges:
        assert result[u][v]["w"] == expected[u][v]["w"], f"Peso errado em ({u} → {v})"
