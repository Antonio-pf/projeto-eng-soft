// Trava o envio dos formulários POST para evitar registro duplicado (clique
// duplo ou Enter repetido) e mostra um spinner no botão enquanto a página carrega.
(function () {
    function destravar(form) {
        form.removeAttribute("aria-busy");
        form.querySelectorAll(".loading").forEach(function (spinner) {
            spinner.parentElement.disabled = false;
            spinner.remove();
        });
    }

    document.addEventListener("submit", function (evento) {
        var form = evento.target;
        if (form.method !== "post") {
            return;
        }
        if (form.hasAttribute("aria-busy")) {
            evento.preventDefault();
            return;
        }
        form.setAttribute("aria-busy", "true");

        var botao = evento.submitter;
        if (botao) {
            botao.disabled = true;
            botao.insertAdjacentHTML(
                "afterbegin",
                '<span class="loading loading-spinner loading-xs" aria-hidden="true"></span>'
            );
        }
    });

    // Ao voltar pelo histórico, o navegador pode restaurar a página com o botão ainda travado.
    window.addEventListener("pageshow", function (evento) {
        if (evento.persisted) {
            document.querySelectorAll("form[aria-busy]").forEach(destravar);
        }
    });

    // Com htmx a página não recarrega: se o formulário continuar na tela (erro de rede,
    // por exemplo), ele precisa voltar a aceitar envio.
    document.addEventListener("htmx:afterRequest", function (evento) {
        var form = evento.detail.elt.closest("form");
        if (form) {
            destravar(form);
        }
    });
})();
