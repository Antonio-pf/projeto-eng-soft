from collections import defaultdict
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
