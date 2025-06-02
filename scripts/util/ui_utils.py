from js import document, window
from pyodide.ffi import create_proxy
import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader
from pyscript import document, when, display
import json

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
        def hide_final():
            toast.classList.add("hidden")
        proxy2 = create_proxy(hide_final)
        window.setTimeout(proxy2, 500)

    proxy = create_proxy(hide_toast)
    window.setTimeout(proxy, 3000)

def log_in_box(msg: str):
    log_box = document.getElementById("log-output")
    log_box.value += msg + "\n"
    log_box.scrollTop = log_box.scrollHeight

def clearScreen():
    # document.getElementById("draw_warning").classList.remove("hidden")
    document.getElementById("step_warning").classList.remove("hidden")
    document.getElementById("export-graph-original").classList.add("hidden")
    document.getElementById("log-section").classList.add("hidden")
    document.getElementById("arborescence-section").classList.add("hidden")

def fillScreen(T):
    # global T
    # document.getElementById("draw_warning").classList.add("hidden")
    document.getElementById("step_warning").classList.add("hidden")
    document.getElementById("export-graph-original").classList.remove("hidden")
    document.getElementById("log-section").classList.remove("hidden")
    # document.getElementById("arborescence-section").classList.remove("hidden")

    if (T.number_of_nodes() > 0):
        document.getElementById("arborescence-section").classList.remove("hidden")
        document.getElementById("step_warning").classList.add("hidden")
    else:
        document.getElementById("arborescence-section").classList.add("hidden")
        document.getElementById("step_warning").classList.remove("hidden")

def toggle_sidebar(event):
    sidebar = document.getElementById("right-sidebar")
    container = document.getElementById("container_step_by_step")
    button = document.getElementById("toggle-sidebar")

    if sidebar.classList.contains("w-80"):
        sidebar.classList.remove("w-80")
        document.getElementById("title_step_area").classList.remove("flex")
        document.getElementById("title_step_area").classList.remove("items-center")
        document.getElementById("title_step_area").classList.remove("py-8")
        document.getElementById("title_step_area").classList.remove("mx-4")
        document.getElementById("title_step_area").classList.remove("gap-6")
        document.getElementById("title_step_area").classList.remove("top-6")
        document.getElementById("title_step_area").classList.add("my-9")
        document.getElementById("title_step_area").classList.add("mx-auto")
        document.getElementById("title_step_area").classList.add("w-max")
        sidebar.classList.add("w-10")
        container.style.display = "none"
        document.getElementById("title_step").style.display = "none"
        button.innerHTML = ""
        button.insertAdjacentHTML("beforeend", """<img id="collapser-icon" src="../assets/process.png" alt="Contrair" class="w-10 h-10 hover:opacity-80" />""")
    else:
        sidebar.classList.remove("w-10")
        document.getElementById("title_step_area").classList.add("flex")
        document.getElementById("title_step_area").classList.add("items-center")
        document.getElementById("title_step_area").classList.add("py-8")
        document.getElementById("title_step_area").classList.add("mx-4")
        document.getElementById("title_step_area").classList.add("gap-6")
        document.getElementById("title_step_area").classList.add("top-6")
        document.getElementById("title_step_area").classList.remove("mx-auto")
        document.getElementById("title_step_area").classList.remove("w-max")
        document.getElementById("title_step_area").classList.remove("my-9")
        sidebar.classList.add("w-80")
        container.style.display = "block"
        document.getElementById("title_step").style.display = "block"
        button.innerHTML = ""
        button.insertAdjacentHTML("beforeend", """<img id="collapser-icon" src="../assets/back_arrow_right.png" alt="Contrair" class="w-5 h-5 hover:opacity-80" />""")

def export_graph(G):
    log_in_box("Exportando grafo...")
    if G.number_of_nodes() == 0:
        log_in_box("[ERRO] O grafo está vazio.")
        show_error_toast("O grafo está vazio! Carregue um exemplo ou desenhe um grafo antes de exportar.")
        return

    # Converte o grafo para JSON
    data = json_graph.node_link_data(G, edges="links")
    json_data = json.dumps(data, indent=4)
    download_json(json_data, filename="graph.json")
    log_in_box("Download do grafo iniciado.")

def download_json(data, filename="graph.json"):
    blob = Blob.new([data], {"type": "application/json"})
    url = URL.createObjectURL(blob)
    link = document.createElement("a")
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)