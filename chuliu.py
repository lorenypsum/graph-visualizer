import networkx as nx
from typing import cast

# Remove todas as arestas que entram no vértice raiz r em G
def remove_in_edges_to(
    D: nx.DiGraph, r: int):
    """
    Remove all edges entering the root vertex r in digraph D.
    Returns the updated graph.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r: The root node

    Returns:
        - D: The updated directed graph (networkx.DiGraph) with edges to r removed
    """

    # Remove all edges entering r
    in_edges = list(D.in_edges(r))
    D.remove_edges_from(in_edges)


# Normalização dos pesos das arestas que entram em um vértice
def reduce_costs(D: nx.DiGraph, v: int):
    """
    Change the costs of incoming edges into the `v`
    by subtracting the minimum incoming weight from each in the digraph D.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - v: The target v whose incoming edges will be adjusted

    Returns:
        - Nothing (the digraph D is modified in place)
    """
    in_edges = D.in_edges(v, data=True)

    # Calculate the minimum weight among the incoming edges
    yv = min((data["w"] for _, _, data in in_edges))

    # Subtract Yv from each incoming edge
    for u, _, _ in in_edges:
        D[u][v]["w"] -= yv


# Cria o conjunto Dzero
def get_Dzero(D: nx.DiGraph, r: int):
    """
    Creates the set D_zero from digraph D and root r.
    An returns a directed digraph D_zero.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r: The root vertex

    Returns:
        - D_zero: A directed graph (networkx.DiGraph) representing F*
    """
    # Create an empty directed graph for D_zero
    D_zero = nx.DiGraph()
    for v in D.nodes():
        if v != r:
            in_edges = D.in_edges(v, data=True)
            u = next((u for u, _, data in in_edges if data["w"] == 0))
            D_zero.add_edge(u, v, w=0)
    return D_zero

# Encontra um circuito (ciclo dirigido) em D_zero
def find_cycle(D_zero: nx.DiGraph):
    """
    Finds a directed cycle in the digraph.
    Returns a subgraph containing the cycle, or None if there is none.

    Parameters:
        - D_zero: A directed graph (networkx.DiGraph)

    Returns:
        - A directed graph (networkx.DiGraph) representing the cycle. 
    """
    nodes_in_cycle = set()
    # Extract nodes involved in the cycle
    for u, v, _ in nx.find_cycle(D_zero, orientation="original"):
        nodes_in_cycle.update([u, v])
    
    # Create a subgraph containing only the cycle
    D_zero_digraph = D_zero.subgraph(nodes_in_cycle).to_directed() # Note: convert to directed graph because subgraph returns a Graph
    return D_zero_digraph


