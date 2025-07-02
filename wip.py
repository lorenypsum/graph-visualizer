import networkx as nx

print("Hello, I am Chu Liu TESTES.")

# Funções auxiliar para alterar peso das arestas
def change_edge_weight(G: nx.DiGraph, node: str):

    """
    Altera o peso das arestas de entrada de um nó `node` no grafo `G`.
    """

    assert node in G, f"change_edge_weight: O vértice '{node}' não existe no grafo."

    # Obtém predecessores com pesos
    predecessors = list(G.in_edges(node, data="w"))

    if not predecessors:
        return

    # Calcula Yv = menor peso de entrada
    yv = min((w for _, _, w in predecessors))

    # Subtrai Yv de cada aresta de entrada
    for u, _, _ in predecessors:
        G[u][node]["w"] -= yv

# Função auxiliar para definir conjunto F_star
def get_Fstar(G: nx.DiGraph, r0: str):

    """
    Cria o conjunto F_star a partir do grafo G e da raiz r0.
    """

    assert r0 in G, f"get_Fstar: O vértice raiz '{r0}' não existe no grafo."

    F_star = nx.DiGraph()

    for v in G.nodes():
        if v != r0: 
            in_edges = list(G.in_edges(v, data="w"))
            if not in_edges:
                continue  # Nenhuma aresta entra em v
            u = next((u for u, _, w in in_edges if w == 0), None)
            if u:
                F_star.add_edge(u, v, w=0)

    return F_star

# Função auxiliar para encontrar um ciclo no grafo
def find_cycle(F_star: nx.DiGraph):

    """
    Encontra um ciclo direcionado / circuito no grafo.
    Retorna um subgrafo contendo o ciclo, ou None se não houver.
    """
    
    # Tenta encontrar um ciclo no grafo
    nodes_in_cycle = set()
    for u, v, _ in nx.find_cycle(F_star, orientation="original"):
        nodes_in_cycle.update([u, v])

    # Retorna o subgrafo contendo apenas o ciclo
    return F_star.subgraph(nodes_in_cycle)


DH = nx.DiGraph()

DH.add_edge("r0", "A", w = 10)
DH.add_edge("A", "B", w = 1)
DH.add_edge("A", "C", w = 3)
DH.add_edge("B", "C", w = 0)
DH.add_edge("C", "D", w = 0)
DH.add_edge("D", "B", w = 0)
DH.add_edge("D", "E", w = 5)
DH.add_edge("B", "F", w = 3)
DH.add_edge("D", "F", w = 2)

C = find_cycle(DH)

print("Ciclo encontrado:", C.edges(data=True))

# Função auxiliar para contrair um ciclo
def contract_cycle(G: nx.DiGraph, C: nx.DiGraph, label: str):

    """
    Contrai um ciclo C no grafo G, substituindo-o por um supervértice com rótulo `label`.
    Devolve o grafo G modificado "G'"com o ciclo contraído, a lista das arestas de entrada (in_edge) e as de saída (out_edge).
    """

    assert label not in G, f"contract_cycle: O rótulo '{label}' já existe como vértice em G."
    
    cycle_nodes: set[str] = set(C.nodes())
    
    # Armazena o vértice u fora do ciclo e o vértice v dentro do ciclo que recebe a aresta de menor peso
    in_to_cycle: dict[str, tuple[str, float]] = {}

    for u in G.nodes:
        if u not in cycle_nodes: 
            # Encontra a aresta de menor peso de u para algum vértice em C
            min_weight_edge_to_cycle = min(
                ((v, w) for _, v, w in G.out_edges(u, data="w") if v in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_to_cycle:
                in_to_cycle[u] = min_weight_edge_to_cycle

    for u, (v, w) in in_to_cycle.items():
        G.add_edge(u, label, w=w)

    # Armazena o vértice v fora do ciclo que recebe a aresta de menor peso de um vértice u dentro do ciclo
    out_from_cycle: dict[str, tuple[str, float]] = {}

    for v in G.nodes:
        if v not in cycle_nodes: 
            # Encontra a aresta de menor peso que v recebe de algum vértice em C
            min_weight_edge_from_cycle = min(
                ((u, w) for u, _, w in G.in_edges(v, data="w") if u in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_from_cycle:
                out_from_cycle[v] = min_weight_edge_from_cycle

    for v, (u, w) in out_from_cycle.items():
        G.add_edge(label, v, w=w)      
    
    # Remove os nós do ciclo original
    G.remove_nodes_from(cycle_nodes)

    return in_to_cycle, out_from_cycle

in_to_cycle, out_from_cycle = contract_cycle(DH, C, "superv")

print("Arestas de entrada para o ciclo contraído:", in_to_cycle)
print("Arestas de saída do ciclo contraído:", out_from_cycle)


# Função auxiliar para remover aresta de um ciclo
def remove_internal_edge_to_cycle_entry(C: nx.DiGraph, external_entry_edge: tuple):

    """
    Remove do ciclo C a aresta interna que entra no vértice de entrada `v`,
    pois `v` agora já recebe uma aresta externa do grafo.
    
    Parâmetros:
    - C: subgrafo do ciclo
    - external_entry_edge: tupla (u, v, w) — aresta externa que conecta o ciclo
    
    Retorna:
    - O ciclo modificado (com uma aresta a menos)
    """

    if not external_entry_edge:
        return C

    _, v, _ = external_entry_edge

    assert v in C, f"O vértice '{v}' da aresta de entrada não está presente no ciclo."

    # Procura uma aresta interna no ciclo que também entra em v
    predecessor = next((u for u, _ in C.in_edges(v)), None)
    if predecessor:
        C.remove_edge(predecessor, v)

    return C

remove_internal_edge_to_cycle_entry(C, ("superv", "A", 10))