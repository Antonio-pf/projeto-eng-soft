from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from django.db.models import Count, Q

from core.models import ACIMA_DO_MINIMO, EM_ALERTA, CategoriaItem, Distribuicao, Doacao, Item

LIMITE_PONTOS_DE_ATENCAO = 5


@dataclass(frozen=True)
class TotalUnidade:
    quantidade: Decimal
    sigla: str


@dataclass(frozen=True)
class EstoqueCategoria:
    nome: str
    totais: tuple[TotalUnidade, ...]
    quantidade_itens: int
    itens_acima_minimo: int

    @property
    def percentual_acima_minimo(self):
        if not self.quantidade_itens:
            return 0
        return round(100 * self.itens_acima_minimo / self.quantidade_itens)


@dataclass(frozen=True)
class ResumoPainel:
    itens_em_estoque: int
    variacao_itens_em_estoque: int
    itens_em_alerta: int
    pontos_de_atencao: tuple[Item, ...]
    categorias: tuple[EstoqueCategoria, ...]

    @property
    def texto_variacao(self):
        if self.variacao_itens_em_estoque > 0:
            return f"+{self.variacao_itens_em_estoque} este mês"
        if self.variacao_itens_em_estoque < 0:
            return f"−{-self.variacao_itens_em_estoque} este mês"
        return "Sem variação este mês"


def saudacao(hora):
    if 5 <= hora < 12:
        return "Bom dia"
    if 12 <= hora < 18:
        return "Boa tarde"
    return "Boa noite"


def montar_resumo(hoje):
    inicio_do_mes = hoje.replace(day=1)
    contagens = (
        Item.objects.com_saldo()
        .com_saldo(campo="saldo_inicio_do_mes", antes_de=inicio_do_mes)
        .aggregate(
            itens_em_estoque=Count("pk", filter=Q(saldo__gt=0)),
            itens_em_estoque_no_inicio=Count("pk", filter=Q(saldo_inicio_do_mes__gt=0)),
            itens_em_alerta=Count("pk", filter=EM_ALERTA),
        )
    )
    pontos_de_atencao = (
        Item.objects.em_alerta()
        .select_related("unidade_medida")
        .order_by("saldo", "nome")[:LIMITE_PONTOS_DE_ATENCAO]
    )

    return ResumoPainel(
        itens_em_estoque=contagens["itens_em_estoque"],
        variacao_itens_em_estoque=(
            contagens["itens_em_estoque"] - contagens["itens_em_estoque_no_inicio"]
        ),
        itens_em_alerta=contagens["itens_em_alerta"],
        pontos_de_atencao=tuple(pontos_de_atencao),
        categorias=_estoque_por_categoria(),
    )


def _estoque_por_categoria():
    totais = defaultdict(lambda: defaultdict(Decimal))
    for movimentacoes, sinal in ((Doacao.objects, 1), (Distribuicao.objects, -1)):
        for linha in movimentacoes.ativas().totais_por_categoria_e_unidade():
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
        categorias.append(
            EstoqueCategoria(
                nome=categoria.nome,
                totais=tuple(
                    TotalUnidade(quantidade, sigla)
                    for sigla, quantidade in sorted(totais[categoria.pk].items())
                    if quantidade
                ),
                quantidade_itens=contagem.get("quantidade", 0),
                itens_acima_minimo=contagem.get("acima_minimo", 0),
            )
        )
    return tuple(categorias)
