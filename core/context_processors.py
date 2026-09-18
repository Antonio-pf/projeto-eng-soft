def usuario_logado(request):
    if request.user.is_authenticated:
        return {"usuario_logado": request.user}
    return {"usuario_logado": None}
