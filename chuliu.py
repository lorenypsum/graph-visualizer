import networkx as nx

def log(msg: str):
    print(msg)

# Funções auxiliar para alterar peso das arestas
def change_edge_weight(G: nx.DiGraph, node: str):

    """
    Altera o peso das arestas de entrada de um nó `node` no grafo `G`.
    """

    # Verifica se o vértice existe
    if node not in G:
        raise ValueError(f"O vértice '{node}' não existe no grafo.")

    # Obtém predecessores com pesos
    predecessors = list(G.in_edges(node, data="w"))

    if not predecessors:
        return G  # ← ESSA LINHA FALTA NO SEU CÓDIGO ATUAL

    # Calcula Yv = menor peso de entrada
    yv = min((w for _, _, w in predecessors))

    # Subtrai Yv de cada aresta de entrada
    for u, _, _ in predecessors:
        G[u][node]["w"] -= yv

    return G

# Função auxiliar para definir conjunto F_star
def get_Fstar(G: nx.DiGraph, r0: str):

    """
    Cria o conjunto F_star a partir do grafo G e da raiz r0.
    """

    # Verifica se a raiz existe no grafo
    if r0 not in G:
        raise ValueError(f"O vértice raiz '{r0}' não existe no grafo.")

    F_star = nx.DiGraph()

    for v in G.nodes():
        if v != r0:
            in_edges = list(G.in_edges(v, data="w"))
            if not in_edges:
                continue  # Nenhuma aresta entra em v
            # Tenta encontrar uma aresta com custo 0
            u = next((u for u, _, w in in_edges if w == 0), None)
            if u:
                F_star.add_edge(u, v, w=0)

    successors = list(G.out_edges(r0, data="w"))
    if not successors:
        raise ValueError(f"O vértice raiz '{r0}' não possui arestas de saída.")

    # Aresta de menor custo saindo da raiz
    v, w = min([(v, w) for _, v, w in successors], key=lambda vw: vw[1])
    F_star.add_edge(r0, v, w=w)

    return F_star

# Função auxiliar para verificar se F_star é uma arborescência
def is_F_star_arborescence(F_star: nx.DiGraph, r0: str):

    """
    Verifica se o grafo F_star é uma arborescência com raiz r0.
    """

    # Verifica se o vértice raiz existe no grafo
    if r0 not in F_star:
        raise ValueError(f"O vértice raiz '{r0}' não existe no grafo.")

    # Se o grafo estiver vazio
    if F_star.number_of_nodes() == 0:
        raise ValueError("O grafo fornecido está vazio.")

    # Verifica se o grafo é acíclico e todos os nós são alcançáveis a partir de r0
    is_reachable = all(nx.has_path(F_star, r0, v) for v in F_star.nodes)
    is_acyclic = nx.is_directed_acyclic_graph(F_star)

    return is_reachable and is_acyclic

# Função auxiliar para encontrar um ciclo no grafo
def find_cycle(F_star: nx.DiGraph):

    """
    Encontra um ciclo direcionado / circuito no grafo.
    Retorna um subgrafo contendo o ciclo, ou None se não houver.
    """

    # Verifica se o grafo tem nós suficientes para conter um ciclo
    if F_star.number_of_edges() == 0 or F_star.number_of_nodes() < 2:
        return None

    # Tenta encontrar um ciclo no grafo
    nodes_in_cycle = set()
    for u, v, _ in nx.find_cycle(F_star, orientation="original"):
        nodes_in_cycle.update([u, v])

    # Retorna o subgrafo contendo apenas o ciclo
    return F_star.subgraph(nodes_in_cycle)

