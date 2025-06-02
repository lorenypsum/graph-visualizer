import networkx as nx
from networkx.readwrite import json_graph
from js import document, FileReader, window
from pyscript import document, when
import json
from util.graph_utils import get_networkx_graph, update_cytoscape_from_networkx
from util.ui_utils import show_error_toast, download_json

G = nx.DiGraph()

@when("click", "#reset-graph")
def reset_graph():
    print('Resetando o grafo...')
    global G
    G = nx.DiGraph()
    window.graph_json = json.dumps({"nodes": [], "edges": []})
    event = window.Event.new("graph_updated")
    document.dispatchEvent(event)

@when("click", "#export-graph-original")
def export_original_graph(event):
    global G
    G = get_networkx_graph()
    if G.number_of_nodes() == 0:
        show_error_toast("O grafo está vazio! Carregue um exemplo ou desenhe um grafo antes de exportar.")
        return

    # Converte o grafo para JSON
    data = json_graph.node_link_data(G, edges="links")
    json_data = json.dumps(data, indent=4)

    # Cria um link de download no navegador
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
        G.clear()
        G = json_graph.node_link_graph(data, edges="links")
        update_cytoscape_from_networkx(G)
        
    reader.onload = onload
    reader.readAsText(file)

@when("click", "#load-test-graph")
def load_test_graph(event):
    global G
    G.clear()
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
    print("Nós do NetworkX:", list(G.nodes))
    print("Arestas do NetworkX:", list(G.edges(data=True)))
    update_cytoscape_from_networkx(G)
