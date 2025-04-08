import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from js import Blob, URL, document, alert
from pyscript import when, display
import json

from chuliu import find_optimum_arborescence, remove_edge_in_r0

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
    G_filtered = remove_edge_in_r0(G, r0)
    T = find_optimum_arborescence(G_filtered, r0, draw_fn=draw_graph)
    draw_graph(T, "Arborescência Ótima")
    log("Execução concluída com sucesso.")