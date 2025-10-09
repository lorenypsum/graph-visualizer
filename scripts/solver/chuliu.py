import networkx as nx

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
    predecessors = list(D.in_edges(node, data="w"))

    if not predecessors:
        return

    # Calculate the minimum weight among the incoming edges
    yv = min((w for _, _, w in predecessors))

    # Subtract Yv from each incoming edge
    for u, _, _ in predecessors:
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
            in_edges = list(D.in_edges(v, data="w"))
            if not in_edges:
                continue  # No edges entering v
            u = next((u for u, _, w in in_edges if w == 0), None)
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
                ((v, w) for _, v, w in D.out_edges(u, data="w") if v in cycle_nodes),
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
                ((u, w) for u, _, w in D.in_edges(v, data="w") if u in cycle_nodes),
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
        id=1, 
        draw_fn=None, 
        draw_step=None, 
        log=None,
        boilerplate: bool = True,
        lang="pt",):

    """
    Finds the optimum arborescence in a directed graph G with root r0 using the Chu-Liu/Edmonds algorithm.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r0: The root node
        - level: The current recursion level (used for logging and visualization)
        - draw_fn: Optional function to visualize the graph at each step
        - log: Optional logging function to log information
        - boilerplate: If True, enables logging and visualization
        - lang: Language for logging messages ("en" for English, "pt" for Portuguese

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

    if boilerplate and log:
        if lang == "en":
            log(f"Starting level {level}")
        elif lang == "pt":
            log(f"Iniciando nível {level}")

    if lang == "en":
        assert (
            r0 in D
        ), f"The root vertex '{r0}' is not present in the graph."
    elif lang == "pt":
        assert (
            r0 in D
        ), f"O vértice raiz '{r0}' não está presente no grafo."

    D_copy = D.copy()

    if boilerplate and log:
        if lang == "en":
            log(
                f"Removing edges entering '{r0}'"
            )
        elif lang == "pt":
            log(
                f"Removendo arestas que entram em '{r0}'"
            )
        if draw_step:
            if lang == "en":
                draw_step(
                    D_copy,
                    id=id, 
                    title = f"After removing incoming edges", 
                    description=f"After removing incoming edges",
                )
            elif lang == "pt":
                draw_step(
                    D_copy,
                    id=id, 
                    title = f"Após remoção de entradas", 
                    description=f"Após remoção de entradas",
                )

    for v in D_copy.nodes:
        if v != r0:
            normalize_incoming_edge_weights(D_copy, v, lang=lang)

        if boilerplate and log:
            if lang == "en":
                log(
                    f"Normalizing weights of incoming edges to '{v}'"
                )
            elif lang == "pt":
                log(
                    f"Normalizando pesos de arestas de entrada para '{v}'"
                )
            
            id=id + 1
            if draw_step:
                if lang == "en":
                    draw_step(
                        D_copy,
                        id=id, 
                        title = f"Weight adjustment", 
                        description= f"After weight adjustment",
                    )
                elif lang == "pt":
                    draw_step(
                        D_copy,
                        id=id, 
                        title = f"Ajuste de pesos", description= f"Após ajuste de pesos",
                    )

    # Build F_star
    F_star = get_Fstar(D_copy, r0, lang=lang)

    id=id + 1
    
    if boilerplate and log:
        if lang == "en":
            log(f"{indent}Building F_star")
        elif lang == "pt":
            log(f"{indent}Construindo F_star")
        if draw_step:
            if lang == "pt":
                draw_step(F_star, id=id, title = f"F_star", description=f"Conjunto F* (arestas de custo zero após ajuste dos pesos de entrada de cada vértice, exceto a raiz).")
            elif lang == "en":
                draw_step(F_star, id=id, title = f"F_star", description=f"Set F* (edges with zero cost after adjusting the weights of incoming edges to each vertex, except the root).")


    if nx.is_arborescence(F_star):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = D[u][v]["w"]
        return F_star

    else:
        if boilerplate and log:
            if lang == "en":
                log(
                    f"{indent}F_star is not an arborescence. Continuing..."
                )
            elif lang == "pt":
                log(
                    f"{indent}F_star não é uma arborescência. Continuando..."
                )

        C: nx.DiGraph = find_cycle(F_star)

        if lang == "en":
            assert C, f"\nNo cycle found in F_star."
        elif lang == "pt":
            assert (
                C
            ), f"\nNenhum ciclo encontrado em F_star."

        contracted_label = f"\n n*{level}"
        in_to_cycle, out_from_cycle = contract_cycle(
            D_copy, C, contracted_label, lang=lang
        )

        # Recursive call
        F_prime = find_optimum_arborescence_chuliu(
            D=D_copy, 
            r0=r0, 
            level=level + 1, 
            id=id, 
            draw_fn=draw_fn,
            draw_step=draw_step,
            log=log,
            boilerplate=boilerplate,
            lang=lang,
        )

        # Identify the vertex in the cycle that received the only incoming edge from the arborescence
        in_edge = next(iter(F_prime.in_edges(contracted_label, data="w")), None)

        if lang == "en":
            assert (
                in_edge
            ), f"\n No incoming edge found for vertex '{contracted_label}'."
        elif lang == "pt":
            assert (
                in_edge
            ), f"\n Nenhuma aresta encontrada entrando no vértice '{contracted_label}'."

        u, _, _ = in_edge

        v, _ = in_to_cycle[u]

        if lang == "en":
            assert (
                v is not None
            ), f"\nNo vertex in the cycle found to receive the incoming edge from '{u}'."
        elif lang == "pt":
            assert (
                v is not None
            ), f"\nNenhum vértice do ciclo encontrado que recebeu a aresta de entrada de '{u}'."

        # Remove the internal edge entering vertex `v` from cycle C
        remove_internal_edge_to_cycle_entry(
            C, v
        )  # Note: w is coming from F_prime, not from G

        # Add the external edge entering the cycle (identified by in_edge), the weight will be corrected at the end using G
        F_prime.add_edge(u, v)
        if boilerplate and log:
            if lang == "en":
                log(
                    f"\n {indent}Adding incoming edge to cycle: ({u}, {v})"
                )
            elif lang == "pt":
                log(
                    f"\n {indent}Adicionando aresta de entrada ao ciclo: ({u}, {v})"
                )

        # Add the remaining edges of the modified cycle C
        for u_c, v_c in C.edges:
            F_prime.add_edge(u_c, v_c)
            if boilerplate and log:
                if lang == "en":
                    log(
                        f"\n {indent}Adding cycle edge: ({u_c}, {v_c})"
                    )
                elif lang == "pt":
                    log(
                        f"\n {indent}Adicionando aresta do ciclo: ({u_c}, {v_c})"
                    )

        # Add the external edges leaving the cycle
        for _, z, _ in F_prime.out_edges(contracted_label, data=True):

            if lang == "en":
                assert (
                    z in out_from_cycle
                ), f"\n No outgoing edge found for vertex '{z}'."
            elif lang == "pt":
                assert (
                    z in out_from_cycle
                ), f"\n Nenhuma aresta de saída encontrada para o vértice '{z}'."

            u_cycle, _ = out_from_cycle[z]
            F_prime.add_edge(u_cycle, z)

            if boilerplate and log:
                if lang == "en":
                    log(
                        f"\n{indent}Adding outgoing edge from cycle: ({u_cycle}, {z})"
                    )
                elif lang == "pt":
                    log(
                        f"\n{indent}Adicionando aresta externa de saída: ({u_cycle}, {z})"
                    )

        # Remove the contracted node
        if lang == "en":
            assert (
                contracted_label in F_prime
            ), f"\nVertex '{contracted_label}' not found in the graph."
        elif lang == "pt":
            assert (
                contracted_label in F_prime
            ), f"\nVértice '{contracted_label}' não encontrado no grafo."
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
        for u, v in F_prime.edges:
            if lang == "en":
                assert (
                    u in D and v in D
                ), f"\n Vertex '{u}' or '{v}' not found in the original graph."
            elif lang == "pt":
                assert (
                    u in D and v in D
                ), f"\n Vértice '{u}' ou '{v}' não encontrado no grafo original."
            F_prime[u][v]["w"] = D[u][v]["w"]

        if boilerplate and log:
            if lang == "en":
                log(
                    f"\n✅{indent}Final arborescence: {list(F_prime.edges)}"
                )
            elif lang == "pt":
                log(
                    f"\n✅{indent}Arborescência final: {list(F_prime.edges)}"
                )
            # if draw_fn:
            #     if lang == "en":
            #         draw_fn(
            #             F_prime,
            #             f"\n{indent}Final Arborescence.",
            #         )
            #     elif lang == "pt":
            #         draw_fn(
            #             F_prime,
            #             f"\n{indent}Arborescência final.",
            #         )
        return F_prime
