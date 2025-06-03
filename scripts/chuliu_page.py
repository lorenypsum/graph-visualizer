import networkx as nx
from networkx.readwrite import json_graph
from js import window, document, alert, FileReader
from pyscript import document, when
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from solver.chuliu import find_optimum_arborescence
from util.visualization_utils import draw_graph, draw_step
from util.ui_utils import show_error_toast, log_in_box, toggle_sidebar, fillScreen, clearScreen, download_json, hide_loader, clearArboArea
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
    print("Nós do NetworkX:", list(G.nodes))
    print("Arestas do NetworkX:", list(G.edges(data=True)))
    update_cytoscape_from_networkx(G)
    fillScreen(T)

@when("click", "#toggle-sidebar")
def on_toggle_sidebar(event):
    toggle_sidebar(event)

# @when("click", "#run-algorithm")
@when("custom-event", "#run-algorithm")
def run_algorithm(event):
    global G
    global T
    r0 = document.getElementById("root-node").value or "r0"
    G = get_networkx_graph()
    if r0 not in G:
        hide_loader()
        log_in_box(f"[ERRO] O nó raiz '{r0}' deve existir no grafo.")
        show_error_toast(f"O nó raiz '{r0}' deve existir no grafo.")
        return

    log_in_box("Executando algoritmo de Chu-Liu...")
    try:
        clearArboArea()
        T = find_optimum_arborescence(G, r0, draw_fn=draw_graph, draw_step=draw_step, log=log_in_box)
        if T.number_of_nodes() == 0:
            log_in_box("[ERRO] O grafo não possui uma arborescência.")
            show_error_toast("O grafo não possui uma arborescência.")
        else:
            update_cytoscape_from_networkx(T, eventName="arborescence_updated")
            fillScreen(T)
            log_in_box("Execução concluída com sucesso.")
    except Exception as e:
        clearArboArea()
        log_in_box(f"[ERRO] Ocorreu um erro ao executar o algoritmo: {str(e)}")
        show_error_toast(f"Ocorreu um erro ao executar o algoritmo")
        print(f"Erro ao executar o algoritmo: {e}")
    finally:
        hide_loader()