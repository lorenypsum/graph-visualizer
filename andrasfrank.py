import networkx as nx
import heapq

print("Hello, I am Andras Frank.")

def build_D_zero(D):
    """
    Build a directed graph D_zero and from the input directed graph D,
    where D_zero contains only the edges with weight zero.
    The function also returns a list of tuples representing the edges with weight zero in D_zero.
    """
    D_zero = nx.DiGraph()
    # A_zero = []
    for v in D.nodes():
        D_zero.add_node(v)
    # for u, v, data in D.edges(data=True):
    #    if data["w"] == 0:
    #        D_zero.add_edge(u, v, **data)
    #        A_zero.append((u, v))
    return D_zero

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

def get_minimum_weight_cut(arcs):
    """
    Get the minimum weight arcs from a list of arcs.
    The function returns a list of tuples representing the minimum weight arcs.
    """
    return min(data["w"] for _, _, data in arcs)

def update_weights_in_X(D, arcs, min_weight, A_zero, D_zero):
    """
    Update the weights of the arcs in a directed graph D for the nodes in set X.
    ATTENTION: The function produces collateral effect in the provided directed graph by updating its arcs weights.
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
    """
    # Verifica se o grafo é uma árvore DFS com raiz r0
    tree = nx.dfs_tree(D, r0) 
    return tree.number_of_nodes() == D.number_of_nodes() 

def phase1_find_minimum_arborescence(D_original, r0):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a list of arcs.
    """
    D_copy = D_original.copy()
    A_zero = []
    D_zero = build_D_zero(D_copy)

    iteration = 0  # Contador de iterações
    
    while True:
        iteration += 1
        print(f"\n 🔄 Iteração {iteration} ----------------------------")
        C = nx.condensation(D_zero) # Calcula os componentes fortemente conexos do grafo D_zero.
        sources = [x for x in C.nodes() if C.in_degree(x) == 0] # As fontes é onde não nenhum arco entrando, o R0 sempre é uma fonte.
        print('Fontes: ', sources)
        if len(sources) == 1: # Se houver apenas uma fonte, significa que é o R0 e não há mais arcos a serem processados.
            break
        for u in sources:
            X = C.nodes[u]['members']
            if r0 in X:
                continue
            arcs = get_arcs_entering_X(D_copy, X)
            min_weight = get_minimum_weight_cut(arcs)
            print(f"\n ✅ Peso mínimo encontrado: {min_weight}")
            update_weights_in_X(D_copy, arcs, min_weight, A_zero, D_zero)
            print(f"\n 🔄 Pesos atualizados nos arcos que entram em X")
    return A_zero

def phase2_find_minimum_arborescence(D_original, r0, A_zero):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a DiGraph.
    """
    Arb = nx.DiGraph()
    
    # Adiciona-se o nó raiz
    Arb.add_node(r0)
    n = len(D_original.nodes())

    # Enquanto houver arcos a serem considerados
    for _ in range(n - 1):
        for u, v in A_zero:
            if u in Arb.nodes() and v not in Arb.nodes():
                edge_data = D_original.get_edge_data(u, v)
                Arb.add_edge(u, v, **edge_data)
                break  # Reinicia o loop após adicionar uma aresta
    return Arb

def phase2_find_minimum_arborescence_v2(D_original, r0, A_zero):
    """
    Find the minimum arborescence in a directed graph D with root r0.
    The function returns the minimum arborescence as a DiGraph.
    """
    D = nx.DiGraph()
    for i, (u, v) in enumerate(A_zero):
        D.add_edge(u, v, w=i)
    V = {r0}  # Conjunto de vértices visitados, começando com a raiz
    q = []  # Fila de prioridade para armazenar os arcos
    for (u, v, data) in D.out_edges(r0, data=True):
        heapq.heappush(q, (data["w"], u, v))  # Adiciona os arcos de saída da raiz à fila de prioridade
    
    A = nx.DiGraph()  # Arborescência resultante
    
    while q:  # Enquanto a fila não estiver vazia
        #u, v = min(q, key=lambda x: x[1])  # Remove o arco com o menor peso
        _, u, v = heapq.heappop(q)
        if v in V:  # Se o vértice já foi visitado, continua
            continue
        A.add_edge(u, v, w = D_original[u][v]["w"])  # Adiciona o arco à arborescência
        V.add(v)  # Marca o vértice como visitado
        for (x, y, data) in D.out_edges(v, data=True):
            heapq.heappush(q, (data["w"], x, y))  # Adiciona os arcos de saída do vértice visitado à fila de prioridade
    return A  # Retorna a arborescência resultante