from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.decorators import admin_obrigatorio, login_obrigatorio
from core.forms import LoginForm, UsuarioForm
from core.models import Usuario


def home(request):
    return render(request, "core/home.html")


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
