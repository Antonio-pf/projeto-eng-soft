// Espera nas trocas feitas pelo htmx fora do modal (painel, listas, históricos e relatório):
// o skeleton só aparece se a resposta passar de 200 ms, para não piscar em conexão rápida,
// e uma falha deixa o conteúdo anterior com um aviso e o botão "Tentar de novo".
// O modal tem as regras dele em modal.js.
(function () {
    var ATRASO = 200;
    var temporizadores = new WeakMap(); // requisição -> temporizador do skeleton
    var pendentes = new WeakMap(); // alvo -> requisições em andamento

    function ehBuscaForaDoModal(detalhe) {
        return detalhe.target && detalhe.target.id !== "modal-conteudo"
            && detalhe.requestConfig && detalhe.requestConfig.verb === "get";
    }

    function tirarFaixa(alvo) {
        var faixa = alvo.querySelector(":scope > .faixa-falha");
        if (faixa) {
            faixa.remove();
        }
    }

    document.addEventListener("htmx:beforeSend", function (evento) {
        var detalhe = evento.detail;
        if (!ehBuscaForaDoModal(detalhe)) {
            return;
        }
        var alvo = detalhe.target;
        tirarFaixa(alvo);
        pendentes.set(alvo, (pendentes.get(alvo) || 0) + 1);
        temporizadores.set(detalhe.xhr, setTimeout(function () {
            alvo.classList.add("carregando");
            alvo.setAttribute("aria-busy", "true");
        }, ATRASO));
    });

    // Também roda quando o htmx cancela a requisição (hx-sync="replace" na busca).
    document.addEventListener("htmx:afterRequest", function (evento) {
        var detalhe = evento.detail;
        if (!temporizadores.has(detalhe.xhr)) {
            return;
        }
        clearTimeout(temporizadores.get(detalhe.xhr));
        temporizadores.delete(detalhe.xhr);

        var alvo = detalhe.target;
        var restantes = (pendentes.get(alvo) || 1) - 1;
        if (restantes > 0) {
            pendentes.set(alvo, restantes);
            return;
        }
        pendentes.delete(alvo);
        alvo.classList.remove("carregando");
        alvo.removeAttribute("aria-busy");
    });

    function mostrarFalha(evento) {
        var detalhe = evento.detail;
        var alvo = detalhe.target;
        var modelo = document.getElementById("faixa-falha");
        if (!ehBuscaForaDoModal(detalhe) || !modelo || !document.body.contains(alvo)) {
            return;
        }
        tirarFaixa(alvo);
        var faixa = modelo.content.firstElementChild.cloneNode(true);
        var origem = detalhe.elt;
        var verbo = detalhe.requestConfig.verb;
        var caminho = detalhe.requestConfig.path;
        faixa.querySelector("button").addEventListener("click", function () {
            faixa.remove();
            // Repete a mesma requisição: com o elemento de origem, o htmx usa o mesmo alvo,
            // a mesma troca e os mesmos filtros (hx-include, campos do formulário).
            if (document.body.contains(origem)) {
                htmx.ajax(verbo, caminho, { source: origem });
            } else {
                htmx.ajax(verbo, caminho, { target: alvo, swap: "outerHTML" });
            }
        });
        alvo.prepend(faixa);
    }

    document.addEventListener("htmx:responseError", mostrarFalha);
    document.addEventListener("htmx:sendError", mostrarFalha);
})();
