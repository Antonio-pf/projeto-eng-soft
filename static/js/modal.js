// Modal compartilhado do painel: abre quando um link de fora dele carrega um
// formulário em #modal-conteudo e fecha quando o servidor avisa que salvou.
(function () {
    document.addEventListener("htmx:afterSwap", function (evento) {
        var modal = document.getElementById("modal");
        // O htmx dispara afterSwap mesmo sem troca (HX-Reswap: none ao salvar);
        // só os links de fora do modal devem abri-lo.
        if (evento.detail.target.id === "modal-conteudo" && !modal.open && !modal.contains(evento.detail.requestConfig.elt)) {
            modal.showModal();
        }
    });

    document.addEventListener("registro-salvo", function () {
        document.getElementById("modal").close();
    });
})();
