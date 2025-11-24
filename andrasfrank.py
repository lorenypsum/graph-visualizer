import networkx as nx
import heapq

def get_in_arcs(D: nx.DiGraph, X: set, **kwargs):
    """
    Get the arcs entering a set X in a directed graph D.
    The function returns a list of tuples representing the arcs entering X with the designated weights.

    Parameters:
    - D: directed graph (DiGraph)
    - X: set of nodes
    - **kwargs: Additional parameters:
        - log: Optional logging function
        - boilerplate: If True, enables logging (default: True)
        - lang: Language for messages ("en" or "pt", default: "pt")

    Returns:
    - arcs: list of tuples (u, v, data) where u not in X and v in X
    """
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")

    arcs = []

    if boilerplate and log:
        if lang == "en":
            log(f" andras_frank: Found {len(arcs)} arcs entering set X={X}")
        elif lang == "pt":
            log(
                f" andras_frank: Encontrados {len(arcs)} arcos entrando no conjunto X={X}"
            )

    return [(u, v, data) for u, v, data in D.edges(data=True) if u not in X and v in X]

def update_weights(
    D: nx.DiGraph,
    arcs: list[tuple[int, int, dict]],
    min_weight: float):
    """
    Update the weights of the arcs in a directed graph D for the nodes in set X.
    ATTENTION: The function produces collateral effect in the provided directed graph
    by updating its arcs weights.

    Parameters:
        - D: directed graph (DiGraph)
        - arcs: list of tuples (u, v, data) where u not in X and v in X
        - min_weight: minimum weight to be subtracted from the arcs weights
        - F: list to store the arcs that reach weight zero
        - D_zero: directed graph (DiGraph) to store the arcs that reach weight zero
        - **kwargs: Additional parameters:
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")

    Returns:
        - Nothing. The function updates D, F, and D_zero in place.
    """
    for u, v, _ in arcs:
        D[u][v]["w"] -= min_weight
        if D[u][v]["w"] == 0:
            a = (u, v)
    return a

def has_arborescence(D: nx.DiGraph, r: int):
    """
    Check if a directed graph D has an arborescence with root r.
    The function returns True if an arborescence exists, otherwise False.

    Parameters:
        - D: directed graph (DiGraph)
        - r: root node

    Returns:
        - bool: True if an arborescence exists, otherwise False
    """
    # Verify if the graph is a DFS tree with root r
    tree = nx.dfs_tree(D, r)

    return tree.number_of_nodes() == D.number_of_nodes()

