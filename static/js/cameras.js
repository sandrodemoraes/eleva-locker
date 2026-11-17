const modalCamera = document.getElementById("modalCamera");
const modalExcluir = document.getElementById("modalExcluir");
const cameraExcluir = document.getElementById("cameraExcluir");
const formExcluir = document.getElementById("formExcluir");
const formCamera = document.getElementById("formCamera");
const tituloModal = document.getElementById("tituloModal");

document.querySelectorAll("a.excluir").forEach(function (botao) {
    botao.addEventListener("click", function (e) {
        e.preventDefault();
        cameraExcluir.innerText = this.dataset.nome;
        formExcluir.action = "/cameras/excluir/" + this.dataset.id;
        modalExcluir.style.display = "flex";
    });
});

function fecharModalExcluir() {
    modalExcluir.style.display = "none";
}

function abrirModal() {
    modalCamera.style.display = "flex";
    formCamera.reset();
    document.getElementById("camera_id").value = "";
    formCamera.action = "/cameras/nova";
    formCamera.method = "POST";
    tituloModal.innerText = "Nova câmera";
    limparMensagem();
}

function fecharModal() {
    modalCamera.style.display = "none";
}

function obterMensagem() {
    let msg = document.getElementById("mensagemErro");

    if (!msg) {
        msg = document.createElement("div");
        msg.id = "mensagemErro";
        msg.style.background = "#ffe5e5";
        msg.style.color = "#b30000";
        msg.style.border = "1px solid #ffb3b3";
        msg.style.padding = "12px";
        msg.style.marginBottom = "16px";
        msg.style.borderRadius = "8px";
        msg.style.fontWeight = "bold";
        formCamera.prepend(msg);
    }

    return msg;
}

function limparMensagem() {
    const msg = document.getElementById("mensagemErro");
    if (msg) {
        msg.remove();
    }
}

document.querySelectorAll("a.editar").forEach(function (botao) {
    botao.addEventListener("click", function (e) {
        e.preventDefault();

        abrirModal();
        tituloModal.innerText = "Editar câmera";

        document.getElementById("camera_id").value = this.dataset.id;
        document.getElementById("nome").value = this.dataset.nome || "";
        document.getElementById("slug").value = this.dataset.slug || "";
        document.getElementById("local").value = this.dataset.local || "";
        document.getElementById("cidade").value = this.dataset.cidade || "";
        document.getElementById("estado").value = this.dataset.estado || "";
        document.getElementById("descricao").value = this.dataset.descricao || "";
        document.getElementById("youtube_video_id").value = this.dataset.youtubeVideoId || "";
        document.getElementById("youtube_channel_url").value = this.dataset.youtubeChannelUrl || "";
        document.getElementById("stream_status").value = this.dataset.streamStatus || "offline";
        document.getElementById("latitude").value = this.dataset.latitude || "";
        document.getElementById("longitude").value = this.dataset.longitude || "";
        document.getElementById("ordem").value = this.dataset.ordem || "0";
        document.getElementById("status").value = this.dataset.status || "1";

        formCamera.action = "/cameras/editar/" + this.dataset.id;
    });
});

formCamera.addEventListener("submit", function (e) {
    if (formCamera.action.indexOf("/cameras/nova") === -1) {
        return;
    }

    e.preventDefault();
    limparMensagem();

    const dados = new FormData(formCamera);

    fetch("/cameras/nova", {
        method: "POST",
        body: dados,
    })
        .then(function (resposta) {
            return resposta.json();
        })
        .then(function (json) {
            if (!json.sucesso) {
                const msg = obterMensagem();
                msg.innerText = json.mensagem || "Não foi possível salvar.";
                return;
            }

            window.location.reload();
        })
        .catch(function () {
            const msg = obterMensagem();
            msg.innerText = "Erro de comunicação com o servidor.";
        });
});

const pesquisa = document.getElementById("pesquisa");
if (pesquisa) {
    pesquisa.addEventListener("keyup", function () {
        const termo = this.value.toLowerCase();
        document.querySelectorAll("#tabelaCameras tbody tr").forEach(function (linha) {
            linha.style.display = linha.innerText.toLowerCase().includes(termo) ? "" : "none";
        });
    });
}
