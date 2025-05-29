import networkx as nx

id = 1

def log_dummy(msg):
    print(msg)

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

def get_arcs_entering_X(D, X):
    """
    Get the arcs entering a set X in a directed graph D.
    The function returns a list of tuples representing the arcs entering X with the designated weights.
    """
    arcs = []
    for u, v, data in D.edges(data=True):
        if u not in X and v in X:
            arcs.append((u, v, data))
    return arcs
    # return [(u, v, data) for v in X for u, v, data in D.in_edges(v, data=True) if u not in X]


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
    ATTENTION: The function produces collateral effect in the provided directed graph by updating its arcs weights.
    """
    for u, v, data in D.edges(data=True):
        if v in X:
            D[u][v]["w"] -= min_weight
            if D[u][v]["w"] == 0:
                A_zero.append((u, v)) # TODO: Não precisa adicionar a informação do peso, pois é zero.
                D_zero.add_edge(u, v, **data)

def has_arborescence(D, r0):
    """
    Check if a directed graph D has an arborescence with root r0.
    The function returns True if an arborescence exists, otherwise False.
    """
    # Verifica se o grafo é uma árvore DFS com raiz r0
    tree = nx.dfs_tree(D, r0) 
    return tree.number_of_nodes() == D.number_of_nodes() 


def phase1_find_minimum_arborescence(D_original, r0, draw_step=None, log=log_dummy):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a list of arcs.
    """
    global id
    D = D_original.copy()
    A_zero = []
    D_zero, A_zero = build_D_zero(D)

    iteration = 0  # Contador de iterações
    continue_execution = True

    while continue_execution:

        iteration += 1
        log(f"Començando a iteração {iteration} da fase 1 do algoritmo de Andras Frank.")

        continue_execution = False
        for v in D.nodes():
            if v == r0:
                continue

            log(f"🔍 Verificando nó: {v}")
            X = nx.ancestors(D_zero, v)  # Obter ancestrais de v

            if r0 in X:
                log(f"   ⚠️ {v} é ancestral de {r0}. Pulando...")
                continue

            else:

                X.add(v)  # Conjunto de ancestrais de v

                assert X is not None, "X não pode ser vazio." # TODO: 

                log(f" ↳ Conjunto X (ancestrais de {v} sem a raiz): {X}")

                arcs = get_arcs_entering_X(D, X)
                log(f" ↳ Arcos que entram em X: {arcs}")

                min_weight = get_minimum_weight_cut(arcs)

                log(f" ✅ Peso mínimo encontrado: {min_weight}")
                if min_weight:
                    continue_execution = True

                update_weights_in_X(D, X, min_weight, A_zero, D_zero)
                log(f"   🔄 Pesos atualizados nos arcos que entram em X")

            if draw_step:
                draw_step(D.copy(), id=id, title = f"Verificando nó: {v}", description=f"Pesos atualizados nos arcos que entram em X (Interação {iteration} da fase 1)")
                id = id + 1

        if iteration > len(D.edges()):
            log("🚨 Limite de iterações excedido. Pode haver loop infinito.")
            break

    return A_zero

def phase2_find_minimum_arborescence(D_original, r0, A_zero, draw_step=None, log=log_dummy):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a DiGraph.
    """
    global id
    log(f"Començando a fase 2 do algoritmo de Andras Frank.")

    Arb = nx.DiGraph()
    
    # Adiciona-se o nó raiz
    Arb.add_node(r0)
    n = len(D_original.nodes())

    # Enquanto houver arcos a serem considerados
    for i in range(n):
        progress = False  
        for i in range(len(A_zero)):
            u, v = A_zero[i]
            if u in Arb.nodes() and v not in Arb.nodes():
                edge_data = D_original.get_edge_data(u, v)
                Arb.add_edge(u, v, **edge_data)
                log(f"Iteração {i+1}: Aresta adicionada: {u} -> {v} com peso {edge_data['w']}")
                if draw_step:
                    draw_step(Arb, id=id, title = f"Interação {i} da fase 2", description=f"Aresta adicionada: {u} -> {v} com peso {edge_data['w']}")
                    id = id + 1
                progress = True
                break  # Reinicia o loop após adicionar uma aresta
        

        # Se não adicionar nenhuma aresta, termina
        if not progress:
            break
        log(f"Arborescência parcial após iteração {i+1}: {Arb.edges(data=True)}")

    return Arb
            
def find_minimum_arborescence(G, r0="r0", draw_step=None, log=log_dummy):
    T = nx.DiGraph()
    if has_arborescence(G, r0):
        log("O grafo possui uma arborescência.")
        A_zero = phase1_find_minimum_arborescence(G, "r0", draw_step=draw_step, log=log)
        log(f"A_zero: {A_zero}")
        T = phase2_find_minimum_arborescence(G, "r0", A_zero, draw_step=draw_step, log=log)
        log(f"Arborescência mínima encontrada:{T.edges(data=True)}")
    else:
        log("O grafo não possui uma arborescência.")

    return T
