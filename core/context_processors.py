from core.models import Usuario


def usuario_logado(request):
    id_usuario = request.session.get("id_usuario")
    if not id_usuario:
        return {"usuario_logado": None}

    usuario = Usuario.objects.filter(id_usuario=id_usuario, ativo=True).first()
    return {"usuario_logado": usuario}
