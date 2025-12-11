#!/bin/bash
# Script para deploy no GitHub Pages (recriando branch)

echo "🚀 Iniciando deploy para GitHub Pages..."

# Verificar se estamos na branch main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Você deve estar na branch main para fazer deploy"
    exit 1
fi

# Deletar branch gh-pages local se existir
git branch -D gh-pages 2>/dev/null || true

# Criar branch gh-pages órfã (sem histórico)
git checkout --orphan gh-pages

# Adicionar apenas arquivos necessários para o site
git add -f index.html pages/ assets/ scripts/ pyscript.json requirements.txt Pipfile tailwind.config.js

# Criar .nojekyll para desabilitar Jekyll
touch .nojekyll
git add .nojekyll

# Commit
git commit -m "Deploy to GitHub Pages - $(date '+%Y-%m-%d %H:%M:%S')"

# Push forçado (substituindo o conteúdo antigo)
git push -f origin gh-pages

# Voltar para main
git checkout main

echo "✅ Deploy concluído! Verifique em alguns minutos: https://lorenypsum.github.io/graph-visualizer/"