def phase1(
    D_original: nx.DiGraph,
    r: int,
    **kwargs,
):
    """
    Find the minimum arborescence in a directed graph D with root r.
    The function returns the minimum arborescence as a list of arcs.

    Parameters:
        - D_original: directed graph (DiGraph)
        - r: root node
        - **kwargs: Additional parameters:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")
            - metrics: Optional dict to collect algorithm metrics

    Returns:
        - F: list of arcs (u, v) that form the minimum arborescence
        - Iam: list of tuples (X, z(X))
    """

    # Extract parameters from kwargs with defaults
    draw_fn = kwargs.get("draw_fn", None)
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")
    metrics = kwargs.get("metrics", None)

    D_copy = D_original.copy()
    F = []
    Iam = []  # List to store the variables (X, z(X))
    D_zero = nx.DiGraph()
    D_zero.add_nodes_from(D_copy.nodes())

    iteration = 0

    if boilerplate and log:
        if lang == "en":
            log(f"\n andras_frank: Phase 1 - Starting the algorithm")
            log(
                f" andras_frank: Graph has {D_copy.number_of_nodes()} nodes and {D_copy.number_of_edges()} edges"
            )
            log(f" andras_frank: Root node: {r}")
        elif lang == "pt":
            log(f"\n andras_frank: Fase 1 - Iniciando algoritmo")
            log(
                f" andras_frank: Grafo possui {D_copy.number_of_nodes()} nós e {D_copy.number_of_edges()} arestas"
            )
            log(f" andras_frank: Nó raiz: {r}")

    if boilerplate and draw_fn:
        if lang == "en":
            draw_fn(D_zero, title="Initial D_zero")
        elif lang == "pt":
            draw_fn(D_zero, title="D_zero Inicial")

    while True:
        iteration += 1
        if boilerplate and log:
            if lang == "en":
                log(f"\nIteration {iteration} ----------------------------")
            elif lang == "pt":
                log(f"\nIteração {iteration} ----------------------------")

        # Calculate the strongly connected components of the graph D_zero.
        C = nx.condensation(D_zero)
        if boilerplate and draw_fn:
            if lang == "en":
                draw_fn(
                    C,
                    title=f"Strongly connected components in D_zero - Iteration {iteration}",
                )
            elif lang == "pt":
                draw_fn(
                    C,
                    title=f"Componentes fortemente conexos em D_zero - Iteração {iteration}",
                )

        # The sources are where there are no incoming arcs, r is always a source.
        sources = [x for x in C.nodes() if C.in_degree(x) == 0]

        if boilerplate and log:
            if lang == "en":
                log(f"\nSources: {sources}")
            elif lang == "pt":
                log(f"\nFontes: {sources}")

        if len(sources) == 1:
            # If there is only one source, it means it is r and there are no more arcs to be processed.
            if boilerplate and log:
                if lang == "en":
                    log(f"\nOnly one source found, algorithm finished.")
                elif lang == "pt":
                    log(f"\nApenas uma fonte encontrada, algoritmo finalizado.")
            break

        for u in sources:
            X = C.nodes[u]["members"]
            if r in X:
                if boilerplate and log:
                    if lang == "en":
                        log(f" andras_frank: Skipping source {u} (contains root {r})")
                    elif lang == "pt":
                        log(f" andras_frank: Ignorando fonte {u} (contém raiz {r})")
                continue

            if boilerplate and log:
                if lang == "en":
                    log(f"\n andras_frank: Processing source {u} with set X={X}")
                elif lang == "pt":
                    log(f"\n andras_frank: Processando fonte {u} com conjunto X={X}")

            arcs = get_in_arcs(D_copy, X, **kwargs)

            if boilerplate and log:
                if lang == "en":
                    log(
                        f" andras_frank: Arcs entering X: {[(u, v, data['w']) for u, v, data in arcs]}"
                    )
                elif lang == "pt":
                    log(
                        f" andras_frank: Arcos entrando em X: {[(u, v, data['w']) for u, v, data in arcs]}"
                    )

            min_weight = min(data["w"] for _, _, data in arcs)

            a = update_weights(D_copy, arcs, min_weight)

            F.append(a)
            D_zero.add_edge(a[0], a[1])

            Iam.append((X, min_weight))

    # Collect metrics if requested
    if metrics is not None:
        metrics["phase1_iterations"] = iteration
        metrics["d0_edges"] = D_zero.number_of_edges()
        metrics["d0_nodes"] = D_zero.number_of_nodes()
        metrics["dual_count"] = len(Iam)

    if boilerplate and log:
        if lang == "en":
            log(f"\n andras_frank: Phase 1 completed in {iteration} iterations")
            log(f" andras_frank: F has {len(F)} arcs")
            log(f" andras_frank: Iam has {len(Iam)} variables")
        elif lang == "pt":
            log(f"\n andras_frank: Fase 1 concluída em {iteration} iterações")
            log(f" andras_frank: F possui {len(F)} arcos")
            log(f" andras_frank: Iam possui {len(Iam)} variáveis")

    return F, Iam

def phase2(D_original: nx.DiGraph, r: int, F: list[tuple[int, int]], **kwargs):
    """
    Find the minimum arborescence in a directed graph D with root r.
    The function returns the minimum arborescence as a DiGraph.

    Parameters:
        - D_original: directed graph (DiGraph)
        - r: root node
        - F: list of arcs (u, v) that form the minimum arborescence
        - **kwargs: Additional parameters:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")

    Returns:
        - Arb: directed graph (DiGraph) representing the minimum arborescence
    """

    # Extract parameters from kwargs with defaults
    draw_fn = kwargs.get("draw_fn", None)
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")
    Arb = nx.DiGraph()

    if boilerplate and log:
        if lang == "en":
            log(f"\n andras_frank: Phase 2 - Building arborescence from F")
            log(f" andras_frank: Starting with root {r}")
            log(f" andras_frank: Total arcs in F: {len(F)}")
        elif lang == "pt":
            log(
                f"\n andras_frank: Fase 2 - Construindo arborescência a partir de F"
            )
            log(f" andras_frank: Iniciando com raiz {r}")
            log(f" andras_frank: Total de arcos em F: {len(F)}")

    # Add the root node
    Arb.add_node(r)
    n = len(D_original.nodes())

    # While there are arcs to be considered
    for _ in range(n - 1):
        for u, v in F:
            if u in Arb.nodes() and v not in Arb.nodes():
                edge_data = D_original.get_edge_data(u, v)
                Arb.add_edge(u, v, **edge_data)
                if boilerplate and log:
                    if lang == "en":
                        log(
                            f" andras_frank: Added arc ({u}, {v}) with weight {edge_data['w']}"
                        )
                    elif lang == "pt":
                        log(
                            f" andras_frank: Adicionado arco ({u}, {v}) com peso {edge_data['w']}"
                        )
                # Restart the loop after adding an edge
                break
        if boilerplate and draw_fn:
            if lang == "en":
                draw_fn(Arb, title=f"Partial arborescence - Iteration {_+1}")
            elif lang == "pt":
                draw_fn(Arb, title=f"Arborescência parcial - Iteração {_+1}")

    if boilerplate and log:
        if lang == "en":
            log(
                f" andras_frank: Phase 2 completed. Arborescence has {Arb.number_of_edges()} edges"
            )
        elif lang == "pt":
            log(
                f" andras_frank: Fase 2 concluída. Arborescência possui {Arb.number_of_edges()} arestas"
            )

    return Arb

