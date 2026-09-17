from django.contrib.auth.hashers import check_password

from core.models import Usuario


def autenticar(email: str, senha: str) -> Usuario | None:
    """Valida credenciais contra Usuario. Retorna None em qualquer falha,
    sem distinguir e-mail inexistente de senha errada"""
    try:
        usuario = Usuario.objects.get(email=email, ativo=True)
    except Usuario.DoesNotExist:
        return None

    if not check_password(senha, usuario.senha_hash):
        return None

    return usuario
