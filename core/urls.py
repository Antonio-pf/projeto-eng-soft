from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("painel/", views.painel_view, name="painel"),
    path("usuarios/", views.usuarios_view, name="usuarios"),
    path("doadores/", views.doadores_view, name="doadores"),
    path(
        "usuarios/<int:id_usuario>/status/",
        views.usuario_alternar_status_view,
        name="usuario_alternar_status",
    ),
]
