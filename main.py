import networkx as nx
import matplotlib.pyplot as plt
# import unittest #não usado ainda
import logging
from js import document, JSON, Blob, URL, __new__
import io
import base64
# from pyodide.ffi import create_proxy

G = nx.DiGraph()

def log(msg):
    log_box = document.getElementById("log-output")
    log_box.value += msg + "\n"
    log_box.scrollTop = log_box.scrollHeight

def update_graph_output(G_display, title="Grafo Atual"):
    plt.clf()
    pos = nx.spring_layout(G_display)
    edge_labels = nx.get_edge_attributes(G_display, 'w')
    nx.draw(G_display, pos, with_labels=True, node_color='lightblue', node_size=2000)
    nx.draw_networkx_edge_labels(G_display, pos, edge_labels=edge_labels, font_color='red')
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    graph_area = document.getElementById("graph-area")
    graph_area.innerHTML = f"<img src='data:image/png;base64,{img_str}' />"

def add_edge(event=None):
    source = document.getElementById("source").value
    target = document.getElementById("target").value
    weight = document.getElementById("weight").value
    if source and target and weight:
        G.add_edge(source, target, w=float(weight))
        log(f"Aresta adicionada: {source} → {target} (peso={weight})")
        update_graph_output(G, "Grafo com Arestas")

def reset_graph(event=None):
    global G
    G.clear()
    document.getElementById("log-output").value = ""
    update_graph_output(G, "Grafo Resetado")
    log("Grafo resetado.")

def export_graph(event=None):
    edges = [{"from": u, "to": v, "weight": d.get("w", 1)} for u, v, d in G.edges(data=True)]
    blob = __new__(Blob.new([JSON.stringify(edges)], {"type": "application/json"}))
    link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = "arborescencia.json"
    link.click()
    log("Exportado como JSON.")

def run_algorithm(event=None):
    from js import setTimeout

    try:
        r0 = "r0"
        if r0 not in G:
            log("[ERRO] O nó raiz 'r0' deve existir no grafo.")
            return

        log("Executando algoritmo de Chu-Liu...")
        T = find_optimum_arborescence(G, r0)
        update_graph_output(T, "Arborescência Ótima")
        log("Execução concluída com sucesso.")

    except Exception as e:
        log(f"[ERRO] {e}")


