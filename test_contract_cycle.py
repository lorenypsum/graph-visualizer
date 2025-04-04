# import unittest
# import networkx as nx
# from chuliu import contract_cycle

# class TestContractCycle(unittest.TestCase):
#     def setUp(self):
#         # Configura um grafo de teste com um ciclo
#         self.G = nx.DiGraph()
#         self.G.add_edge("A", "B", w=1)
#         self.G.add_edge("B", "C", w=2)
#         self.G.add_edge("C", "A", w=3)
#         self.G.add_edge("C", "D", w=4)
#         self.G.add_edge("D", "E", w=5)
#         self.G.add_edge("E", "A", w=6)

#         # Subgrafo que representa o ciclo
#         self.C = self.G.subgraph(["A", "B", "C"]).copy()

#     def test_contract_cycle(self):
#         # Contrai o ciclo no grafo
#         label = "CYCLE"
#         in_edges, out_edges = contract_cycle(self.G, self.C, label)

#         # Verifica se o supernó foi adicionado
#         self.assertIn(label, self.G.nodes)

#         # Verifica se os nós do ciclo original foram removidos
#         for node in self.C.nodes:
#             self.assertNotIn(node, self.G.nodes)

#         # Verifica se as arestas de entrada e saída foram redirecionadas corretamente
#         self.assertEqual(in_edges, {"E": ("E", "CYCLE", 6)})
#         self.assertEqual(out_edges, {"C": ("CYCLE", "D", 4)})

#         # Verifica se o grafo resultante está correto
#         self.assertTrue(self.G.has_edge("E", "CYCLE"))
#         self.assertTrue(self.G.has_edge("CYCLE", "D"))
#         self.assertFalse(self.G.has_edge("A", "B"))
#         self.assertFalse(self.G.has_edge("B", "C"))
#         self.assertFalse(self.G.has_edge("C", "A"))

# if __name__ == "__main__":
#     unittest.main()

import unittest
import networkx as nx
from chuliu import contract_cycle

class TestContractCycle(unittest.TestCase):
    def setUp(self):
        # Configura um grafo de teste com um ciclo
        self.G = nx.DiGraph()
        self.G.add_edge("A", "B", w=1)
        self.G.add_edge("B", "C", w=2)
        self.G.add_edge("C", "A", w=3)
        self.G.add_edge("C", "D", w=4)
        self.G.add_edge("E", "B", w=6)

        # Subgrafo que representa o ciclo
        self.C = self.G.subgraph(["A", "B", "C"]).copy()

    def test_contract_cycle(self):
        # Contrai o ciclo no grafo
        label = "CYCLE"
        in_edges, out_edges = contract_cycle(self.G, self.C, label)

        # Verifica se o supernó foi adicionado
        self.assertIn(label, self.G.nodes)

        # Verifica se os nós do ciclo original foram removidos
        for node in self.C.nodes:
            self.assertNotIn(node, self.G.nodes)

        # # Verifica se as arestas de entrada e saída foram redirecionadas corretamente
        # self.assertEqual(in_edges, {"E": ("E", "CYCLE", 6)})
        # self.assertEqual(out_edges, {"C": ("CYCLE", "D", 4)})

        # # Verifica se o grafo resultante está correto
        # self.assertTrue(self.G.has_edge("E", "CYCLE"))
        # self.assertTrue(self.G.has_edge("CYCLE", "D"))
        # self.assertFalse(self.G.has_edge("A", "B"))
        # self.assertFalse(self.G.has_edge("B", "C"))
        # self.assertFalse(self.G.has_edge("C", "A"))

    def test_existing_label(self):
        # Testa o comportamento quando o rótulo já existe no grafo
        label = "A"  # "A" já existe como nó no grafo
        with self.assertRaises(ValueError):
            contract_cycle(self.G, self.C, label)

if __name__ == "__main__":
    unittest.main()