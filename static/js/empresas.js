// =========================
// ELEMENTOS DA PÁGINA
// =========================

const modalEmpresa = document.getElementById("modalEmpresa");
const modalExcluir = document.getElementById("modalExcluir");

const empresaExcluir = document.getElementById("empresaExcluir");
const formExcluir = document.getElementById("formExcluir");
const formEmpresa = document.getElementById("formEmpresa");


// =========================
// EXCLUIR EMPRESA
// =========================

document.querySelectorAll("a.excluir").forEach(function (botao) {

    botao.addEventListener("click", function (e) {

        e.preventDefault();

        empresaExcluir.innerText = this.dataset.razao;

        formExcluir.action =
            "/empresas/excluir/" + this.dataset.id;

        modalExcluir.classList.add("active");

    });

});

function fecharModalExcluir() {

    modalExcluir.classList.remove("active");

}


// =========================
// ABRIR / FECHAR MODAL
// =========================

function abrirModal() {

    modalEmpresa.classList.add("active");

    formEmpresa.reset();

    document.getElementById("empresa_id").value = "";

    formEmpresa.action = "/empresas/nova";

    limparMensagem();

}

function fecharModal() {

    modalEmpresa.classList.remove("active");

}


// =========================
// MENSAGENS
// =========================

function obterMensagem() {

    let msg = document.getElementById("mensagemErro");

    if (!msg) {

        msg = document.createElement("div");

        msg.id = "mensagemErro";

        msg.style.background = "#ffe5e5";
        msg.style.color = "#b00020";
        msg.style.border = "1px solid #ffb0b0";
        msg.style.padding = "10px";
        msg.style.marginBottom = "15px";
        msg.style.borderRadius = "6px";
        msg.style.display = "none";

        formEmpresa.prepend(msg);

    }

    return msg;

}

function mostrarMensagem(texto) {

    const msg = obterMensagem();

    msg.innerText = texto;

    msg.style.display = "block";

}

function limparMensagem() {

    const msg = document.getElementById("mensagemErro");

    if (msg) {

        msg.style.display = "none";

        msg.innerText = "";

    }

}


// =========================
// ENVIO AJAX
// =========================

formEmpresa.addEventListener("submit", async function (e) {

    // Somente para NOVO cadastro
    if (!formEmpresa.action.endsWith("/empresas/nova")) {

        return;

    }

    e.preventDefault();

    limparMensagem();

    const dados = new FormData(formEmpresa);

    try {

        const resposta = await fetch(formEmpresa.action, {

            method: "POST",

            body: dados

        });

        const json = await resposta.json();

        if (json.sucesso) {

            fecharModal();

            location.reload();

            return;

        }

        mostrarMensagem(json.mensagem);

    }

    catch (erro) {

        mostrarMensagem("Erro ao comunicar com o servidor.");

        console.error(erro);

    }

});
// =========================
// PESQUISA
// =========================

const pesquisa = document.getElementById("pesquisa");

if (pesquisa) {

    pesquisa.addEventListener("keyup", function () {

        let filtro = this.value.toLowerCase();

        let linhas = document.querySelectorAll("#tabelaEmpresas tbody tr");

        linhas.forEach(function (linha) {

            let texto = linha.innerText.toLowerCase();

            if (texto.indexOf(filtro) > -1) {

                linha.style.display = "";

            } else {

                linha.style.display = "none";

            }

        });

    });

}


// =========================
// EDITAR EMPRESA
// =========================

document.querySelectorAll(".editar").forEach(function (botao) {

    botao.addEventListener("click", function (e) {

        e.preventDefault();

        abrirModal();

        const id = this.dataset.id;

        document.getElementById("empresa_id").value = id;

        formEmpresa.action = "/empresas/editar/" + id;

        document.querySelector("[name=razao_social]").value =
            this.dataset.razao;

        document.querySelector("[name=nome_fantasia]").value =
            this.dataset.fantasia;

        let cnpj = this.dataset.cnpj.replace(/\D/g, "");

        if (cnpj.length === 14) {

            cnpj = cnpj.replace(/^(\d{2})(\d)/, "$1.$2");
            cnpj = cnpj.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
            cnpj = cnpj.replace(/\.(\d{3})(\d)/, ".$1/$2");
            cnpj = cnpj.replace(/(\d{4})(\d)/, "$1-$2");

        }

        document.querySelector("[name=cnpj]").value = cnpj;

        document.querySelector("[name=inscricao_estadual]").value =
            this.dataset.ie;

        document.querySelector("[name=responsavel]").value =
            this.dataset.responsavel;

        document.querySelector("[name=telefone]").value =
            this.dataset.telefone;

        document.querySelector("[name=whatsapp]").value =
            this.dataset.whatsapp;

        document.querySelector("[name=email]").value =
            this.dataset.email;

        document.querySelector("[name=cep]").value =
            this.dataset.cep;

        document.querySelector("[name=endereco]").value =
            this.dataset.endereco;

        document.querySelector("[name=numero]").value =
            this.dataset.numero;

        document.querySelector("[name=bairro]").value =
            this.dataset.bairro;

        document.querySelector("[name=cidade]").value =
            this.dataset.cidade;

        document.querySelector("[name=estado]").value =
            this.dataset.estado;

        document.querySelector("[name=status]").value =
            this.dataset.status;

        limparMensagem();

    });

});


// =========================
// SUBMIT DA EDIÇÃO
// =========================

formEmpresa.addEventListener("submit", function (e) {

    if (formEmpresa.action.endsWith("/empresas/nova")) {

        return;

    }

    // edição continua utilizando POST normal
    // exatamente como está no backend

});
// =========================
// MÁSCARA CNPJ
// =========================

function mascaraCNPJ(campo) {

    let valor = campo.value.replace(/\D/g, "");

    valor = valor.replace(/^(\d{2})(\d)/, "$1.$2");
    valor = valor.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
    valor = valor.replace(/\.(\d{3})(\d)/, ".$1/$2");
    valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

    campo.value = valor.substring(0, 18);

}

document.querySelectorAll("[name=cnpj]").forEach(function (campo) {

    campo.addEventListener("input", function () {

        mascaraCNPJ(this);

    });

});


// =========================
// FORMATA CNPJ DA TABELA
// =========================

document.querySelectorAll(".cnpj").forEach(function (campo) {

    let valor = campo.innerText.replace(/\D/g, "");

    if (valor.length === 14) {

        valor = valor.replace(/^(\d{2})(\d)/, "$1.$2");
        valor = valor.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
        valor = valor.replace(/\.(\d{3})(\d)/, ".$1/$2");
        valor = valor.replace(/(\d{4})(\d)/, "$1-$2");

        campo.innerText = valor;

    }

});


// =========================
// FECHAR MODAL AO CLICAR FORA
// =========================

window.addEventListener("click", function (e) {

    if (e.target === modalEmpresa) {

        fecharModal();

    }

    if (e.target === modalExcluir) {

        fecharModalExcluir();

    }

});


// =========================
// TECLA ESC
// =========================

document.addEventListener("keydown", function (e) {

    if (e.key === "Escape") {

        fecharModal();

        fecharModalExcluir();

    }

});


// =========================
// FIM DO ARQUIVO
// =========================