document.addEventListener("DOMContentLoaded", function () {
    let nodeId = 1; 
    let selectedNode = null;
    const cy = cytoscape({
        container: document.getElementById('graph-editor'),
        elements: [],
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#5A3CE5',
                    'label': 'data(id)',
                    'color': '#fff',
                    'text-valign': 'center',
                    'text-halign': 'center',
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(weight)'
                }
            }
        ],
        layout: { name: 'preset' }
    });
    
    // Adiciona nó ao clicar no canvas
    cy.on('tap', function (event) {
        if (event.target === cy) {
            const pos = event.position;
            const newId = `N${nodeId++}`;
            cy.add({
                group: 'nodes',
                data: { id: newId },
                position: { x: pos.x, y: pos.y }
            });
        }
    });

    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        if (!selectedNode) {
            selectedNode = node;
            node.style('border-color', '#F59E42');
            node.style('border-width', '4px');
        } else if (selectedNode.id() !== node.id()) {
            // Pergunta o peso da aresta
            const weight = prompt('Peso da aresta:', '1');
            if (weight !== null) {
                cy.add({
                    group: 'edges',
                    data: {
                        id: `e${selectedNode.id()}_${node.id()}`,
                        source: selectedNode.id(),
                        target: node.id(),
                        weight: weight
                    }
                });
            }
            // Reseta seleção visual
            selectedNode.style('border-color', '#5A3CE5');
            selectedNode.style('border-width', '0px');
            selectedNode = null;
        } else {
            // Clique duplo no mesmo nó: desmarca
            selectedNode.style('border-color', '#5A3CE5');
            selectedNode.style('border-width', '0px');
            selectedNode = null;
        }
    });

    cy.on('dbltap', 'node', function(evt) {
        const oldNode = evt.target;
        const oldId = oldNode.id();
        const newId = prompt('Novo nome para o nó:', oldId);
        if (newId && newId !== oldId) {
            const position = oldNode.position();
            // Salva as arestas conectadas
            const connectedEdges = oldNode.connectedEdges().map(edge => ({
                data: { ...edge.data() }
            }));

            // Remove o nó antigo
            oldNode.remove();

            // Adiciona o novo nó
            cy.add({
                group: 'nodes',
                data: { id: newId },
                position: position
            });

            // Reconecta as arestas
            connectedEdges.forEach(edge => {
                // Atualiza source/target se necessário
                if (edge.data.source === oldId) edge.data.source = newId;
                if (edge.data.target === oldId) edge.data.target = newId;
                // Remove id duplicado de aresta se necessário
                edge.data.id = `e${edge.data.source}_${edge.data.target}`;
                // Evita duplicar arestas já existentes
                if (!cy.getElementById(edge.data.id).length) {
                    cy.add({
                        group: 'edges',
                        data: edge.data
                    });
                }
            });
        }
    });

    // Função para remover elemento selecionado
    // function showDeleteMenu(ele, x, y) {
    //     // Remove menu antigo se existir
    //     let oldMenu = document.getElementById('cy-delete-menu');
    //     if (oldMenu) oldMenu.remove();

    //     // Cria menu simples
    //     const menu = document.createElement('div');
    //     menu.id = 'cy-delete-menu';
    //     menu.style.position = 'fixed';
    //     menu.style.left = x + 'px';
    //     menu.style.top = y + 'px';
    //     menu.style.background = '#fff';
    //     menu.style.border = '1px solid #ccc';
    //     menu.style.padding = '6px 12px';
    //     menu.style.borderRadius = '6px';
    //     menu.style.cursor = 'pointer';
    //     menu.style.zIndex = 1000;
    //     menu.innerText = 'Excluir';

    //     menu.onclick = function() {
    //         ele.remove();
    //         menu.remove();
    //     };

    //     document.body.appendChild(menu);

    //     // Remove menu ao clicar fora
    //     document.addEventListener('click', function handler() {
    //         menu.remove();
    //         document.removeEventListener('click', handler);
    //     });
    // }

    // // Botão direito em nó
    // cy.on('cxttap', 'node', function(evt) {
    //     const node = evt.target;
    //     const pos = evt.originalEvent;
    //     showDeleteMenu(node, pos.clientX, pos.clientY);
    // });

    // Função para menu de contexto em nó (renomear e excluir)
    function showNodeMenu(node, x, y) {
        // Remove menu antigo se existir
        let oldMenu = document.getElementById('cy-node-menu');
        if (oldMenu) oldMenu.remove();

        // Cria menu
        const menu = document.createElement('div');
        menu.id = 'cy-node-menu';
        menu.style.position = 'fixed';
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.background = '#fff';
        menu.style.border = '1px solid #ccc';
        menu.style.padding = '6px 0';
        menu.style.borderRadius = '6px';
        menu.style.zIndex = 1000;
        menu.style.minWidth = '120px';

        // Opção Renomear
        const rename = document.createElement('div');
        rename.innerText = 'Renomear';
        rename.style.padding = '6px 16px';
        rename.style.cursor = 'pointer';
        rename.onmouseover = () => rename.style.background = '#eee';
        rename.onmouseout = () => rename.style.background = '#fff';
        rename.onclick = function() {
            menu.remove();
            const oldId = node.id();
            const newId = prompt('Novo nome para o nó:', oldId);
            if (newId && newId !== oldId) {
                const position = node.position();
                const connectedEdges = node.connectedEdges().map(edge => ({
                    data: { ...edge.data() }
                }));
                node.remove();
                cy.add({
                    group: 'nodes',
                    data: { id: newId },
                    position: position
                });
                connectedEdges.forEach(edge => {
                    if (edge.data.source === oldId) edge.data.source = newId;
                    if (edge.data.target === oldId) edge.data.target = newId;
                    edge.data.id = `e${edge.data.source}_${edge.data.target}`;
                    if (!cy.getElementById(edge.data.id).length) {
                        cy.add({ group: 'edges', data: edge.data });
                    }
                });
            }
        };
        menu.appendChild(rename);

        // Opção Excluir
        const del = document.createElement('div');
        del.innerText = 'Excluir';
        del.style.padding = '6px 16px';
        del.style.cursor = 'pointer';
        del.onmouseover = () => del.style.background = '#eee';
        del.onmouseout = () => del.style.background = '#fff';
        del.onclick = function() {
            node.remove();
            menu.remove();
        };
        menu.appendChild(del);

        document.body.appendChild(menu);

        // Remove menu ao clicar fora
        document.addEventListener('click', function handler() {
            menu.remove();
            document.removeEventListener('click', handler);
        });
    
        // Remove menu ao clicar fora dele
        setTimeout(() => {
            document.addEventListener('click', function handler(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', handler);
                }
            });
        }, 0);

        // Impede que o clique no menu feche ele
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        document.body.appendChild(menu);
    }

    // Substitua o evento do botão direito em nó:
    cy.on('cxttap', 'node', function(evt) {
        const node = evt.target;
        const pos = evt.originalEvent;
        showNodeMenu(node, pos.clientX, pos.clientY);
    });

    // Função para menu de contexto em aresta
    function showEdgeMenu(edge, x, y) {
        let oldMenu = document.getElementById('cy-edge-menu');
        if (oldMenu) oldMenu.remove();

        const menu = document.createElement('div');
        menu.id = 'cy-edge-menu';
        menu.style.position = 'fixed';
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.background = '#fff';
        menu.style.border = '1px solid #ccc';
        menu.style.padding = '6px 0';
        menu.style.borderRadius = '6px';
        menu.style.zIndex = 1000;
        menu.style.minWidth = '120px';

        // Opção Alterar peso
        const edit = document.createElement('div');
        edit.innerText = 'Alterar peso';
        edit.style.padding = '6px 16px';
        edit.style.cursor = 'pointer';
        edit.onmouseover = () => edit.style.background = '#eee';
        edit.onmouseout = () => edit.style.background = '#fff';
        edit.onclick = function() {
            menu.remove();
            const newWeight = prompt('Novo peso:', edge.data('weight'));
            if (newWeight !== null) {
                edge.data('weight', newWeight);
            }
        };
        menu.appendChild(edit);

        // Opção Excluir
        const del = document.createElement('div');
        del.innerText = 'Excluir';
        del.style.padding = '6px 16px';
        del.style.cursor = 'pointer';
        del.onmouseover = () => del.style.background = '#eee';
        del.onmouseout = () => del.style.background = '#fff';
        del.onclick = function() {
            edge.remove();
            menu.remove();
        };
        menu.appendChild(del);

        document.body.appendChild(menu);

        // Remove menu ao clicar fora
        document.addEventListener('click', function handler() {
            menu.remove();
            document.removeEventListener('click', handler);
        });

         // Remove menu ao clicar fora dele
        setTimeout(() => {
            document.addEventListener('click', function handler(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', handler);
                }
            });
        }, 0);

        // Impede que o clique no menu feche ele
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        document.body.appendChild(menu);
    }

    // Substitua o evento do botão direito em aresta:
    cy.on('cxttap', 'edge', function(evt) {
        const edge = evt.target;
        const pos = evt.originalEvent;
        showEdgeMenu(edge, pos.clientX, pos.clientY);
    });

    function exportGraphToJSON() {
        return cy.json().elements;
    }

    function updatePyScriptGraph() {
        window.graph_json = JSON.stringify(exportGraphToJSON());
    }

    // Chame updatePyScriptGraph() sempre que houver alteração no grafo:
    cy.on('add remove data', function() {
        updatePyScriptGraph();
    });

    // Inicialize a variável na primeira carga
    updatePyScriptGraph();
});