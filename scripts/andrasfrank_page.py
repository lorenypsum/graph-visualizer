import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader
from pyscript import document, when, display
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from andrasfrank_alg import find_minimum_arborescence

def log_in_box(msg: str):
    log_box = document.getElementById("log-output")
    log_box.value += msg + "\n"
    log_box.scrollTop = log_box.scrollHeight

def draw_graph(G: nx.DiGraph, title="Digrafo", append=True, target="original-graph-area"):
    plt.clf()  # Limpa a figura atual
    pos = nx.planar_layout(G)  # Layout para posicionamento dos nós
    bg_color = (229/255, 229/255, 229/255)
    plt.figure(figsize=(6, 4))  # Tamanho da figura
    # Desenha os nós e arestas
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=2000,
        font_size=12,
    )
    weights = nx.get_edge_attributes(G, "w")
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=weights, font_color="red", font_size=12
    )
    plt.title(title)
    display(title, target=target, append=append)
    display(plt, target=target, append=append)
    ax = plt.gca() 
    ax.set_facecolor("#e5e5e5")
    plt.close()  # Fecha a figura para liberar memória

def draw_step(G: nx.DiGraph, id=1, title="Passo do Algoritmo", description=""):
    html_content = f"""
        <div id="step_{id}" class="mb-5">
            <div class="btn_step grid grid-cols-10 gap-1 hover:bg-[#e3e3e3] rounded px-1 py-[1px]">
                <div class="my-1 col-span-2">
                    <div
                        class="flex items-center justify-center w-5 h-5 bg-[#787486] text-white text-[12px] rounded-full">
                        <span>{id}</span>
                    </div>
                </div>
                <div class="col-span-6">
                    <span class="flex text-base text-[#787486] justify-left">{title}</span>
                </div>
                <div class="my-1 col-span-2">
                    <div class="flex justify-end items-center">
                        <img id="step_{id}_icon" src="../assets/plus.png" alt="Contrair"
                            class="cursor-pointer w-5 h-5 hover:opacity-80"
                            onclick="toggleStep('step_{id}', 'step_{id}_icon')" />
                    </div>
                </div>
            </div>
            <div class="detalhes hidden transition-all duration-500 ease-in-out">
                <div class="border-t-2 border-[#5030E5] w-full rounded-full my-2"></div>
                <div class="my-1 gap-4 py-2 px-2 bg-white rounded-lg">
                    <div class="flex justify-center items-center">
                        <div id="graph-step-{id}"></div>
                    </div>
                    <div class="border-t-2 border-[#DBDBDB] w-full rounded-full my-2"></div>
                    <span class="flex text-xs text-[#BDBACA] justify-left">
                        {description}
                    </span>
                </div>
            </div>
        </div>
    """
    container = document.getElementById("container_step_by_step")
    container.insertAdjacentHTML("beforeend", html_content)
    target = f"graph-step-{id}"
    plt.clf() 
    pos = nx.planar_layout(G) 
    plt.figure(figsize=(6, 4))  
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=2000,
        font_size=12,
    )
    weights = nx.get_edge_attributes(G, "w")
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=weights, font_color="red", font_size=12
    )
    display(plt, target=target, append=False)
    plt.close()

G = nx.DiGraph()
O = nx.DiGraph()
T = nx.DiGraph()

@when("click", "#add-edge")
def add_edge():
    global G
    global O
    source = document.getElementById("source").value
    target = document.getElementById("target").value
    weight = document.getElementById("weight").value
    if source and target and weight:
        G.add_edge(source, target, w=float(weight))
        log_in_box(f"Aresta adicionada: {source} → {target} (peso={weight})")
        draw_graph(G, "Grafo com Arestas", append=False, target="original-graph-area")
        O = G.copy()
        fillScreen()
    else:
        log_in_box("[ERRO] Preencha todos os campos para adicionar uma aresta.")
    

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
    draw_graph(G, "Grafo Resetado", append=False)
    log_in_box("Grafo resetado.")

def export_graph(G):
    log_in_box("Exportando grafo...")
    if G.number_of_nodes() == 0:
        log_in_box("[ERRO] O grafo está vazio.")
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

    log_in_box("Download do grafo iniciado.")

@when("click", "#export-graph-arborescencia")
def export_arborescencia_graph(event):
    log_in_box("Botão 'Exportar Arborescência' clicado.")
    global T
    export_graph(T)

@when("click", "#export-graph-original")
def export_original_graph(event):
    log_in_box("Botão 'Exportar grafo original' clicado.")
    global O
    export_graph(O)

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
        draw_graph(G, "Grafo Importado", append=False, target="original-graph-area")
        fillScreen()
        log_in_box("Grafo importado com sucesso.")

    reader.onload = onload
    reader.readAsText(file)

@when("click", "#load-test-graph")
def load_test_graph(event):
    global G
    global O
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
    draw_graph(G, "Grafo de Teste", append=False, target="original-graph-area")
    fillScreen()

@when("click", "#toggle-sidebar")
def toggle_sidebar(evt):
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

def clearScreen():
    document.getElementById("draw_warning").classList.remove("hidden")
    document.getElementById("step_warning").classList.remove("hidden")
    document.getElementById("export-graph-original").classList.add("hidden")
    document.getElementById("log-section").classList.add("hidden")
    document.getElementById("arborescence-section").classList.add("hidden")

def fillScreen():
    global T
    document.getElementById("draw_warning").classList.add("hidden")
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

@when("click", "#run-algorithm")
def run_algorithm(event):
    global G
    global T
    r0 = document.getElementById("root-node").value or "r0"
    if r0 not in G:
        alert(f"[ERRO] O nó raiz '{r0}' deve existir no grafo.")
        return

    log_in_box("Executando algoritmo de Andras Frank...")
    T = find_minimum_arborescence(G, r0, draw_step=draw_step, log=log_in_box)
    if T.number_of_nodes() == 0:
        log_in_box("[ERRO] O grafo não possui uma arborescência.")
    else:
        draw_graph(T, "Arborescência Ótima", append=False, target='arborescence-graph-area')
        fillScreen()
        log_in_box("Execução concluída com sucesso.")