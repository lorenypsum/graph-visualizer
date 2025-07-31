import csv
import os
import random
import time
import traceback

import networkx as nx

from andrasfrank import (
    phase1_find_minimum_arborescence,
    phase2_find_minimum_arborescence,
    phase2_find_minimum_arborescence_v2,
)
from chuliu import find_optimum_arborescence

# Parâmetros gerais
NUM_TESTS = 2000
MIN_VERTICES = 4
MAX_VERTICES = 4
LOG_CSV_PATH = "test_results.csv"
LOG_TXT_PATH = "test_log.txt"
ROOT = "r0"

# Garante saída limpa
if os.path.exists(LOG_CSV_PATH):
    os.remove(LOG_CSV_PATH)
if os.path.exists(LOG_TXT_PATH):
    os.remove(LOG_TXT_PATH)


def log_console_and_file(msg):
    print(msg)
    with open(LOG_TXT_PATH, "a") as f:
        f.write(msg + "\n")


def build_rooted_digraph(n, m, r0, peso_min=1, peso_max=20):
    if m is None:
        m = 2 * n  # número de arestas default

    D = nx.DiGraph()
    D.add_node(r0)
    nodes = [f"v{i}" for i in range(n - 1)]
    all_nodes = [r0] + nodes

    reached = {r0}
    remaining = set(nodes)

    while remaining:
        v = remaining.pop()
        u = random.choice(list(reached))
        D.add_edge(u, v, w=random.randint(peso_min, peso_max))
        reached.add(v)

    while D.number_of_edges() < m:
        u, v = random.sample(all_nodes, 2)
        if not D.has_edge(u, v) and u != v:
            D.add_edge(u, v, w=random.randint(peso_min, peso_max))

    return D


def get_total_cost(G):
    return sum(data["w"] for _, _, data in G.edges(data=True))


def contains_arborescence(D, r0):
    tree = nx.dfs_tree(D, source=r0)
    return tree.number_of_nodes() == D.number_of_nodes()

def remove_edges_to_r0(D, r0):
    D.remove_edges_from(list(D.in_edges(r0)))
    return D

# Header do CSV
with open(LOG_CSV_PATH, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Teste",
        "Vértices",
        "Arestas",
        "Custo_ChuLiu",
        "Custo_Frank1",
        "Custo_Frank2",
        "Sucesso",
        "Erro",
        "Tempo_execucao_seg",
    ])

success_count = 0
failure_count = 0

for i in range(1, NUM_TESTS + 1):
    n = random.randint(MIN_VERTICES, MAX_VERTICES)
    m = random.randint(n, 3 * n)

    log_console_and_file(f"\n=== Teste #{i} - Vértices: {n}, Arestas: {m} ===")
    success = False
    erro = ""
    custo1 = custo2 = custo3 = "-"
    start_time = time.time()

    try:
        D = build_rooted_digraph(n=n, m=m, r0=ROOT)
        print(f"🔍 Grafo original: {D.edges(data=True)}")
        if not contains_arborescence(D, ROOT):
            raise Exception("Grafo gerado não tem arborescência com raiz.")

        # Remover arestas que entram em ROOT para uniformizar a entrada
        D1 = D.copy()
        D1 = remove_edges_to_r0(D1, ROOT)

        arbo1 = find_optimum_arborescence(D1, ROOT)
        custo1 = get_total_cost(arbo1)
        print(f"🔍Custo ChuLiu:{custo1} Arbo ChuLiu: {arbo1.edges(data=True)}")

        A_zero = phase1_find_minimum_arborescence(D1, ROOT)

        arbo2 = phase2_find_minimum_arborescence(D1, ROOT, A_zero)
        custo2 = get_total_cost(arbo2)
        print(f"Custo Frank: {custo2} 🔍 Arbo Frank: {arbo2.edges(data=True)}")

        arbo3 = phase2_find_minimum_arborescence_v2(D1, ROOT, A_zero)
        custo3 = get_total_cost(arbo3)
        print(f"Custo Frank V2: {custo3} 🔍 Arbo Frank V2: {arbo3.edges(data=True)}")

        assert custo1 == custo2 == custo3, (
            f"Custos divergentes: CHULIU {custo1}, FRANK {custo2}, FRANK_V2 {custo3}"
        )
        success = True
        log_console_and_file(f"✅ Sucesso - Custo: {custo1}")
    except Exception as e:
        erro = str(e)
        log_console_and_file(f"❌ Erro: {erro}")
        traceback.print_exc(file=open(LOG_TXT_PATH, "a"))

    elapsed = round(time.time() - start_time, 4)

    # Escreve no CSV
    with open(LOG_CSV_PATH, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            i,
            n,
            m,
            custo1,
            custo2,
            custo3,
            "OK" if success else "FAIL",
            erro,
            elapsed,
        ])

    # Atualiza contadores
    if success:
        success_count += 1
    else:
        failure_count += 1

# Registro final de totais de sucesso e falha
log_console_and_file(
    f"\n🧪 Testagem em volume finalizada. Sucessos: {success_count}, Falhas: {failure_count}."
)

