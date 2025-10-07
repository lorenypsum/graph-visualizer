import networkx as nx
from typing import Optional, cast


# Normalização dos pesos das arestas que entram em um vértice
def normalize_incoming_edge_weights(D: nx.DiGraph, node: str, lang="pt"):
    """
    Change the weights of incoming edges into the `node`
    by subtracting the minimum incoming weight from each in the Graph G.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - node: The target node whose incoming edges will be adjusted
        - lang: Language for error messages ("en" for English, "pt" for Portuguese)

    Returns:
        - Nothing (the graph G is modified in place)
    """

    if lang == "en":
        assert (
            node in D
        ), f"\nnormalize_incoming_edge_weights: The vertex '{node}' does not exist in the graph."
    elif lang == "pt":
        assert (
            node in D
        ), f"\nnormalize_incoming_edge_weights: O vértice '{node}' não existe no grafo."

    # Get the incoming edges of the node with their weights
    predecessors = list(D.in_edges(node, data=True))

    if not predecessors:
        return

    # Calculate the minimum weight among the incoming edges
    yv = min((data.get("w", 0) for _, _, data in predecessors))

    # Subtract Yv from each incoming edge
    for u, _, _ in predecessors:
        # Ensure the edge has a weight attribute
        if "w" not in D[u][node]:
            D[u][node]["w"] = 0
        D[u][node]["w"] -= yv


# Cria o conjunto F*
def get_Fstar(D: nx.DiGraph, r0: str, lang="pt"):
    """
    Creates the set F_star from graph G and root r0.
    An returns a directed graph F_star.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r0: The root node
        - lang: Language for error messages ("en" for English, "pt" for Portuguese)

    Returns:
        - F_star: A directed graph (networkx.DiGraph) representing F*
    """

    if lang == "en":
        assert (
            r0 in D
        ), f"\nget_Fstar: The root vertex '{r0}' does not exist in the graph."
    elif lang == "pt":
        assert r0 in D, f"\nget_Fstar: O vértice raiz '{r0}' não existe no grafo."

    # Create an empty directed graph for F_star
    F_star = nx.DiGraph()

    for v in D.nodes():
        if v != r0:
            in_edges = list(D.in_edges(v, data=True))
            if not in_edges:
                continue  # No edges entering v
            u = next((u for u, _, data in in_edges if data.get("w", None) == 0), None)
            if u:
                F_star.add_edge(u, v, w=0)
    return F_star


# Encontra um circuito (ciclo dirigido) em G
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

    if lang == "en":
        assert (
            label not in D
        ), f"\ncontract_cycle: The label '{label}' already exists as a vertex in G."
    elif lang == "pt":
        assert (
            label not in D
        ), f"\ncontract_cycle: O rótulo '{label}' já existe como vértice em G."

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


# Remove todas as arestas que entram no vértice raiz r0 em G
def remove_edges_to_r0(
    D: nx.DiGraph, r0: str, log=None, boilerplate: bool = True, lang="pt"
):
    """
    Remove all edges entering the root vertex r0 in graph G.
    Returns the updated graph.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r0: The root node
        - log: Optional logging function to log information
        - boilerplate: If True, enables logging
        - lang: Language for logging messages ("en" for English, "pt" for Portuguese

    Returns:
        - D: The updated directed graph (networkx.DiGraph) with edges to r0 removed
    """

    # Verify that r0 exists in G
    if lang == "en":
        assert (
            r0 in D
        ), f"\nremove_edges_to_r0: The root vertex '{r0}' does not exist in the graph."
    elif lang == "pt":
        assert (
            r0 in D
        ), f"\nremove_edges_to_r0: O vértice raiz '{r0}' não existe no grafo."

    # Remove all edges entering r0
    in_edges = list(D.in_edges(r0))
    if not in_edges:
        if boilerplate and log:
            if lang == "en":
                log(f"\nremove_edges_to_r0: No edges entering '{r0}' to remove.")
            elif lang == "pt":
                log(
                    f"\nremove_edges_to_r0: Nenhuma aresta entrando em '{r0}' para remover."
                )
    else:
        D.remove_edges_from(in_edges)
        if boilerplate and log:
            if lang == "en":
                log(
                    f"\nremove_edges_to_r0: Removed {len(in_edges)} edges entering '{r0}'."
                )
            elif lang == "pt":
                log(
                    f"\nremove_edges_to_r0: Removidas {len(in_edges)} arestas entrando em '{r0}'."
                )
    return D


