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
    function showDeleteMenu(ele, x, y) {
        // Remove menu antigo se existir
        let oldMenu = document.getElementById('cy-delete-menu');
        if (oldMenu) oldMenu.remove();

        // Cria menu simples
        const menu = document.createElement('div');
        menu.id = 'cy-delete-menu';
        menu.style.position = 'fixed';
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.background = '#fff';
        menu.style.border = '1px solid #ccc';
        menu.style.padding = '6px 12px';
        menu.style.borderRadius = '6px';
        menu.style.cursor = 'pointer';
        menu.style.zIndex = 1000;
        menu.innerText = 'Excluir';

        menu.onclick = function() {
            ele.remove();
            menu.remove();
        };

        document.body.appendChild(menu);

        // Remove menu ao clicar fora
        document.addEventListener('click', function handler() {
            menu.remove();
            document.removeEventListener('click', handler);
        });
    }

    // Botão direito em nó
    cy.on('cxttap', 'node', function(evt) {
        const node = evt.target;
        const pos = evt.originalEvent;
        showDeleteMenu(node, pos.clientX, pos.clientY);
    });

    // Botão direito em aresta
    cy.on('cxttap', 'edge', function(evt) {
        const edge = evt.target;
        const pos = evt.originalEvent;
        showDeleteMenu(edge, pos.clientX, pos.clientY);
    });
});