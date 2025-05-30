import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader
from pyscript import document, when, display
import json
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt


@when("click", "#add-edge")
def add_edge():
    pass

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