# Contrai um ciclo C em D, substituindo-o por um supernó rotulado pelo `label`
def contract_cycle(D: nx.DiGraph, C: nx.DiGraph, label: int):
    """
    Contract a cycle C in digraph D, replacing it with a supernode labeled `label`.
    Returns the modified digraph D' with the contracted cycle, the list of incoming edges (in_edge), and outgoing edges (out_edge).
    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - C: A directed graph (networkx.DiGraph) representing the cycle to be contracted
        - label: The label for the new supernode

    Returns:
        - in_to_cycle: A dictionary mapping nodes outside the cycle to tuples (node_in_cycle, weight)
        - out_from_cycle: A dictionary mapping nodes outside the cycle to tuples (node_in_cycle, weight)
    """

    cycle_nodes: set[int] = set(C.nodes())

    # Stores the vertex u outside the cycle and the vertex v inside the cycle that receives the minimum weight edge
    in_to_cycle: dict[int, tuple[int, float]] = {}

    for u in D.nodes:
        if u not in cycle_nodes:
            # Find the minimum weight edge that u has to any vertex in C
            min_weight_edge_to_cycle = min(
                (
                    (v, data["w"])
                    for _, v, data in D.out_edges(u, data=True)
                    if v in cycle_nodes
                ),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_to_cycle:
                in_to_cycle[u] = min_weight_edge_to_cycle

    for u, (v, c) in in_to_cycle.items():
        D.add_edge(u, label, w=c)

    # Stores the vertex v outside the cycle that receives the minimum weight edge from a vertex u inside the cycle
    out_from_cycle: dict[int, tuple[int, float]] = {}

    for v in D.nodes:
        if v not in cycle_nodes:
            # Find the minimum weight edge that v receives from any vertex in C
            min_weight_edge_from_cycle = min(
                (
                    (u, data["w"])
                    for u, _, data in D.in_edges(v, data=True)
                    if u in cycle_nodes
                ),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_from_cycle:
                out_from_cycle[v] = min_weight_edge_from_cycle

    for v, (u, c) in out_from_cycle.items():
        D.add_edge(label, v, w=c)

    # Remove all nodes in the cycle from G
    D.remove_nodes_from(cycle_nodes)
    return in_to_cycle, out_from_cycle

def chuliu_edmonds(
    D: nx.DiGraph,
    r: int,
    level=0,
    **kwargs,
):
    """
    Wrapper function for the Chu-Liu/Edmonds algorithm.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r: The root node
        - level: Recursion level (default: 0)
        - **kwargs: Additional parameters passed to cle:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")
            - metrics: Optional dict to collect algorithm metrics

    Returns:
        - Optimum arborescence as a directed graph (networkx.DiGraph)
    """
    return cle(
        D,
        r,
        len(D.nodes),
        level,
        **kwargs,
    )


# Encontra a arborescência ótima em G com raiz r usando o algoritmo de Chu-Liu/Edmonds
def cle(
    D: nx.DiGraph,
    r: int,
    label: int,
    level=0,
    **kwargs,
):
    """
    Finds the optimum arborescence in a directed graph G with root r using the Chu-Liu/Edmonds algorithm.

    Parameters:
        - D: A directed graph (networkx.DiGraph)
        - r: The root node
        - label: Label for contracted supernodes
        - level: Recursion level (default: 0)
        - **kwargs: Additional parameters:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")
            - metrics: Optional dict to collect algorithm metrics

    Returns:
        - Optimum arborescence as a directed graph (networkx.DiGraph)
    """

    # Extract parameters from kwargs with defaults
    draw_fn = kwargs.get("draw_fn", None)
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")
    metrics = kwargs.get("metrics", None)

    indent = "  " * level

    # Initialize metrics if provided
    if metrics is not None:
        metrics.setdefault("contractions", 0)
        metrics.setdefault("max_depth", 0)
        if level > metrics["max_depth"]:
            metrics["max_depth"] = level

    if boilerplate and log:
        if lang == "en":
            log(f"\n chuliu_edmonds:{indent}Starting level {level}")
        elif lang == "pt":
            log(f"\n chuliu_edmonds:{indent}Iniciando nível {level}")

    if lang == "en":
        assert r in D, (
            "\n chuliu_edmonds: The root vertex '"
            + str(r)
            + "' is not present in the graph."
        )
    elif lang == "pt":
        assert r in D, (
            "\n chuliu_edmonds: O vértice raiz '"
            + str(r)
            + "' não está presente no grafo."
        )

    D_copy = cast(nx.DiGraph, D.copy())

    if boilerplate and log:
        if lang == "en":
            log(f"\n chuliu_edmonds:{indent}Removing edges entering '{r}'")
        elif lang == "pt":
            log(f"\n chuliu_edmonds:{indent}Removendo arestas que entram em '{r}'")
        if draw_fn:
            if lang == "en":
                draw_fn(
                    D_copy,
                    f"\n chuliu_edmonds:{indent}After removing incoming edges",
                )
            elif lang == "pt":
                draw_fn(
                    D_copy,
                    f"\n chuliu_edmonds:{indent}Após remoção de entradas",
                )

    for v in D_copy.nodes:
        if v != r:
            reduce_costs(D_copy, v)

        if boilerplate and log:
            if lang == "en":
                log(
                    f"\n chuliu_edmonds:{indent}Normalizing weights of incoming edges to '{v}'"
                )
            elif lang == "pt":
                log(
                    f"\n chuliu_edmonds:{indent}Normalizando pesos de arestas de entrada para '{v}'"
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

    # Build D_zero
    D_zero = get_Dzero(D_copy, r)

    if boilerplate and log:
        if lang == "en":
            log(f"\nchuliu_edmonds:{indent}Building D_zero")
        elif lang == "pt":
            log(f"\nchuliu_edmonds:{indent}Construindo D_zero")
        if draw_fn:
            if lang == "en":
                draw_fn(D_zero, f"\nchuliu_edmonds:{indent}D_zero")
            elif lang == "pt":
                draw_fn(D_zero, f"\nchuliu_edmonds:{indent}D_zero")

    if nx.is_arborescence(D_zero):
        for u, v in D_zero.edges:
            D_zero[u][v]["w"] = D[u][v]["w"]
        return D_zero

    # Otherwise, contract a cycle and recurse
    if boilerplate and log:
        if lang == "en":
            log(
                f"\nchuliu_edmonds:{indent}D_zero is not an arborescence. Continuing..."
            )
        elif lang == "pt":
            log(
                f"\nchuliu_edmonds:{indent}D_zero não é uma arborescência. Continuando..."
            )

    C = find_cycle(D_zero)

    if metrics is not None:
        metrics["contractions"] += 1

    in_to_cycle, out_from_cycle = contract_cycle(D_copy, C, label)

    # Recursive call
    F_prime = cle(
        D_copy,
        r,
        label + 1,
        level + 1,
        draw_fn=None,
        log=None,
        boilerplate=boilerplate,
        lang=lang,
        metrics=metrics,
    )

    in_edge = next(iter(F_prime.in_edges(label, data=True)))

    if lang == "en":
        assert (
            in_edge is not None
        ), f"\nchuliu_edmonds: No incoming edge found for vertex '{label}'."
    elif lang == "pt":
        assert (
            in_edge is not None
        ), f"\nchuliu_edmonds: Nenhuma aresta encontrada entrando no vértice '{label}'."
    # At this point in_edge is guaranteed not None
    u, _, _ = cast(tuple, in_edge)
    v, _ = in_to_cycle[u]

    if lang == "en":
        assert (
            v is not None
        ), f"\n chuliu_edmonds: No vertex in the cycle found to receive the incoming edge from '{u}'."
    elif lang == "pt":
        assert (
            v is not None
        ), f"\n chuliu_edmonds: Nenhum vértice do ciclo encontrado que recebeu a aresta de entrada de '{u}'."

    # Add the external edge entering the cycle and restore remaining cycle edges
    F_prime.add_edge(u, v)
    if boilerplate and log:
        if lang == "en":
            log(f"\n chuliu_edmonds:{indent}Adding incoming edge to cycle: ({u}, {v})")
        elif lang == "pt":
            log(
                f"\n chuliu_edmonds:{indent}Adicionando aresta de entrada ao ciclo: ({u}, {v})"
            )

    for u_c, v_c in C.edges:
        if v_c != v:
            F_prime.add_edge(u_c, v_c)
        if boilerplate and log:
            if lang == "en":
                log(f"\nchuliu_edmonds:{indent}Adding cycle edge: ({u_c}, {v_c})")
            elif lang == "pt":
                log(
                    f"\nchuliu_edmonds:{indent}Adicionando aresta do ciclo: ({u_c}, {v_c})"
                )

    # Add the external edges leaving the cycle
    for _, z, _ in list(F_prime.out_edges(label, data=True)):
        if lang == "en":
            assert (
                z in out_from_cycle
            ), f"\n chuliu_edmonds: No outgoing edge found for vertex '{z}'."
        elif lang == "pt":
            assert (
                z in out_from_cycle
            ), f"\n chuliu_edmonds: Nenhuma aresta de saída encontrada para o vértice '{z}'."
        u_cycle, _ = out_from_cycle[z]
        F_prime.add_edge(u_cycle, z)
        if boilerplate and log:
            if lang == "en":
                log(
                    f"\n chuliu_edmonds:{indent}Adding outgoing edge from cycle: ({u_cycle}, {z})"
                )
            elif lang == "pt":
                log(
                    f"\n chuliu_edmonds:{indent}Adicionando aresta externa de saída: ({u_cycle}, {z})"
                )

    # Remove the contracted node
    if lang == "en":
        assert (
            label in F_prime
        ), f"\nchuliu_edmonds: Vertex '{label}' not found in the graph."
    elif lang == "pt":
        assert (
            label in F_prime
        ), f"\nchuliu_edmonds: Vértice '{label}' não encontrado no grafo."
    F_prime.remove_node(label)

    if boilerplate and log:
        if lang == "en":
            log(f"\n chuliu_edmonds:{indent}Contracted vertex '{label}' removed.")
        elif lang == "pt":
            log(f"\n chuliu_edmonds:{indent}Vértice contraído '{label}' removido.")

    # Update the edge weights with the original weights from G
    for u2, v2 in F_prime.edges:
        if lang == "en":
            assert (
                u2 in D and v2 in D
            ), f"\n chuliu_edmonds: Vertex '{u2}' or '{v2}' not found in the original graph."
        elif lang == "pt":
            assert (
                u2 in D and v2 in D
            ), f"\n chuliu_edmonds: Vértice '{u2}' ou '{v2}' não encontrado no grafo original."
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