# Configuração do logger
logging.basicConfig(
    level=logging.INFO,  # Altere para DEBUG se quiser mais detalhes
    format='[%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)

# Funções para desenho do grafo
def draw_graph(G, title="Digrafo"):
    try:
        # Verifica se G é um grafo válido
        if not isinstance(G, (nx.Graph, nx.DiGraph)):
            raise TypeError("O objeto fornecido não é um grafo do tipo networkx.Graph ou networkx.DiGraph.")

        if G.number_of_nodes() == 0:
            print(f"[AVISO] Grafo vazio — nada a desenhar. ({title})")
            return

        pos = nx.planar_layout(G)  # Layout para posicionamento dos nós
        plt.figure(figsize=(6, 4))  # Tamanho da figura

        # Desenha os nós e arestas
        nx.draw(
            G, pos, with_labels=True,
            node_color='lightblue', edge_color='gray',
            node_size=2000, font_size=12
        )

        # Tenta obter os pesos das arestas
        weights = nx.get_edge_attributes(G, 'w')
        if not weights:
            print(f"[INFO] Nenhum peso ('w') encontrado nas arestas para exibir no grafo.")

        # Desenha os rótulos dos pesos, se existirem
        nx.draw_networkx_edge_labels(G, pos, edge_labels=weights, font_color='red', font_size=12)

        plt.title(title)
        plt.show()

    except Exception as e:
        print(f"[ERRO] Ocorreu um problema ao desenhar o grafo: {e}")

# Grafo de teste   
# TODO - Fazer testes com grafos maioress     

# Criando Digrafo com a biblioteca networkx para testes
DG = nx.DiGraph()

# Adicionando vértices (opcional, pois são criados automaticamente ao adicionar arestas)
DG.add_nodes_from(["A", "B", "C", "D"])

# Adicionando arestas com pesos (custo)
DG.add_edge("r0", "B", w = 10)
DG.add_edge("r0", "A", w = 2)
DG.add_edge("r0", "C", w = 10)
DG.add_edge("B", "A", w = 1)
DG.add_edge("A", "C", w = 4)
DG.add_edge("C", "D", w = 2)
DG.add_edge("D", "B", w = 2)
DG.add_edge("B", "E", w = 8)
DG.add_edge("C", "E", w = 4)
print(DG)

# Funções auxiliares ao algoritmo de Chu-Liu
def change_edge_weight(G, node):
    try:
        # Verifica se é um grafo direcionado válido
        if not isinstance(G, nx.DiGraph):
            raise TypeError("O grafo fornecido deve ser do tipo networkx.DiGraph.")

        # Verifica se o nó existe
        if node not in G:
            raise ValueError(f"O nó '{node}' não existe no grafo.")

        # Obtém predecessores com pesos
        predecessors = list(G.in_edges(node, data='w'))

        if not predecessors:
            raise ValueError(f"Nenhum arco entra no nó '{node}'.")

        # Verifica se todos os predecessores possuem pesos válidos
        weights = []
        for u, v, w in predecessors:
            if w is None:
                raise ValueError(f"A aresta ({u}, {v}) não possui atributo de peso 'w'.")
            if not isinstance(w, (int, float)):
                raise TypeError(f"Peso inválido na aresta ({u}, {v}): esperado número, obtido {type(w)}.")
            weights.append(w)

        # Calcula Yv = menor peso de entrada
        yv = min(weights)

        # Subtrai Yv de cada aresta de entrada
        for u, _, _ in predecessors:
            G[u][node]['w'] -= yv

        return G

    except Exception as e:
        print(f"[ERRO] change_edge_weight falhou: {e}")
        return G  # Retorna o grafo original inalterado como fallback

def get_Fstar(G, r0):
    try:
        # Verifica se é um grafo direcionado válido
        if not isinstance(G, nx.DiGraph):
            raise TypeError("O grafo fornecido deve ser do tipo networkx.DiGraph.")

        # Verifica se a raiz existe no grafo
        if r0 not in G:
            raise ValueError(f"O nó raiz '{r0}' não existe no grafo.")

        F_star = nx.DiGraph()

        for v in G.nodes():
            if v != r0:
                in_edges = list(G.in_edges(v, data='w'))
                if not in_edges:
                    continue  # Nenhuma aresta entra em v
                # Tenta encontrar uma aresta com custo 0
                u = next((u for u, _, w in in_edges if w == 0), None)
                if u:
                    F_star.add_edge(u, v, w=0)

        successors = list(G.out_edges(r0, data='w'))
        if not successors:
            raise ValueError(f"O nó raiz '{r0}' não possui arestas de saída.")

        # Verifica validade dos pesos
        for _, v, w in successors:
            if w is None:
                raise ValueError(f"A aresta ({r0}, {v}) não possui atributo de peso 'w'.")
            if not isinstance(w, (int, float)):
                raise TypeError(f"Peso inválido na aresta ({r0}, {v}): tipo {type(w)}.")

        # Aresta de menor custo saindo da raiz
        v, w = min([(v, w) for _, v, w in successors], key=lambda vw: vw[1])
        F_star.add_edge(r0, v, w=w)

        return F_star

    except Exception as e:
        print(f"[ERRO] Falha ao construir F_star: {e}")
        return nx.DiGraph()  # Retorna grafo vazio como fallback    

def is_F_star_arborescence(F_star, r0):
    try:
        # Verifica se é um grafo dirigido
        if not isinstance(F_star, nx.DiGraph):
            raise TypeError("O grafo fornecido deve ser do tipo networkx.DiGraph.")

        # Verifica se o nó raiz existe no grafo
        if r0 not in F_star:
            raise ValueError(f"O nó raiz '{r0}' não existe no grafo.")

        # Se o grafo estiver vazio
        if F_star.number_of_nodes() == 0:
            raise ValueError("O grafo fornecido está vazio.")

        # Verifica se o grafo é acíclico e todos os nós são alcançáveis a partir de r0
        is_reachable = all(nx.has_path(F_star, r0, v) for v in F_star.nodes)
        is_acyclic = nx.is_directed_acyclic_graph(F_star)

        return is_reachable and is_acyclic

    except Exception as e:
        print(f"[ERRO] Falha ao verificar se é arborescência: {e}")
        return False    

def find_cycle(F_star):
    """
    Encontra um ciclo direcionado / circuito no grafo.
    Retorna um subgrafo contendo o ciclo, ou None se não houver.
    """
    try:
        # Verifica se o grafo é do tipo esperado
        if not isinstance(F_star, nx.DiGraph):
            raise TypeError("O grafo fornecido deve ser do tipo networkx.DiGraph.")

        # Verifica se o grafo tem nós suficientes para conter um ciclo
        if F_star.number_of_edges() == 0 or F_star.number_of_nodes() < 2:
            return None

        # Tenta encontrar um ciclo no grafo
        nodes_in_cycle = set()
        for u, v, _ in nx.find_cycle(F_star, orientation="original"):
            nodes_in_cycle.update([u, v])

        # Retorna o subgrafo contendo apenas o ciclo
        return F_star.subgraph(nodes_in_cycle)

    except nx.NetworkXNoCycle:
        return None
    except Exception as e:
        print(f"[ERRO] Falha ao procurar ciclo em F_star: {e}")
        return None

def contract_cycle(G, C, label):
    """
    Contrai um ciclo C no grafo G, substituindo-o por um supernó com rótulo `label`.
    Devolve o novo grafo (G'), a aresta de entrada (in_edge) e a de saída (out_edge).
    """
    try:
        # Verificações iniciais de tipo
        if not isinstance(G, nx.DiGraph) or not isinstance(C, (nx.DiGraph, nx.Graph)):
            raise TypeError("G e C devem ser grafos (preferencialmente nx.DiGraph).")

        if label in G: # TODO - Pensar em uma forma mas elegante de tratar o label
            raise ValueError(f"O rótulo '{label}' já existe como nó em G.")

        G_prime = G.copy() # TODO - Remover o deep copy, não é necessário
        cycle_nodes = list(C.nodes()) # TODO Otimizar o processo de busca até a linha 219 - não é uma boa ideia deixar o cycle_nodes como losta, mas sim como um conjunto

        if not cycle_nodes: # TODO - No final dos testes podemos remover esse if, já que se ele existe significa que algo deu errado.
            raise ValueError("O ciclo fornecido (C) está vazio e não pode ser contraído.")

        # Encontra aresta de fora -> ciclo
        in_candidates = [(u, v, w) for u, v, w in G.edges(data='w') if u not in cycle_nodes and v in cycle_nodes]
        in_edge = min(in_candidates, key=lambda e: e[2]) if in_candidates else None # TODO - Temos que fazer essa operação para cada vértice u
        if in_edge:
            u, v, w = in_edge
            G_prime.add_edge(u, label, w=w)

        # Encontra aresta de ciclo -> fora
        out_candidates = [(u, v, w) for u, v, w in G.edges(data='w') if u in cycle_nodes and v not in cycle_nodes]
        out_edge = min(out_candidates, key=lambda e: e[2]) if out_candidates else None
        if out_edge:
            u, v, w = out_edge
            G_prime.add_edge(label, v, w=w)

        # Remove os nós do ciclo original
        G_prime.remove_nodes_from(cycle_nodes)

        return G_prime, in_edge, out_edge

    except Exception as e:
        print(f"[ERRO] Falha ao contrair ciclo: {e}")
        return G.copy(), None, None  # Retorna o grafo original como fallback

def remove_edge_in_r0(G, r0):
    """
    Remove todas as arestas que entram no nó raiz r0 no grafo G.
    Retorna o grafo atualizado.
    """
    try:
        # Verifica se G é um grafo direcionado
        if not isinstance(G, nx.DiGraph):
            raise TypeError("O grafo fornecido deve ser do tipo networkx.DiGraph.")

        # Verifica se r0 existe no grafo
        if r0 not in G:
            raise ValueError(f"O nó raiz '{r0}' não existe no grafo.")

        # Remove as arestas que entram em r0
        in_edges = list(G.in_edges(r0))
        if not in_edges:
            print(f"[INFO] Nenhuma aresta entrando em '{r0}' para remover.")
        else:
            G.remove_edges_from(in_edges)

        return G

    except Exception as e:
        print(f"[ERRO] Falha ao remover arestas que entram em '{r0}': {e}")
        return G  # Retorna o grafo original como fallback

def remove_edge_from_cycle(C, G, in_edge):
    """
    Remove do ciclo C a aresta que entra no vértice `v` (obtido de `in_edge`)
    caso esse vértice já tenha um predecessor em C.
    """
    try:
        # Verifica se C é um grafo válido
        if not isinstance(C, (nx.DiGraph, nx.Graph)):
            raise TypeError("O ciclo fornecido (C) deve ser um grafo válido.")

        C = C.copy()  # Cópia segura

        if in_edge:
            if len(in_edge) != 3:
                raise ValueError("A aresta in_edge deve ter 3 elementos (u, v, w).")
            _, v, _ = in_edge

            if v not in C:
                raise ValueError(f"O vértice destino '{v}' da in_edge não está presente no ciclo.")

            # Procura um predecessor em C que leva até v
            u = next((u for u, _ in C.in_edges(v)), None)
            if u:
                C.remove_edge(u, v)
        return C

    except Exception as e:
        print(f"[ERRO] Falha ao remover aresta do ciclo: {e}")
        return C  # Retorna o ciclo original inalterado como fallback

# Algoritmo de Chu-Liu
def find_optimum_arborescence(G, r0, level=0, raise_on_error=False):
    indent = "  " * level
    try:
        logger.info(f"{indent}Iniciando nível {level}")
        if not isinstance(G, nx.DiGraph):
            raise TypeError("O grafo fornecido deve ser um networkx.DiGraph.")
        if r0 not in G:
            raise ValueError(f"O nó raiz '{r0}' não está presente no grafo.")

        G_arb = G.copy()
        draw_graph(G_arb, f"{indent}Grafo original")
        remove_edge_in_r0(G_arb, r0)
        draw_graph(G_arb, f"{indent}Após remoção de entradas")

        for v in G_arb.nodes:
            if v != r0:
                change_edge_weight(G_arb, v)
        draw_graph(G_arb, f"{indent}Após ajuste de pesos")

        F_star = get_Fstar(G_arb, r0)
        draw_graph(F_star, f"{indent}F_star")

        if is_F_star_arborescence(F_star, r0):
            for u, v in F_star.edges:
                F_star[u][v]['w'] = G[u][v]['w']
            return F_star

        C = find_cycle(F_star)
        if not C or C.number_of_nodes() == 0: # TODO - No final dos testes podemos remover esse if, já que se ele existe significa que algo deu errado.
            raise RuntimeError("Ciclo não encontrado em F_star")

        contracted_label = f"C*{level}"
        G_prime, in_edge, out_edge = contract_cycle(G_arb, C, contracted_label)
        F_prime = find_optimum_arborescence(G_prime, r0, level + 1, raise_on_error)

        C = remove_edge_from_cycle(C, G, in_edge)
        for u, v in C.edges:
            F_prime.add_edge(u, v)
        if in_edge:
            u, v, w = in_edge
            F_prime.add_edge(u, v, w=w)
        if out_edge:
            u, v, w = out_edge
            F_prime.add_edge(u, v, w=w)
        if contracted_label in F_prime:
            F_prime.remove_node(contracted_label)

        for u, v in F_prime.edges:
            F_prime[u][v]['w'] = G[u][v]['w']
        return F_prime

    except Exception as e:
        logger.error(f"{indent}Erro no nível {level}: {e}")
        if raise_on_error:
            raise
        return nx.DiGraph()

# Para testar
def load_test_graph(event=None):
    global G
    G.clear()
    # Grafo exemplo
    G.add_edge("r0", "B", w=10)
    G.add_edge("r0", "A", w=2)
    G.add_edge("r0", "C", w=10)
    G.add_edge("B", "A", w=1)
    G.add_edge("A", "C", w=4)
    G.add_edge("C", "D", w=2)
    G.add_edge("D", "B", w=2)
    G.add_edge("B", "E", w=8)
    G.add_edge("C", "E", w=4)

    log("Grafo de teste carregado.")
    update_graph_output(G, "Grafo de Teste (DG)")

def show_ready_arborescence(event=None):
    T = nx.DiGraph()
    T.add_edge("r0", "A", w=2)
    T.add_edge("A", "C", w=4)
    T.add_edge("C", "D", w=2)
    T.add_edge("D", "B", w=2)
    T.add_edge("C", "E", w=4)
    update_graph_output(T, "Arborescência Pré-definida")
    log("Arborescência pronta exibida.")
