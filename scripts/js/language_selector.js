const translations = {
  pt: {
    "step1-title": "Crie um grafo",
    "draw_text": "Desenhe um grafo,",
    "load-test-graph": "carregue",
    "load_pt_2": "um exemplo ou",
    "import-graph": "importe",
    "import_pt2": "um grafo já existente",
    "choose_node": "Escolha o nó raiz",
    "run": "Execute o algoritmo",
    "graph-editor-text": "Grafo Original",
    "arborescence-viewer-text": "Arborescência",
    "log-text": "Log de Execução",
    "title_step": "Passo a Passo",
    "step_warning": 'Execute o algoritmo para visualizar o passo-a-passo',
    "toast-danger-msg": 'Ocorreu um erro.',
    "close": 'Fechar',
    "loading_text": 'Processando...',
    "peso": 'Peso da Aresta',
    "edge-weight-cancel": 'Cancelar',
    "edge-weight-ok": 'OK'

  },
  en: {
    "step1-title": "Create a graph",
    "draw_text": "Draw a graph,",
    "load-test-graph": "load",
    "load_pt_2": "an example or",
    "import-graph": "import",
    "import_pt2": "an existing graph",
    "choose_node": "Choose the root node",
    "run": "Run the algorithm",
    "graph-editor-text": "Original Graph",
    "arborescence-viewer-text": "Arborescence",
    "log-text": "Execution Log",
    "title_step": "Step by Step",
    "step_warning": 'Run the algorithm to see the step-by-step',
    "toast-danger-msg": 'An error occurred.',
    "close": 'Close',
    "loading_text": 'Processing...',
    "peso": 'Edge Weight',
    "edge-weight-cancel": 'Cancel',
    "edge-weight-ok": 'OK'

  }
};

document.getElementById('language-selector').addEventListener('change', function(e) {
  const lang = e.target.value;
  localStorage.setItem('lang', lang);
  updateTexts(lang);
});

function updateTexts(lang) {
  for (const key in translations[lang]) {
    const el = document.getElementById(key);
    if (el) el.textContent = translations[lang][key];
  }
}

const lang = localStorage.getItem('lang') || 'pt';
document.getElementById('language-selector').value = lang;
updateTexts(lang);