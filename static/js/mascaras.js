// Máscaras dos campos com data-mascara (cpf-cnpj, telefone, inteiro, decimal): o que o
// campo não aceita é descartado na hora, o valor é formatado enquanto se digita e o cursor
// fica no lugar. Vale também para os formulários que o htmx carrega no modal. O servidor
// continua validando (core/forms.py); sem JavaScript, o pattern do campo segura o envio.
(function () {
    function digitos(texto) {
        return texto.replace(/\D/g, "");
    }

    // Põe cada separador antes do dígito da posição indicada, só se esse dígito já existe.
    function montar(numeros, separadores) {
        var resultado = "";
        for (var i = 0; i < numeros.length; i++) {
            separadores.forEach(function (separador) {
                if (separador[0] === i) {
                    resultado += separador[1];
                }
            });
            resultado += numeros[i];
        }
        return resultado;
    }

    var TIPOS = {
        "cpf-cnpj": {
            util: /\d/,
            limpar: function (texto) {
                return digitos(texto).slice(0, 14);
            },
            formatar: function (numeros) {
                if (numeros.length <= 11) {
                    return montar(numeros, [[3, "."], [6, "."], [9, "-"]]);
                }
                return montar(numeros, [[2, "."], [5, "."], [8, "/"], [12, "-"]]);
            },
        },
        telefone: {
            util: /\d/,
            limpar: function (texto) {
                return digitos(texto).slice(0, 11);
            },
            formatar: function (numeros) {
                // Com 11 dígitos o bloco do meio tem 5: (00)00000-0000; até 10, tem 4.
                var meio = numeros.length === 11 ? 5 : 4;
                return montar(numeros, [[0, "("], [2, ")"], [2 + meio, "-"]]);
            },
        },
        inteiro: {
            util: /\d/,
            limpar: function (texto) {
                return digitos(texto).slice(0, 10);
            },
            formatar: function (numeros) {
                return numeros;
            },
        },
        decimal: {
            util: /[\d,]/,
            // Ponto vira vírgula; uma vírgula só; até 8 dígitos antes e 2 depois dela.
            limpar: function (texto) {
                var limpo = texto.replace(/\./g, ",").replace(/[^\d,]/g, "");
                var virgula = limpo.indexOf(",");
                if (virgula === -1) {
                    return limpo.slice(0, 8);
                }
                var inteiro = limpo.slice(0, virgula).slice(0, 8) || "0";
                var casas = limpo.slice(virgula + 1).replace(/,/g, "").slice(0, 2);
                return inteiro + "," + casas;
            },
            formatar: function (valor) {
                return valor;
            },
        },
    };

    function tipoDe(campo) {
        return campo && campo.dataset ? TIPOS[campo.dataset.mascara] : undefined;
    }

    function contarUteis(texto, util) {
        var total = 0;
        for (var i = 0; i < texto.length; i++) {
            if (util.test(texto[i])) {
                total++;
            }
        }
        return total;
    }

    // Posição logo depois do n-ésimo caractere útil do valor formatado.
    function posicaoDepois(valor, quantidade, util) {
        if (quantidade <= 0) {
            return 0;
        }
        var contados = 0;
        for (var i = 0; i < valor.length; i++) {
            if (util.test(valor[i])) {
                contados++;
                if (contados === quantidade) {
                    return i + 1;
                }
            }
        }
        return valor.length;
    }

    function aplicar(campo, tipo, valor, cursor) {
        var novo = tipo.formatar(tipo.limpar(valor));
        var uteisAntes = contarUteis(tipo.limpar(valor.slice(0, cursor)), tipo.util);
        var posicao = posicaoDepois(novo, uteisAntes, tipo.util);
        if (novo !== campo.value) {
            campo.value = novo;
        }
        if (document.activeElement === campo) {
            campo.setSelectionRange(posicao, posicao);
        }
    }

    document.addEventListener("input", function (evento) {
        var campo = evento.target;
        var tipo = tipoDe(campo);
        if (!tipo || evento.isComposing) {
            return;
        }
        var cursor = campo.selectionStart === null ? campo.value.length : campo.selectionStart;
        aplicar(campo, tipo, campo.value, cursor);
    });

    // Backspace ou Delete encostado num separador apaga o dígito vizinho; sem isso, a
    // formatação poria o separador de volta e o cursor ficaria preso.
    document.addEventListener("keydown", function (evento) {
        var campo = evento.target;
        var tipo = tipoDe(campo);
        var tecla = evento.key;
        if (!tipo || (tecla !== "Backspace" && tecla !== "Delete")
            || evento.ctrlKey || evento.metaKey || evento.altKey) {
            return;
        }
        var inicio = campo.selectionStart;
        if (inicio === null || inicio !== campo.selectionEnd) {
            return;
        }
        var valor = campo.value;
        var bruto;
        var cursor;
        if (tecla === "Backspace") {
            var antes = inicio;
            while (antes > 0 && !tipo.util.test(valor[antes - 1])) {
                antes--;
            }
            if (antes === inicio || antes === 0) {
                return;
            }
            bruto = valor.slice(0, antes - 1) + valor.slice(inicio);
            cursor = antes - 1;
        } else {
            var depois = inicio;
            while (depois < valor.length && !tipo.util.test(valor[depois])) {
                depois++;
            }
            if (depois === inicio || depois === valor.length) {
                return;
            }
            bruto = valor.slice(0, inicio) + valor.slice(depois + 1);
            cursor = inicio;
        }
        evento.preventDefault();
        aplicar(campo, tipo, bruto, cursor);
        campo.dispatchEvent(new Event("input", { bubbles: true }));
    });

    // A máscara limita os dígitos sozinha; o maxlength cortaria um valor colado com
    // pontuação a mais, como "(11) 98765-4321".
    document.addEventListener("focusin", function (evento) {
        if (tipoDe(evento.target)) {
            evento.target.removeAttribute("maxlength");
        }
    });
})();
