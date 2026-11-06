import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Max, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from core.decorators import admin_obrigatorio, login_obrigatorio
from core.forms import (
    CategoriaItemForm,
    DistribuicaoForm,
    DoacaoForm,
    DoadorForm,
    FamiliaForm,
    ItemForm,
    LoginForm,
    UsuarioForm,
)
from core.models import (
    EM_ALERTA,
    CategoriaItem,
    Distribuicao,
    Doacao,
    Doador,
    Familia,
    Item,
    Usuario,
)
from core.painel import montar_resumo, saudacao
from core.privacidade import (
    AVISO_ATUALIZADO_EM,
    FINALIDADES,
    PRAZO_RETENCAO_ANOS,
    controlador,
)

# Nome, login no GitHub e se a foto do perfil foi copiada para static/img/equipe/<login>.jpg.
# Quem não tem foto no GitHub aparece com as iniciais; para incluir, copie a foto e marque True.
EQUIPE = (
    ("Alexandre Victoriano Ribeiro Ulhoa", "viktoralex321", False),
    ("Antonio Pires Felipe", "Antonio-pf", True),
    ("Daniel Souza Monteiro de Carvalho", "DanielSouzaMC", False),
    ("Luiz Henrique Neres", "luiz-Henrique-neres", True),
)


def _parcial(request):
    """O htmx pede só um trecho da página; ao restaurar o histórico, precisa da página inteira."""
    return (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-History-Restore-Request") != "true"
    )


def _render(request, template, parcial, contexto):
    """Renderiza a página inteira ou, para o htmx, só o trecho que ele vai trocar."""
    eh_parcial = _parcial(request)
    contexto = {**contexto, "parcial": eh_parcial}
    response = render(request, parcial if eh_parcial else template, contexto)
    patch_vary_headers(response, ["HX-Request"])
    return response


def _salvo(request, mensagem, destino, evento="registro-salvo"):
    """Sem htmx, redireciona; no modal, mostra o toast e dispara o evento htmx."""
    messages.success(request, mensagem)
    if not _parcial(request):
        return redirect(destino)
    response = render(request, "partials/_mensagens.html", {"oob": True})
    response["HX-Trigger"] = evento
    response["HX-Reswap"] = "none"
    return response


def home(request):
    equipe = [
        {
            "nome": nome,
            "iniciais": nome[0] + nome.split()[-1][0],
            "login": login,
            "perfil": f"https://github.com/{login}",
            "foto": f"img/equipe/{login}.jpg" if tem_foto else None,
        }
        for nome, login, tem_foto in EQUIPE
    ]
    return render(request, "core/home.html", {"equipe": equipe})


def health(request):
    return JsonResponse({"status": "ok"})


