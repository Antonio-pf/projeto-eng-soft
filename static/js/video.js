// Vídeo da Mostra Virtual na página inicial: a capa troca de lugar com o player
// do YouTube só quando alguém clica nela. Até o clique, a página não carrega nada
// do YouTube. Sem JavaScript, a capa é um link e abre o vídeo no próprio YouTube.
(function () {
    document.addEventListener("click", function (evento) {
        // Ctrl, Cmd, Shift ou o botão do meio continuam abrindo o YouTube numa aba.
        if (evento.button !== 0 || evento.ctrlKey || evento.metaKey || evento.shiftKey) {
            return;
        }
        var capa = evento.target.closest("[data-video-capa]");
        var moldura = capa && capa.closest("[data-video]");
        if (!moldura) {
            return;
        }
        evento.preventDefault();

        var player = document.createElement("iframe");
        player.src = moldura.dataset.embed;
        player.title = moldura.dataset.titulo;
        player.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
        player.allowFullscreen = true;
        // O Django manda Referrer-Policy: same-origin; sem a origem, o YouTube recusa tocar (erro 153).
        player.referrerPolicy = "strict-origin-when-cross-origin";
        capa.replaceWith(player);
        player.focus();
    });
})();
