<<<<<<< HEAD
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.decorators import admin_obrigatorio, login_obrigatorio
from core.forms import LoginForm, UsuarioForm
from core.models import Usuario
=======
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaItemForm, DoadorForm, FamiliaForm, ItemForm
from .models import CategoriaItem, Doador, Familia, Item
>>>>>>> ef7ff43 (feat(core): implementa cadastros, listagens e testes para doadores, famílias, categorias e itens)


def home(request):
    return render(request, "core/home.html")


def health(request):
    return JsonResponse({"status": "ok"})


<<<<<<< HEAD
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
=======
def doador_create(request):
    if request.method == "POST":
        form = DoadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador cadastrado com sucesso!")
            return redirect("home")
    else:
        form = DoadorForm()
    return render(request, "core/doador_form.html", {"form": form})


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
        {"page_obj": page_obj, "query": query},
    )


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
        {"page_obj": page_obj, "query": query},
    )


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
>>>>>>> ef7ff43 (feat(core): implementa cadastros, listagens e testes para doadores, famílias, categorias e itens)
