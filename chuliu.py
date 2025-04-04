import networkx as nx

# Funções auxiliares ao algoritmo de Chu-Liu
def change_edge_weight(G: nx.DiGraph, node: str):
    # Verifica se o nó existe
    if node not in G:
        raise ValueError(f"O nó '{node}' não existe no grafo.")

    # Obtém predecessores com pesos
    predecessors = list(G.in_edges(node, data="w"))

    # Calcula Yv = menor peso de entrada
    yv = min((w for _, _, w in predecessors))

    # Subtrai Yv de cada aresta de entrada
    for u, _, _ in predecessors:
        G[u][node]["w"] -= yv

    return G


def get_Fstar(G: nx.DiGraph, r0: str):
    # Verifica se a raiz existe no grafo
    if r0 not in G:
        raise ValueError(f"O nó raiz '{r0}' não existe no grafo.")

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
        raise ValueError(f"O nó raiz '{r0}' não possui arestas de saída.")

    # Aresta de menor custo saindo da raiz
    v, w = min([(v, w) for _, v, w in successors], key=lambda vw: vw[1])
    F_star.add_edge(r0, v, w=w)

    return F_star


def is_F_star_arborescence(F_star: nx.DiGraph, r0: str):
    # Verifica se o nó raiz existe no grafo
    if r0 not in F_star:
        raise ValueError(f"O nó raiz '{r0}' não existe no grafo.")

    # Se o grafo estiver vazio
    if F_star.number_of_nodes() == 0:
        raise ValueError("O grafo fornecido está vazio.")

    # Verifica se o grafo é acíclico e todos os nós são alcançáveis a partir de r0
    is_reachable = all(nx.has_path(F_star, r0, v) for v in F_star.nodes)
    is_acyclic = nx.is_directed_acyclic_graph(F_star)

    return is_reachable and is_acyclic


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


def contract_cycle(G: nx.DiGraph, C: nx.DiGraph, label: str):
    """
    Contrai um ciclo C no grafo G, substituindo-o por um supernó com rótulo `label`.
    Devolve o novo grafo (G'), a aresta de entrada (in_edge) e a de saída (out_edge).
    """
    if label in G:
        raise ValueError(f"O rótulo '{label}' já existe como nó em G.")

    cycle_nodes: set[str] = set(C.nodes())

    # TODO Encontra arestas de fora -> ciclo
    # Fazer um filtro dos vértices que estão fora de C
    # Para cada um deles, faz outro filtro: pegando os arcos
    # que tem uma ponta nele e outra dentro de C
    # Generator expression, tratar caso devolva um None
    # "Para cada vértice u fora de C, determina o arco de menor custo
    # que tem uma ponta em u e outra
    # em algum vértice de C. E ficar some com aqueles que estão em C
    # escolhendo a aresta minima
    # Posso ter um arco que não tem um vértice na vizinhança de C
    # Fazer a mesma coisa para quem tá saindo

    # HOW_TO_FIX 
    # Arestas de fora para o ciclo (in_edges):
        # Para cada nó fora do ciclo (u), encontre a aresta de menor peso que conecta u a um nó dentro do ciclo (v).
        # Use uma expressão geradora para filtrar as arestas de entrada de G e selecione a de menor peso.
    # Arestas do ciclo para fora (out_edges):
        # Para cada nó dentro do ciclo (u), encontre a aresta de menor peso que conecta u a um nó fora do ciclo (v).
        # Use uma lógica semelhante para filtrar as arestas de saída de G.
    # Tratamento de casos especiais:
    #   Certifique-se de lidar com casos onde não há arestas válidas (retornar None ou ignorar).

    in_edges: dict[str, tuple[str, float]] = {}
    for u in G.nodes:
        if u not in cycle_nodes:
            # Encontra a aresta de menor peso de u para algum nó em C
            in_edge = min(
                ((v, w) for _, v, w in G.out_edges(u, data="w") if v in cycle_nodes),
                key=lambda x: x[1],
                default=None,
            )
            if in_edge:
                in_edges[u] = in_edge

    for u, (v, w) in in_edges.items():
        G.add_edge(u, label, w=w)

    # Encontra arestas de ciclo -> fora
    out_edges: dict[str, tuple[str, float]] = {}
    
    for u in cycle_nodes: 
        out_edge = min(
            ((v, w) for _, v, w in G.out_edges(u, data="w") if v not in cycle_nodes),
            key=lambda x: x[1],  
            default=None,        
        )
        if out_edge:
            out_edges[u] = out_edge  # Armazena a aresta de menor peso

    for u, (v, w) in out_edges.items():
        G.add_edge(label, v, w=w)      
    

    # Remove os nós do ciclo original
    G.remove_nodes_from(cycle_nodes)

    return in_edges, out_edges


def remove_edge_in_r0(G: nx.DiGraph, r0: str):
    """
    Remove todas as arestas que entram no nó raiz r0 no grafo G.
    Retorna o grafo atualizado.
    """
    # Verifica se r0 existe no grafo
    if r0 not in G:
        raise ValueError(f"O nó raiz '{r0}' não existe no grafo.")

    # Remove as arestas que entram em r0
    in_edges = list(G.in_edges(r0))
    if not in_edges:
        log(f"[INFO] Nenhuma aresta entrando em '{r0}' para remover.")
    else:
        G.remove_edges_from(in_edges)

    return G


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
def find_optimum_arborescence(G: nx.DiGraph, r0: str, level=0):
    indent = "  " * level
    log(f"{indent}Iniciando nível {level}")
    if r0 not in G:
        raise ValueError(f"O nó raiz '{r0}' não está presente no grafo.")

    G_arb = G.copy()
    draw_graph(G_arb, f"{indent}Grafo original")
    remove_edge_in_r0(G_arb, r0)
    draw_graph(G_arb, f"{indent}Após remoção de entradas")

    for v in G_arb.nodes:
        if v != r0:
            change_edge_weight(G_arb, v)
    draw_graph(G_arb, f"{indent}Após ajuste de pesos")

    F_star = get_Fstar(G_arb, r0)
    draw_graph(F_star, f"{indent}F_star")

    if is_F_star_arborescence(F_star, r0):
        for u, v in F_star.edges:
            F_star[u][v]["w"] = G[u][v]["w"]
        return F_star

    C = find_cycle(F_star)

    contracted_label = f"C*{level}"
    in_edges, out_edges = contract_cycle(G_arb, C, contracted_label)
    F_prime = find_optimum_arborescence(G_arb, r0, level + 1)

    # Dúvida: como escolher a aresta que vamos remover do ciclo?
    # Provisoriamente, escolhemos a aresta de maior peso
    # Resposta: Eu vou remover a aresta que chega no vértice v que recebe a única aresta da arborescência
    # Criar um dicionário auxiliar para armazenas para cada u qual era o nome original do arco u  para v em C.
    edge_to_remove = max(
        ((u, v, w) for v, (u, w) in in_edges.items()), key=lambda x: x[2]
    )

    C = remove_edge_from_cycle(C, edge_to_remove)
    for u, v in C.edges:
        F_prime.add_edge(u, v)
    for v, (u, w) in in_edges.items():
        F_prime.add_edge(u, v, w=w)
    for u, (v, w) in out_edges.items():
        F_prime.add_edge(u, v, w=w)
    if contracted_label in F_prime:
        F_prime.remove_node(contracted_label)

    for u, v in F_prime.edges:
        F_prime[u][v]["w"] = G[u][v]["w"]
    return F_prime
