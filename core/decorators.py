from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from core.models import Usuario


def login_obrigatorio(view_func):
    # Usuário desativado perde o acesso porque o login_required consulta Usuario.is_active.
    view_protegida = login_required(view_func, login_url="login", redirect_field_name=None)

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # O htmx seguiria o redirect e mostraria a tela de login dentro do modal ou da lista.
        if request.headers.get("HX-Request") == "true" and not request.user.is_authenticated:
            response = HttpResponse(status=204)
            response["HX-Redirect"] = reverse("login")
            return response
        return view_protegida(request, *args, **kwargs)

    return wrapper


def admin_obrigatorio(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.perfil != Usuario.Perfil.ADMINISTRADOR:
            return HttpResponseForbidden("Acesso restrito a administradores.")
        return view_func(request, *args, **kwargs)

    return wrapper
