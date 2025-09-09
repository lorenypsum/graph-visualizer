import networkx as nx

def normalize_incoming_edge_weights(G: nx.DiGraph, node: str):
    """
    Change the weights of incoming edges into the `node`
    by subtracting the minimum incoming weight from each in the Graph G.

    Parameters:
        - G: A directed graph (networkx.DiGraph)
        - node: The target node whose incoming edges will be adjusted

    Returns:
        - None (the graph G is modified in place)
    """

    assert node in G, f"change_edge_weight: O vértice '{node}' não existe no grafo."

    # Get the incoming edges of the node with their weights
    predecessors = list(G.in_edges(node, data="w"))

    if not predecessors:
        return

    # Calculate the minimum weight among the incoming edges
    yv = min((w for _, _, w in predecessors))

    # Subtract Yv from each incoming edge
    for u, _, _ in predecessors:
        G[u][node]["w"] -= yv


def get_Fstar(G: nx.DiGraph, r0: str):
    """
    Creates the set F_star from graph G and root r0.
    An returns a directed graph F_star.

    Parameters:
        - G: A directed graph (networkx.DiGraph)
        - r0: The root node

    Returns:
        - F_star: A directed graph (networkx.DiGraph) representing F*
    """

    assert r0 in G, f"get_Fstar: O vértice raiz '{r0}' não existe no grafo."

    # Create an empty directed graph for F_star
    F_star = nx.DiGraph()

    for v in G.nodes():
        if v != r0:
            in_edges = list(G.in_edges(v, data="w"))
            if not in_edges:
                continue  # No edges entering v
            u = next((u for u, _, w in in_edges if w == 0), None)
            if u:
                F_star.add_edge(u, v, w=0)
    return F_star


def find_cycle(F_star: nx.DiGraph):
    """
    Finds a directed cycle in the graph.
    Returns a subgraph containing the cycle, or None if there is none.

    Parameters:
        - F_star: A directed graph (networkx.DiGraph)

    Returns:
        - A directed graph (networkx.DiGraph) representing the cycle, or None if no cycle is found.
    """

    try:
        nodes_in_cycle = set()
        # Extract nodes involved in the cycle
        for u, v, _ in nx.find_cycle(F_star, orientation="original"):
            nodes_in_cycle.update([u, v])
        # Create a subgraph containing only the cycle
        return F_star.subgraph(nodes_in_cycle).copy()

    except nx.NetworkXNoCycle:
        return None


