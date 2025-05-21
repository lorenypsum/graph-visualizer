function toggleCollapser() {
    const content = document.getElementById("log-collapser-content");
    const icon = document.getElementById("collapser-icon");

    // Alterna a visibilidade do conteúdo
    content.classList.toggle("hidden");

    // Alterna a imagem do botão
    if (content.classList.contains("hidden")) {
        icon.src = "../assets/plus.png"; // Ícone de expandir
    } else {
        icon.src = "../assets/minus.png"; // Ícone de contrair
    }
}
function toggleStep(stepId, iconId) {
    const content = document.querySelector(`#${stepId} .detalhes`);
    const icon = document.getElementById(iconId);
    const btn_step = document.querySelector(`#${stepId} .btn_step`);


    // Alterna a visibilidade do conteúdo
    content.classList.toggle("hidden");

    // Alterna a imagem do botão
    if (content.classList.contains("hidden")) {
        icon.src = "../assets/plus.png"; // Ícone de expandir
        btn_step.classList.remove("bg-[#f5f5f5]");
    } else {
        icon.src = "../assets/minus.png"; // Ícone de contrair
        btn_step.classList.add("bg-[#f5f5f5]");
    }
}