def phase2_v2(D_original: nx.DiGraph, r: int, F: list[tuple[int, int]], **kwargs):
    """
    Find the minimum arborescence in a directed graph D with root r.
    The function returns the minimum arborescence as a DiGraph.

    Parameters:
        - D_original: directed graph (DiGraph)
        - r: root node
        - F: list of arcs (u, v) that form the minimum arborescence
        - **kwargs: Additional parameters:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")

    Returns:
        - Arb: directed graph (DiGraph) representing the minimum arborescence
    """

    # Extract parameters from kwargs with defaults
    draw_fn = kwargs.get("draw_fn", None)
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")

    if boilerplate and log:
        if lang == "en":
            log(
                f"\n andras_frank: Phase 2 v2 - Building arborescence using priority queue"
            )
            log(f" andras_frank: Starting with root {r}")
            log(f" andras_frank: Total arcs in F: {len(F)}")
        elif lang == "pt":
            log(
                f"\n andras_frank: Fase 2 v2 - Construindo arborescência usando fila de prioridade"
            )
            log(f" andras_frank: Iniciando com raiz {r}")
            log(f" andras_frank: Total de arcos em F: {len(F)}")

    Arb = nx.DiGraph()
    for i, (u, v) in enumerate(F):
        Arb.add_edge(u, v, w=i)

    # Set of visited vertices, starting with the root
    V = {r}

    # Priority queue to store the edges
    q = []
    for u, v, data in Arb.out_edges(r, data=True):
        # Add edges to the priority queue with their weights
        heapq.heappush(q, (data["w"], u, v))

    if boilerplate and log:
        if lang == "en":
            log(
                f" andras_frank: Initialized priority queue with {len(q)} edges from root"
            )
        elif lang == "pt":
            log(
                f" andras_frank: Inicializada fila de prioridade com {len(q)} arestas da raiz"
            )

    A = nx.DiGraph()  # Arborescência resultante

    if boilerplate and draw_fn:
        if lang == "en":
            draw_fn(Arb, title=f"Initial arborescence with weights - Phase 2")
        elif lang == "pt":
            draw_fn(Arb, title=f"Arborescência inicial com pesos - Fase 2")

    # While the queue is not empty
    edges_added = 0
    while q:
        _, u, v = heapq.heappop(q)

        if v in V:  # If the vertex has already been visited, continue
            continue

        # Add the edge to the arborescence
        weight = D_original[u][v]["w"]
        A.add_edge(u, v, w=weight)
        edges_added += 1

        if boilerplate and log:
            if lang == "en":
                log(f" andras_frank: Added arc ({u}, {v}) with weight {weight}")
            elif lang == "pt":
                log(f" andras_frank: Adicionado arco ({u}, {v}) com peso {weight}")

        # Mark the vertex as visited
        V.add(v)

        # Add the outgoing edges of the visited vertex to the priority queue
        new_edges = 0
        for x, y, data in Arb.out_edges(v, data=True):
            heapq.heappush(q, (data["w"], x, y))
            new_edges += 1

        if boilerplate and log and new_edges > 0:
            if lang == "en":
                log(f" andras_frank: Added {new_edges} new edges to priority queue")
            elif lang == "pt":
                log(
                    f" andras_frank: Adicionadas {new_edges} novas arestas à fila de prioridade"
                )

    if boilerplate and log:
        if lang == "en":
            log(
                f" andras_frank: Phase 2 v2 completed. Arborescence has {A.number_of_edges()} edges"
            )
        elif lang == "pt":
            log(
                f" andras_frank: Fase 2 v2 concluída. Arborescência possui {A.number_of_edges()} arestas"
            )

    if boilerplate and draw_fn:
        if lang == "en":
            draw_fn(A, title=f"Final arborescence - Phase 2")
        elif lang == "pt":
            draw_fn(A, title=f"Arborescência final - Fase 2")
    # Return the resulting arborescence
    return A