# Função auxiliar para contrair um ciclo
def contract_cycle(G: nx.DiGraph, C: nx.DiGraph, label: str):

    """
    Contrai um ciclo C no grafo G, substituindo-o por um supernó com rótulo `label`.
    Devolve o novo grafo (G'), a aresta de entrada (in_edge) e a de saída (out_edge).
    """

    if label in G:
        raise ValueError(f"O rótulo '{label}' já existe como vértice em G.")

    cycle_nodes: set[str] = set(C.nodes())
    
    # TODO: Criar um dicionário auxiliar para armazenar para cada u o nome original do arco v em c
    out_edges: dict[str, tuple[str, float]] = {}

    for u in G.nodes:
        if u not in cycle_nodes: 
            # Encontra a aresta de menor peso de u para algum vértice em C
            out_edge = min(
                ((v, w) for _, v, w in G.out_edges(u, data="w") if v in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if out_edge:
                out_edges[u] = out_edge

    for u, (v, w) in out_edges.items():
        G.add_edge(u, label, w=w)

    # Encontra arestas de ciclo -> fora
    in_edges: dict[str, tuple[str, float]] = {}

    for v in G.nodes:
        if v not in cycle_nodes: 
            # Encontra a aresta de menor peso que v recebe de algum vértice em C
            in_edge = min(
                ((u, w) for u, _, w in G.in_edges(u, data="w") if u in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if in_edge:
                in_edges[v] = in_edge

    for u, (v, w) in in_edges.items():
        G.add_edge(label, v, w=w)      
    
    # Remove os nós do ciclo original
    G.remove_nodes_from(cycle_nodes)

    return out_edges, in_edges

# Função auxiliar para remover arestas que entram em um vértice raiz
def remove_edge_in_r0(G: nx.DiGraph, r0: str):

    """
    Remove todas as arestas que entram no vértice raiz r0 no grafo G.
    Retorna o grafo atualizado.
    """

    # Verifica se r0 existe no grafo
    if r0 not in G:
        raise ValueError(f"O vértice raiz '{r0}' não existe no grafo.")

    # Remove as arestas que entram em r0
    in_edges = list(G.in_edges(r0))
    if not in_edges:
        log(f"[INFO] Nenhuma aresta entrando em '{r0}' para remover.")
    else:
        G.remove_edges_from(in_edges)

    return G

# Função auxiliar para remover aresta de um ciclo
def remove_edge_from_cycle(C: nx.DiGraph, in_edge: tuple[str, str, float]):

    """
    Remove do ciclo C a aresta que entra no vértice `v` (obtido de `in_edge`)
    caso esse vértice já tenha um predecessor em C.
    """

    C = C.copy()  # Cópia segura

    if in_edge:
        if len(in_edge) != 3:
            raise ValueError("A aresta in_edge deve ter 3 elementos (u, v, w).")
        _, v, _ = in_edge

        if v not in C:
            raise ValueError(
                f"O vértice destino '{v}' da in_edge não está presente no ciclo."
            )

        # Procura um predecessor em C que leva até v
        u = next((u for u, _ in C.in_edges(v)), None)
        if u:
            C.remove_edge(u, v)
    return C

# Algoritmo de Chu-Liu
def find_optimum_arborescence(G: nx.DiGraph, r0: str, level=0, draw_fn=None):

    """"
    Encontra recursivamente a arborescência ótima em um grafo direcionado G com raiz r0.
    """

    indent = "  " * level
    log(f"{indent}Iniciando nível {level}")

    if r0 not in G:
        raise ValueError(f"O vértice raiz '{r0}' não está presente no grafo.")

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

    if is_F_star_arborescence(F_star, r0):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = G[u][v]["w"]
        return F_star
    
    else:

        log(f"{indent}F_star não é uma arborescência. Continuando...")

        C = find_cycle(F_star)

        contracted_label = f"C*{level}"
        out_edges, in_edges = contract_cycle(G_arb, C, contracted_label)

        # Chamada Recursiva
        F_prime = find_optimum_arborescence(G_arb, r0, level + 1, draw_fn=draw_fn)

        # Identifica o vértice do ciclo que recebeu a única aresta de entrada da arborescência
        candidatos = [
            v for v in in_edges if v in C and F_prime.in_degree(v) == 1
        ]

        if not candidatos:
            raise ValueError(
            "[ERRO] A solução recursiva não utilizou nenhuma entrada externa para o ciclo, "
            "o que viola o algoritmo de Chu-Liu/Edmonds. Isso indica erro na contração ou reconstrução."
        )
        else:
            vertice_reentrada = candidatos[0]
            u, w = in_edges[vertice_reentrada]
            edge_to_remove = (u, vertice_reentrada, w)
            C = remove_edge_from_cycle(C, edge_to_remove)

        for u, v in C.edges:
            F_prime.add_edge(u, v)
        for v, (u, w) in out_edges.items():
            F_prime.add_edge(u, v)
        for u, (v, w) in in_edges.items():
            F_prime.add_edge(u, v)
            
        if contracted_label in F_prime:
            F_prime.remove_node(contracted_label)
        else:
            log(f"[AVISO] Vértice '{contracted_label}' não encontrado para remoção.")    

        for u, v in F_prime.edges:
            if G.has_edge(u, v):
                F_prime[u][v]["w"] = G[u][v]["w"]
            else:
                print(f"[AVISO] Aresta ({u} → {v}) não encontrada no grafo original.")
        
        print("Arborescência final:", list(F_prime.edges))
        return F_prime
