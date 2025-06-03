import networkx as nx
from networkx.readwrite import json_graph
from js import window, document, alert, FileReader
from pyscript import document, when, display
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from solver.andrasfrank import find_minimum_arborescence
from util.visualization_utils import draw_graph, draw_step
from util.ui_utils import show_error_toast, log_in_box, toggle_sidebar, fillScreen, clearScreen, export_graph, download_json
from util.graph_utils import get_networkx_graph, update_cytoscape_from_networkx

G = nx.DiGraph()
O = nx.DiGraph()
T = nx.DiGraph()

@when("click", "#reset-graph")
def reset_graph():
    global G
    global O
    global T
    
    clearScreen()

    G.clear()
    O.clear()
    T.clear()
    
    document.getElementById("log-output").value = ""
    window.graph_json = json.dumps({"nodes": [], "edges": []})
    event = window.Event.new("graph_updated")
    document.dispatchEvent(event)
    log_in_box("Grafo resetado.")


@when("click", "#export-graph-arborescencia")
def export_arborescencia_graph(event):
    log_in_box("Botão 'Exportar Arborescência' clicado.")
    global T
    if T.number_of_nodes() == 0:
        show_error_toast("O grafo está vazio! Execute o algoritmo antes de exportar.")
        return

    data = json_graph.node_link_data(G, edges="links")
    json_data = json.dumps(data, indent=4)
    download_json(json_data, filename="graph.json")

@when("click", "#export-graph-original")
def export_original_graph(event):
    log_in_box("Botão 'Exportar grafo original' clicado.")
    global O
    O = get_networkx_graph()
    if O.number_of_nodes() == 0:
        show_error_toast("O grafo está vazio! Carregue um exemplo ou desenhe um grafo antes de exportar.")
        return

    data = json_graph.node_link_data(G, edges="links")
    json_data = json.dumps(data, indent=4)

    download_json(json_data, filename="graph.json")


@when("click", "#import-graph")
def open_file_selector(event):
    document.getElementById("file-input").click()

# Lê o arquivo quando for selecionado
@when("change", "#file-input")
def handle_file_upload(event):
    file = event.target.files.item(0)
    if not file:
        return

    reader = FileReader.new()

    def onload(e):
        contents = e.target.result
        data = json.loads(contents) 
        global G
        global O
        global T
        G.clear()
        G = json_graph.node_link_graph(data, edges="links")
        O = G.copy()
        update_cytoscape_from_networkx(G)
        fillScreen(T)
        log_in_box("Grafo importado com sucesso.")

    reader.onload = onload
    reader.readAsText(file)

@when("click", "#load-test-graph")
def load_test_graph(event):
    global G
    global O
    global T
    G.clear()
    O.clear()
    G = nx.DiGraph()
    G.add_edge("r0", "A", w=2)
    G.add_edge("r0", "B", w=10)
    G.add_edge("r0", "C", w=10)
    G.add_edge("A", "C", w=4)
    G.add_edge("B", "A", w=1)
    G.add_edge("C", "D", w=2)
    G.add_edge("D", "B", w=2)
    G.add_edge("B", "E", w=8)
    G.add_edge("C", "E", w=4)
    O = G.copy()
    
    input_element = document.getElementById("root-node")
    input_element.value = "r0"

    log_in_box("Grafo de teste carregado.")
    print("Nós do NetworkX:", list(G.nodes))
    print("Arestas do NetworkX:", list(G.edges(data=True)))
    update_cytoscape_from_networkx(G)
    fillScreen(T)

@when("click", "#toggle-sidebar")
def on_toggle_sidebar(event):
    toggle_sidebar(event)

@when("click", "#run-algorithm")
def run_algorithm(event):
    global G
    global T
    r0 = document.getElementById("root-node").value or "r0"
    G = get_networkx_graph()
    if r0 not in G:
        log_in_box(f"[ERRO] O nó raiz '{r0}' deve existir no grafo.")
        show_error_toast(f"O nó raiz '{r0}' deve existir no grafo.")
        return

    log_in_box("Executando algoritmo de Andras Frank...")
    T = find_minimum_arborescence(G, r0, draw_step=draw_step, log=log_in_box)
    if T.number_of_nodes() == 0:
        log_in_box("[ERRO] O grafo não possui uma arborescência.")
        show_error_toast("O grafo não possui uma arborescência.")
    else:
        update_cytoscape_from_networkx(T, eventName="arborescence_updated")
        fillScreen(T)
        log_in_box("Execução concluída com sucesso.")