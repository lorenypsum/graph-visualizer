import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader, window
from pyscript import document, when, display
import json
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt

G = nx.DiGraph()
O = nx.DiGraph()
T = nx.DiGraph()

def get_graph_from_js():
    data = json.loads(window.graph_json)
    print("Grafo recebido do JS:", data)
    return data

def cytoscape_to_networkx(data):
    if not data or 'nodes' not in data or 'edges' not in data:
        return nx.DiGraph()
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

def networkx_to_cytoscape(G):
    pos = nx.spring_layout(G)  # ou outro layout de sua preferência
    nodes = []
    for n in G.nodes:
        x, y = pos[n]
        # Escale as posições para caber melhor no Cytoscape
        nodes.append({
            "data": {"id": str(n)},
            "position": {"x": float(x)*300+250, "y": float(y)*300+250}
        })
    edges = []
    for u, v, d in G.edges(data=True):
        edges.append({
            "data": {
                "id": f"e{u}_{v}",
                "source": str(u),
                "target": str(v),
                "weight": d.get("w", d.get("weight",1))
            }
        })
    return {"nodes": nodes, "edges": edges}

def get_networkx_graph():
    data = get_graph_from_js()
    G = cytoscape_to_networkx(data)
    return G

@when("click", "#reset-graph")
def reset_graph():
    print('Resetando o grafo...')
    global G
    G = nx.DiGraph()
    window.graph_json = json.dumps({"nodes": [], "edges": []})
    event = window.Event.new("graph_updated")
    document.dispatchEvent(event)

from pyodide.ffi import create_proxy

def show_error_toast(msg="Ocorreu um erro."):
    toast = document.getElementById("toast-danger")
    toast_msg = document.getElementById("toast-danger-msg")
    toast_msg.textContent = msg
    toast.classList.remove("hidden")
    toast.classList.remove("opacity-0")
    toast.classList.add("opacity-100")

    def hide_toast():
        toast.classList.remove("opacity-100")
        toast.classList.add("opacity-0")
        # Esconde de vez após a transição (500ms)
        def hide_final():
            toast.classList.add("hidden")
        proxy2 = create_proxy(hide_final)
        window.setTimeout(proxy2, 500)

    proxy = create_proxy(hide_toast)
    window.setTimeout(proxy, 3000)

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
    blob = Blob.new([json_data], {"type": "application/json"})
    url = URL.createObjectURL(blob)

    # Configura e dispara o download
    link = document.createElement("a")
    link.href = url
    link.download = "graph.json"
    link.click()
    URL.revokeObjectURL(url)

    
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
        cyto_data = networkx_to_cytoscape(G)
        json_str = json.dumps(cyto_data)
        window.graph_json = json_str
        event = window.Event.new("graph_updated")
        document.dispatchEvent(event)
        
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
    print("Nós do NetworkX:", list(G.nodes))
    print("Arestas do NetworkX:", list(G.edges(data=True)))
    cyto_data = networkx_to_cytoscape(G)
    json_str = json.dumps(cyto_data)
    window.graph_json = json_str
    event = window.Event.new("graph_updated")
    document.dispatchEvent(event)

