from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.auth import autenticar
from core.decorators import admin_obrigatorio, login_obrigatorio
from core.forms import LoginForm, UsuarioForm
from core.models import Usuario


def home(request):
    return render(request, "core/home.html")


def health(request):
    return JsonResponse({"status": "ok"})


def login_view(request):
    if request.session.get("id_usuario"):
        return redirect("painel")

    erro = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = autenticar(form.cleaned_data["email"], form.cleaned_data["senha"])
            if usuario is not None:
                request.session["id_usuario"] = usuario.id_usuario
                request.session["usuario_perfil"] = usuario.perfil
                return redirect("painel")
            erro = "E-mail ou senha inválidos."
    else:
        form = LoginForm()

    return render(request, "core/login.html", {"form": form, "erro": erro})


def logout_view(request):
    request.session.flush()
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
            Usuario.objects.create(
                nome=form.cleaned_data["nome"],
                email=form.cleaned_data["email"],
                senha_hash=make_password(form.cleaned_data["senha"]),
                perfil=form.cleaned_data["perfil"],
            )
            return redirect("usuarios")
    else:
        form = UsuarioForm()

    usuarios = Usuario.objects.order_by("id_usuario")
    return render(request, "core/usuarios.html", {"form": form, "usuarios": usuarios})
