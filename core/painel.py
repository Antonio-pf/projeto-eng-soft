from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum

from core.models import ACIMA_DO_MINIMO, EM_ALERTA, CategoriaItem, Distribuicao, Doacao, Item


def saudacao(hora):
    if 5 <= hora < 12:
        return "Bom dia"
    if 12 <= hora < 18:
        return "Boa tarde"
    return "Boa noite"


def texto_variacao(variacao):
    if variacao > 0:
        return f"+{variacao} este mês"
    if variacao < 0:
        return f"−{-variacao} este mês"
    return "Sem variação este mês"


def texto_variacao_mes_anterior(variacao):
    if variacao > 0:
        return f"+{variacao} em relação ao mês anterior"
    if variacao < 0:
        return f"−{-variacao} em relação ao mês anterior"
    return "Igual ao mês anterior"


def periodo_equivalente_do_mes_anterior(hoje):
    """Do dia 1 ao mesmo dia do mês anterior, limitado ao fim dele (31/03 -> 01/02 a 28/02)."""
    fim_do_mes_anterior = hoje.replace(day=1) - timedelta(days=1)
    inicio = fim_do_mes_anterior.replace(day=1)
    fim = fim_do_mes_anterior.replace(day=min(hoje.day, fim_do_mes_anterior.day))
    return inicio, fim


def _doacoes_e_familias_do_mes(hoje):
    inicio_do_mes = hoje.replace(day=1)
    doacoes = Doacao.objects.ativas().aggregate(
        no_mes=Count("pk", filter=Q(data__range=(inicio_do_mes, hoje))),
        no_mes_anterior=Count(
            "pk", filter=Q(data__range=periodo_equivalente_do_mes_anterior(hoje))
        ),
    )
    familias_atendidas = (
        Distribuicao.objects.ativas()
        .filter(data__range=(inicio_do_mes, hoje))
        .aggregate(total=Count("familia", distinct=True))["total"]
    )
    variacao = doacoes["no_mes"] - doacoes["no_mes_anterior"]
    return {
        "doacoes_no_mes": doacoes["no_mes"],
        "variacao_doacoes": variacao,
        "texto_variacao_doacoes": texto_variacao_mes_anterior(variacao),
        "familias_atendidas": familias_atendidas,
    }


def movimentacoes_recentes(limite=5):
    """Últimas doações e distribuições não canceladas, pela data e depois pela hora do registro."""
    ordem = ("-data", "-criado_em", "-pk")
    doacoes = (
        Doacao.objects.ativas()
        .select_related("doador", "item__unidade_medida")
        .order_by(*ordem)[:limite]
    )
    distribuicoes = (
        Distribuicao.objects.ativas()
        .select_related("familia", "item__unidade_medida")
        .order_by(*ordem)[:limite]
    )
    linhas = [_linha_recente(doacao, "Doação", True, doacao.doador.nome) for doacao in doacoes] + [
        _linha_recente(distribuicao, "Distribuição", False, distribuicao.familia.nome_responsavel)
        for distribuicao in distribuicoes
    ]
    linhas.sort(key=lambda linha: (linha["data"], linha["criado_em"]), reverse=True)
    return linhas[:limite]


def _linha_recente(movimentacao, tipo, entrada, pessoa):
    return {
        "tipo": tipo,
        "entrada": entrada,
        "pessoa": pessoa,
        "item": movimentacao.item.nome,
        "quantidade": movimentacao.quantidade,
        "sigla": movimentacao.item.unidade_medida.sigla,
        "data": movimentacao.data,
        "criado_em": movimentacao.criado_em,
    }


def montar_resumo(hoje):
    contagens = (
        Item.objects.com_saldo()
        .com_saldo(campo="saldo_inicio_do_mes", antes_de=hoje.replace(day=1))
        .aggregate(
            itens_em_estoque=Count("pk", filter=Q(saldo__gt=0)),
            itens_em_estoque_no_inicio=Count("pk", filter=Q(saldo_inicio_do_mes__gt=0)),
            itens_em_alerta=Count("pk", filter=EM_ALERTA),
        )
    )
    variacao = contagens["itens_em_estoque"] - contagens["itens_em_estoque_no_inicio"]
    pontos_de_atencao = (
        Item.objects.em_alerta().select_related("unidade_medida").order_by("saldo", "nome")[:5]
    )

    return {
        "itens_em_estoque": contagens["itens_em_estoque"],
        "variacao_itens_em_estoque": variacao,
        "texto_variacao": texto_variacao(variacao),
        "itens_em_alerta": contagens["itens_em_alerta"],
        "pontos_de_atencao": list(pontos_de_atencao),
        "categorias": _estoque_por_categoria(),
        **_doacoes_e_familias_do_mes(hoje),
        "movimentacoes_recentes": movimentacoes_recentes(),
    }


def _estoque_por_categoria():
    totais = defaultdict(lambda: defaultdict(Decimal))
    for movimentacoes, sinal in ((Doacao.objects, 1), (Distribuicao.objects, -1)):
        linhas = (
            movimentacoes.ativas()
            .order_by()
            .values("item__categoria_id", "item__unidade_medida__sigla")
            .annotate(total=Sum("quantidade"))
        )
        for linha in linhas:
            sigla = linha["item__unidade_medida__sigla"]
            totais[linha["item__categoria_id"]][sigla] += sinal * linha["total"]

    itens_por_categoria = {
        linha["categoria_id"]: linha
        for linha in Item.objects.com_saldo()
        .order_by()
        .values("categoria_id")
        .annotate(quantidade=Count("pk"), acima_minimo=Count("pk", filter=ACIMA_DO_MINIMO))
    }

    categorias = []
    for categoria in CategoriaItem.objects.order_by("nome"):
        contagem = itens_por_categoria.get(categoria.pk, {})
        quantidade_itens = contagem.get("quantidade", 0)
        acima_minimo = contagem.get("acima_minimo", 0)
        categorias.append(
            {
                "nome": categoria.nome,
                "totais": [
                    {"quantidade": quantidade, "sigla": sigla}
                    for sigla, quantidade in sorted(totais[categoria.pk].items())
                    if quantidade
                ],
                "quantidade_itens": quantidade_itens,
                "percentual_acima_minimo": (
                    round(100 * acima_minimo / quantidade_itens) if quantidade_itens else 0
                ),
            }
        )
    return categorias
