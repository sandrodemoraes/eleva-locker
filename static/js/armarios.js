function abrirModalNovo() {
    document.getElementById("tituloModal").textContent = "Novo Armário";
    document.getElementById("formArmario").action = "/armarios/novo";
    document.getElementById("formArmario").reset();
    document.getElementById("status").value = "Ativo";
    document.getElementById("modalArmario").classList.add("aberto");
}

function fecharModal() {
    document.getElementById("modalArmario").classList.remove("aberto");
}

function fecharModalExcluir() {
    document.getElementById("modalExcluir").classList.remove("aberto");
}

document.addEventListener("click", function (evento) {
    const editar = evento.target.closest("a.editar");
    if (editar) {
        evento.preventDefault();

        document.getElementById("tituloModal").textContent = "Editar Armário";
        document.getElementById("formArmario").action =
            "/armarios/editar/" + editar.dataset.id;

        document.getElementById("nome").value = editar.dataset.nome || "";
        document.getElementById("endereco").value = editar.dataset.endereco || "";
        document.getElementById("cidade").value = editar.dataset.cidade || "";
        document.getElementById("estado").value = editar.dataset.estado || "";
        document.getElementById("status").value = editar.dataset.status || "Ativo";

        document.getElementById("modalArmario").classList.add("aberto");
        return;
    }

    const excluir = evento.target.closest("a.excluir");
    if (excluir) {
        evento.preventDefault();
        document.getElementById("nomeExcluir").textContent = excluir.dataset.nome || "";
        document.getElementById("formExcluir").action =
            "/armarios/excluir/" + excluir.dataset.id;
        document.getElementById("modalExcluir").classList.add("aberto");
    }
});

document.getElementById("pesquisa").addEventListener("input", function () {
    const termo = this.value.toLowerCase();
    const linhas = document.querySelectorAll("#tabelaArmarios tbody tr");

    linhas.forEach(function (linha) {
        const texto = linha.textContent.toLowerCase();
        linha.style.display = texto.includes(termo) ? "" : "none";
    });
});

document.getElementById("modalArmario").addEventListener("click", function (evento) {
    if (evento.target === this) {
        fecharModal();
    }
});

document.getElementById("modalExcluir").addEventListener("click", function (evento) {
    if (evento.target === this) {
        fecharModalExcluir();
    }
});