def contract_cycle(G: nx.DiGraph, C: nx.DiGraph, label: str):
    """
    Contract a cycle C in graph G, replacing it with a supernode labeled `label`.
    Returns the modified graph G' with the contracted cycle, the list of incoming edges (in_edge), and outgoing edges (out_edge).

    Parameters:
        - G: A directed graph (networkx.DiGraph)
        - C: A directed graph (networkx.DiGraph) representing the cycle to be contracted
        - label: The label for the new supernode

    Returns:
        - in_to_cycle: A dictionary mapping nodes outside the cycle to tuples (node_in_cycle, weight)
        - out_from_cycle: A dictionary mapping nodes outside the cycle to tuples (node_in_cycle, weight)
    """

    assert (
        label not in G
    ), f"contract_cycle: O rótulo '{label}' já existe como vértice em G."

    cycle_nodes: set[str] = set(C.nodes())

    # Stores the vertex u outside the cycle and the vertex v inside the cycle that receives the minimum weight edge
    in_to_cycle: dict[str, tuple[str, float]] = {}

    for u in G.nodes:
        if u not in cycle_nodes:
            # Find the minimum weight edge that u has to any vertex in C
            min_weight_edge_to_cycle = min(
                ((v, w) for _, v, w in G.out_edges(u, data="w") if v in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_to_cycle:
                in_to_cycle[u] = min_weight_edge_to_cycle

    for u, (v, w) in in_to_cycle.items():
        G.add_edge(u, label, w=w)

    # Stores the vertex v outside the cycle that receives the minimum weight edge from a vertex u inside the cycle
    out_from_cycle: dict[str, tuple[str, float]] = {}

    for v in G.nodes:
        if v not in cycle_nodes:
            # Find the minimum weight edge that v receives from any vertex in C
            min_weight_edge_from_cycle = min(
                ((u, w) for u, _, w in G.in_edges(v, data="w") if u in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_from_cycle:
                out_from_cycle[v] = min_weight_edge_from_cycle

    for v, (u, w) in out_from_cycle.items():
        G.add_edge(label, v, w=w)

    # Remove all nodes in the cycle from G
    G.remove_nodes_from(cycle_nodes)

    return in_to_cycle, out_from_cycle


def remove_edges_to_r0(G: nx.DiGraph, r0: str, log=None, boilerplate: bool = True):
    """
    Remove all edges entering the root vertex r0 in graph G.
    Returns the updated graph.

    Parameters:
        - G: A directed graph (networkx.DiGraph)
        - r0: The root node
        - logger: Optional logging function to log information

    Returns:
        - G: The updated directed graph (networkx.DiGraph) with edges to r0 removed
    """

    # Verify that r0 exists in G
    assert r0 in G, f"remove_edges_to_r0: O vértice raiz '{r0}' não existe no grafo."

    # Remove all edges entering r0
    in_edges = list(G.in_edges(r0))
    if not in_edges:
        if boilerplate:
            if log:
                log(f"Nenhuma aresta entrando em '{r0}' para remover.")
    else:
        G.remove_edges_from(in_edges)

    return G


def remove_internal_edge_to_cycle_entry(C: nx.DiGraph, v):
    """
    Remove the internal edge entering the entry vertex `v` from cycle C,
    since `v` now receives an external edge from the graph.

    Parameters:
        - C: subgraph of the cycle
        - external_entry_edge: tuple (u, v, w) — external edge connecting to the cycle

    Returns:
        - The modified cycle (with one less edge)
    """

    predecessor = next((u for u, _ in C.in_edges(v)), None)

    C.remove_edge(predecessor, v)


# Chu-Liu Algorithm
def find_optimum_arborescence(
    G: nx.DiGraph, r0: str, level=0, draw_fn=None, log=None, boilerplate: bool = True
):
    """
    Finds the optimum arborescence in a directed graph G with root r0 using the Chu-Liu/Edmonds algorithm.

    Parameters:
        - G: A directed graph (networkx.DiGraph)
        - r0: The root node
        - level: The current recursion level (used for logging and visualization)
        - draw_fn: Optional function to visualize the graph at each step
        - log: Optional logging function to log information

    Returns:
        - A directed graph (networkx.DiGraph) representing the optimum arborescence

    Raises:
        - AssertionError: If the root node r0 is not in the graph G
        - AssertionError: If no cycle is found in F_star when expected
        - AssertionError: If the contracted label already exists in the graph G
        - AssertionError: If no incoming edge is found for the contracted node in F_prime
        - AssertionError: If no vertex in the cycle is found to receive the incoming edge
        - AssertionError: If the contracted label is not found in F_prime
        - AssertionError: If vertices u or v are not found in the original graph G
    """

    indent = "  " * level

    if boilerplate:
        if log:
            log(f"{indent}Iniciando nível {level}")

    assert (
        r0 in G
    ), f"find_optimum_arborescence: O vértice raiz '{r0}' não está presente no grafo."

    G_arb = G.copy()

    if boilerplate:
        log(f"{indent}Removendo arestas que entram em '{r0}'")
        if draw_fn:
            draw_fn(G_arb, f"{indent}Após remoção de entradas")

    for v in G_arb.nodes:
        if v != r0:
            normalize_incoming_edge_weights(G_arb, v)

        if boilerplate:
            log(f"{indent}Normalizando pesos de arestas de entrada para '{v}'")
            if draw_fn:
                draw_fn(G_arb, f"{indent}Após ajuste de pesos")

    # Build F_star
    F_star = get_Fstar(G_arb, r0)

    if boilerplate:
        log(f"{indent}Construindo F_star")
        if draw_fn:
            draw_fn(F_star, f"{indent}F_star")

    if nx.is_arborescence(F_star):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = G[u][v]["w"]
        return F_star

    else:
        if boilerplate:
            log(f"{indent}F_star não é uma arborescência. Continuando...")

        C: nx.DiGraph = find_cycle(F_star)

        assert C, f"find_optimum_arborescence: Nenhum ciclo encontrado em F_star."

        contracted_label = f"n*{level}"
        in_to_cycle, out_from_cycle = contract_cycle(G_arb, C, contracted_label)

        # Recursive call
        F_prime = find_optimum_arborescence(
            G_arb, r0, level + 1, draw_fn=draw_fn, log=log
        )

        # Identify the vertex in the cycle that received the only incoming edge from the arborescence
        in_edge = next(iter(F_prime.in_edges(contracted_label, data="w")), None)

        assert (
            in_edge
        ), f"find_optimum_arborescence: Nenhuma aresta encontrada entrando no vértice '{contracted_label}'."
        u, _, _ = in_edge

        v, _ = in_to_cycle[u]

        assert (
            v is not None
        ), f"find_optimum_arborescence: Nenhum vértice do ciclo encontrado que recebeu a aresta de entrada de '{u}'."

        # Remove the internal edge entering vertex `v` from cycle C
        remove_internal_edge_to_cycle_entry(
            C, v
        )  # Note: w is coming from F_prime, not from G

        # Add the external edge entering the cycle (identified by in_edge), the weight will be corrected at the end using G
        F_prime.add_edge(u, v)
        if boilerplate:
            log(f"{indent}Adicionando aresta de entrada ao ciclo: ({u}, {v})")

        # Add the remaining edges of the modified cycle C
        for u_c, v_c in C.edges:
            F_prime.add_edge(u_c, v_c)
            if boilerplate:
                log(f"{indent}  Adicionando aresta do ciclo: ({u_c}, {v_c})")

        # Add the external edges leaving the cycle
        for _, z, _ in F_prime.out_edges(contracted_label, data=True):
            assert (
                z in out_from_cycle
            ), f"find_optimum_arborescence: Nenhuma aresta de saída encontrada para o vértice '{z}'."
            u_cycle, _ = out_from_cycle[z]
            F_prime.add_edge(u_cycle, z)
            if boilerplate:
                log(f"{indent}  Adicionando aresta externa de saída: ({u_cycle}, {z})")

        # Remove the contracted node
        assert (
            contracted_label in F_prime
        ), f"Vértice '{contracted_label}' não encontrado no grafo."
        F_prime.remove_node(contracted_label)
        if boilerplate:
            log(f"{indent}  Vértice contraído '{contracted_label}' removido.")

        # Update the edge weights with the original weights from G
        for u, v in F_prime.edges:
            assert (
                u in G and v in G
            ), f"find_optimum_arborescence: Vértice '{u}' ou '{v}' não encontrado no grafo original."
            F_prime[u][v]["w"] = G[u][v]["w"]

        if boilerplate:
            log("Arborescência final:", list(F_prime.edges))
            if draw_fn:
                draw_fn(F_prime, f"{indent}Arborescência final")

        return F_prime
