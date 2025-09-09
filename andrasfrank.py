import networkx as nx
import heapq

from test import build_rooted_digraph

D1 = build_rooted_digraph(10, 20, "r0", 1, 10)

# TODO: Verificar se precisa mesmo dessa função
def build_D_zero(D):
    """
    Build a directed graph D_zero and from the input directed graph D,
    where D_zero contains only the edges with weight zero.
    The function also returns a list of tuples representing the edges with weight zero in D_zero.

    Parameters:
    - D: directed graph (DiGraph)

    Returns:
    - D_zero: directed graph (DiGraph) containing only edges with weight zero ???
    """

    D_zero = nx.DiGraph()

    for v in D.nodes():
        D_zero.add_node(v)

    return D_zero


def get_arcs_entering_X(D, X):
    """
    Get the arcs entering a set X in a directed graph D.
    The function returns a list of tuples representing the arcs entering X with the designated weights.

    Parameters:
    - D: directed graph (DiGraph)
    - X: set of nodes

    Returns:
    - arcs: list of tuples (u, v, data) where u not in X and v in X
    """

    arcs = []

    for u, v, data in D.edges(data=True):
        if u not in X and v in X:
            arcs.append((u, v, data))

    return arcs

def get_minimum_weight_cut(arcs):
    """
    Get the minimum weight arcs from a list of arcs.
    The function returns a list of tuples representing the minimum weight arcs.

    Parameters:
    - arcs: list of tuples (u, v, data)

    Returns:
    - min_weight: minimum weight found among the arcs
    """

    return min(data["w"] for _, _, data in arcs)

def update_weights_in_X(D, arcs, min_weight, A_zero, D_zero):
    """
    Update the weights of the arcs in a directed graph D for the nodes in set X.
    ATTENTION: The function produces collateral effect in the provided directed graph by updating its arcs weights.

    Parameters:
        - D: directed graph (DiGraph)
        - arcs: list of tuples (u, v, data) where u not in X and v in X
        - min_weight: minimum weight to be subtracted from the arcs weights
        - A_zero: list to store the arcs that reach weight zero
        - D_zero: directed graph (DiGraph) to store the arcs that reach weight zero

    Returns:
        - None
    """

    for u, v, _ in arcs:
        D[u][v]["w"] -= min_weight
        if D[u][v]["w"] == 0:
            A_zero.append((u, v))
            D_zero.add_edge(u, v)


def has_arborescence(D, r0):
    """
    Check if a directed graph D has an arborescence with root r0.
    The function returns True if an arborescence exists, otherwise False.

    Parameters:
        - D: directed graph (DiGraph)
        - r0: root node

    Returns:
        - bool: True if an arborescence exists, otherwise False
    """

    # Verify if the graph is a DFS tree with root r0
    tree = nx.dfs_tree(D, r0)

    return tree.number_of_nodes() == D.number_of_nodes()


def phase1_find_minimum_arborescence(D_original, r0, draw_fn=None, log=None, boilerplate: bool = True):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a list of arcs.

    Parameters:
        - D_original: directed graph (DiGraph)
        - r0: root node

    Returns:
        - A_zero: list of arcs (u, v) that form the minimum arborescence
        - Dual_list: list of tuples (X, z(X)) representing the dual variables
    """

    D_copy = D_original.copy()
    A_zero = []
    Dual_list = []  # List to store the dual variables (X, z(X))
    D_zero = build_D_zero(D_copy)

    iteration = 0

    while True:
        iteration += 1
        if boilerplate:
            if log:
                log(f"\n 🔄 Iteração {iteration} ----------------------------")
        
        # Calculate the strongly connected components of the graph D_zero.
        C = nx.condensation(
            D_zero
        )  
        if boilerplate:
            if log:
                log(f"\n Componentes fortemente conexos em D_zero:")
                if draw_fn:
                    draw_fn(C, title=f"Componentes fortemente conexos em D_zero - Iteração {iteration}")

        # The sources are where there are no incoming arcs, R0 is always a source.
        sources = [
            x for x in C.nodes() if C.in_degree(x) == 0
        ]

        if boilerplate:
            if log:
                log(f"Fontes: {sources}")

        if (len(sources) == 1):  
            # If there is only one source, it means it is R0 and there are no more arcs to be processed.
            break

        for u in sources:
            X = C.nodes[u]["members"]
            if r0 in X:
                continue
            arcs = get_arcs_entering_X(D_copy, X)
            min_weight = get_minimum_weight_cut(arcs)

            if boilerplate:
                if log:
                    log(f"\n Conjunto X: {X}")
                    log(f"Arestas que entram em X: {arcs}")
                    log(f"Peso mínimo encontrado: {min_weight}")
            
            update_weights_in_X(D_copy, arcs, min_weight, A_zero, D_zero)

            if boilerplate:
                if log:
                    log(f"\n Pesos atualizados nos arcos que entram em X")
            
            # If min_weight is zero, ignore
            if min_weight == 0:
                continue
            else:
                # Otherwise, add to the dual list the set X and its min_weight
                Dual_list.append((X, min_weight))
    return A_zero, Dual_list


def phase2_find_minimum_arborescence(D_original, r0, A_zero, draw_fn=None, log=None, boilerplate: bool = True):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a DiGraph.

    Parameters:
        - D_original: directed graph (DiGraph)
        - r0: root node
        - A_zero: list of arcs (u, v) that form the minimum arborescence

    Returns:
        - Arb: directed graph (DiGraph) representing the minimum arborescence
    """
    Arb = nx.DiGraph()

    # Add the root node
    Arb.add_node(r0)
    n = len(D_original.nodes())

    # While there are arcs to be considered
    for _ in range(n - 1):
        for u, v in A_zero:
            if u in Arb.nodes() and v not in Arb.nodes():
                edge_data = D_original.get_edge_data(u, v)
                Arb.add_edge(u, v, **edge_data)
                # Restart the loop after adding an edge
                break
        if boilerplate:
            if log:
                log(f"\n Arborescência parcial:")
                if draw_fn:
                    draw_fn(Arb, title=f"Arborescência parcial - Iteração {_+1}")     
    return Arb


