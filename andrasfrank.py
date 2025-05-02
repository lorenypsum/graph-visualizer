import networkx as nx

print("Hello, I am Andras Frank.")

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


def build_D_zero(D):
    """
    Build a directed graph D_zero and from the input directed graph D,
    where D_zero contains only the edges with weight zero.
    The function also returns a list of tuples representing the edges with weight zero in D_zero.
    """
    D_zero = nx.DiGraph()
    A_zero = []
    for v in D.nodes():
        D_zero.add_node(v)
    for u, v, data in D.edges(data=True):
        if data["w"] == 0:
            D_zero.add_edge(u, v, **data)
            A_zero.append((u, v))
    return D_zero, A_zero


G_zero, A_zero = build_D_zero(G)

print("G_zero: ", G_zero.nodes(data=True))
print("A_zero: ", A_zero)


def get_ancestors_without_root(D_zero, node, root):
    """
    Get the ancestors of a node in a directed graph D_zero, excluding the root node.
    The function returns a set of ancestors, including the node itself.
    """

    if node == root:
        return None
    ancestors = nx.ancestors(D_zero, node)
    ancestors.discard(root)  # remove a raíz, se estiver presente
    return ancestors | {node}  # inclui o próprio nó


X = get_ancestors_without_root(G_zero, "A", "r0")

print("Conjunto X: ", X)


def get_arcs_entering_X(D, X):
    """
    Get the arcs entering a set of nodes X in a directed graph D.
    The function returns a list of tuples representing the arcs entering X with the designated weights.
    """
    arcs = []
    for u, v, data in D.edges(data=True):
        if u not in X and v in X:
            arcs.append((u, v, data))
    return arcs


arcs = get_arcs_entering_X(G, X)

print("Arcos: ", arcs)


def get_minimum_weight_arcs(arcs):
    """
    Get the minimum weight arcs from a list of arcs.
    The function returns a list of tuples representing the minimum weight arcs.
    """

    min_weight = min(data["w"] for _, _, data in arcs)
    min_arcs = [(u, v, data) for u, v, data in arcs if data["w"] == min_weight]
    return min_arcs, min_weight


min_arcs, min_weight = get_minimum_weight_arcs(arcs)

print("Arco de menor valor: ", min_arcs, min_weight)


def update_weights_in_X(D, X, min_weight, A_zero, D_zero):
    """
    Update the weights of the arcs in a directed graph D for the nodes in set X.
    The function returns a new directed graph with updated weights.
    """

    for u, v, data in D.edges(data=True):
        if u not in X and v in X:
            D[u][v]["w"] -= min_weight
            if D[u][v]["w"] == 0:
                A_zero.append((u, v))
                D_zero.add_edge(u, v, **data)
    return D, D_zero, A_zero


D_updated, D_zero, A_zero = update_weights_in_X(G, X, min_weight, A_zero, G_zero)

print("D_updated: ", D_updated.edges(data=True))

print("D_zero: ", D_zero.edges(data=True))

print("A_zero: ", A_zero)


def phase1_find_minimum_arborescence(D, r0):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a list of arcs.
    """

    D = D.copy()
    A_zero = []
    D_zero, A_zero = build_D_zero(D)
    visited = set()

    iteration = 0  # Contador de iterações

    while True:
        iteration += 1
        print(f"\n🔄 Iteração {iteration} ----------------------------")

        for v in D.nodes():
            if v == r0 or v in visited:
                continue

            print(f"🔍 Verificando nó: {v}")
            X = get_ancestors_without_root(D_zero, v, r0)

            if X is not None:
                print(f"   ↳ Conjunto X (ancestrais de {v} sem a raiz): {X}")
                arcs = get_arcs_entering_X(D, X)
                print(f"   ↳ Arcos que entram em X: {arcs}")

                if not arcs:
                    print(f"   ⚠️ Nenhum arco entra em X. Marcando {v} como visitado.")
                    visited.add(v)
                    continue

                min_arcs, min_weight = get_minimum_weight_arcs(arcs)

                print(f"   ✅ Arco mínimo encontrado: {min_arcs[0]} com peso {min_weight}")
        

                D, D_zero, A_zero = update_weights_in_X(D, X, min_weight, A_zero, D_zero)
                print(f"   🔄 Pesos atualizados nos arcos que entram em X")
                found = True
                break  # reinicia o laço externo    
            else:
                print(f"   ❌ {v} já alcançável a partir da raiz ou sem ancestrais. Marcando como visitado.")
                visited.add(v)

        if not found:
            print("✅ Nenhum novo arco adicionado. Finalizando.")
            break

        if iteration > 50:
            print("🚨 Limite de iterações excedido. Pode haver loop infinito.")
            break

    return A_zero


arborescence = phase1_find_minimum_arborescence(G, "r0")
print("Arborescência mínima:", arborescence)