@require_GET
def privacidade(request):
    """Aviso de privacidade público (LGPD, art. 9º): o titular não tem login no sistema."""
    return render(
        request,
        "core/privacidade.html",
        {
            "controlador": controlador(),
            "finalidades": FINALIDADES,
            "prazo_anos": PRAZO_RETENCAO_ANOS,
            "atualizado_em": AVISO_ATUALIZADO_EM,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("painel")

    erro = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = authenticate(
                request,
                email=form.cleaned_data["email"],
                password=form.cleaned_data["senha"],
            )
            if usuario is not None:
                login(request, usuario)
                return redirect("painel")
            erro = "E-mail ou senha inválidos."
    else:
        form = LoginForm()

    return render(request, "core/login.html", {"form": form, "erro": erro})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_obrigatorio
def painel_view(request):
    agora = timezone.localtime()
    contexto = {
        "agora": agora,
        "saudacao": saudacao(agora.hour),
        "primeiro_nome": request.user.nome.split()[0],
        "resumo": montar_resumo(agora.date()),
    }
    return render(request, "core/painel.html", contexto)


@login_obrigatorio
@admin_obrigatorio
def usuarios_view(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            Usuario.objects.create_user(
                nome=form.cleaned_data["nome"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["senha"],
                perfil=form.cleaned_data["perfil"],
            )
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect("usuarios")
    else:
        form = UsuarioForm()

    usuarios = Usuario.objects.order_by("id_usuario")
    return render(request, "core/usuarios.html", {"form": form, "usuarios": usuarios})


@login_obrigatorio
@admin_obrigatorio
@require_POST
def usuario_alternar_status_view(request, id_usuario):
    if id_usuario == request.user.id_usuario:
        return redirect("usuarios")

    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    usuario.ativo = not usuario.ativo
    usuario.save(update_fields=["ativo"])
    estado = "reativado" if usuario.ativo else "desativado"
    messages.success(request, f"Acesso de {usuario.nome} {estado}.")
    return redirect("usuarios")


@login_obrigatorio
def doador_create(request):
    if request.method == "POST":
        form = DoadorForm(request.POST)
        if form.is_valid():
            form.save()
            return _salvo(request, "Doador cadastrado com sucesso!", "doador_list")
    else:
        form = DoadorForm()
    return _render(request, "core/doador_form.html", "partials/_doador_form.html", {"form": form})


@login_obrigatorio
@admin_obrigatorio
def doador_update(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if doador.anonimizado:
        # O código ANON-<id> não passaria na validação de CPF/CNPJ, e não há o que corrigir.
        raise Http404("Doador anonimizado.")
    if request.method == "POST":
        form = DoadorForm(request.POST, instance=doador)
        if form.is_valid():
            form.save()
            return _salvo(request, "Doador atualizado com sucesso!", "doador_list")
    else:
        form = DoadorForm(instance=doador)
    return _render(
        request,
        "core/doador_form.html",
        "partials/_doador_form.html",
        {"form": form, "editing": True},
    )


@login_obrigatorio
def doador_list(request):
    query = request.GET.get("q", "").strip()
    doadores_list = Doador.objects.order_by("-criado_em")
    if query:
        doadores_list = doadores_list.filter(nome__icontains=query)

    paginator = Paginator(doadores_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return _render(
        request,
        "core/doador_list.html",
        "partials/_doador_lista.html",
        {"page_obj": page_obj, "query": query},
    )


@login_obrigatorio
def familia_create(request):
    if request.method == "POST":
        form = FamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            return _salvo(request, "Família cadastrada com sucesso!", "familia_list")
    else:
        form = FamiliaForm()
    return _render(request, "core/familia_form.html", "partials/_familia_form.html", {"form": form})


@login_obrigatorio
def familia_list(request):
    query = request.GET.get("q", "").strip()
    familias_list = Familia.objects.order_by("-criado_em")
    if query:
        familias_list = familias_list.filter(nome_responsavel__icontains=query)

    paginator = Paginator(familias_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return _render(
        request,
        "core/familia_list.html",
        "partials/_familia_lista.html",
        {"page_obj": page_obj, "query": query},
    )


@login_obrigatorio
@admin_obrigatorio
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaItemForm(request.POST)
        if form.is_valid():
            form.save()
            return _salvo(request, "Categoria cadastrada com sucesso!", "categoria_list")
    else:
        form = CategoriaItemForm()
    return _render(
        request, "core/categoria_form.html", "partials/_categoria_form.html", {"form": form}
    )


@login_obrigatorio
@admin_obrigatorio
def categoria_update(request, pk):
    categoria = get_object_or_404(CategoriaItem, pk=pk)
    if request.method == "POST":
        form = CategoriaItemForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return _salvo(request, "Categoria atualizada com sucesso!", "categoria_list")
    else:
        form = CategoriaItemForm(instance=categoria)
    return _render(
        request,
        "core/categoria_form.html",
        "partials/_categoria_form.html",
        {"form": form, "editing": True},
    )


@login_obrigatorio
def categoria_list(request):
    query = request.GET.get("q", "").strip()
    categorias_list = CategoriaItem.objects.order_by("nome")
    if query:
        categorias_list = categorias_list.filter(nome__icontains=query)

    paginator = Paginator(categorias_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return _render(
        request,
        "core/categoria_list.html",
        "partials/_categoria_lista.html",
        {"page_obj": page_obj, "query": query},
    )


@login_obrigatorio
@admin_obrigatorio
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return _salvo(request, "Item cadastrado com sucesso!", "item_list")
    else:
        form = ItemForm()
    return _render(request, "core/item_form.html", "partials/_item_form.html", {"form": form})


@login_obrigatorio
@admin_obrigatorio
def item_update(request, pk):
    item = get_object_or_404(Item.objects.com_saldo().select_related("unidade_medida"), pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return _salvo(request, "Item atualizado com sucesso!", "item_list")
    else:
        form = ItemForm(instance=item)
    return _render(
        request,
        "core/item_form.html",
        "partials/_item_form.html",
        {"form": form, "editing": True, "item": item},
    )


@login_obrigatorio
def item_list(request):
    query = request.GET.get("q", "").strip()
    estoque = request.GET.get("estoque", "")
    itens_list = (
        Item.objects.com_saldo().select_related("categoria", "unidade_medida").order_by("nome")
    )
    if query:
        itens_list = itens_list.filter(nome__icontains=query)
    if estoque == "baixo":
        itens_list = itens_list.filter(EM_ALERTA)

    paginator = Paginator(itens_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return _render(
        request,
        "core/item_list.html",
        "partials/_item_lista.html",
        {
            "page_obj": page_obj,
            "query": query,
            "estoque": estoque,
            "total_em_alerta": Item.objects.em_alerta().count(),
        },
    )


@login_obrigatorio
def movimentacao_nova(request):
    return _render(
        request, "core/movimentacao_nova.html", "partials/_movimentacao_escolha.html", {}
    )


@login_obrigatorio
def doacao_create(request):
    if request.method == "POST":
        form = DoacaoForm(request.POST)
        if form.is_valid():
            doacao = form.save(commit=False)
            doacao.registrado_por = request.user
            doacao.save()
            return _salvo(request, "Doação registrada com sucesso!", "doacao_create")
    else:
        form = DoacaoForm(initial={"item": request.GET.get("item")})
    return _render(request, "core/doacao_form.html", "partials/_doacao_form.html", {"form": form})


def _data(texto):
    try:
        return parse_date(texto) if texto else None
    except ValueError:
        return None


ATALHOS_DE_PERIODO = {"mes": "Este mês", "30dias": "Últimos 30 dias", "ano": "Este ano"}


def _periodo(atalho, hoje):
    inicio = {
        "mes": hoje.replace(day=1),
        "30dias": hoje - timedelta(days=29),
        "ano": hoje.replace(month=1, day=1),
    }[atalho]
    return inicio.isoformat(), hoje.isoformat()


def _filtrar(movimentacoes, request, campo_pessoa, parametro):
    filtros = {
        nome: request.GET.get(nome, "").strip() for nome in (parametro, "data_inicio", "data_fim")
    }
    hoje = timezone.localdate()
    atalho = request.GET.get("periodo")
    if atalho in ATALHOS_DE_PERIODO:
        filtros["data_inicio"], filtros["data_fim"] = _periodo(atalho, hoje)
    periodo_atual = (filtros["data_inicio"], filtros["data_fim"])
    filtros["atalhos"] = [
        {"valor": valor, "rotulo": rotulo, "ativo": _periodo(valor, hoje) == periodo_atual}
        for valor, rotulo in ATALHOS_DE_PERIODO.items()
    ]
    if filtros[parametro].isdigit():
        movimentacoes = movimentacoes.filter(**{campo_pessoa: filtros[parametro]})
    inicio = _data(filtros["data_inicio"])
    if inicio:
        movimentacoes = movimentacoes.filter(data__gte=inicio)
    fim = _data(filtros["data_fim"])
    if fim:
        movimentacoes = movimentacoes.filter(data__lte=fim)
    return movimentacoes, filtros


@login_obrigatorio
def doacao_list(request):
    # As canceladas continuam na lista, marcadas, para mostrar que o histórico foi preservado.
    doacoes_list, filtros = _filtrar(
        Doacao.objects.select_related("doador", "item", "registrado_por", "cancelado_por").order_by(
            "-data", "-pk"
        ),
        request,
        "doador_id",
        "id_doador",
    )

    totais_por_doador = (
        doacoes_list.ativas()
        .values("doador_id", "doador__nome", "item_id", "item__nome", "item__unidade_medida__sigla")
        .annotate(total=Sum("quantidade"))
        .order_by("doador__nome", "doador_id", "item__nome", "item_id")
    )

    paginator = Paginator(doacoes_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return _render(
        request,
        "core/doacao_list.html",
        "partials/_doacao_historico.html",
        {
            "totais_por_doador": totais_por_doador,
            "page_obj": page_obj,
            "doadores": Doador.objects.order_by("nome"),
            **filtros,
        },
    )


@login_obrigatorio
def distribuicao_create(request):
    itens_saldo = {
        str(item.pk): {"saldo": f"{item.saldo_atual:.2f}", "unidade": item.unidade_medida.sigla}
        for item in Item.objects.select_related("unidade_medida")
    }
    if request.method == "POST":
        form = DistribuicaoForm(request.POST)
        if form.is_valid():
            distribuicao = form.save(commit=False)
            distribuicao.registrado_por = request.user
            distribuicao.save()
            return _salvo(request, "Distribuição registrada com sucesso!", "distribuicao_create")
    else:
        form = DistribuicaoForm(
            initial={"item": request.GET.get("item"), "familia": request.GET.get("familia")}
        )
    return _render(
        request,
        "core/distribuicao_form.html",
        "partials/_distribuicao_form.html",
        {"form": form, "itens_saldo": itens_saldo},
    )


@login_obrigatorio
def distribuicao_list(request):
    distribuicoes_list, filtros = _filtrar(
        Distribuicao.objects.select_related(
            "familia", "item", "registrado_por", "cancelado_por"
        ).order_by("-data"),
        request,
        "familia_id",
        "id_familia",
    )

    paginator = Paginator(distribuicoes_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return _render(
        request,
        "core/distribuicao_list.html",
        "partials/_distribuicao_historico.html",
        {
            "page_obj": page_obj,
            "familias": Familia.objects.order_by("nome_responsavel"),
            **filtros,
        },
    )


def _cancelar(request, movimentacao, *, rotulo, pessoa_rotulo, pessoa, url, destino):
    """GET mostra a confirmação; POST cancela ou mostra no próprio diálogo por que não pode."""
    if request.method == "POST":
        try:
            movimentacao.cancelar(request.user)
        except ValidationError as erro:
            motivo = erro.messages[0]
        else:
            return _salvo(request, f"{rotulo} cancelada.", destino, evento="movimentacao-cancelada")
    else:
        motivo = movimentacao.motivo_para_nao_cancelar()
    return _render(
        request,
        "core/movimentacao_cancelar.html",
        "partials/_movimentacao_cancelar.html",
        {
            "movimentacao": movimentacao,
            "rotulo": rotulo,
            "pessoa_rotulo": pessoa_rotulo,
            "pessoa": pessoa,
            "url_cancelar": url,
            "destino": destino,
            "motivo": motivo,
        },
    )


@login_obrigatorio
@admin_obrigatorio
@require_http_methods(["GET", "POST"])
def doacao_cancelar(request, pk):
    doacao = get_object_or_404(
        Doacao.objects.select_related("doador", "item__unidade_medida"), pk=pk
    )
    return _cancelar(
        request,
        doacao,
        rotulo="Doação",
        pessoa_rotulo="Doador",
        pessoa=doacao.doador.nome,
        url=reverse("doacao_cancelar", args=[pk]),
        destino="doacao_list",
    )


@login_obrigatorio
@admin_obrigatorio
@require_http_methods(["GET", "POST"])
def distribuicao_cancelar(request, pk):
    distribuicao = get_object_or_404(
        Distribuicao.objects.select_related("familia", "item__unidade_medida"), pk=pk
    )
    return _cancelar(
        request,
        distribuicao,
        rotulo="Distribuição",
        pessoa_rotulo="Família",
        pessoa=distribuicao.familia.nome_responsavel,
        url=reverse("distribuicao_cancelar", args=[pk]),
        destino="distribuicao_list",
    )


def _relatorio_de_distribuicoes(request):
    """Linhas do relatório de distribuições (#21), usadas pela tela e pelo CSV (#23).

    As duas saídas leem a mesma consulta para que o arquivo exportado traga sempre
    os mesmos dados e filtros que a tela mostra.
    """
    distribuicoes, filtros = _filtrar(
        Distribuicao.objects.filter(cancelado=False), request, "familia_id", "id_familia"
    )
    linhas = (
        distribuicoes.values(
            "familia__id_familia",
            "familia__nome_responsavel",
            "item__id_item",
            "item__nome",
            "item__categoria__nome",
            "item__unidade_medida__sigla",
        )
        .annotate(
            quantidade_total=Sum("quantidade"),
            numero_distribuicoes=Count("id_distribuicao"),
            ultimo_registro=Max("data"),
        )
        .order_by("familia__nome_responsavel", "item__nome")
    )
    return distribuicoes, linhas, filtros


# Planilhas tratam como fórmula a célula que começa com estes caracteres (OWASP, CSV injection).
INICIOS_DE_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def _celula_csv(valor):
    """Põe um apóstrofo antes do texto que a planilha executaria como fórmula."""
    if isinstance(valor, str) and valor.startswith(INICIOS_DE_FORMULA):
        return f"'{valor}"
    return valor


@login_obrigatorio
def distribuicao_exportar_csv(request):
    _, linhas, _ = _relatorio_de_distribuicoes(request)

    # Com charset utf-8-sig o Django codifica cada linha à parte e repete o BOM em todas;
    # por isso o BOM, que faz o Excel ler os acentos, é escrito uma vez só.
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="relatorio_distribuicoes.csv"'
    response.write("﻿")
    writer = csv.writer(response)
    writer.writerow(
        [
            "Família",
            "Item",
            "Categoria",
            "Qtd total",
            "Unidade",
            "Nº distribuições",
            "Último registro",
        ]
    )
    # A soma vem como 5 no SQLite e 5.00 no PostgreSQL; duas casas deixam o arquivo igual nos dois.
    for linha in linhas:
        writer.writerow(
            [
                _celula_csv(linha["familia__nome_responsavel"]),
                _celula_csv(linha["item__nome"]),
                _celula_csv(linha["item__categoria__nome"]),
                f"{linha['quantidade_total']:.2f}",
                _celula_csv(linha["item__unidade_medida__sigla"]),
                linha["numero_distribuicoes"],
                linha["ultimo_registro"].strftime("%d/%m/%Y"),
            ]
        )
    return response


@login_obrigatorio
def distribuicao_relatorio(request):
    distribuicoes, linhas, filtros = _relatorio_de_distribuicoes(request)
    # Somar kg com pacote não diz nada a quem lê o relatório, então o total sai por unidade.
    total_por_unidade = (
        distribuicoes.values("item__unidade_medida__sigla")
        .annotate(total=Sum("quantidade"))
        .order_by("item__unidade_medida__sigla")
    )
    resumo = distribuicoes.aggregate(
        familias_atendidas=Count("familia", distinct=True),
        numero_distribuicoes=Count("id_distribuicao"),
    )

    return render(
        request,
        "core/distribuicao_relatorio.html",
        {
            "linhas": linhas,
            "total_por_unidade": total_por_unidade,
            "resumo": resumo,
            "familias": Familia.objects.order_by("nome_responsavel"),
            **filtros,
        },
    )
