document.addEventListener("DOMContentLoaded", function () {
    let nodeId = 1;
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

    // Adiciona um nó inicial para teste
    cy.add({ group: 'nodes', data: { id: 'A' }, position: { x: 100, y: 100 } });

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
});