import networkx as nx

print("Hello, I am Chu Liu.")

def log_dummy(msg: str):
    print(msg)

# Funções auxiliar para alterar peso das arestas
def change_edge_weight(G: nx.DiGraph, node: str):

    """
    Altera o peso das arestas de entrada de um nó `node` no grafo `G`.
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
        if v != r0: 
            in_edges = list(G.in_edges(v, data="w"))
            if not in_edges:
                continue  # Nenhuma aresta entra em v
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
    try:
        nodes_in_cycle = set()
        for u, v, _ in nx.find_cycle(F_star, orientation="original"):
            nodes_in_cycle.update([u, v])
        # Retorna o subgrafo contendo apenas o ciclo
        return F_star.subgraph(nodes_in_cycle).copy()
    except nx.NetworkXNoCycle:
        # Se não houver ciclo, retorna None
        return None

# Função auxiliar para contrair um ciclo
def contract_cycle(G: nx.DiGraph, C: nx.DiGraph, label: str):

    """
    Contrai um ciclo C no grafo G, substituindo-o por um supervértice com rótulo `label`.
    Devolve o grafo G modificado "G'"com o ciclo contraído, a lista das arestas de entrada (in_edge) e as de saída (out_edge).
    """

    assert label not in G, f"contract_cycle: O rótulo '{label}' já existe como vértice em G."
    
    cycle_nodes: set[str] = set(C.nodes())
    
    # Armazena o vértice u fora do ciclo e o vértice v dentro do ciclo que recebe a aresta de menor peso
    in_to_cycle: dict[str, tuple[str, float]] = {}

    for u in G.nodes:
        if u not in cycle_nodes: 
            # Encontra a aresta de menor peso de u para algum vértice em C
            min_weight_edge_to_cycle = min(
                ((v, w) for _, v, w in G.out_edges(u, data="w") if v in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_to_cycle:
                in_to_cycle[u] = min_weight_edge_to_cycle

    for u, (v, w) in in_to_cycle.items():
        G.add_edge(u, label, w=w)

    # Armazena o vértice v fora do ciclo que recebe a aresta de menor peso de um vértice u dentro do ciclo
    out_from_cycle: dict[str, tuple[str, float]] = {}

    for v in G.nodes:
        if v not in cycle_nodes: 
            # Encontra a aresta de menor peso que v recebe de algum vértice em C
            min_weight_edge_from_cycle = min(
                ((u, w) for u, _, w in G.in_edges(v, data="w") if u in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if min_weight_edge_from_cycle:
                out_from_cycle[v] = min_weight_edge_from_cycle

    for v, (u, w) in out_from_cycle.items():
        G.add_edge(label, v, w=w)      
    
    # Remove os nós do ciclo original
    G.remove_nodes_from(cycle_nodes)

    return in_to_cycle, out_from_cycle

# Função auxiliar para remover arestas que entram em um vértice raiz
def remove_edges_to_r0(G: nx.DiGraph, r0: str, logger=None):

    """
    Remove todas as arestas que entram no vértice raiz r0 no grafo G.
    Retorna o grafo atualizado.
    """

    # Verifica se r0 existe no grafo
    assert r0 in G, f"remove_edges_to_r0: O vértice raiz '{r0}' não existe no grafo."

    # Remove as arestas que entram em r0
    in_edges = list(G.in_edges(r0))
    if not in_edges:
        if logger:
            logger(f"[INFO] Nenhuma aresta entrando em '{r0}' para remover.")
    else:
        G.remove_edges_from(in_edges)

    return G

# Função auxiliar para remover aresta de um ciclo
def remove_internal_edge_to_cycle_entry(C: nx.DiGraph, external_entry_edge: tuple):

    """
    Remove do ciclo C a aresta interna que entra no vértice de entrada `v`,
    pois `v` agora já recebe uma aresta externa do grafo.
    
    Parâmetros:
    - C: subgrafo do ciclo
    - external_entry_edge: tupla (u, v, w) — aresta externa que conecta o ciclo
    
    Retorna:
    - O ciclo modificado (com uma aresta a menos)
    """

    if not external_entry_edge:
        return C

    _, v, _ = external_entry_edge

    assert v in C, f"O vértice '{v}' da aresta de entrada não está presente no ciclo."

    # Procura uma aresta interna no ciclo que também entra em v
    predecessor = next((u for u, _ in C.in_edges(v)), None)
    if predecessor:
        C.remove_edge(predecessor, v)

    return C


# Algoritmo de Chu-Liu
def find_optimum_arborescence(G: nx.DiGraph, r0: str, level=0, draw_fn=None, log=log_dummy):

    """"
    Encontra recursivamente a arborescência ótima em um grafo direcionado G com raiz r0.
    """

    indent = "  " * level
    log(f"{indent}Iniciando nível {level}")

    assert r0 in G, f"find_optimum_arborescence: O vértice raiz '{r0}' não está presente no grafo."

    G_arb = G.copy()

    if draw_fn:
        draw_fn(G_arb, f"{indent}Após remoção de entradas")

    for v in G_arb.nodes:
        if v != r0:
            change_edge_weight(G_arb, v)

        if draw_fn:
            draw_fn(G_arb, f"{indent}Após ajuste de pesos")

    F_star = get_Fstar(G_arb, r0)

    if draw_fn:
        draw_fn(F_star, f"{indent}F_star")

    if nx.is_arborescence(F_star):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = G[u][v]["w"]
        return F_star
    
    else:
        log(f"{indent}F_star não é uma arborescência. Continuando...")

        C: nx.DiGraph = find_cycle(F_star)

        assert C, f"find_optimum_arborescence: Nenhum ciclo encontrado em F_star."

        contracted_label = f"n*{level}"
        in_to_cycle, out_from_cycle = contract_cycle(G_arb, C, contracted_label)

        # Chamada Recursiva
        F_prime = find_optimum_arborescence(G_arb, r0, level + 1, draw_fn=draw_fn, log=log)

        # Identifica o vértice do ciclo que recebeu a única aresta de entrada da arborescência
        in_edge = next(iter(F_prime.in_edges(contracted_label, data="w")), None)
        assert in_edge, f"find_optimum_arborescence: Nenhuma aresta encontrada entrando no vértice '{contracted_label}'."
        u, _, w = in_edge

        # Identifica o vértice do ciclo que recebeu a aresta de entrada
        # v = next((v_ciclo for v_ciclo, (u_out, _) in in_to_cycle.items() if u_out == u), None)
        v, _ = in_to_cycle.get(u, (None, None))

        # TODO: Confirmar esse trecho fallback (caso de raiz sem mapeamento explícito)
        if v is None:
            # tenta encontrar qualquer vértice do ciclo com aresta de entrada de u
            for v_ciclo in C.nodes:
                if G.has_edge(u, v_ciclo):
                    v = v_ciclo
                    break

        assert v is not None, f"find_optimum_arborescence: Nenhum vértice do ciclo encontrado que recebeu a aresta de entrada de '{u}'."

        # Remove a aresta que entra no vértice `v` do ciclo
        C = remove_internal_edge_to_cycle_entry(C, (u, v, w)) # Nota: w está vindo de F_prime, não de G

        # 1. Adiciona a aresta externa que entra no ciclo (identificada por in_edge)
        # O peso será corrigido no final usando G
        F_prime.add_edge(u, v) 
        log(f"{indent}  Adicionando aresta externa de entrada: ({u}, {v})")

        # 2. Adiciona as arestas restantes do ciclo modificado C
        for u_c, v_c in C.edges:
            F_prime.add_edge(u_c, v_c)
            log(f"{indent}  Adicionando aresta do ciclo: ({u_c}, {v_c})")

        # 3. Adiciona as arestas que saem do ciclo
        # Para cada aresta (contracted_label, z) em F_prime,
        # encontrar a aresta original (u_cycle, z) que a originou usando in_edges.
        for _, z, _ in F_prime.out_edges(contracted_label, data=True):
            # in_edges[z] = (u_cycle, original_weight)
            assert z in out_from_cycle, f"find_optimum_arborescence: Nenhuma aresta de saída encontrada para o vértice '{z}'."
            u_cycle, _ = out_from_cycle[z]
            F_prime.add_edge(u_cycle, z)
            log(f"{indent}  Adicionando aresta externa de saída: ({u_cycle}, {z})")

        # Remove o nó contraído
        assert contracted_label in F_prime, f"Vértice '{contracted_label}' não encontrado no grafo."
        F_prime.remove_node(contracted_label)
        log(f"{indent}  Nó contraído '{contracted_label}' removido.")

        # Atualiza os pesos das arestas com os pesos originais de G
        for u, v in F_prime.edges:
            assert u in G and v in G, f"find_optimum_arborescence: Vértice '{u}' ou '{v}' não encontrado no grafo original."
            F_prime[u][v]["w"] = G[u][v]["w"]
        
        print("Arborescência final:", list(F_prime.edges))
        return F_prime
