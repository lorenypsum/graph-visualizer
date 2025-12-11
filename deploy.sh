#!/bin/bash
# Script para deploy no GitHub Pages

echo "🚀 Iniciando deploy para GitHub Pages..."

# Verificar se estamos na branch main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Você deve estar na branch main para fazer deploy"
    exit 1
fi

# Garantir que tudo está commitado
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Você tem mudanças não commitadas. Commit ou stash antes de fazer deploy."
    exit 1
fi

# Checkout da branch gh-pages
git checkout gh-pages

# Fazer merge da main
git merge main --no-edit

# Adicionar todos os arquivos necessários
git add -f index.html pages/ assets/ scripts/ *.py *.json requirements.txt Pipfile

# Commit
git commit -m "Deploy to GitHub Pages - $(date '+%Y-%m-%d %H:%M:%S')" || echo "Nada para commitar"

# Push
git push origin gh-pages

# Voltar para main
git checkout main

echo "✅ Deploy concluído! Verifique em alguns minutos: https://lorenypsum.github.io/graph-visualizer/"
