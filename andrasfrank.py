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


def get_arcs_entering_X(X):
    """
    Get the arcs entering a set of nodes X in a directed graph D.
    The function returns a list of tuples representing the arcs entering X with the designated weights.
    """
    arcs = []
    for u, v, data in X.edges(data=True):
        if u not in X and v in X:
            arcs.append((u, v, data))
    return arcs


def get_minimum_weight_cut(arcs):
    """
    Get the minimum weight arcs from a list of arcs.
    The function returns a list of tuples representing the minimum weight arcs.
    """
    min_weight = min(data["w"] for _, _, data in arcs)
    return min_weight


def update_weights_in_X(D, X, min_weight, A_zero, D_zero):
    """
    Update the weights of the arcs in a directed graph D for the nodes in set X.
    ATTENTION: The function produces colateral effect in the provided directed graph by updating its arcs weights.
    """
    for u, v, data in X.edges(data=True):
        D[u][v]["w"] -= min_weight
        if D[u][v]["w"] == 0:
            A_zero.append((u, v))
            D_zero.add_edge(u, v, **data)
    return D_zero, A_zero


def has_arborescence(D, r0):
    """
    Check if a directed graph D has an arborescence with root r0.
    The function returns True if an arborescence exists, otherwise False.
    """
    has_arborescence = True
    for v in D.nodes():
        if nx.has_path(D, r0, v) == False:
            has_arborescence = False
            break
    return has_arborescence


def phase1_find_minimum_arborescence(D_original, r0):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a list of arcs.
    """

    D = D_original.copy()
    A_zero = []
    D_zero, A_zero = build_D_zero(D)

    iteration = 0  # Contador de iterações

    while True:
        iteration += 1
        print(f"\n🔄 Iteração {iteration} ----------------------------")

        for v in D.nodes():
            if v == r0:
                continue

            print(f"🔍 Verificando nó: {v}")
            X = nx.ancestors(D, v)  # Obter ancestrais de v

            assert X is not None, "X não pode ser vazio"

            print(f" ↳ Conjunto X (ancestrais de {v} sem a raiz): {X}")

            arcs = get_arcs_entering_X(D, X)
            print(f" ↳ Arcos que entram em X: {arcs}")

            # TODO:  NÃO FAZER ISSO AGORA
            # if not arcs:
            #     print(f"   ⚠️ Nenhum arco entra em X.")
            #     continue

            min_weight = get_minimum_weight_cut(arcs)

            print(f" ✅ Peso mínimo encontrado: {min_weight}")

            D_zero, A_zero = update_weights_in_X(D, X, min_weight, A_zero, D_zero)
            print(f"   🔄 Pesos atualizados nos arcos que entram em X")
            
            found = True
            # TODO: continue_execution = TRUE, quando entra no laço fica falso. Quando entrar na condicao de pegar o peso minimo levo pra TRUE. e ai ele para.
            break  # reinicia o laço externo

        if not found:
            print("✅ Nenhum novo arco adicionado. Finalizando.")
            break

        if iteration > 50:
            print("🚨 Limite de iterações excedido. Pode haver loop infinito.")
            break

    return A_zero


# arborescence = phase1_find_minimum_arborescence(G, "r0")
# print("Arborescência mínima:", arborescence)
