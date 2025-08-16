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
    Dual_list = []  # Lista para armazenar os pares (X, min_weight)
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
            # Se o min_weight for zero ignora
            if min_weight == 0:
                continue
            # Caso contrário que a lista dual onde entra o X e o min_weight
            Dual_list.append((X, min_weight))
            print(f"\n ✅ Peso mínimo encontrado: {min_weight}")
            update_weights_in_X(D_copy, arcs, min_weight, A_zero, D_zero)
            print(f"\n 🔄 Pesos atualizados nos arcos que entram em X")
    return A_zero, Dual_list

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
        # u, v = min(q, key=lambda x: x[1])  # Remove o arco com o menor peso
        _, u, v = heapq.heappop(q)
        if v in V:  # Se o vértice já foi visitado, continua
            continue
        A.add_edge(u, v, w = D_original[u][v]["w"])  # Adiciona o arco à arborescência
        V.add(v)  # Marca o vértice como visitado
        for (x, y, data) in D.out_edges(v, data=True):
            heapq.heappush(q, (data["w"], x, y))  # Adiciona os arcos de saída do vértice visitado à fila de prioridade
    return A  # Retorna a arborescência resultante

# Escrever uma função para chamar a fase 1 e a fase 2, 
# empacotar as chamadas em função.
def andras_frank_algorithm(D1):
    print("\n🔍 Executando algoritmo de András Frank...")
    A_zero = phase1_find_minimum_arborescence(D1, "r0")
    arborescencia_frank = phase2_find_minimum_arborescence(D1,"r0", A_zero)
    arborescencia_frank_v2 = phase2_find_minimum_arborescence_v2(D1, "r0", A_zero)
    return arborescencia_frank, arborescencia_frank_v2

# O conjunto X devolvido na linha 80
# prega o caso no qual o r0 n # pertence ao conjunto X, ou seja, o r0 é uma fonte.
# Pega o par X, minweight em uma lista de pares
# Além do A_zero tem que devolver essa lista
# Pois essa lista constitui uma solução para o problema dual
# Ai na fase 2, pegamos essa lista que é solução para o dual
# que estamos chamado de lista dual D = [x1, y1; x2, y2; ...]
# E construimos a fase 2. A fase 2 devolve uma arborescencia
# Precisamos criar uma função para checar se as soluçoes estão corretas
# O algoritmo prova que é uma arboreescencia
# Checar que a solucáo é correta
# 1. Arb tem que ser uma arborescencia
# 2. Para cada xi, yi em D, tem que existir um arco de arb que entra em xi e apenas um
# Escrever uma função para verificar essas condições estão sendo satisfeitas
# basicamente checar a seguinte condição:
# z(X) > 0 implies ϱF (X)= 1.


# def check_solution(Arb, D, A_zero):
#     """
#     Check if the solution is a valid arborescence.
#     The function checks if Arb is an arborescence and if each (x, y) in A_zero has an incoming arc in Arb.
#     """
#     # Check if Arb is an arborescence
#     if not has_arborescence(Arb, list(Arb.nodes())[0]):
#         return False
    
#     # Check if each (x, y) in A_zero has an incoming arc in Arb
#     for u, v in A_zero:
#         if not Arb.has_edge(u, v):
#             return False
    
#     return True

# basicamente checar a seguinte condição:
# z(X) > 0 implies ϱF (X)= 1.

# Para cada cara que o zi deu maior que zero, deve ter exatamente um arco
# da arborescencia que entra em xi
# [(x1, z1), (x2, z2), ... ]
# Na implementação devemos não colocar na lista quando o min-weight for zero.
# Na linha 86 do código, quando o min-weight for zero, não devemos adicionar o arco na lista A_zero.
# Talvez a melhor ideia pode ser colocar e ignorar, se o min-weight for zero, dá um continue.
# Se não fazemos o update_weights_in_X, não atualiza o D_zero, e não adiciona o arco na lista A_
# Esse X é o min_weight, do algoritmo.

# Fazemos primeiro essa versão do Frank
# E depois fazemos na versão do Edmonds, que é mais dificil, pois precisa ficar descontraindo
# Verificar essas coisas prova a corretude.


