# from ui_utils import show_error_toast, log_in_box
# import networkx as nx
# from networkx.readwrite import json_graph
# from js import Blob, URL, document, alert, FileReader
# from pyscript import document, when, display
# import json

# def export_graph(G):
#     log_in_box("Exportando grafo...")
#     if G.number_of_nodes() == 0:
#         log_in_box("[ERRO] O grafo está vazio.")
#         show_error_toast("O grafo está vazio! Carregue um exemplo ou desenhe um grafo antes de exportar.")
#         return

#     # Converte o grafo para JSON
#     data = json_graph.node_link_data(G, edges="links")
#     json_data = json.dumps(data, indent=4)
#     download_json(json_data, filename="graph.json")
#     log_in_box("Download do grafo iniciado.")

# def download_json(data, filename="graph.json"):
#     blob = Blob.new([data], {"type": "application/json"})
#     url = URL.createObjectURL(blob)
#     link = document.createElement("a")
#     link.href = url
#     link.download = filename
#     link.click()
#     URL.revokeObjectURL(url)