from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.decorators import admin_obrigatorio, login_obrigatorio
from core.forms import (
    CategoriaItemForm,
    DoacaoForm,
    DoadorForm,
    FamiliaForm,
    ItemForm,
    LoginForm,
    UsuarioForm,
)
from core.models import CategoriaItem, Distribuicao, Doacao, Doador, Familia, Item, Usuario


def home(request):
    return render(request, "core/home.html")


def health(request):
    return JsonResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Gestão de usuários (Admin)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Doadores
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Famílias
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Categorias
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Itens
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Doações
# ---------------------------------------------------------------------------


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
def doacao_relatorio(request):
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    doacoes = Doacao.objects.filter(cancelado=False).select_related(
        "doador", "item", "item__unidade_medida"
    )
    if data_inicio:
        doacoes = doacoes.filter(data__gte=data_inicio)
    if data_fim:
        doacoes = doacoes.filter(data__lte=data_fim)

    totais = (
        doacoes.values(
            "doador__id_doador",
            "doador__nome",
            "doador__cpf_cnpj",
            "item__id_item",
            "item__nome",
            "item__unidade_medida__sigla",
        )
        .annotate(total_quantidade=Sum("quantidade"))
        .order_by("doador__nome", "item__nome")
    )

    doadores_dict = defaultdict(
        lambda: {"doador": None, "cpf_cnpj": "", "itens": [], "total_geral": 0}
    )

    for row in totais:
        d_id = row["doador__id_doador"]
        if doadores_dict[d_id]["doador"] is None:
            doadores_dict[d_id]["doador"] = row["doador__nome"]
            doadores_dict[d_id]["cpf_cnpj"] = row["doador__cpf_cnpj"]

        doadores_dict[d_id]["itens"].append(
            {
                "item_nome": row["item__nome"],
                "unidade": row["item__unidade_medida__sigla"],
                "quantidade": row["total_quantidade"],
            }
        )
        doadores_dict[d_id]["total_geral"] += row["total_quantidade"]

    relatorio = sorted(
        doadores_dict.values(), key=lambda x: x["total_geral"], reverse=True
    )

    return render(
        request,
        "core/doacao_relatorio.html",
        {
            "relatorio": relatorio,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        },
    )


@login_obrigatorio
def distribuicao_relatorio(request):
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()
    familia_id = request.GET.get("familia", "").strip()

    distribuicoes = Distribuicao.objects.filter(cancelado=False).select_related(
        "familia", "item", "item__categoria", "item__unidade_medida"
    )
    if data_inicio:
        distribuicoes = distribuicoes.filter(data__gte=data_inicio)
    if data_fim:
        distribuicoes = distribuicoes.filter(data__lte=data_fim)
    if familia_id:
        distribuicoes = distribuicoes.filter(familia_id=familia_id)

    totais = (
        distribuicoes.values(
            "familia__id_familia",
            "familia__nome_responsavel",
            "familia__endereco",
            "item__id_item",
            "item__nome",
            "item__categoria__nome",
            "item__unidade_medida__sigla",
        )
        .annotate(
            total_quantidade=Sum("quantidade"),
            numero_distribuicoes=Count("id_distribuicao"),
        )
        .order_by("familia__nome_responsavel", "item__nome")
    )

    familias_dict = defaultdict(
        lambda: {"familia": None, "endereco": "", "itens": [], "total_geral": 0}
    )

    for row in totais:
        f_id = row["familia__id_familia"]
        if familias_dict[f_id]["familia"] is None:
            familias_dict[f_id]["familia"] = row["familia__nome_responsavel"]
            familias_dict[f_id]["endereco"] = row["familia__endereco"]

        familias_dict[f_id]["itens"].append(
            {
                "item_nome": row["item__nome"],
                "categoria": row["item__categoria__nome"],
                "unidade": row["item__unidade_medida__sigla"],
                "quantidade": row["total_quantidade"],
                "num_distribuicoes": row["numero_distribuicoes"],
            }
        )
        familias_dict[f_id]["total_geral"] += row["total_quantidade"]

    relatorio = sorted(
        familias_dict.values(), key=lambda x: x["total_geral"], reverse=True
    )
    familias = Familia.objects.all().order_by("nome_responsavel")

    return render(
        request,
        "core/distribuicao_relatorio.html",
        {
            "relatorio": relatorio,
            "familias": familias,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "familia_selecionada": familia_id,
        },
    )
