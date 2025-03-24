import networkx as nx
from js import document, console
from pyodide.ffi import create_proxy

G = nx.DiGraph()

def log(msg):
    log_box = document.getElementById("log-output")
    log_box.value += msg + "\\n"
    log_box.scrollTop = log_box.scrollHeight

def update_visual():
    svg = document.getElementById("graph")
    svg.innerHTML = ""

    width, height = 800, 500
    pos = nx.spring_layout(G, seed=42)

    for u, v, data in G.edges(data=True):
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        line = document.createElementNS("http://www.w3.org/2000/svg", "line")
        line.setAttribute("x1", str(x1 * width))
        line.setAttribute("y1", str(y1 * height))
        line.setAttribute("x2", str(x2 * width))
        line.setAttribute("y2", str(y2 * height))
        line.setAttribute("stroke", "gray")
        svg.appendChild(line)

        label = document.createElementNS("http://www.w3.org/2000/svg", "text")
        label.setAttribute("x", str((x1 + x2) * width / 2))
        label.setAttribute("y", str((y1 + y2) * height / 2 - 5))
        label.setAttribute("fill", "red")
        label.textContent = str(data.get("w", ""))
        svg.appendChild(label)

    for node in G.nodes:
        cx, cy = pos[node]
        circle = document.createElementNS("http://www.w3.org/2000/svg", "circle")
        circle.setAttribute("cx", str(cx * width))
        circle.setAttribute("cy", str(cy * height))
        circle.setAttribute("r", "18")
        circle.setAttribute("fill", "lightblue")
        svg.appendChild(circle)

        label = document.createElementNS("http://www.w3.org/2000/svg", "text")
        label.setAttribute("x", str(cx * width))
        label.setAttribute("y", str(cy * height + 4))
        label.setAttribute("text-anchor", "middle")
        label.setAttribute("font-weight", "bold")
        label.textContent = node
        svg.appendChild(label)

def add_edge(event=None):
    source = document.getElementById("source").value
    target = document.getElementById("target").value
    weight = document.getElementById("weight").value

    if source and target and weight:
        G.add_edge(source, target, w=float(weight))
        log(f"Aresta adicionada: {source} → {target} (peso={weight})")
        update_visual()

def reset_graph(event=None):
    global G
    G.clear()
    document.getElementById("log-output").value = ""
    update_visual()
    log("Grafo resetado.")

def export_tree(event=None):
    import json
    edges = [{"from": u, "to": v, "weight": data.get("w", 1)} for u, v, data in G.edges(data=True)]
    blob = __new__(Blob.new([JSON.stringify(edges)], {"type": "application/json"}))
    link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = "arborescencia.json"
    link.click()
    log("Arborescência exportada como JSON.")

def run_algorithm(event=None):
    try:
        from networkx.algorithms.tree.branchings import maximum_spanning_arborescence
        T = maximum_spanning_arborescence(G, attr='w', default=0)
        log("Arborescência ótima encontrada:")
        for u, v, d in T.edges(data=True):
            log(f"{u} → {v} (peso={d['weight']})")
        global G
        G = T
        update_visual()
    except Exception as e:
        log(f"[ERRO] {e}")
