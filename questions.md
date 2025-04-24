## Dúvidas sobre a implementação 


> “Choose a minimal non-empty subset X ⊆ V − r₀ with no entering 0-edge.”

---

### Função 1 – Identificação do território sem entrada de custo 0

**Entradas:**
- Grafo `G`
- Lista `L` contendo os arcos de custo 0 já existentes em `G`
- Estrutura auxiliar `D₀` (opcional)
- Raiz `r₀`

**Processamento:**
1. Escolho um vértice arbitrário `v ∈ V`, tal que `v ≠ r₀`.
2. Verifico os caminhos que chegam em `v`.

   **Dúvidas:**
   - Devo considerar apenas os caminhos de **custo 0** para essa análise?
     - Se sim, **qual a melhor forma de construir esses caminhos**?
     - No ínicio, reutilizo a função `change_edge_weight()` usada no algoritmo de Chu-Liu para forçar os custos a 0?
   - Para armazenar os caminhos, uso uma estrutura como o `D₀`.
   - Gravo em D0, tais caminhos de forma reversa ou seja (de v até a origem do caminho)
   - Uso a função Nx.is_path(v, u) sendo v o vértice citado, e u, cada um dos vértices
     - **Ou posso simplesmente utilizar a função `networkx.ancestors()`?** (link)[https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.ancestors.html]
     - Exemplo: `sorted(nx.ancestors(DG, 2))` retorna `[0, 1]`.
  
3. Os vértices obtidos formarão um "território".
4. Verifico se `r₀` está neste território:
   - Se **não** estiver: retorno o território como subconjunto mínimo `X`.
   - Caso contrário: escolho outro `v` e repito.

**Saída esperada:**
- Um subconjunto `X` ⊂ V - r₀, mínimo e não vazio, tal que nenhuma aresta de custo 0 entra em `X`.

---

### Função 2 – Modificação dos custos dos arcos que entram em `X`

**Entradas:**
- Cópia do grafo `G` (`G_copy`)
- Território `X`

**Processamento:**
1. Identifico todos os arcos **positivos** que entram em `X`.
2. Subtraio de todos esses arcos o **menor valor entre eles**.
3. Adiciono o(s) novo(s) arco(s) com custo 0 resultante(s) à lista `L`.

**Saídas:**
- `G_copy` modificado
- Lista `L` atualizada

---

#### Resumo das dúvidas

1. O território deve ser construído apenas com arestas de custo 0?
2. Qual a melhor forma de construir os caminhos que chegam em `v`?
3. Devo usar a função `networkx.ancestors()` ou `Nx.is_path(v, u)`?
4. A função `change_edge_weight()` do algoritmo de Chu-Liu é adequada para forçar os custos a 0? Ou como eu zero os custos no começo do processamento?
