import networkx as nx
from typing import Optional, cast


# Remove todas as arestas que entram no vértice raiz r0 em G
def remove_in_edges_to(
    D: nx.DiGraph, r: int, log=None, boilerplate: bool = True, lang="pt"
):
    """
    Remove all edges entering the root vertex r in graph G.
    Returns the updated graph.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r: The root node
        - log: Optional logging function to log information
        - boilerplate: If True, enables logging
        - lang: Language for logging messages ("en" for English, "pt" for Portuguese

    Returns:
        - D: The updated directed graph (networkx.DiGraph) with edges to r0 removed
    """

    # Remove all edges entering r0
    in_edges = list(D.in_edges(r))
    D.remove_edges_from(in_edges)


# Normalização dos pesos das arestas que entram em um vértice
def reduce_costs(D: nx.DiGraph, v: str, lang="pt"):
    """
    Change the costs of incoming edges into the `v`
    by subtracting the minimum incoming weight from each in the Graph G.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - v: The target v whose incoming edges will be adjusted
        - lang: Language for error messages ("en" for English, "pt" for Portuguese)

    Returns:
        - Nothing (the graph G is modified in place)
    """
    in_edges = D.in_edges(v, data=True)

    # Calculate the minimum weight among the incoming edges
    yv = min((data.get("w", 0) for _, _, data in in_edges))

    # Subtract Yv from each incoming edge
    for u, _, _ in in_edges:
        D[u][v]["w"] -= yv


# Cria o conjunto A0
def get_Azero(D: nx.DiGraph, r0: str, lang="pt"):
    """
    Creates the set A_zero from graph G and root r0.
    An returns a directed graph A_zero.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r0: The rootve
        - lang: Language for error messages ("en" for English, "pt" for Portuguese)

    Returns:
        - A_zero: A directed graph (networkx.DiGraph) representing F*
    """

    # Create an empty directed graph for A_zero
    A_zero = nx.DiGraph()

    for v in D.nodes():
        if v != r0:
            in_edges = D.in_edges(v, data=True)
            u = next((u for u, _, data in in_edges if data.get("w") == 0))
            A_zero.add_edge(u, v, w=0)
    return A_zero


# Encontra um circuito (ciclo dirigido) em G
def find_cycle(A_zero: nx.DiGraph):
    """
    Finds a directed cycle in the graph.
    Returns a subgraph containing the cycle, or None if there is none.

    Parameters:
        - A_zero: A directed graph (networkx.DiGraph)

    Returns:
        - A directed graph (networkx.DiGraph) representing the cycle, or None if no cycle is found.
    """

    nodes_in_cycle = set()
    # Extract nodes involved in the cycle
    for u, v, _ in nx.find_cycle(A_zero, orientation="original"):
        nodes_in_cycle.update([u, v])
    # Create a subgraph containing only the cycle
    return A_zero.subgraph(nodes_in_cycle).copy()


