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

const imageModal = document.getElementById('image-modal');
const imageModalImg = document.getElementById('image-modal-img');

document.addEventListener('click', function (e) {
    // Clique no botão expandir
    let btn = e.target.closest('.expand-button');
    if (btn) {
        e.stopPropagation();
        const imgId = btn.getAttribute('data-img-id');
        const img = document.getElementById(imgId);
        if (img) {
            imageModalImg.src = img.src;
            imageModal.classList.remove('hidden');
        }
        return;
    }
    // Clique fora da imagem (no overlay)
    if (e.target === imageModal) {
        imageModal.classList.add('hidden');
        imageModalImg.src = "";
    }
});

document.getElementById("run-algorithm").addEventListener("click", function() {
    
    showLoader();
    setTimeout(() => {
        const event = new Event("custom-event");
        document.getElementById("run-algorithm").dispatchEvent(event);
    }, 100);
});

function showLoader() {
    document.getElementById('loader-modal').classList.remove('hidden');
}

function hideLoader() {
    document.getElementById('loader-modal').classList.add('hidden');
}