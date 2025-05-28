import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader
from pyscript import document, when, display
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from chuliu_alg import find_optimum_arborescence

def log_in_box(msg: str):
    pass
    # log_box = document.getElementById("log-output")
    # log_box.value += msg + "\n"
    # log_box.scrollTop = log_box.scrollHeight

def draw_graph(G: nx.DiGraph, title="Digrafo", append=True, target="original-graph-area"):
    plt.clf()  # Limpa a figura atual
    pos = nx.planar_layout(G)  # Layout para posicionamento dos nós
    bg_color = (229/255, 229/255, 229/255)
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
    display(title, target=target, append=append)
    display(plt, target=target, append=append)
    ax = plt.gca() 
    ax.set_facecolor("#e5e5e5")
    plt.close()  # Fecha a figura para liberar memória

G = nx.DiGraph()
O = nx.DiGraph()
T = nx.DiGraph()

@when("click", "#add-edge")
def add_edge():
    global G
    global O
    source = document.getElementById("source").value
    target = document.getElementById("target").value
    weight = document.getElementById("weight").value
    if source and target and weight:
        G.add_edge(source, target, w=float(weight))
        log_in_box(f"Aresta adicionada: {source} → {target} (peso={weight})")
        draw_graph(G, "Grafo com Arestas", append=False, target="original-graph-area")
        O = G.copy()
        fillScreen()
    else:
        log_in_box("[ERRO] Preencha todos os campos para adicionar uma aresta.")
    

@when("click", "#reset-graph")
def reset_graph():
    global G
    global O
    global T
    
    clearScreen()

    G.clear()
    O.clear()
    T.clear()
    
    draw_graph(G, "Grafo Resetado", append=False)
    log_in_box("Grafo resetado.")

def export_graph(G):
    log_in_box("Exportando grafo...")
    if G.number_of_nodes() == 0:
        log_in_box("[ERRO] O grafo está vazio.")
        return

    # Converte o grafo para JSON
    data = json_graph.node_link_data(G, edges="links")
    json_data = json.dumps(data, indent=4)

    # Cria um link de download no navegador
    blob = Blob.new([json_data], {"type": "application/json"})
    url = URL.createObjectURL(blob)

    # Configura e sdispara o download
    link = document.createElement("a")
    link.href = url
    link.download = "graph.json"
    link.click()
    URL.revokeObjectURL(url)

    log_in_box("Download do grafo iniciado.")

@when("click", "#export-graph-original")
def export_original_graph(event):
    log_in_box("Botão 'Exportar grafo original' clicado.")
    global O
    export_graph(O)

@when("click", "#import-graph")
def open_file_selector(evt):
    document.getElementById("file-input").click()

# Lê o arquivo quando for selecionado
@when("change", "#file-input")
def handle_file_upload(evt):
    file = evt.target.files.item(0)
    if not file:
        return

    reader = FileReader.new()

    def onload(e):
        contents = e.target.result
        data = json.loads(contents) 
        global G
        global O
        G.clear()
        G = json_graph.node_link_graph(data, edges="links")
        O = G.copy()
        draw_graph(G, "Grafo Importado", append=False, target="original-graph-area")
        fillScreen()
        log_in_box("Grafo importado com sucesso.")

    reader.onload = onload
    reader.readAsText(file)

@when("click", "#load-test-graph")
def load_test_graph(event):
    global G
    global O
    G.clear()
    O.clear()
    G.add_edges_from([('0', '1', {"w": 3}),
                    ('0', '2', {"w": 6}),
                    ('1', '2', {"w": 1}),
                    ('2', '1', {'w': 1}),
                    ('1', '3', {"w": 2}),
                    ('1', '4', {"w": 10}),
                    ('3', '4', {"w": 1}),
                    ('4', '2', {"w": 10}),
                    ('4', '5', {'w': 1}),
                    ('5', '6', {'w': 1}),
                    ('6', '4', {'w': 1}),
                    ('6', '7', {'w': 8}),
                    ('7', '8', {'w': 4}),
                    ('8', '6', {'w': 5}),
                    ('6', '8', {'w': 2})])
    O = G.copy()
    
    input_element = document.getElementById("root-node")
    input_element.value = "0"

    log_in_box("Grafo de teste carregado.")
    draw_graph(G, "Grafo de Teste", append=False, target="original-graph-area")
    fillScreen()

def clearScreen():
    document.getElementById("draw_warning").classList.remove("hidden")
    document.getElementById("export-graph-original").classList.add("hidden")

def fillScreen():
    document.getElementById("draw_warning").classList.add("hidden")
    document.getElementById("export-graph-original").classList.remove("hidden")

