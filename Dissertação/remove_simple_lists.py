#!/usr/bin/env python3
"""
Remove itemizações simples e converte para texto corrido.
Mantém apenas listas realmente necessárias (algoritmos, passos, múltiplos itens técnicos).
"""

import re
import os


def should_keep_list(content):
    """Decide se uma lista deve ser mantida baseado no contexto."""
    # Manter se contém mais de 4 itens
    item_count = content.count("\\item")
    if item_count > 4:
        return True

    # Manter se é enumerate (passos numerados)
    if "enumerate" in content:
        return True

    # Manter se tem estrutura aninhada
    if "\\begin{enumerate}" in content or content.count("\\begin{itemize}") > 1:
        return True

    # Manter se contém código ou fórmulas complexas
    if "\\texttt{" in content or "$$" in content:
        return True

    # Converter se é lista simples de 2-3 propriedades
    if item_count <= 3 and len(content) < 500:
        return False

    return True


def convert_simple_list(match):
    """Converte uma lista simples em texto corrido."""
    full_match = match.group(0)

    if should_keep_list(full_match):
        return full_match

    # Extrair os itens
    items = re.findall(r"\\item\s+([^\n]+(?:\n(?!\\item|\\end)[^\n]+)*)", full_match)

    if len(items) == 0:
        return full_match

    # Converter para texto corrido
    if len(items) == 1:
        text = items[0].strip()
    elif len(items) == 2:
        text = f"{items[0].strip()} e {items[1].strip()}"
    else:
        text = ", ".join(items[:-1]) + f" e {items[-1].strip()}"

    # Adicionar ponto final se não houver
    if not text.endswith("."):
        text += "."

    return "\n" + text + "\n"


def process_file(filepath):
    """Processa um arquivo removendo listas simples."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Padrão para capturar listas itemize simples
    pattern = r"\\begin\{itemize\}.*?\\end\{itemize\}"

    content = re.sub(pattern, convert_simple_list, content, flags=re.DOTALL)

    if content != original:
        changes = original.count("\\begin{itemize}") - content.count("\\begin{itemize}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return changes

    return 0


def main():
    """Processa todos os arquivos de capítulos."""
    base_dir = (
        "/Users/lorenypsum/Desktop/Repositórios/GraphVisualizer.nosync/Dissertação"
    )

    files_to_check = [
        "capitulos/fundamentacao-teorica/main.tex",
        "capitulos/problema-arborescencia/main.tex",
        "capitulos/implementacao-chuliu/main.tex",
        "capitulos/implementacao-andrasfrank/main.tex",
        "capitulos/fundamentacao-didatica/main.tex",
        "capitulos/implementacao-web/main.tex",
        "capitulos/resultados/main.tex",
        "capitulos/introducao.tex",
        "capitulos/conclusao.tex",
    ]

    total_removed = 0

    for file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            continue

        removed = process_file(full_path)
        if removed > 0:
            print(f"✅ {file_path}: {removed} listas convertidas")
            total_removed += removed

    print(f"\n✅ Total: {total_removed} listas simples convertidas em texto corrido")


if __name__ == "__main__":
    main()
