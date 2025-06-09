# pseudocodigo

# arcs que vem da fase 1

#def fase 2(arcs, r0):
 
  # D = digrafo com conjunto de arcos arcs (que veio do parametro)
    # for (i, a) in enumerate(arcs):
        #D.add_edge (a, i) -> onde o i é indice do enumerate que vira o peso do arco
       # V = {r)} um conjunto que comeca com r
         # q = priority queue
          # for (a, i) in D. out_edges(r):
          #   q.add(a,i)
        # A := Digraph
#         while q: (enquanto a fila n for vazia)
#             (u, v) = q.remove_min()
#             if v e V : continue
#             A.add_edge(u, v)           
#             V.add(v) := V + {v} 
#             for (a, i) in D.out_edges(v):
#                q.add(a, i)
# return A    

# TODO:
# _prime = find_optimum_arborescence(G_arb, r0, level + 1, draw_fn=draw_fn, log=log)
# Esse parametro level+1 é justamente pra realizar a nomeação do ciclo.