function abrirModalNovo() {
    document.getElementById("tituloModal").textContent = "Novo ESP32";
    document.getElementById("formEsp32").action = "/esp32/novo";
    document.getElementById("formEsp32").reset();
    document.getElementById("status").value = "Ativo";
    document.getElementById("modalEsp32").classList.add("aberto");
}

function fecharModal() {
    document.getElementById("modalEsp32").classList.remove("aberto");
}

function fecharModalExcluir() {
    document.getElementById("modalExcluir").classList.remove("aberto");
}

document.addEventListener("click", function (evento) {
    const editar = evento.target.closest("a.editar");
    if (editar) {
        evento.preventDefault();

        document.getElementById("tituloModal").textContent = "Editar ESP32";
        document.getElementById("formEsp32").action =
            "/esp32/editar/" + editar.dataset.id;

        document.getElementById("nome").value = editar.dataset.nome || "";
        document.getElementById("ip").value = editar.dataset.ip || "";
        document.getElementById("mac").value = editar.dataset.mac || "";
        document.getElementById("armario").value = editar.dataset.armario || "";
        document.getElementById("status").value = editar.dataset.status || "Ativo";

        document.getElementById("modalEsp32").classList.add("aberto");
        return;
    }

    const excluir = evento.target.closest("a.excluir");
    if (excluir) {
        evento.preventDefault();
        document.getElementById("nomeExcluir").textContent = excluir.dataset.nome || "";
        document.getElementById("formExcluir").action =
            "/esp32/excluir/" + excluir.dataset.id;
        document.getElementById("modalExcluir").classList.add("aberto");
    }
});

document.getElementById("pesquisa").addEventListener("input", function () {
    const termo = this.value.toLowerCase();
    const linhas = document.querySelectorAll("#tabelaEsp32 tbody tr");

    linhas.forEach(function (linha) {
        const texto = linha.textContent.toLowerCase();
        linha.style.display = texto.includes(termo) ? "" : "none";
    });
});

document.getElementById("modalEsp32").addEventListener("click", function (evento) {
    if (evento.target === this) {
        fecharModal();
    }
});

document.getElementById("modalExcluir").addEventListener("click", function (evento) {
    if (evento.target === this) {
        fecharModalExcluir();
    }
});