# Contrai um ciclo C em G, substituindo-o por um supernó rotulado pelo `label`
def contract_cycle(D: nx.DiGraph, C: nx.DiGraph, label: str, lang="pt"):
    """
    Contract a cycle C in graph G, replacing it with a supernode labeled `label`.
    Returns the modified graph G' with the contracted cycle, the list of incoming edges (in_edge), and outgoing edges (out_edge).

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - C: A directed graph (networkx.DiGraph) representing the cycle to be contracted
        - label: The label for the new supernode
        - lang: Language for error messages ("en" for English, "pt" for Portuguese)

    Returns:
        - in_to_cycle: A dictionary mapping nodes outside the cycle to tuples (node_in_cycle, weight)
        - out_from_cycle: A dictionary mapping nodes outside the cycle to tuples (node_in_cycle, weight)
    """

    cycle_nodes: set[str] = set(C.nodes())

    # Stores the vertex u outside the cycle and the vertex v inside the cycle that receives the minimum weight edge
    in_to_cycle: dict[str, tuple[str, float]] = {}

    for u in D.nodes:
        if u not in cycle_nodes:
            # Find the minimum weight edge that u has to any vertex in C
            min_weight_edge_to_cycle = min(
                (
                    (v, data.get("w", float("inf")))
                    for _, v, data in D.out_edges(u, data=True)
                    if v in cycle_nodes
                ),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_to_cycle:
                in_to_cycle[u] = min_weight_edge_to_cycle

    for u, (v, w) in in_to_cycle.items():
        D.add_edge(u, label, w=w)

    # Stores the vertex v outside the cycle that receives the minimum weight edge from a vertex u inside the cycle
    out_from_cycle: dict[str, tuple[str, float]] = {}

    for v in D.nodes:
        if v not in cycle_nodes:
            # Find the minimum weight edge that v receives from any vertex in C
            min_weight_edge_from_cycle = min(
                (
                    (u2, data.get("w", float("inf")))
                    for u2, _, data in D.in_edges(v, data=True)
                    if u2 in cycle_nodes
                ),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_from_cycle:
                out_from_cycle[v] = min_weight_edge_from_cycle

    for v, (u, w) in out_from_cycle.items():
        D.add_edge(label, v, w=w)

    # Remove all nodes in the cycle from G
    D.remove_nodes_from(cycle_nodes)
    return in_to_cycle, out_from_cycle


# Remove a aresta interna que entra no vértice de entrada do ciclo
def remove_edge_cycle(C: nx.DiGraph, v):
    """
    Remove the internal edge entering the entry vertex `v` from cycle C,
    since `v` now receives an external edge from the graph.

    Parameters:
        - C: subgraph of the cycle
        - external_entry_edge: tuple (u, v, w) — external edge connecting to the cycle

    Returns:
        - The modified cycle (with one less edge)
    """

    predecessor = next((u for u, _ in C.in_edges(v)))
    C.remove_edge(predecessor, v)


# Encontra a arborescência ótima em G com raiz r0 usando o algoritmo de Chu-Liu/Edmonds
def chuliu_edmonds(
    D: nx.DiGraph,
    r0: str,
    level=0,
    draw_fn=None,
    log=None,
    boilerplate: bool = True,
    lang="pt",
    metrics: dict | None = None,
):
    """
    Finds the optimum arborescence in a directed graph G with root r0 using the Chu-Liu/Edmonds algorithm.
    """

    indent = "  " * level

    # Initialize metrics if provided
    if metrics is not None:
        metrics.setdefault("contractions", 0)
        metrics.setdefault("max_depth", 0)
        if level > metrics["max_depth"]:
            metrics["max_depth"] = level

    if boilerplate and log:
        if lang == "en":
            log(f"\nchuliu_edmonds:{indent}Starting level {level}")
        elif lang == "pt":
            log(f"\nchuliu_edmonds:{indent}Iniciando nível {level}")

    if lang == "en":
        assert r0 in D, (
            "\nchuliu_edmonds: The root vertex '"
            + r0
            + "' is not present in the graph."
        )
    elif lang == "pt":
        assert r0 in D, (
            "\nchuliu_edmonds: O vértice raiz '" + r0 + "' não está presente no grafo."
        )

    D_copy = cast(nx.DiGraph, D.copy())

    if boilerplate and log:
        if lang == "en":
            log(f"\nchuliu_edmonds:{indent}Removing edges entering '{r0}'")
        elif lang == "pt":
            log(f"\nchuliu_edmonds:{indent}Removendo arestas que entram em '{r0}'")
        if draw_fn:
            if lang == "en":
                draw_fn(
                    D_copy,
                    f"\nchuliu_edmonds:{indent}After removing incoming edges",
                )
            elif lang == "pt":
                draw_fn(
                    D_copy,
                    f"\nchuliu_edmonds:{indent}Após remoção de entradas",
                )

    for v in D_copy.nodes:
        if v != r0:
            reduce_costs(D_copy, v, lang=lang)

        if boilerplate and log:
            if lang == "en":
                log(
                    f"\nchuliu_edmonds:{indent}Normalizing weights of incoming edges to '{v}'"
                )
            elif lang == "pt":
                log(
                    f"\nchuliu_edmonds:{indent}Normalizando pesos de arestas de entrada para '{v}'"
                )
            if draw_fn:
                if lang == "en":
                    draw_fn(
                        D_copy,
                        f"\nchuliu_edmonds:{indent}After weight adjustment",
                    )
                elif lang == "pt":
                    draw_fn(
                        D_copy,
                        f"\nchuliu_edmonds:{indent}Após ajuste de pesos",
                    )

    # Build A_zero
    A_zero = get_Azero(D_copy, r0, lang=lang)

    if boilerplate and log:
        if lang == "en":
            log(f"\nchuliu_edmonds:{indent}Building A_zero")
        elif lang == "pt":
            log(f"\nchuliu_edmonds:{indent}Construindo A_zero")
        if draw_fn:
            if lang == "en":
                draw_fn(A_zero, f"\nchuliu_edmonds:{indent}A_zero")
            elif lang == "pt":
                draw_fn(A_zero, f"\nchuliu_edmonds:{indent}A_zero")

    if nx.is_arborescence(A_zero):
        for u, v in A_zero.edges:
            A_zero[u][v]["w"] = D[u][v]["w"]
        return A_zero

    # Otherwise, contract a cycle and recurse
    if boilerplate and log:
        if lang == "en":
            log(
                f"\nchuliu_edmonds:{indent}A_zero is not an arborescence. Continuing..."
            )
        elif lang == "pt":
            log(
                f"\nchuliu_edmonds:{indent}A_zero não é uma arborescência. Continuando..."
            )

    C = find_cycle(A_zero)

    cl = f"\n n*{level}"  # contracted label
    if metrics is not None:
        metrics["contractions"] += 1
    in_to_cycle, out_from_cycle = contract_cycle(D_copy, C, cl, lang=lang)

    # Recursive call
    F_prime = chuliu_edmonds(
        D_copy,
        r0,
        level + 1,
        draw_fn=None,
        log=None,
        boilerplate=boilerplate,
        lang=lang,
        metrics=metrics,
    )

    in_edge = next(iter(F_prime.in_edges(cl, data=True)))

    if lang == "en":
        assert (
            in_edge is not None
        ), f"\nchuliu_edmonds: No incoming edge found for vertex '{cl}'."
    elif lang == "pt":
        assert (
            in_edge is not None
        ), f"\nchuliu_edmonds: Nenhuma aresta encontrada entrando no vértice '{cl}'."

    # At this point in_edge is guaranteed not None
    u, _, _ = cast(tuple, in_edge)
    v, _ = in_to_cycle[u]

    if lang == "en":
        assert (
            v is not None
        ), f"\nchuliu_edmonds: No vertex in the cycle found to receive the incoming edge from '{u}'."
    elif lang == "pt":
        assert (
            v is not None
        ), f"\nchuliu_edmonds: Nenhum vértice do ciclo encontrado que recebeu a aresta de entrada de '{u}'."

    # Remove the internal edge entering vertex `v` from cycle C
    remove_edge_cycle(C, v)

    # Add the external edge entering the cycle and restore remaining cycle edges
    F_prime.add_edge(u, v)
    if boilerplate and log:
        if lang == "en":
            log(f"\nchuliu_edmonds:{indent}Adding incoming edge to cycle: ({u}, {v})")
        elif lang == "pt":
            log(
                f"\nchuliu_edmonds:{indent}Adicionando aresta de entrada ao ciclo: ({u}, {v})"
            )

    for u_c, v_c in C.edges:
        F_prime.add_edge(u_c, v_c)
        if boilerplate and log:
            if lang == "en":
                log(f"\nchuliu_edmonds:{indent}Adding cycle edge: ({u_c}, {v_c})")
            elif lang == "pt":
                log(
                    f"\nchuliu_edmonds:{indent}Adicionando aresta do ciclo: ({u_c}, {v_c})"
                )

    # Add the external edges leaving the cycle
    for _, z, _ in F_prime.out_edges(cl, data=True):
        if lang == "en":
            assert (
                z in out_from_cycle
            ), f"\nchuliu_edmonds: No outgoing edge found for vertex '{z}'."
        elif lang == "pt":
            assert (
                z in out_from_cycle
            ), f"\nchuliu_edmonds: Nenhuma aresta de saída encontrada para o vértice '{z}'."
        u_cycle, _ = out_from_cycle[z]
        F_prime.add_edge(u_cycle, z)
        if boilerplate and log:
            if lang == "en":
                log(
                    f"\nchuliu_edmonds:{indent}Adding outgoing edge from cycle: ({u_cycle}, {z})"
                )
            elif lang == "pt":
                log(
                    f"\nchuliu_edmonds:{indent}Adicionando aresta externa de saída: ({u_cycle}, {z})"
                )

    # Remove the contracted node
    if lang == "en":
        assert cl in F_prime, f"\nchuliu_edmonds: Vertex '{cl}' not found in the graph."
    elif lang == "pt":
        assert (
            cl in F_prime
        ), f"\nchuliu_edmonds: Vértice '{cl}' não encontrado no grafo."
    F_prime.remove_node(cl)

    if boilerplate and log:
        if lang == "en":
            log(f"\nchuliu_edmonds:{indent}Contracted vertex '{cl}' removed.")
        elif lang == "pt":
            log(f"\nchuliu_edmonds:{indent}Vértice contraído '{cl}' removido.")

    # Update the edge weights with the original weights from G
    for u2, v2 in F_prime.edges:
        if lang == "en":
            assert (
                u2 in D and v2 in D
            ), f"\nchuliu_edmonds: Vertex '{u2}' or '{v2}' not found in the original graph."
        elif lang == "pt":
            assert (
                u2 in D and v2 in D
            ), f"\nchuliu_edmonds: Vértice '{u2}' ou '{v2}' não encontrado no grafo original."
        F_prime[u2][v2]["w"] = D[u2][v2]["w"]

    if boilerplate and log:
        if lang == "en":
            log(f"\n✅{indent}Final arborescence: {list(F_prime.edges)}")
        elif lang == "pt":
            log(f"\n✅{indent}Arborescência final: {list(F_prime.edges)}")
        if draw_fn:
            if lang == "en":
                draw_fn(F_prime, f"\n{indent}Final Arborescence.")
            elif lang == "pt":
                draw_fn(F_prime, f"\n{indent}Arborescência final.")
    return F_prime


# Note: interactive test removed to avoid execution and type-checking issues.
