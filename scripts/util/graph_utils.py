import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader, window
from pyscript import document, when, display
import json

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
        G.add_edge(source, target, w=weight)
    return G

def networkx_to_cytoscape(G):
    width, height = 500, 500 
    scale = 0.8
    pos = nx.spring_layout(G)  
    nodes = []
    for n in G.nodes:
        x, y = pos[n]
        # Escale as posições para caber melhor no Cytoscape
        nodes.append({
            "data": {"id": str(n)},
            "position": {
                "x": width/2 + x * (width/2) * scale,
                "y": height/2 + y * (height/2) * scale
            }
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
    print(f"Convertendo grafo para a estrutura do NetworkX: {G.nodes} -> {G.edges}")
    return G

def update_cytoscape_from_networkx(G, eventName="graph_updated"):
    cyto_data = networkx_to_cytoscape(G)
    print('Convertendo NetworkX para Cytoscape:', cyto_data)
    json_str = json.dumps(cyto_data)
    if eventName == "graph_updated":
        window.graph_json = json_str
    elif eventName == "arborescence_updated":
        window.arborescence_json = json_str
    else:
        print(f"[ERRO] Evento desconhecido: {eventName}")
    event = window.Event.new(eventName)
    document.dispatchEvent(event)