# Remove a aresta interna que entra no vértice de entrada do ciclo
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


# Encontra a arborescência ótima em G com raiz r0 usando o algoritmo de Chu-Liu/Edmonds
def find_optimum_arborescence_chuliu(
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
            log(f"\nfind_optimum_arborescence_chuliu:{indent}Starting level {level}")
        elif lang == "pt":
            log(f"\nfind_optimum_arborescence_chuliu:{indent}Iniciando nível {level}")

    if lang == "en":
        assert r0 in D, (
            "\nfind_optimum_arborescence_chuliu: The root vertex '"
            + r0
            + "' is not present in the graph."
        )
    elif lang == "pt":
        assert r0 in D, (
            "\nfind_optimum_arborescence_chuliu: O vértice raiz '"
            + r0
            + "' não está presente no grafo."
        )

    D_copy = cast(nx.DiGraph, D.copy())

    if boilerplate and log:
        if lang == "en":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}Removing edges entering '{r0}'"
            )
        elif lang == "pt":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}Removendo arestas que entram em '{r0}'"
            )
        if draw_fn:
            if lang == "en":
                draw_fn(
                    D_copy,
                    f"\nfind_optimum_arborescence_chuliu:{indent}After removing incoming edges",
                )
            elif lang == "pt":
                draw_fn(
                    D_copy,
                    f"\nfind_optimum_arborescence_chuliu:{indent}Após remoção de entradas",
                )

    for v in D_copy.nodes:
        if v != r0:
            normalize_incoming_edge_weights(D_copy, v, lang=lang)

        if boilerplate and log:
            if lang == "en":
                log(
                    f"\nfind_optimum_arborescence_chuliu:{indent}Normalizing weights of incoming edges to '{v}'"
                )
            elif lang == "pt":
                log(
                    f"\nfind_optimum_arborescence_chuliu:{indent}Normalizando pesos de arestas de entrada para '{v}'"
                )
            if draw_fn:
                if lang == "en":
                    draw_fn(
                        D_copy,
                        f"\nfind_optimum_arborescence_chuliu:{indent}After weight adjustment",
                    )
                elif lang == "pt":
                    draw_fn(
                        D_copy,
                        f"\nfind_optimum_arborescence_chuliu:{indent}Após ajuste de pesos",
                    )

    # Build F_star
    F_star = get_Fstar(D_copy, r0, lang=lang)

    if boilerplate and log:
        if lang == "en":
            log(f"\nfind_optimum_arborescence_chuliu:{indent}Building F_star")
        elif lang == "pt":
            log(f"\nfind_optimum_arborescence_chuliu:{indent}Construindo F_star")
        if draw_fn:
            if lang == "en":
                draw_fn(F_star, f"\nfind_optimum_arborescence_chuliu:{indent}F_star")
            elif lang == "pt":
                draw_fn(F_star, f"\nfind_optimum_arborescence_chuliu:{indent}F_star")

    if nx.is_arborescence(F_star):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = D[u][v]["w"]
        return F_star

    # Otherwise, contract a cycle and recurse
    if boilerplate and log:
        if lang == "en":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}F_star is not an arborescence. Continuing..."
            )
        elif lang == "pt":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}F_star não é uma arborescência. Continuando..."
            )

    C_opt: Optional[nx.DiGraph] = find_cycle(F_star)
    if lang == "en":
        assert (
            C_opt is not None
        ), "\nfind_optimum_arborescence_chuliu: No cycle found in F_star."
    elif lang == "pt":
        assert (
            C_opt is not None
        ), "\nfind_optimum_arborescence_chuliu: Nenhum ciclo encontrado em F_star."
    C = cast(nx.DiGraph, C_opt)

    contracted_label = f"\n n*{level}"
    if metrics is not None:
        metrics["contractions"] += 1
    in_to_cycle, out_from_cycle = contract_cycle(D_copy, C, contracted_label, lang=lang)

    # Recursive call
    F_prime = find_optimum_arborescence_chuliu(
        D_copy,
        r0,
        level + 1,
        draw_fn=None,
        log=None,
        boilerplate=boilerplate,
        lang=lang,
        metrics=metrics,
    )

    # Identify the vertex in the cycle that received the only incoming edge
    in_edges_list = list(F_prime.in_edges(contracted_label, data=True))
    in_edge = in_edges_list[0] if in_edges_list else None
    if lang == "en":
        assert (
            in_edge is not None
        ), f"\nfind_optimum_arborescence_chuliu: No incoming edge found for vertex '{contracted_label}'."
    elif lang == "pt":
        assert (
            in_edge is not None
        ), f"\nfind_optimum_arborescence_chuliu: Nenhuma aresta encontrada entrando no vértice '{contracted_label}'."
    # At this point in_edge is guaranteed not None by asserts above
    u, _, _ = cast(tuple, in_edge)
    v, _ = in_to_cycle[u]

    if lang == "en":
        assert (
            v is not None
        ), f"\nfind_optimum_arborescence_chuliu: No vertex in the cycle found to receive the incoming edge from '{u}'."
    elif lang == "pt":
        assert (
            v is not None
        ), f"\nfind_optimum_arborescence_chuliu: Nenhum vértice do ciclo encontrado que recebeu a aresta de entrada de '{u}'."

    # Remove the internal edge entering vertex `v` from cycle C
    remove_internal_edge_to_cycle_entry(C, v)

    # Add the external edge entering the cycle and restore remaining cycle edges
    F_prime.add_edge(u, v)
    if boilerplate and log:
        if lang == "en":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}Adding incoming edge to cycle: ({u}, {v})"
            )
        elif lang == "pt":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}Adicionando aresta de entrada ao ciclo: ({u}, {v})"
            )

    for u_c, v_c in C.edges:
        F_prime.add_edge(u_c, v_c)
        if boilerplate and log:
            if lang == "en":
                log(
                    f"\nfind_optimum_arborescence_chuliu:{indent}Adding cycle edge: ({u_c}, {v_c})"
                )
            elif lang == "pt":
                log(
                    f"\nfind_optimum_arborescence_chuliu:{indent}Adicionando aresta do ciclo: ({u_c}, {v_c})"
                )

    # Add the external edges leaving the cycle
    for _, z, _ in F_prime.out_edges(contracted_label, data=True):
        if lang == "en":
            assert (
                z in out_from_cycle
            ), f"\nfind_optimum_arborescence_chuliu: No outgoing edge found for vertex '{z}'."
        elif lang == "pt":
            assert (
                z in out_from_cycle
            ), f"\nfind_optimum_arborescence_chuliu: Nenhuma aresta de saída encontrada para o vértice '{z}'."
        u_cycle, _ = out_from_cycle[z]
        F_prime.add_edge(u_cycle, z)
        if boilerplate and log:
            if lang == "en":
                log(
                    f"\nfind_optimum_arborescence_chuliu:{indent}Adding outgoing edge from cycle: ({u_cycle}, {z})"
                )
            elif lang == "pt":
                log(
                    f"\nfind_optimum_arborescence_chuliu:{indent}Adicionando aresta externa de saída: ({u_cycle}, {z})"
                )

    # Remove the contracted node
    if lang == "en":
        assert (
            contracted_label in F_prime
        ), f"\nfind_optimum_arborescence_chuliu: Vertex '{contracted_label}' not found in the graph."
    elif lang == "pt":
        assert (
            contracted_label in F_prime
        ), f"\nfind_optimum_arborescence_chuliu: Vértice '{contracted_label}' não encontrado no grafo."
    F_prime.remove_node(contracted_label)

    if boilerplate and log:
        if lang == "en":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}Contracted vertex '{contracted_label}' removed."
            )
        elif lang == "pt":
            log(
                f"\nfind_optimum_arborescence_chuliu:{indent}Vértice contraído '{contracted_label}' removido."
            )

    # Update the edge weights with the original weights from G
    for u2, v2 in F_prime.edges:
        if lang == "en":
            assert (
                u2 in D and v2 in D
            ), f"\nfind_optimum_arborescence_chuliu: Vertex '{u2}' or '{v2}' not found in the original graph."
        elif lang == "pt":
            assert (
                u2 in D and v2 in D
            ), f"\nfind_optimum_arborescence_chuliu: Vértice '{u2}' ou '{v2}' não encontrado no grafo original."
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
