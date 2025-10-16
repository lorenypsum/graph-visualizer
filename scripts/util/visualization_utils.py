import networkx as nx
from networkx.readwrite import json_graph
from js import Blob, URL, document, alert, FileReader
from pyscript import document, when, display
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


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
                    <div class="image-wrapper flex justify-center items-center relative">
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
    print("Drawing step", id)
    print(G.edges(data=True))
    print(G.nodes)
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
    img = document.querySelector(f"#{target} img")
    if img:
        img.id = f"img-{id}"
    
    btn_html = f"""<button class="expand-button absolute top-1 right-1 rounded" data-img-id="img-{id}">
        <img src="../assets/expand.png" alt="Expandir"
        class="cursor-pointer w-3 h-3 hover:opacity-80" hover:bg-gray-300" transition/>
    </button>"""
    document.getElementById(target).insertAdjacentHTML("beforeend", btn_html)

def draw_graph(G: nx.DiGraph, title="Digrafo", append=True, target="original-graph-area"):
    plt.clf()  # Limpa a figura atual
    pos = nx.planar_layout(G)  # Layout para posicionamento dos nós
    bg_color = (229/255, 229/255, 229/255)
    plt.figure(figsize=(16, 12))  # Tamanho da figura
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
    try:
        display(title, target=target, append=append)
        display(plt, target=target, append=append)
    except Exception as e:
        alert(f"Erro ao exibir o gráfico: {e}")
    ax = plt.gca() 
    ax.set_facecolor("#e5e5e5")
    plt.close()  # Fecha a figura para liberar memória