def phase2_find_minimum_arborescence_v2(D_original, r0, A_zero, draw_fn=None, log=None, boilerplate: bool = True):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a DiGraph.

    Parameters:
        - D_original: directed graph (DiGraph)
        - r0: root node
        - A_zero: list of arcs (u, v) that form the minimum arborescence

    Returns:
        - Arb: directed graph (DiGraph) representing the minimum arborescence
    """
    Arb = nx.DiGraph()
    for i, (u, v) in enumerate(A_zero):
        Arb.add_edge(u, v, w=i)

    # Set of visited vertices, starting with the root
    V = {r0}
    
    # Priority queue to store the edges
    q = []
    for u, v, data in Arb.out_edges(r0, data=True):

        # Add edges to the priority queue with their weights
        heapq.heappush(
            q, (data["w"], u, v)
        )

    A = nx.DiGraph()  # Arborescência resultante

    if boilerplate:
        if log:
            log(f"\n Construindo arborescência usando fila de prioridade:")
            if draw_fn:
                draw_fn(Arb, title=f"Arborescência inicial com pesos - Fase 2")

    # While the queue is not empty
    while q:
        _, u, v = heapq.heappop(q)

        if v in V:  # If the vertex has already been visited, continue
            continue

        # Add the edge to the arborescence
        A.add_edge(u, v, w=D_original[u][v]["w"])

        # Mark the vertex as visited  
        V.add(v)

        # Add the outgoing edges of the visited vertex to the priority queue  
        for x, y, data in Arb.out_edges(v, data=True):
            heapq.heappush(
                q, (data["w"], x, y)
            )

    if boilerplate:
        if log:
            log(f"\n Arborescência final:")
            if draw_fn:
                draw_fn(A, title=f"Arborescência final - Fase 2")        
    # Return the resulting arborescence
    return A


def check_dual_optimality_condition(Arb, Dual_list, log=None, boilerplate: bool = True):
    """
    Verifica a condição dual: z(X) > 0 implica que exatamente uma aresta de Arb entra em X.

    Parameters:
        - Arb: arborescência (DiGraph)
        - Dual_list: lista de tuplas (X, z(X)) representando as variáveis duais
        - r0: nó raiz

    Returns:
        - bool: True se a condição dual é satisfeita, False caso contrário
    """
    for X, z in Dual_list:
        for u, v in Arb.edges():
            count = 0
            if u not in X and v in X:
                count += 1
                if count > 1:
                    if boilerplate:
                        if log:
                            log(f"❌ Falha na condição dual para X={X} com z(X)={z}. Arcos entrando: {count}")
                    return False
    return True

# empacotar as chamadas em função.
def andras_frank_algorithm(D, draw_fn=None, log=None, boilerplate: bool = True):
    if boilerplate:
        if log:
            log(f"\n🔍 Executando algoritmo de András Frank...")
    A_zero, Dual_list = phase1_find_minimum_arborescence(D, "r0", draw_fn=draw_fn, log=log, boilerplate=boilerplate)
    if boilerplate:
        if log:
            log(f"A_zero: {A_zero}")
            log(f"Dual_list: {Dual_list}")
    if not has_arborescence(D, "r0"):
        if boilerplate:
            if log:
                log(f"O grafo não contém uma arborescência com raiz r0.")
        return None, None
    

    arborescencia_frank = phase2_find_minimum_arborescence(D, "r0", A_zero)
    arborescencia_frank_v2 = phase2_find_minimum_arborescence_v2(D, "r0", A_zero)
    dual_frank = check_dual_optimality_condition(arborescencia_frank, Dual_list, "r0")
    dual_frank_v2 = check_dual_optimality_condition(
        arborescencia_frank_v2, Dual_list, "r0"
    )

    if boilerplate:
        if log:
            if dual_frank and dual_frank_v2:
                log(f"✅ Condição dual satisfeita para András Frank.")
            else:
                log(f"❌ Condição dual falhou para András Frank.")
        if draw_fn:
            draw_fn(arborescencia_frank, title="Arborescência de András Frank - Método 1")
            draw_fn(arborescencia_frank_v2, title="Arborescência de András Frank - Método 2")        

    return arborescencia_frank, arborescencia_frank_v2, dual_frank, dual_frank_v2



