import networkx as nx

def log_dummy(msg: str):
    print(msg)

# Funções auxiliar para alterar peso das arestas
def change_edge_weight(G: nx.DiGraph, node: str):

    """
    Altera o peso das arestas de entrada de um nó node no grafo G.
    """

    assert node in G, f"change_edge_weight: O vértice '{node}' não existe no grafo."

    # Obtém predecessores com pesos
    predecessors = list(G.in_edges(node, data="w"))

    if not predecessors:
        return

    # Calcula Yv = menor peso de entrada
    yv = min((w for _, _, w in predecessors))

    # Subtrai Yv de cada aresta de entrada
    for u, _, _ in predecessors:
        G[u][node]["w"] -= yv

# Função auxiliar para definir conjunto F_star
def get_Fstar(G: nx.DiGraph, r0: str):

    """
    Cria o conjunto F_star a partir do grafo G e da raiz r0.
    """

    assert r0 in G, f"get_Fstar: O vértice raiz '{r0}' não existe no grafo."

    F_star = nx.DiGraph()

    for v in G.nodes():
        # Mais fácil: Se v =/ r0, jogar todas arestas de custo zero ao invés de apenas uma (com o next).
        # Isso pode fazer o algoritmo executar menos passos.
        # Mas, precisaria mudar a forma de verificar se F_star é uma arborescência.
        # Verificar se F_star contém uma arborescência, mas a biblioteca parece não ter essa função.
        if v != r0:
            in_edges = list(G.in_edges(v, data="w"))
            if not in_edges:
                continue  # Nenhuma aresta entra em v
            # Tenta encontrar uma aresta com custo 0
            for u, _, w in in_edges:
                if w == 0:
                    F_star.add_edge(u, v, w=w)
            u = next((u for u, _, w in in_edges if w == 0), None)
            if u:
                F_star.add_edge(u, v, w=0)

    return F_star

# Função auxiliar para encontrar um ciclo no grafo
def find_cycle(F_star: nx.DiGraph):

    """
    Encontra um ciclo direcionado / circuito no grafo.
    Retorna um subgrafo contendo o ciclo, ou None se não houver.
    """

    # Tenta encontrar um ciclo no grafo
    return nx.Digraph(nx.find_cycle(F_star))

# Função auxiliar para contrair um ciclo
def contract_cycle(G: nx.DiGraph, C: nx.DiGraph, label: str):

    """
    Contrai um ciclo C no grafo G, substituindo-o por um supervértice com rótulo label.
    Devolve o grafo G modificado "G'"com o ciclo contraído, a lista das arestas de entrada (in_edge) e as de saída (out_edge).
    """

    assert label not in G, f"contract_cycle: O rótulo '{label}' já existe como vértice em G."


    # Armazena o vértice u fora do ciclo e o vértive v dentro do ciclo que recebe a aresta de menor peso
    out_edges: dict[str, str] = {}

    V = set(G.nodes)
    for u in V:
        if u not in C.nodes:
            # Encontra a aresta de menor peso de u para algum vértice em C
            out_edge = min(
                ((v, w) for _, v, w in G.out_edges(u, data="w") if v in C.nodes),
                key=lambda x: x[1],
                default=None,
            )
            if out_edge:
                out_edges[u] = out_edge[0]
                G.add_edge(u, label, w=out_edge[1])

    # Armazena o vértice v fora do ciclo que recebe a aresta de de menor peso de um vértice u dentro do ciclo
    in_edges: dict[str, str] = {}

    for v in V:
        if v not in C.nodes:
            # Encontra a aresta de menor peso que v recebe de algum vértice em C
            in_edge = min(
                ((u, w) for u, _, w in G.in_edges(v, data="w") if u in C.nodes),
                key=lambda x: x[1],
                default=None,
            )
            if in_edge:
                in_edges[v] = in_edge[0]
                G.add_edge(label, v, w=in_edge[1])



    # Remove os nós do ciclo original
    G.remove_nodes_from(C.nodes)

    return out_edges, in_edges

# Função auxiliar para remover aresta de um ciclo
def remove_edge_from_cycle(C: nx.DiGraph, v: str):
    u, v = next(iter(C.in_edges(v)))
    C.remove_edge(u, v)
    return C


# Algoritmo de Chu-Liu
def find_optimum_arborescence(G: nx.DiGraph, r0: str, level=0, id=1, draw_fn=None, draw_step=None, log=log_dummy):

    """
    Encontra recursivamente a arborescência ótima em um grafo direcionado G com raiz r0.
    """

    indent = "  " * level
    log(f"{indent}Iniciando nível {level}")
    G_arb = G.copy()

    if draw_step:
        draw_step(G_arb, id=id, title = f"Após remoção de entradas", description=f"Removendo arestas de entrada de {r0} para evitar ciclos.")

    for v in G_arb.nodes:
        if v != r0:
            change_edge_weight(G_arb, v)

        id=id + 1
        if draw_step:
            draw_step(G_arb, id=id, title = f"Ajuste de pesos", description=f"Ajustando pesos das arestas de entrada de {v}")

    F_star = get_Fstar(G_arb, r0)

    id=id + 1
    if draw_step:
        draw_step(F_star, id=id, title = f"F_star", description=f"Conjunto F* (arestas de custo zero após ajuste dos pesos de entrada de cada vértice, exceto a raiz).")

    if nx.is_arborescence(F_star):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = G[u][v]["w"]
        return F_star
    else:
        log(f"{indent}F_star não é uma arborescência. Continuando...")
        C = nx.DiGraph(nx.find_cycle(F_star))
        contracted_label = f"C*{level}"
        out_edges, in_edges = contract_cycle(G_arb, C, contracted_label)
        F_prime = find_optimum_arborescence(G_arb, r0, level + 1, id, draw_fn, draw_step, log=log)
        
        u, _ = next(iter(F_prime.in_edges(contracted_label)), None)

        # Identifica o vértice do ciclo que recebeu a aresta de entrada
        v = out_edges[u]
        
        # Remove a aresta que entra no vértice v do ciclo
        C.remove_edge(*next(iter(C.in_edges(v))))
        
        # 1. Adiciona a aresta externa que entra no ciclo (identificada por in_edge)
        # O peso será corrigido no final usando G
        F_prime.add_edge(u, v)
        # 2. Adiciona as arestas restantes do ciclo modificado C
        F_prime.add_edges_from(C.edges)

        # 3. Adiciona as arestas que saem do ciclo
        # Para cada aresta (contracted_label, z) em F_prime,
        # encontrar a aresta original (u_cycle, z) que a originou usando in_edges.
        for _, z in F_prime.out_edges(contracted_label):
            u_cycle = in_edges[z]
            F_prime.add_edge(u_cycle, z)
            log(f"{indent}  Adicionando aresta externa de saída: ({u_cycle}, {z})")
        # Remove o nó contraído
       
        F_prime.remove_node(contracted_label)
        log(f"{indent}  Nó contraído '{contracted_label}' removido.")
        
        # Atualiza os pesos das arestas com os pesos originais de G
        for u, v in F_prime.edges:
            F_prime[u][v]["w"] = G[u][v]["w"]
        
        log(f"Arborescência final: {list(F_prime.edges)}")
        return F_prime
