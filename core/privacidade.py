"""Fonte única do aviso de privacidade (LGPD): prazo, bases legais, controlador e máscara.

A página /privacidade/, os avisos dos formulários e o comando anonimizar_vencidos leem
daqui, para o que o aviso promete e o que o sistema faz não divergirem. A base legal e o
prazo são proposta da equipe, a validar com o cliente (história #25).
"""

import re
from datetime import date

from django.conf import settings

PRAZO_RETENCAO_ANOS = 5

NOME_ANONIMIZADO = "Titular anonimizado"
PREFIXO_DOCUMENTO_ANONIMIZADO = "ANON-"

NOME_ONG_PADRAO = "a ONG responsável por este sistema"
CONTATO_PADRAO = "Fale com a equipe da ONG no local de atendimento."

AVISO_ATUALIZADO_EM = date(2026, 11, 6)

FINALIDADES = (
    {
        "finalidade": "Registrar as doações recebidas e comprovar de quem vieram",
        "titulares": "Doadores",
        "base_legal": (
            "Execução de contrato (art. 7º, V, da LGPD): a doação é um contrato "
            "do qual o doador é parte (art. 538 do Código Civil)"
        ),
    },
    {
        "finalidade": "Cadastrar as famílias e registrar as doações entregues a elas",
        "titulares": "Famílias atendidas",
        "base_legal": (
            "Execução de contrato ou de procedimentos preliminares a pedido do titular "
            "(art. 7º, V, da LGPD): a família pede para ser atendida pela ONG"
        ),
    },
    {
        "finalidade": (
            "Prestar contas a financiadores e parceiros com o relatório de distribuições"
        ),
        "titulares": "Famílias atendidas",
        "base_legal": "Legítimo interesse da ONG (art. 7º, IX, da LGPD)",
    },
)

_DIGITO = re.compile(r"\d")


def controlador():
    """Nome e contato da ONG, das variáveis de ambiente, ou os textos padrão sem elas."""
    nome = getattr(settings, "ONG_NOME", "")
    contato = getattr(settings, "ONG_CONTATO_PRIVACIDADE", "")
    return {
        "nome": nome or NOME_ONG_PADRAO,
        "contato": contato or CONTATO_PADRAO,
        "contato_configurado": bool(contato),
    }


def data_limite(hoje):
    """Cadastros com a última movimentação até esta data já passaram do prazo."""
    try:
        return hoje.replace(year=hoje.year - PRAZO_RETENCAO_ANOS)
    except ValueError:  # 29/02 num ano que não é bissexto
        return hoje.replace(year=hoje.year - PRAZO_RETENCAO_ANOS, day=28)


def mascarar_documento(valor):
    """Troca por * todos os dígitos menos os 4 últimos e mantém a pontuação."""
    total = len(_DIGITO.findall(valor))
    if total <= 4:
        return valor
    escondidos = total - 4
    partes = []
    for caractere in valor:
        if caractere.isdigit() and escondidos > 0:
            partes.append("*")
            escondidos -= 1
        else:
            partes.append(caractere)
    return "".join(partes)
