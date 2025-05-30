import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader, window
from pyscript import document, when, display
import json
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt


def get_graph_from_js():
    data = json.loads(window.graph_json)
    print("Grafo recebido do JS:", data)
    return data

def cytoscape_to_networkx(data):
    G = nx.DiGraph()
    # Adiciona nós
    for node in data['nodes']:
        node_id = node['data']['id']
        G.add_node(node_id)
    # Adiciona arestas
    for edge in data['edges']:
        source = edge['data']['source']
        target = edge['data']['target']
        weight = edge['data'].get('weight', 1)
        # Se o peso veio como string, converte para número
        try:
            weight = float(weight)
        except Exception:
            weight = 1
        G.add_edge(source, target, weight=weight)
    return G

def get_networkx_graph():
    data = get_graph_from_js()
    G = cytoscape_to_networkx(data)
    return G

@when("click", "#add-edge")
def add_edge():
    G = get_networkx_graph()
    print("Nós do NetworkX:", list(G.nodes))
    print("Arestas do NetworkX:", list(G.edges(data=True)))

@when("click", "#reset-graph")
def reset_graph():
    pass

def export_graph(G):
    pass

@when("click", "#export-graph-original")
def export_original_graph(event):
    global G
    G = get_networkx_graph()
    if G.number_of_nodes() == 0:
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

    

@when("click", "#import-graph")
def open_file_selector(evt):
    pass

@when("change", "#file-input")
def handle_file_upload(evt):
    pass

@when("click", "#load-test-graph")
def load_test_graph(event):
    pass

