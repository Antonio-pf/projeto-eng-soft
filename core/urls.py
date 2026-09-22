from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
<<<<<<< HEAD
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("painel/", views.painel_view, name="painel"),
    path("usuarios/", views.usuarios_view, name="usuarios"),
    path(
        "usuarios/<int:id_usuario>/status/",
        views.usuario_alternar_status_view,
        name="usuario_alternar_status",
    ),
=======
    path("doadores/", views.doador_list, name="doador_list"),
    path("doadores/novo/", views.doador_create, name="doador_create"),
    path("doadores/<int:pk>/editar/", views.doador_update, name="doador_update"),
    path("familias/", views.familia_list, name="familia_list"),
    path("familias/nova/", views.familia_create, name="familia_create"),
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nova/", views.categoria_create, name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.categoria_update, name="categoria_update"),
    path("itens/", views.item_list, name="item_list"),
    path("itens/novo/", views.item_create, name="item_create"),
    path("itens/<int:pk>/editar/", views.item_update, name="item_update"),
>>>>>>> ef7ff43 (feat(core): implementa cadastros, listagens e testes para doadores, famílias, categorias e itens)
]
