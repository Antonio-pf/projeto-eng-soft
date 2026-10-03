import csv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

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
from core.models import CategoriaItem, Distribuicao, Doacao, Doador, Familia, Item, Usuario

EQUIPE = (
    "Alexandre Victoriano Ribeiro Ulhoa",
    "Antonio Pires Felipe",
    "Daniel Souza Monteiro de Carvalho",
    "Luiz Henrique Neres",
)


def home(request):
    equipe = [{"nome": nome, "iniciais": nome[0] + nome.split()[-1][0]} for nome in EQUIPE]
    return render(request, "core/home.html", {"equipe": equipe})


def health(request):
    return JsonResponse({"status": "ok"})


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
    return render(request, "core/painel.html")


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
    return redirect("usuarios")


@login_obrigatorio
def doador_create(request):
    if request.method == "POST":
        form = DoadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador cadastrado com sucesso!")
            return redirect("doador_list")
    else:
        form = DoadorForm()
    return render(request, "core/doador_form.html", {"form": form})


@login_obrigatorio
@admin_obrigatorio
def doador_update(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == "POST":
        form = DoadorForm(request.POST, instance=doador)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador atualizado com sucesso!")
            return redirect("doador_list")
    else:
        form = DoadorForm(instance=doador)
    return render(request, "core/doador_form.html", {"form": form, "editing": True})


@login_obrigatorio
def doador_list(request):
    query = request.GET.get("q", "").strip()
    doadores_list = Doador.objects.all().order_by("-criado_em")
    if query:
        doadores_list = doadores_list.filter(nome__icontains=query)

    paginator = Paginator(doadores_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/doador_list.html",
        {"page_obj": page_obj, "query": query, "form": DoadorForm()},
    )


@login_obrigatorio
def familia_create(request):
    if request.method == "POST":
        form = FamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Família cadastrada com sucesso!")
            return redirect("familia_list")
    else:
        form = FamiliaForm()
    return render(request, "core/familia_form.html", {"form": form})


@login_obrigatorio
def familia_list(request):
    query = request.GET.get("q", "").strip()
    familias_list = Familia.objects.all().order_by("-criado_em")
    if query:
        familias_list = familias_list.filter(nome_responsavel__icontains=query)

    paginator = Paginator(familias_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/familia_list.html",
        {"page_obj": page_obj, "query": query, "form": FamiliaForm()},
    )


@login_obrigatorio
@admin_obrigatorio
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria cadastrada com sucesso!")
            return redirect("categoria_list")
    else:
        form = CategoriaItemForm()
    return render(request, "core/categoria_form.html", {"form": form})


@login_obrigatorio
@admin_obrigatorio
def categoria_update(request, pk):
    categoria = get_object_or_404(CategoriaItem, pk=pk)
    if request.method == "POST":
        form = CategoriaItemForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso!")
            return redirect("categoria_list")
    else:
        form = CategoriaItemForm(instance=categoria)
    return render(request, "core/categoria_form.html", {"form": form, "editing": True})


@login_obrigatorio
def categoria_list(request):
    query = request.GET.get("q", "").strip()
    categorias_list = CategoriaItem.objects.all().order_by("nome")
    if query:
        categorias_list = categorias_list.filter(nome__icontains=query)

    paginator = Paginator(categorias_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/categoria_list.html",
        {"page_obj": page_obj, "query": query},
    )


@login_obrigatorio
@admin_obrigatorio
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item cadastrado com sucesso!")
            return redirect("item_list")
    else:
        form = ItemForm()
    return render(request, "core/item_form.html", {"form": form})


@login_obrigatorio
@admin_obrigatorio
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item atualizado com sucesso!")
            return redirect("item_list")
    else:
        form = ItemForm(instance=item)
    return render(request, "core/item_form.html", {"form": form, "editing": True})


@login_obrigatorio
def item_list(request):
    query = request.GET.get("q", "").strip()
    itens_list = Item.objects.select_related("categoria", "unidade_medida").all().order_by("nome")
    if query:
        itens_list = itens_list.filter(nome__icontains=query)

    paginator = Paginator(itens_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/item_list.html",
        {"page_obj": page_obj, "query": query},
    )


@login_obrigatorio
def doacao_create(request):
    if request.method == "POST":
        form = DoacaoForm(request.POST)
        if form.is_valid():
            doacao = form.save(commit=False)
            doacao.registrado_por = request.user
            doacao.save()
            messages.success(request, "Doação registrada com sucesso!")
            return redirect("doacao_create")
    else:
        form = DoacaoForm()
    return render(request, "core/doacao_form.html", {"form": form})


@login_obrigatorio
def doacao_list(request):
    id_doador = request.GET.get("id_doador", "").strip()
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    doacoes_list = (
        Doacao.objects.filter(cancelado=False)
        .select_related("doador", "item", "registrado_por")
        .order_by("-data")
    )
    if id_doador:
        doacoes_list = doacoes_list.filter(doador_id=id_doador)
    data_inicio_parsed = parse_date(data_inicio) if data_inicio else None
    if data_inicio_parsed:
        doacoes_list = doacoes_list.filter(data__gte=data_inicio_parsed)
    data_fim_parsed = parse_date(data_fim) if data_fim else None
    if data_fim_parsed:
        doacoes_list = doacoes_list.filter(data__lte=data_fim_parsed)

    paginator = Paginator(doacoes_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "core/doacao_list.html",
        {
            "page_obj": page_obj,
            "doadores": Doador.objects.order_by("nome"),
            "id_doador": id_doador,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        },
    )


@login_obrigatorio
def distribuicao_create(request):
    itens_saldo = {
        str(item.pk): {"saldo": f"{item.saldo_atual:.2f}", "unidade": item.unidade_medida.sigla}
        for item in Item.objects.select_related("unidade_medida").all()
    }
    if request.method == "POST":
        form = DistribuicaoForm(request.POST)
        if form.is_valid():
            distribuicao = form.save(commit=False)
            distribuicao.registrado_por = request.user
            distribuicao.save()
            messages.success(request, "Distribuição registrada com sucesso!")
            return redirect("distribuicao_create")
    else:
        form = DistribuicaoForm()
    return render(
        request, "core/distribuicao_form.html", {"form": form, "itens_saldo": itens_saldo}
    )


@login_obrigatorio
def distribuicao_list(request):
    id_familia = request.GET.get("id_familia", "").strip()
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    distribuicoes_list = (
        Distribuicao.objects.filter(cancelado=False)
        .select_related("familia", "item", "registrado_por")
        .order_by("-data")
    )

    if id_familia:
        distribuicoes_list = distribuicoes_list.filter(familia_id=id_familia)

    data_inicio_parsed = parse_date(data_inicio) if data_inicio else None
    if data_inicio_parsed:
        distribuicoes_list = distribuicoes_list.filter(data__gte=data_inicio_parsed)

    data_fim_parsed = parse_date(data_fim) if data_fim else None
    if data_fim_parsed:
        distribuicoes_list = distribuicoes_list.filter(data__lte=data_fim_parsed)

    paginator = Paginator(distribuicoes_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "core/distribuicao_list.html",
        {
            "page_obj": page_obj,
            "familias": Familia.objects.order_by("nome_responsavel"),
            "id_familia": id_familia,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        },
    )


@login_obrigatorio
def distribuicao_exportar_csv(request):
    id_familia = request.GET.get("id_familia", "").strip()
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    distribuicoes = (
        Distribuicao.objects.filter(cancelado=False)
        .select_related("familia", "item", "registrado_por")
        .order_by("-data")
    )

    if id_familia:
        distribuicoes = distribuicoes.filter(familia_id=id_familia)

    data_inicio_parsed = parse_date(data_inicio) if data_inicio else None
    if data_inicio_parsed:
        distribuicoes = distribuicoes.filter(data__gte=data_inicio_parsed)

    data_fim_parsed = parse_date(data_fim) if data_fim else None
    if data_fim_parsed:
        distribuicoes = distribuicoes.filter(data__lte=data_fim_parsed)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")

    response["Content-Disposition"] = 'attachment; filename="relatorio_distribuicoes.csv"'

    writer = csv.writer(response)

    writer.writerow(
        [
            "Data",
            "Família",
            "Item",
            "Quantidade",
            "Usuário",
        ]
    )

    for distribuicao in distribuicoes:
        writer.writerow(
            [
                distribuicao.data.strftime("%d/%m/%Y"),
                distribuicao.familia.nome_responsavel,
                distribuicao.item.nome,
                distribuicao.quantidade,
                distribuicao.registrado_por.nome,
            ]
        )

    return response
