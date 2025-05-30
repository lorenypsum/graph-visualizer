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
    # nodes = [n['data']['id'] for n in data['nodes']]
    # edges = [(e['data']['source'], e['data']['target'], e['data'].get('weight', 1)) for e in data['edges']]
    print("Grafo recebido do JS:", data)
    return data

@when("click", "#add-edge")
def add_edge():
    get_graph_from_js()

@when("click", "#reset-graph")
def reset_graph():
    pass

def export_graph(G):
    pass

@when("click", "#export-graph-original")
def export_original_graph(event):
    pass

@when("click", "#import-graph")
def open_file_selector(evt):
    pass

@when("change", "#file-input")
def handle_file_upload(evt):
    pass

@when("click", "#load-test-graph")
def load_test_graph(event):
    pass

