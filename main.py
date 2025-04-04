import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from js import Blob, URL, document, alert
from pyscript import when, display
import json


def log(msg: str):
    log_box = document.getElementById("log-output")
    log_box.value += msg + "\n"
    log_box.scrollTop = log_box.scrollHeight


def draw_graph(G: nx.DiGraph, title="Digrafo", append=True):
    plt.clf()  # Limpa a figura atual
    pos = nx.planar_layout(G)  # Layout para posicionamento dos nós
    plt.figure(figsize=(6, 4))  # Tamanho da figura
    # Desenha os nós e arestas
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=2000,
        font_size=12,
    )
    weights = nx.get_edge_attributes(G, "w")
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=weights, font_color="red", font_size=12
    )
    plt.title(title)
    display(title, target="graph-area", append=append)
    display(plt, target="graph-area", append=append)
    plt.close()  # Fecha a figura para liberar memória


G = nx.DiGraph()


@when("click", "#add-edge")
def add_edge():
    global G
    source = document.getElementById("source").value
    target = document.getElementById("target").value
    weight = document.getElementById("weight").value
    if source and target and weight:
        G.add_edge(source, target, w=float(weight))
        log(f"Aresta adicionada: {source} → {target} (peso={weight})")
        draw_graph(G, "Grafo com Arestas", append=False)


@when("click", "#reset-graph")
def reset_graph():
    global G
    G.clear()
    document.getElementById("log-output").value = ""
    draw_graph(G, "Grafo Resetado", append=False)
    log("Grafo resetado.")


@when("click", "#export-graph")
def export_graph(event):
    log("Exportando grafo...")
    global G
    if G.number_of_nodes() == 0:
        log("[ERRO] O grafo está vazio.")
        return

    # Converte o grafo para JSON
    data = json_graph.node_link_data(G, edges="links")
    json_data = json.dumps(data, indent=4)

    # Cria um link de download no navegador
    blob = Blob.new([json_data], {"type": "application/json"})
    url = URL.createObjectURL(blob)

    # Configura e dispara o download
    link = document.createElement("a")
    link.href = url
    link.download = "graph_teste.json"
    link.click()
    URL.revokeObjectURL(url)

    log("Download do grafo iniciado.")

@when("click", "#load-test-graph")
def load_test_graph(event):
    global G
    G.clear()
    G.add_edge("r0", "B", w=10)
    G.add_edge("r0", "A", w=2)
    G.add_edge("r0", "C", w=10)
    G.add_edge("B", "A", w=1)
    G.add_edge("A", "C", w=4)
    G.add_edge("C", "D", w=2)
    G.add_edge("D", "B", w=2)
    G.add_edge("B", "E", w=8)
    G.add_edge("C", "E", w=4)

    log("Grafo de teste carregado.")
    draw_graph(G, "Grafo de Teste (DG)", append=False)


@when("click", "#show-ready-arborescence")
def show_ready_arborescence(event):
    T = nx.DiGraph()
    T.add_edge("r0", "A", w=2)
    T.add_edge("A", "C", w=4)
    T.add_edge("C", "D", w=2)
    T.add_edge("D", "B", w=2)
    T.add_edge("C", "E", w=4)
    draw_graph(T, "Arborescência Pré-definida")
    log("Arborescência pronta exibida.")


@when("click", "#run-algorithm")
def run_algorithm(event):
    global G
    r0 = document.getElementById("root-node").value or "r0"
    if r0 not in G:
        alert(f"[ERRO] O nó raiz '{r0}' deve existir no grafo.")
        return

    log("Executando algoritmo de Chu-Liu...")
    T = find_optimum_arborescence(G, r0)
    draw_graph(T, "Arborescência Ótima")
    log("Execução concluída com sucesso.")


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

    # Encontra arestas de fora -> ciclo
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

    in_edges: dict[str, tuple[str, float]] = {}
    for v in cycle_nodes:
        in_edge = min(
            ((u, w) for u, _, w in G.in_edges(v, data="w") if u not in cycle_nodes),
            key=lambda x: x[1],
            default=None,
        )
        if in_edge:
            in_edges[v] = in_edge
    for v, (u, w) in in_edges.items():
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
            out_edges[u] = out_edge
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
