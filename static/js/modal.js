// Modal compartilhado do painel: abre quando um link de fora dele carrega um
// formulário em #modal-conteudo e fecha quando o servidor avisa que salvou.
// Se o conteúdo passa de 200 ms, o modal abre com o skeleton da forma pedida no
// link (data-esqueleto, modelos em partials/_modelos_carregamento.html); se a
// busca falha, mostra a mensagem com "Tentar de novo".
(function () {
    var ATRASO = 200;
    var abertura = null; // busca em andamento para o modal (só uma por vez)
    var canceladas = new WeakSet(); // buscas canceladas ao fechar o modal
    var formaDaRepeticao = null;

    function modal() {
        return document.getElementById("modal");
    }

    function conteudo() {
        return document.getElementById("modal-conteudo");
    }

    function ehBuscaDoModal(detalhe) {
        return detalhe.target && detalhe.target.id === "modal-conteudo"
            && detalhe.requestConfig && detalhe.requestConfig.verb === "get";
    }

    function clonarModelo(id) {
        var modelo = document.getElementById(id);
        return modelo ? modelo.content.cloneNode(true) : null;
    }

    function abrir() {
        if (!modal().open) {
            modal().showModal();
        }
    }

    function tirarEsqueleto() {
        var caixa = conteudo();
        caixa.classList.remove("carregando");
        caixa.removeAttribute("aria-busy");
        caixa.querySelectorAll(":scope > .modal-esqueleto").forEach(function (esqueleto) {
            esqueleto.remove();
        });
    }

    // O conteúdo anterior só é escondido (CSS de #modal-conteudo.carregando): se o link
    // que fez a busca saísse da página, o htmx não avisaria o fim da requisição.
    function mostrarEsqueleto(forma) {
        var esqueleto = clonarModelo("modal-esqueleto-" + forma) || clonarModelo("modal-esqueleto-pares");
        if (!esqueleto) {
            return;
        }
        tirarEsqueleto();
        var caixa = conteudo();
        caixa.append(esqueleto);
        caixa.classList.add("carregando");
        caixa.setAttribute("aria-busy", "true");
        abrir();
    }

    function focarPrimeiroCampo() {
        var caixa = conteudo();
        var campo = caixa.querySelector(
            "input:not([type=hidden]):not([disabled]), select:not([disabled]), textarea:not([disabled])"
        ) || caixa.querySelector("a[href], button:not([disabled])");
        if (campo) {
            campo.focus();
        }
    }

    function mostrarFalha(busca) {
        var falha = clonarModelo("modal-falha");
        if (!falha) {
            return;
        }
        tirarEsqueleto();
        var caixa = conteudo();
        caixa.replaceChildren(falha);
        var tentar = caixa.querySelector("[data-modal-tentar]");
        tentar.addEventListener("click", function () {
            formaDaRepeticao = busca.forma;
            htmx.ajax(busca.verbo, busca.caminho, { source: caixa, target: caixa, swap: "innerHTML" });
        });
        abrir();
        tentar.focus();
    }

    // Clique repetido (no mesmo link ou em outro) enquanto o modal ainda carrega: é barrado
    // no htmx:confirm, que vem antes da fila do htmx (sem isso, o segundo clique no mesmo
    // link entraria na fila e seria enviado logo depois do primeiro).
    document.addEventListener("htmx:confirm", function (evento) {
        var detalhe = evento.detail;
        if (abertura && detalhe.target && detalhe.target.id === "modal-conteudo" && detalhe.verb === "get") {
            evento.preventDefault();
        }
    });

    document.addEventListener("htmx:beforeRequest", function (evento) {
        var detalhe = evento.detail;
        if (!ehBuscaDoModal(detalhe)) {
            return;
        }
        if (abertura) {
            evento.preventDefault();
            return;
        }
        var forma = detalhe.elt.getAttribute("data-esqueleto") || formaDaRepeticao || "pares";
        formaDaRepeticao = null;
        abertura = {
            xhr: detalhe.xhr,
            elemento: detalhe.elt,
            verbo: detalhe.requestConfig.verb,
            caminho: detalhe.requestConfig.path,
            forma: forma,
        };
        abertura.temporizador = setTimeout(function () {
            mostrarEsqueleto(forma);
        }, ATRASO);
    });

    document.addEventListener("htmx:beforeSwap", function (evento) {
        if (canceladas.has(evento.detail.xhr)) {
            evento.detail.shouldSwap = false;
        }
    });

    document.addEventListener("htmx:afterSwap", function (evento) {
        if (evento.detail.target.id !== "modal-conteudo") {
            return;
        }
        if (abertura && evento.detail.xhr === abertura.xhr) {
            clearTimeout(abertura.temporizador);
        }
        conteudo().classList.remove("carregando");
        conteudo().removeAttribute("aria-busy");
        // O htmx dispara afterSwap mesmo sem troca (HX-Reswap: none ao salvar);
        // só os links de fora do modal devem abri-lo.
        if (!modal().open && !modal().contains(evento.detail.requestConfig.elt)) {
            modal().showModal();
        }
        if (evento.detail.requestConfig.verb === "get") {
            focarPrimeiroCampo();
        }
    });

    document.addEventListener("htmx:afterRequest", function (evento) {
        if (!abertura || evento.detail.xhr !== abertura.xhr) {
            return;
        }
        var busca = abertura;
        abertura = null;
        clearTimeout(busca.temporizador);
        if (!evento.detail.successful && !canceladas.has(busca.xhr)) {
            mostrarFalha(busca);
        }
    });

    // Fechar o modal (Esc, fundo ou botão) durante a espera cancela a busca,
    // e a resposta que ainda chegar não reabre o modal.
    document.addEventListener("close", function (evento) {
        if (evento.target.id !== "modal" || !abertura) {
            return;
        }
        var busca = abertura;
        abertura = null;
        clearTimeout(busca.temporizador);
        canceladas.add(busca.xhr);
        tirarEsqueleto();
        htmx.trigger(busca.elemento, "htmx:abort");
    }, true);

    // Fecha quando o servidor avisa que salvou um cadastro ou cancelou uma movimentação.
    ["registro-salvo", "movimentacao-cancelada"].forEach(function (evento) {
        document.addEventListener(evento, function () {
            document.getElementById("modal").close();
        });
    });
})();
