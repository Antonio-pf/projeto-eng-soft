from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from core.models import Usuario


def login_obrigatorio(view_func):
    # Wrapper sobre login_required; usuário desativado perde acesso automático (Usuario.is_active).
    return login_required(view_func, login_url="login", redirect_field_name=None)


def admin_obrigatorio(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.perfil != Usuario.Perfil.ADMINISTRADOR:
            return HttpResponseForbidden("Acesso restrito a administradores.")
        return view_func(request, *args, **kwargs)

    return wrapper
