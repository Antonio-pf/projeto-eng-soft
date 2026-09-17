from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from core.models import Usuario


def login_obrigatorio(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("id_usuario"):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_obrigatorio(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("id_usuario"):
            return redirect("login")
        if request.session.get("usuario_perfil") != Usuario.Perfil.ADMINISTRADOR:
            return HttpResponseForbidden("Acesso restrito a administradores.")
        return view_func(request, *args, **kwargs)

    return wrapper