def check_dual_optimality_condition(
    Arb: nx.DiGraph, Iam: list[tuple[set[int], float]], **kwargs
):
    """
    Verifica a condição dual: z(X) > 0 implica que exatamente uma aresta de Arb entra em X.

    Parameters:
        - Arb: arborescência (DiGraph)
        - Iam: lista de tuplas (X, z(X)) representando as variáveis duais
        - **kwargs: Additional parameters:
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")

    Returns:
        - bool: True se a condição dual é satisfeita, False caso contrário
    """

    # Extract parameters from kwargs with defaults
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")

    if boilerplate and log:
        if lang == "en":
            log(f"\n andras_frank: Checking dual optimality condition")
            log(f" andras_frank: Checking {len(Iam)} dual variables")
        elif lang == "pt":
            log(f"\n andras_frank: Verificando condição de otimalidade dual")
            log(f" andras_frank: Verificando {len(Iam)} variáveis duais")

    for X, z in Iam:
        count = 0
        for u, v in Arb.edges():
            if u not in X and v in X:
                count += 1
                if count > 1:
                    if boilerplate and log:
                        if lang == "en":
                            log(
                                f"\n andras_frank: ❌ Dual condition failed for X={X} with z(X)={z}. Incoming arcs: {count}"
                            )
                        elif lang == "pt":
                            log(
                                f"\n andras_frank: ❌ Falha na condição dual para X={X} com z(X)={z}. Arcos entrando: {count}"
                            )
                    return False

        if boilerplate and log:
            if lang == "en":
                log(
                    f" andras_frank: ✓ Dual condition satisfied for X={X} with z(X)={z}. Incoming arcs: {count}"
                )
            elif lang == "pt":
                log(
                    f" andras_frank: ✓ Condição dual satisfeita para X={X} com z(X)={z}. Arcos entrando: {count}"
                )

    if boilerplate and log:
        if lang == "en":
            log(f" andras_frank: ✅ All dual conditions satisfied")
        elif lang == "pt":
            log(f" andras_frank: ✅ Todas as condições duais satisfeitas")

    return True

def andras_frank_algorithm(
    D: nx.DiGraph,
    **kwargs,
):
    """
    Execute the András Frank algorithm to find minimum arborescence.

    Parameters:
        - D: directed graph (DiGraph)
        - **kwargs: Additional parameters:
            - draw_fn: Optional drawing function
            - log: Optional logging function
            - boilerplate: If True, enables logging (default: True)
            - lang: Language for messages ("en" or "pt", default: "pt")
            - metrics: Optional dict to collect algorithm metrics

    Returns:
        - arborescence_frank: DiGraph from phase2
        - arborescence_frank_v2: DiGraph from phase2_v2
        - dual_frank: bool indicating if dual condition is satisfied
        - dual_frank_v2: bool indicating if dual condition is satisfied for v2
    """
    # Extract parameters from kwargs with defaults
    draw_fn = kwargs.get("draw_fn", None)
    log = kwargs.get("log", None)
    boilerplate = kwargs.get("boilerplate", True)
    lang = kwargs.get("lang", "pt")

    if boilerplate and log:
        if lang == "en":
            log(f"\nExecuting András Frank algorithm...")
        elif lang == "pt":
            log(f"\nExecutando algoritmo de András Frank...")

    F, Iam = phase1(
        D,
        0,
        **kwargs,
    )

    if boilerplate and log:
        log(f"\nF: \n{F}")
        log(f"\nIam: \n{Iam}")

    if not has_arborescence(D, 0):
        if boilerplate and log:
            if lang == "en":
                log(f"\nThe graph does not contain an arborescence with root 0.")
            elif lang == "pt":
                log(f"\nO grafo não contém uma arborescência com raiz 0.")
        return None, None

    arborescence_frank = phase2(D, 0, F, **kwargs)
    arborescence_frank_v2 = phase2_v2(D, 0, F, **kwargs)
    dual_frank = check_dual_optimality_condition(
        arborescence_frank, Iam, **kwargs
    )

    dual_frank_v2 = check_dual_optimality_condition(
        arborescence_frank_v2, Iam, **kwargs
    )

    if dual_frank and dual_frank_v2:
        if boilerplate and log:
            if lang == "en":
                log(f"\n✅ Dual condition satisfied for András Frank.")
            elif lang == "pt":
                log(f"\n✅ Condição dual satisfeita para András Frank.")
    else:
        if boilerplate and log:
            if lang == "en":
                log(f"\n❌ Dual condition failed for András Frank.")
            elif lang == "pt":
                log(f"\n❌ Condição dual falhou para András Frank.")

        if draw_fn:
            if boilerplate and draw_fn:
                if lang == "en":
                    draw_fn(
                        arborescence_frank,
                        title="András Frank Arborescence - Method 1",
                    )
                    draw_fn(
                        arborescence_frank_v2,
                        title="András Frank Arborescence - Method 2",
                    )
                elif lang == "pt":
                    draw_fn(
                        arborescence_frank,
                        title="Arborescência de András Frank - Método 1",
                    )

                    draw_fn(
                        arborescence_frank_v2,
                        title="Arborescência de András Frank - Método 2",
                    )

    return arborescence_frank, arborescence_frank_v2, dual_frank, dual_frank_v2
