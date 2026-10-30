import re
import runpy
import sys
from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.contrib.auth import SESSION_KEY, authenticate
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, connection, transaction
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from core.forms import UsuarioForm
from core.models import (
    CategoriaItem,
    Distribuicao,
    Doacao,
    Doador,
    Familia,
    Item,
    UnidadeMedida,
    Usuario,
)
from core.painel import montar_resumo, saudacao


class CoreSmokeTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conecta Social")

    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})


class HomePageTests(TestCase):
    def test_apresenta_secoes_e_equipe_sem_ra(self):
        response = self.client.get(reverse("home"))

        for secao in ("problema", "como-funciona", "perfis", "andamento", "equipe"):
            self.assertContains(response, f'id="{secao}"')
            self.assertContains(response, f'href="#{secao}"')
        for nome in (
            "Alexandre Victoriano Ribeiro Ulhoa",
            "Antonio Pires Felipe",
            "Daniel Souza Monteiro de Carvalho",
            "Luiz Henrique Neres",
        ):
            self.assertContains(response, nome)
        self.assertNotContains(response, "2840482")

    def test_visitante_ve_botao_de_entrar(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertNotContains(response, "Ir para o painel")

    def test_usuario_logado_ve_atalho_para_o_painel(self):
        usuario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-correta"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.force_login(usuario)

        response = self.client.get(reverse("home"))

        self.assertContains(response, f'href="{reverse("painel")}"')
        self.assertContains(response, "Maria Voluntária")
        self.assertNotContains(response, "Entrar no Conecta")


class AutenticarTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-correta"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )

    def test_credenciais_validas_retornam_usuario(self):
        resultado = authenticate(email="maria@conectasocial.org", password="senha-correta")

        self.assertEqual(resultado, self.usuario)

    def test_senha_errada_retorna_none(self):
        self.assertIsNone(authenticate(email="maria@conectasocial.org", password="senha-errada"))

    def test_email_inexistente_retorna_none(self):
        self.assertIsNone(authenticate(email="ninguem@conectasocial.org", password="senha-correta"))

    def test_usuario_inativo_retorna_none(self):
        self.usuario.ativo = False
        self.usuario.save()

        self.assertIsNone(authenticate(email="maria@conectasocial.org", password="senha-correta"))


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-correta"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )

    def test_login_valido_redireciona_para_painel(self):
        response = self.client.post(
            reverse("login"),
            {"email": "maria@conectasocial.org", "senha": "senha-correta"},
        )

        self.assertRedirects(response, reverse("painel"))
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.usuario.id_usuario)

    def test_login_invalido_mostra_erro_generico_e_nao_autentica(self):
        response = self.client.post(
            reverse("login"),
            {"email": "maria@conectasocial.org", "senha": "senha-errada"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "E-mail ou senha inválidos.")
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_painel_sem_sessao_redireciona_para_login(self):
        response = self.client.get(reverse("painel"))

        self.assertRedirects(response, reverse("login"))

    def test_logout_limpa_sessao_e_bloqueia_painel(self):
        self.client.post(
            reverse("login"),
            {"email": "maria@conectasocial.org", "senha": "senha-correta"},
        )

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn(SESSION_KEY, self.client.session)

        response = self.client.get(reverse("painel"))
        self.assertRedirects(response, reverse("login"))


class UsuarioFormTests(TestCase):
    def setUp(self):
        Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("alterar-senha"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )

    def _dados_validos(self, **overrides):
        dados = {
            "nome": "Nova Pessoa",
            "email": "nova@conectasocial.org",
            "senha": "uma-senha-bem-forte-123",
            "perfil": Usuario.Perfil.VOLUNTARIO,
        }
        dados.update(overrides)
        return dados

    def test_dados_validos_sao_aceitos(self):
        form = UsuarioForm(data=self._dados_validos())

        self.assertTrue(form.is_valid())

    def test_email_duplicado_e_rejeitado(self):
        form = UsuarioForm(data=self._dados_validos(email="maria@conectasocial.org"))

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_senha_fraca_e_rejeitada(self):
        form = UsuarioForm(data=self._dados_validos(senha="123"))

        self.assertFalse(form.is_valid())
        self.assertIn("senha", form.errors)


class UsuariosViewTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Sistema",
            email="admin@conectasocial.org",
            password=make_password("alterar-senha"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("alterar-senha"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )

    def _login(self, usuario, senha="alterar-senha"):
        self.client.post(
            reverse("login"),
            {"email": usuario.email, "senha": senha},
        )

    def test_acesso_anonimo_redireciona_para_login(self):
        response = self.client.get(reverse("usuarios"))

        self.assertRedirects(response, reverse("login"))

    def test_voluntario_recebe_403(self):
        self._login(self.voluntario)

        response = self.client.get(reverse("usuarios"))

        self.assertEqual(response.status_code, 403)

    def test_admin_cria_usuario_e_aparece_na_listagem(self):
        self._login(self.admin)

        response = self.client.post(
            reverse("usuarios"),
            {
                "nome": "João Voluntário",
                "email": "joao@conectasocial.org",
                "senha": "uma-senha-bem-forte-123",
                "perfil": Usuario.Perfil.VOLUNTARIO,
            },
        )

        self.assertRedirects(response, reverse("usuarios"))
        novo_usuario = Usuario.objects.get(email="joao@conectasocial.org")
        self.assertTrue(novo_usuario.password.startswith("pbkdf2_"))
        self.assertNotEqual(novo_usuario.password, "uma-senha-bem-forte-123")

        response_lista = self.client.get(reverse("usuarios"))
        self.assertContains(response_lista, "João Voluntário")

    def test_cadastro_de_usuario_mostra_notificacao(self):
        self._login(self.admin)

        response = self.client.post(
            reverse("usuarios"),
            {
                "nome": "João Voluntário",
                "email": "joao@conectasocial.org",
                "senha": "uma-senha-bem-forte-123",
                "perfil": Usuario.Perfil.VOLUNTARIO,
            },
            follow=True,
        )

        self.assertContains(response, "Usuário cadastrado com sucesso!")

    def test_email_duplicado_mostra_erro_e_nao_duplica(self):
        self._login(self.admin)
        total_antes = Usuario.objects.count()

        response = self.client.post(
            reverse("usuarios"),
            {
                "nome": "Maria Duplicada",
                "email": self.voluntario.email,
                "senha": "uma-senha-bem-forte-123",
                "perfil": Usuario.Perfil.VOLUNTARIO,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este e-mail já está cadastrado.")
        self.assertEqual(Usuario.objects.count(), total_antes)

    def test_voluntario_recem_criado_nao_acessa_usuarios(self):
        self._login(self.admin)
        self.client.post(
            reverse("usuarios"),
            {
                "nome": "João Voluntário",
                "email": "joao@conectasocial.org",
                "senha": "uma-senha-bem-forte-123",
                "perfil": Usuario.Perfil.VOLUNTARIO,
            },
        )
        self.client.get(reverse("logout"))

        self._login(
            Usuario.objects.get(email="joao@conectasocial.org"),
            senha="uma-senha-bem-forte-123",
        )
        response = self.client.get(reverse("usuarios"))

        self.assertEqual(response.status_code, 403)


class UsuarioAlternarStatusViewTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Sistema",
            email="admin@conectasocial.org",
            password=make_password("alterar-senha"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("alterar-senha"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )

    def _login(self, usuario, senha="alterar-senha"):
        self.client.post(
            reverse("login"),
            {"email": usuario.email, "senha": senha},
        )

    def test_admin_desativa_usuario(self):
        self._login(self.admin)

        response = self.client.post(
            reverse("usuario_alternar_status", args=[self.voluntario.id_usuario])
        )

        self.assertRedirects(response, reverse("usuarios"))
        self.voluntario.refresh_from_db()
        self.assertFalse(self.voluntario.ativo)

    def test_admin_reativa_usuario(self):
        self.voluntario.ativo = False
        self.voluntario.save()
        self._login(self.admin)

        self.client.post(reverse("usuario_alternar_status", args=[self.voluntario.id_usuario]))

        self.voluntario.refresh_from_db()
        self.assertTrue(self.voluntario.ativo)

    def test_usuario_desativado_nao_consegue_fazer_login(self):
        self._login(self.admin)
        self.client.post(reverse("usuario_alternar_status", args=[self.voluntario.id_usuario]))
        self.client.get(reverse("logout"))

        response = self.client.post(
            reverse("login"),
            {"email": self.voluntario.email, "senha": "alterar-senha"},
        )

        self.assertContains(response, "E-mail ou senha inválidos.")

    def test_usuario_desativado_com_sessao_ativa_perde_acesso(self):
        self._login(self.voluntario)

        self.voluntario.ativo = False
        self.voluntario.save()

        response = self.client.get(reverse("painel"))

        self.assertRedirects(response, reverse("login"))

    def test_admin_nao_consegue_desativar_a_si_mesmo(self):
        self._login(self.admin)

        self.client.post(reverse("usuario_alternar_status", args=[self.admin.id_usuario]))

        self.admin.refresh_from_db()
        self.assertTrue(self.admin.ativo)

    def test_voluntario_nao_pode_alternar_status(self):
        self._login(self.voluntario)

        response = self.client.post(
            reverse("usuario_alternar_status", args=[self.admin.id_usuario])
        )

        self.assertEqual(response.status_code, 403)

    def test_get_nao_e_permitido(self):
        self._login(self.admin)

        response = self.client.get(
            reverse("usuario_alternar_status", args=[self.voluntario.id_usuario])
        )

        self.assertEqual(response.status_code, 405)

    def test_listagem_distingue_ativos_e_inativos(self):
        self._login(self.admin)
        self.client.post(reverse("usuario_alternar_status", args=[self.voluntario.id_usuario]))

        response = self.client.get(reverse("usuarios"))

        self.assertContains(response, "Inativo")
        self.assertContains(response, "Ativo")

    def test_desativar_pede_confirmacao_em_modal(self):
        self._login(self.admin)

        response = self.client.get(reverse("usuarios"))

        self.assertContains(
            response, f'<dialog id="confirmar-desativacao-{self.voluntario.id_usuario}"'
        )
        self.assertContains(response, "Desativar o acesso de Maria Voluntária?")
        self.assertNotContains(
            response, f'<dialog id="confirmar-desativacao-{self.admin.id_usuario}"'
        )

    def test_alternar_status_mostra_notificacao(self):
        self._login(self.admin)
        url = reverse("usuario_alternar_status", args=[self.voluntario.id_usuario])

        response = self.client.post(url, follow=True)
        self.assertContains(response, "Acesso de Maria Voluntária desativado.")

        response = self.client.post(url, follow=True)
        self.assertContains(response, "Acesso de Maria Voluntária reativado.")


class DoadorTestCase(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Voluntário Teste",
            email="vol@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "vol@conectasocial.org", "senha": "senha-teste"},
        )

    def test_cadastrar_doador_com_sucesso(self):
        response = self.client.post(
            reverse("doador_create"),
            {
                "nome": "João da Silva",
                "cpf_cnpj": "123.456.789-01",
                "telefone": "(11) 98765-4321",
                "email": "joao@example.com",
            },
        )
        self.assertRedirects(response, reverse("doador_list"))
        self.assertEqual(Doador.objects.count(), 1)
        doador = Doador.objects.first()
        self.assertEqual(doador.nome, "João da Silva")
        self.assertEqual(doador.cpf_cnpj, "123.456.789-01")

    def test_cadastro_mostra_notificacao_na_listagem(self):
        response = self.client.post(
            reverse("doador_create"),
            {"nome": "João da Silva", "cpf_cnpj": "123.456.789-01"},
            follow=True,
        )

        self.assertContains(response, 'role="status"')
        self.assertContains(response, "Doador cadastrado com sucesso!")

        response = self.client.get(reverse("doador_list"))
        self.assertNotContains(response, "Doador cadastrado com sucesso!")

    def test_cadastrar_doador_campos_opcionais_vazios(self):
        response = self.client.post(
            reverse("doador_create"),
            {
                "nome": "Maria Souza",
                "cpf_cnpj": "987.654.321-09",
                "telefone": "",
                "email": "",
            },
        )
        self.assertRedirects(response, reverse("doador_list"))
        self.assertEqual(Doador.objects.count(), 1)
        doador = Doador.objects.first()
        self.assertEqual(doador.nome, "Maria Souza")
        self.assertEqual(doador.telefone, "")
        self.assertEqual(doador.email, "")

    def test_cpf_formato_invalido(self):
        response = self.client.post(
            reverse("doador_create"),
            {
                "nome": "Teste Formato",
                "cpf_cnpj": "123456789",
                "telefone": "",
                "email": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("cpf_cnpj", form.errors)
        self.assertEqual(Doador.objects.count(), 0)

    def test_cpf_duplicado(self):
        Doador.objects.create(
            nome="Doador Existente",
            cpf_cnpj="123.456.789-01",
        )
        response = self.client.post(
            reverse("doador_create"),
            {
                "nome": "Outro Doador",
                "cpf_cnpj": "123.456.789-01",
                "telefone": "",
                "email": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("cpf_cnpj", form.errors)
        self.assertEqual(Doador.objects.count(), 1)

    def test_listar_doadores(self):
        Doador.objects.create(nome="Carlos Silva", cpf_cnpj="111.111.111-11")
        Doador.objects.create(nome="Ana Pereira", cpf_cnpj="222.222.222-22")
        response = self.client.get(reverse("doador_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carlos Silva")
        self.assertContains(response, "111.111.111-11")
        self.assertContains(response, "Ana Pereira")
        self.assertContains(response, "222.222.222-22")

    def test_buscar_doador_por_nome(self):
        Doador.objects.create(nome="Carlos Silva", cpf_cnpj="111.111.111-11")
        Doador.objects.create(nome="Ana Pereira", cpf_cnpj="222.222.222-22")
        response = self.client.get(reverse("doador_list"), {"q": "Carlos"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carlos Silva")
        self.assertNotContains(response, "Ana Pereira")

    def test_paginacao_doadores(self):
        for i in range(25):
            cpf = f"111.111.11{i:02d}-11" if i < 10 else f"11.{i:03d}.111/0001-11"
            Doador.objects.create(nome=f"Doador {i:02d}", cpf_cnpj=cpf)

        response = self.client.get(reverse("doador_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 20)
        self.assertTrue(response.context["page_obj"].has_next())

        response_page_2 = self.client.get(reverse("doador_list") + "?page=2")
        self.assertEqual(response_page_2.status_code, 200)
        self.assertEqual(len(response_page_2.context["page_obj"]), 5)


class DoadorUpdateTestCase(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "admin@conectasocial.org", "senha": "senha-teste"},
        )
        self.doador1 = Doador.objects.create(
            nome="Doador Um",
            cpf_cnpj="111.111.111-11",
            telefone="(11) 1111-1111",
            email="um@example.com",
        )
        self.doador2 = Doador.objects.create(
            nome="Doador Dois",
            cpf_cnpj="222.222.222-22",
            telefone="(22) 2222-2222",
            email="dois@example.com",
        )

    def test_doador_edit_get_prefilled(self):
        response = self.client.get(reverse("doador_update", args=[self.doador1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.doador1.nome)
        self.assertContains(response, self.doador1.cpf_cnpj)
        self.assertTrue(response.context.get("editing"))

    def test_doador_edit_success(self):
        response = self.client.post(
            reverse("doador_update", args=[self.doador1.pk]),
            {
                "nome": "Doador Um Atualizado",
                "cpf_cnpj": "111.111.111-11",
                "telefone": "(11) 9999-9999",
                "email": "um_novo@example.com",
            },
        )
        self.assertRedirects(response, reverse("doador_list"))
        self.doador1.refresh_from_db()
        self.assertEqual(self.doador1.nome, "Doador Um Atualizado")
        self.assertEqual(self.doador1.telefone, "(11)9999-9999")

    def test_doador_edit_duplicate_cpf_cnpj(self):
        response = self.client.post(
            reverse("doador_update", args=[self.doador1.pk]),
            {
                "nome": "Doador Um Conflito",
                "cpf_cnpj": "222.222.222-22",
                "telefone": "(11) 1111-1111",
                "email": "um@example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("cpf_cnpj", form.errors)


class FamiliaTestCase(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Voluntário Teste",
            email="vol@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "vol@conectasocial.org", "senha": "senha-teste"},
        )

    def test_cadastrar_familia_com_sucesso(self):
        response = self.client.post(
            reverse("familia_create"),
            {
                "nome_responsavel": "Família Silva",
                "endereco": "Rua A, 123",
                "telefone": "(11) 98888-7777",
                "num_membros": 4,
            },
        )
        self.assertRedirects(response, reverse("familia_list"))
        from core.models import Familia

        self.assertEqual(Familia.objects.count(), 1)
        familia = Familia.objects.first()
        self.assertEqual(familia.nome_responsavel, "Família Silva")
        self.assertEqual(familia.num_membros, 4)

    def test_cadastrar_familia_telefone_opcional(self):
        response = self.client.post(
            reverse("familia_create"),
            {
                "nome_responsavel": "Família Oliveira",
                "endereco": "Rua B, 456",
                "telefone": "",
                "num_membros": 2,
            },
        )
        self.assertRedirects(response, reverse("familia_list"))
        from core.models import Familia

        self.assertEqual(Familia.objects.count(), 1)
        familia = Familia.objects.first()
        self.assertEqual(familia.telefone, "")

    def test_cadastrar_familia_num_membros_invalido(self):
        response = self.client.post(
            reverse("familia_create"),
            {
                "nome_responsavel": "Família Erro",
                "endereco": "Rua C, 789",
                "telefone": "",
                "num_membros": 0,
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("num_membros", form.errors)

    def test_listar_e_buscar_familias(self):
        from core.models import Familia

        Familia.objects.create(nome_responsavel="João da Silva", endereco="Rua 1", num_membros=3)
        Familia.objects.create(nome_responsavel="Maria Santos", endereco="Rua 2", num_membros=2)

        response = self.client.get(reverse("familia_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "João da Silva")
        self.assertContains(response, "Maria Santos")

        response_search = self.client.get(reverse("familia_list"), {"q": "João"})
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, "João da Silva")
        self.assertNotContains(response_search, "Maria Santos")


class DoadoresEFamiliasComHtmxTests(TestCase):
    """Cadastro em modal e busca sem recarregar em Doadores e Famílias."""

    HTMX = {"HTTP_HX_REQUEST": "true"}

    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        self.client.force_login(self.admin)

    def _familia(self, nome="Ana Paula Ferreira"):
        return Familia.objects.create(
            nome_responsavel=nome, endereco="Rua das Flores, 120", num_membros=5
        )

    def test_lista_de_doadores_abre_o_cadastro_no_modal(self):
        response = self.client.get(reverse("doador_list"))

        self.assertContains(response, f'hx-get="{reverse("doador_create")}"')
        self.assertContains(response, "+ Novo doador")
        self.assertNotContains(response, f'action="{reverse("doador_create")}"')

    def test_novo_doador_no_modal_devolve_so_o_formulario(self):
        response = self.client.get(reverse("doador_create"), **self.HTMX)

        self.assertNotContains(response, "<html")
        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, "Novo doador")
        self.assertContains(response, f'hx-post="{reverse("doador_create")}"')

    def test_salvar_doador_no_modal_fecha_e_atualiza_a_lista(self):
        response = self.client.post(
            reverse("doador_create"),
            {"nome": "Padaria Pão Quente", "cpf_cnpj": "123.456.789-01"},
            **self.HTMX,
        )

        self.assertEqual(response["HX-Trigger"], "registro-salvo")
        self.assertContains(response, "Doador cadastrado com sucesso!")
        self.assertTrue(Doador.objects.filter(nome="Padaria Pão Quente").exists())

    def test_cpf_duplicado_aparece_dentro_do_modal(self):
        Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")

        response = self.client.post(
            reverse("doador_create"),
            {"nome": "Outro", "cpf_cnpj": "123.456.789-01"},
            **self.HTMX,
        )

        self.assertNotIn("HX-Trigger", response)
        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, 'class="text-xs text-error"')

    def test_editar_doador_no_modal(self):
        doador = Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")

        response = self.client.get(reverse("doador_update", args=[doador.pk]), **self.HTMX)

        self.assertContains(response, "Editar doador")
        self.assertContains(response, 'value="Mercado Central"')

    def test_pagina_de_cadastro_de_doador_tem_titulo_de_cadastro(self):
        response = self.client.get(reverse("doador_create"))

        self.assertContains(response, "<title>Cadastrar Doador | Conecta Social</title>")
        self.assertNotContains(response, "Editar Doador")

    def test_busca_de_doadores_com_htmx_devolve_so_a_lista(self):
        Doador.objects.create(nome="Carlos Silva", cpf_cnpj="111.111.111-11")
        Doador.objects.create(nome="Ana Pereira", cpf_cnpj="222.222.222-22")

        response = self.client.get(reverse("doador_list"), {"q": "carl"}, **self.HTMX)

        self.assertContains(response, 'id="doador-lista"')
        self.assertContains(response, "Carlos Silva")
        self.assertNotContains(response, "Ana Pereira")
        self.assertNotContains(response, 'id="sidebar"')
        self.assertIn("HX-Request", response["Vary"])

    def test_doador_tem_atalho_para_suas_doacoes(self):
        doador = Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")

        response = self.client.get(reverse("doador_list"))

        self.assertContains(response, f'href="{reverse("doacao_list")}?id_doador={doador.pk}"')

    def test_voluntario_cadastra_doador_mas_nao_edita(self):
        doador = Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")
        self.client.force_login(self.voluntario)

        response = self.client.get(reverse("doador_list"))

        self.assertContains(response, "+ Novo doador")
        self.assertNotContains(response, reverse("doador_update", args=[doador.pk]))

    def test_doadores_vazio_e_busca_sem_resultado(self):
        response = self.client.get(reverse("doador_list"))
        self.assertContains(response, "Nenhum doador cadastrado ainda.")
        self.assertContains(response, "Cadastrar doador")

        Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")
        response = self.client.get(reverse("doador_list"), {"q": "xyz"})
        self.assertContains(response, "Nenhum doador encontrado para “xyz”.")

    def test_lista_de_familias_abre_o_cadastro_no_modal(self):
        response = self.client.get(reverse("familia_list"))

        self.assertContains(response, f'hx-get="{reverse("familia_create")}"')
        self.assertContains(response, "+ Nova família")
        self.assertNotContains(response, f'action="{reverse("familia_create")}"')

    def test_familia_no_modal(self):
        response = self.client.get(reverse("familia_create"), **self.HTMX)
        self.assertContains(response, 'id="modal-titulo"')
        self.assertNotContains(response, "<html")

        response = self.client.post(
            reverse("familia_create"),
            {
                "nome_responsavel": "Ana Paula Ferreira",
                "endereco": "Rua das Flores, 120",
                "telefone": "",
                "num_membros": 5,
            },
            **self.HTMX,
        )
        self.assertEqual(response["HX-Trigger"], "registro-salvo")
        self.assertContains(response, "Família cadastrada com sucesso!")

    def test_busca_de_familias_com_htmx_devolve_so_a_lista(self):
        self._familia("Ana Paula Ferreira")
        self._familia("Carlos Henrique Santos")

        response = self.client.get(reverse("familia_list"), {"q": "ana"}, **self.HTMX)

        self.assertContains(response, 'id="familia-lista"')
        self.assertContains(response, "Ana Paula Ferreira")
        self.assertNotContains(response, "Carlos Henrique Santos")
        self.assertNotContains(response, 'id="sidebar"')

    def test_familia_tem_atalho_para_distribuir(self):
        familia = self._familia()

        response = self.client.get(reverse("familia_list"))

        self.assertContains(
            response, f'href="{reverse("distribuicao_create")}?familia={familia.pk}"'
        )

    def test_atalho_de_distribuir_ja_seleciona_a_familia(self):
        familia = self._familia()

        response = self.client.get(reverse("distribuicao_create"), {"familia": familia.pk})

        self.assertContains(response, f'<option value="{familia.pk}" selected>')

    def test_familias_vazio_e_busca_sem_resultado(self):
        response = self.client.get(reverse("familia_list"))
        self.assertContains(response, "Nenhuma família cadastrada ainda.")
        self.assertContains(response, "Cadastrar família")

        self._familia()
        response = self.client.get(reverse("familia_list"), {"q": "xyz"})
        self.assertContains(response, "Nenhuma família encontrada para “xyz”.")


class CategoriaTestCase(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "admin@conectasocial.org", "senha": "senha-teste"},
        )

    def test_cadastrar_categoria_com_sucesso(self):
        response = self.client.post(
            reverse("categoria_create"),
            {
                "nome": "Alimento",
                "descricao": "Alimentos não perecíveis",
            },
        )
        self.assertRedirects(response, reverse("categoria_list"))
        self.assertEqual(CategoriaItem.objects.count(), 1)
        cat = CategoriaItem.objects.first()
        self.assertEqual(cat.nome, "Alimento")
        self.assertEqual(cat.descricao, "Alimentos não perecíveis")

    def test_cadastrar_categoria_nome_duplicado(self):
        CategoriaItem.objects.create(nome="Roupa", descricao="Vestuário")
        response = self.client.post(
            reverse("categoria_create"),
            {
                "nome": "Roupa",
                "descricao": "Outra descrição",
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("nome", form.errors)
        self.assertEqual(CategoriaItem.objects.count(), 1)

    def test_listar_categorias(self):
        CategoriaItem.objects.create(nome="Higiene")
        response = self.client.get(reverse("categoria_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Higiene")

    def test_editar_categoria(self):
        cat = CategoriaItem.objects.create(nome="Limpeza")
        response = self.client.post(
            reverse("categoria_update", args=[cat.pk]),
            {
                "nome": "Limpeza Geral",
                "descricao": "Atualizado",
            },
        )
        self.assertRedirects(response, reverse("categoria_list"))
        cat.refresh_from_db()
        self.assertEqual(cat.nome, "Limpeza Geral")


class ItemTestCase(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "admin@conectasocial.org", "senha": "senha-teste"},
        )
        self.categoria = CategoriaItem.objects.create(nome="Alimento")
        self.unidade = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")

    def test_cadastrar_item_com_sucesso(self):
        response = self.client.post(
            reverse("item_create"),
            {
                "nome": "Arroz 5kg",
                "categoria": self.categoria.pk,
                "unidade_medida": self.unidade.pk,
                "estoque_minimo": 10,
            },
        )
        self.assertRedirects(response, reverse("item_list"))
        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.first()
        self.assertEqual(item.nome, "Arroz 5kg")
        self.assertEqual(item.estoque_minimo, 10)
        self.assertEqual(item.saldo_atual, 0)

    def test_cadastrar_item_estoque_minimo_invalido(self):
        response = self.client.post(
            reverse("item_create"),
            {
                "nome": "Feijão",
                "categoria": self.categoria.pk,
                "unidade_medida": self.unidade.pk,
                "estoque_minimo": -1,
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("estoque_minimo", form.errors)

    def test_listar_itens_com_saldo_e_destaque(self):
        Item.objects.create(
            nome="Arroz",
            categoria=self.categoria,
            unidade_medida=self.unidade,
            estoque_minimo=5,
        )
        response = self.client.get(reverse("item_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Arroz")
        self.assertContains(response, "0")  # Saldo zero
        self.assertContains(response, "Baixo Estoque")  # 0 <= 5

    def test_editar_item(self):
        item = Item.objects.create(
            nome="Macarrão",
            categoria=self.categoria,
            unidade_medida=self.unidade,
            estoque_minimo=2,
        )
        response = self.client.post(
            reverse("item_update", args=[item.pk]),
            {
                "nome": "Macarrão Integral",
                "categoria": self.categoria.pk,
                "unidade_medida": self.unidade.pk,
                "estoque_minimo": 4,
            },
        )
        self.assertRedirects(response, reverse("item_list"))
        item.refresh_from_db()
        self.assertEqual(item.nome, "Macarrão Integral")


class ItensECategoriasComHtmxTests(TestCase):
    """Cadastro em modal e busca sem recarregar; sem htmx, as páginas continuam funcionando."""

    HTMX = {"HTTP_HX_REQUEST": "true"}

    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        self.categoria = CategoriaItem.objects.create(nome="Alimento")
        self.unidade = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.doador = Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")
        self.client.force_login(self.admin)

    def _item(self, nome, minimo=0):
        return Item.objects.create(
            nome=nome, categoria=self.categoria, unidade_medida=self.unidade, estoque_minimo=minimo
        )

    def _doar(self, item, quantidade):
        Doacao.objects.create(
            doador=self.doador,
            item=item,
            registrado_por=self.admin,
            quantidade=Decimal(quantidade),
            data=timezone.localdate(),
        )

    def _dados_item(self, **extras):
        return {
            "nome": "Arroz 5kg",
            "categoria": self.categoria.pk,
            "unidade_medida": self.unidade.pk,
            "estoque_minimo": 10,
            **extras,
        }

    def test_novo_item_no_modal_devolve_so_o_formulario(self):
        response = self.client.get(reverse("item_create"), **self.HTMX)

        self.assertNotContains(response, "<html")
        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, f'hx-post="{reverse("item_create")}"')

    def test_salvar_no_modal_fecha_e_pede_para_a_lista_atualizar(self):
        response = self.client.post(reverse("item_create"), self._dados_item(), **self.HTMX)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Trigger"], "registro-salvo")
        self.assertEqual(response["HX-Reswap"], "none")
        self.assertContains(response, 'hx-swap-oob="innerHTML"')
        self.assertContains(response, "Item cadastrado com sucesso!")
        self.assertTrue(Item.objects.filter(nome="Arroz 5kg").exists())

    def test_erro_no_modal_reapresenta_o_formulario_com_a_mensagem(self):
        response = self.client.post(
            reverse("item_create"), self._dados_item(estoque_minimo=-1), **self.HTMX
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("HX-Trigger", response)
        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, 'class="text-xs text-error"')
        self.assertFalse(Item.objects.exists())

    def test_editar_no_modal_mostra_o_saldo_atual(self):
        item = self._item("Feijão 1kg")
        self._doar(item, "12")

        response = self.client.get(reverse("item_update", args=[item.pk]), **self.HTMX)

        self.assertContains(response, "Editar item")
        self.assertContains(response, "Saldo atual: <strong>12 kg</strong>")

    def test_busca_com_htmx_devolve_so_a_lista(self):
        self._item("Arroz")
        self._item("Feijão")

        response = self.client.get(reverse("item_list"), {"q": "arr"}, **self.HTMX)

        self.assertContains(response, 'id="item-lista"')
        self.assertContains(response, "Arroz")
        self.assertNotContains(response, "Feijão")
        self.assertNotContains(response, 'id="sidebar"')
        self.assertIn("HX-Request", response["Vary"])

    def test_sessao_expirada_no_htmx_leva_a_pagina_de_login(self):
        self.client.logout()

        response = self.client.get(reverse("item_list"), {"q": "arr"}, **self.HTMX)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["HX-Redirect"], reverse("login"))

    def test_restauracao_do_historico_recebe_a_pagina_inteira(self):
        response = self.client.get(
            reverse("item_list"), HTTP_HX_REQUEST="true", HTTP_HX_HISTORY_RESTORE_REQUEST="true"
        )

        self.assertContains(response, 'id="sidebar"')

    def test_filtro_de_baixo_estoque(self):
        self._item("Arroz", minimo=5)
        self._doar(self._item("Feijão", minimo=5), "20")

        response = self.client.get(reverse("item_list"), {"estoque": "baixo"})

        self.assertContains(response, "Arroz")
        self.assertNotContains(response, "Feijão")
        self.assertContains(response, "Baixo estoque (1)")

    def test_paginacao_preserva_busca_e_filtro(self):
        for indice in range(21):
            self._item(f"Arroz {indice:02d}", minimo=5)

        response = self.client.get(reverse("item_list"), {"q": "Arroz", "estoque": "baixo"})

        self.assertContains(response, "?q=Arroz&amp;estoque=baixo&amp;page=2")

    def test_linhas_tem_atalhos_de_doacao_e_distribuicao(self):
        item = self._item("Arroz")

        response = self.client.get(reverse("item_list"))

        self.assertContains(response, f'href="{reverse("doacao_create")}?item={item.pk}"')
        self.assertContains(response, f'href="{reverse("distribuicao_create")}?item={item.pk}"')

    def test_voluntario_nao_ve_cadastro_nem_edicao(self):
        item = self._item("Arroz")
        self.client.force_login(self.voluntario)

        response = self.client.get(reverse("item_list"))

        self.assertNotContains(response, reverse("item_create"))
        self.assertNotContains(response, reverse("item_update", args=[item.pk]))
        self.assertContains(response, f'href="{reverse("doacao_create")}?item={item.pk}"')

    def test_lista_vazia_oferece_cadastro(self):
        response = self.client.get(reverse("item_list"))

        self.assertContains(response, "Nenhum item cadastrado ainda.")
        self.assertContains(response, "Cadastrar item")

    def test_busca_sem_resultado_oferece_limpar(self):
        self._item("Arroz")

        response = self.client.get(reverse("item_list"), {"q": "xyz"})

        self.assertContains(response, "Nenhum item encontrado para “xyz”.")
        self.assertContains(response, "Limpar filtros")

    def test_abas_ligam_itens_e_categorias(self):
        for nome_url in ("item_list", "categoria_list"):
            with self.subTest(pagina=nome_url):
                response = self.client.get(reverse(nome_url))

                self.assertContains(response, f'href="{reverse("item_list")}"')
                self.assertContains(response, f'href="{reverse("categoria_list")}"')
                self.assertContains(response, 'aria-current="page"')

    def test_categoria_no_modal(self):
        response = self.client.get(reverse("categoria_create"), **self.HTMX)
        self.assertContains(response, 'id="modal-titulo"')
        self.assertNotContains(response, "<html")

        response = self.client.post(
            reverse("categoria_create"), {"nome": "Higiene", "descricao": ""}, **self.HTMX
        )
        self.assertEqual(response["HX-Trigger"], "registro-salvo")
        self.assertContains(response, "Categoria cadastrada com sucesso!")

    def test_busca_de_categorias_com_htmx_devolve_so_a_lista(self):
        CategoriaItem.objects.create(nome="Higiene")

        response = self.client.get(reverse("categoria_list"), {"q": "hig"}, **self.HTMX)

        self.assertContains(response, 'id="categoria-lista"')
        self.assertContains(response, "Higiene")
        self.assertNotContains(response, "Alimento")
        self.assertNotContains(response, 'id="sidebar"')


class DoacaoTestCase(TestCase):
    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.doador = Doador.objects.create(nome="João Doador", cpf_cnpj="123.456.789-00")
        categoria = CategoriaItem.objects.create(nome="Alimento")
        unidade = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.item = Item.objects.create(
            nome="Arroz 5kg",
            categoria=categoria,
            unidade_medida=unidade,
            estoque_minimo=10,
        )
        self._login(self.voluntario)

    def _login(self, usuario, senha="senha-teste"):
        self.client.post(reverse("login"), {"email": usuario.email, "senha": senha})

    def test_cadastrar_doacao_com_sucesso(self):
        response = self.client.post(
            reverse("doacao_create"),
            {
                "doador": self.doador.pk,
                "item": self.item.pk,
                "quantidade": "5",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertRedirects(response, reverse("doacao_create"))
        self.assertEqual(Doacao.objects.count(), 1)
        doacao = Doacao.objects.first()
        self.assertEqual(doacao.doador, self.doador)
        self.assertEqual(doacao.item, self.item)
        self.assertEqual(doacao.quantidade, Decimal("5"))
        self.assertEqual(doacao.registrado_por, self.voluntario)
        self.item.refresh_from_db()
        self.assertEqual(self.item.saldo_atual, Decimal("5"))

    def test_atalho_da_lista_de_itens_ja_seleciona_o_item(self):
        response = self.client.get(reverse("doacao_create"), {"item": self.item.pk})

        self.assertContains(response, f'<option value="{self.item.pk}" selected>')

    def test_registro_mostra_notificacao_no_proprio_formulario(self):
        response = self.client.post(
            reverse("doacao_create"),
            {
                "doador": self.doador.pk,
                "item": self.item.pk,
                "quantidade": "5",
                "data": timezone.localdate().isoformat(),
            },
            follow=True,
        )

        self.assertEqual(response.redirect_chain, [(reverse("doacao_create"), 302)])
        self.assertContains(response, "Doação registrada com sucesso!")

    def test_cadastrar_doacao_quantidade_zero_ou_negativa_invalida(self):
        for quantidade in ["0", "-3"]:
            response = self.client.post(
                reverse("doacao_create"),
                {
                    "doador": self.doador.pk,
                    "item": self.item.pk,
                    "quantidade": quantidade,
                    "data": timezone.localdate().isoformat(),
                },
            )
            self.assertEqual(response.status_code, 200)
            form = response.context["form"]
            self.assertIn("quantidade", form.errors)
        self.assertEqual(Doacao.objects.count(), 0)

    def test_cadastrar_doacao_quantidade_fracionada_permitida(self):
        response = self.client.post(
            reverse("doacao_create"),
            {
                "doador": self.doador.pk,
                "item": self.item.pk,
                "quantidade": "2.5",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertRedirects(response, reverse("doacao_create"))
        doacao = Doacao.objects.first()
        self.assertEqual(doacao.quantidade, Decimal("2.50"))

    def test_cadastrar_doacao_data_futura_invalida(self):
        data_futura = timezone.localdate() + timedelta(days=1)
        response = self.client.post(
            reverse("doacao_create"),
            {
                "doador": self.doador.pk,
                "item": self.item.pk,
                "quantidade": "3",
                "data": data_futura.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("data", form.errors)
        self.assertEqual(Doacao.objects.count(), 0)

    def test_cadastrar_doacao_acesso_anonimo_redireciona_para_login(self):
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("doacao_create"))
        self.assertRedirects(response, reverse("login"))

    def test_administrador_tambem_pode_registrar_doacao(self):
        self.client.get(reverse("logout"))
        self._login(self.admin)
        response = self.client.post(
            reverse("doacao_create"),
            {
                "doador": self.doador.pk,
                "item": self.item.pk,
                "quantidade": "1",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertRedirects(response, reverse("doacao_create"))
        self.assertEqual(Doacao.objects.count(), 1)

    def test_formulario_abre_com_data_de_hoje_em_formato_iso(self):
        response = self.client.get(reverse("doacao_create"))
        self.assertContains(response, f'value="{timezone.localdate().isoformat()}"')


class DistribuicaoTestCase(TestCase):
    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.familia = Familia.objects.create(
            nome_responsavel="Família Silva", endereco="Rua A, 123", num_membros=4
        )
        doador = Doador.objects.create(nome="João Doador", cpf_cnpj="123.456.789-00")
        categoria = CategoriaItem.objects.create(nome="Alimento")
        unidade = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.item = Item.objects.create(
            nome="Arroz 5kg",
            categoria=categoria,
            unidade_medida=unidade,
            estoque_minimo=10,
        )
        Doacao.objects.create(
            doador=doador,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("10"),
            data=timezone.localdate(),
        )
        self._login(self.voluntario)

    def _login(self, usuario, senha="senha-teste"):
        self.client.post(reverse("login"), {"email": usuario.email, "senha": senha})

    def test_atalho_da_lista_de_itens_ja_seleciona_o_item(self):
        response = self.client.get(reverse("distribuicao_create"), {"item": self.item.pk})

        self.assertContains(response, f'<option value="{self.item.pk}" selected>')

    def test_registrar_distribuicao_com_sucesso(self):
        response = self.client.post(
            reverse("distribuicao_create"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": "4",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertRedirects(response, reverse("distribuicao_create"))
        self.assertEqual(Distribuicao.objects.count(), 1)
        distribuicao = Distribuicao.objects.first()
        self.assertEqual(distribuicao.familia, self.familia)
        self.assertEqual(distribuicao.item, self.item)
        self.assertEqual(distribuicao.quantidade, Decimal("4"))
        self.assertEqual(distribuicao.registrado_por, self.voluntario)
        self.item.refresh_from_db()
        self.assertEqual(self.item.saldo_atual, Decimal("6"))

    def test_registrar_distribuicao_quantidade_zero_ou_negativa_invalida(self):
        for quantidade in ["0", "-3"]:
            response = self.client.post(
                reverse("distribuicao_create"),
                {
                    "familia": self.familia.pk,
                    "item": self.item.pk,
                    "quantidade": quantidade,
                    "data": timezone.localdate().isoformat(),
                },
            )
            self.assertEqual(response.status_code, 200)
            form = response.context["form"]
            self.assertIn("quantidade", form.errors)
        self.assertEqual(Distribuicao.objects.count(), 0)

    def test_registrar_distribuicao_data_futura_invalida(self):
        data_futura = timezone.localdate() + timedelta(days=1)
        response = self.client.post(
            reverse("distribuicao_create"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": "3",
                "data": data_futura.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("data", form.errors)
        self.assertEqual(Distribuicao.objects.count(), 0)

    def test_registrar_distribuicao_saldo_insuficiente_bloqueada(self):
        response = self.client.post(
            reverse("distribuicao_create"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": "11",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("Saldo insuficiente", str(form.errors))
        self.assertIn("10.00", str(form.errors))
        self.assertIn("11.00", str(form.errors))
        self.assertEqual(Distribuicao.objects.count(), 0)
        self.item.refresh_from_db()
        self.assertEqual(self.item.saldo_atual, Decimal("10"))

    def test_registrar_distribuicao_saldo_exatamente_igual_permitida(self):
        response = self.client.post(
            reverse("distribuicao_create"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": "10",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertRedirects(response, reverse("distribuicao_create"))
        self.assertEqual(Distribuicao.objects.count(), 1)
        self.item.refresh_from_db()
        self.assertEqual(self.item.saldo_atual, Decimal("0"))

    def test_registrar_distribuicao_acesso_anonimo_redireciona_para_login(self):
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("distribuicao_create"))
        self.assertRedirects(response, reverse("login"))

    def test_administrador_tambem_pode_registrar_distribuicao(self):
        self.client.get(reverse("logout"))
        self._login(self.admin)
        response = self.client.post(
            reverse("distribuicao_create"),
            {
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": "1",
                "data": timezone.localdate().isoformat(),
            },
        )
        self.assertRedirects(response, reverse("distribuicao_create"))
        self.assertEqual(Distribuicao.objects.count(), 1)

    def test_formulario_exibe_saldo_inline_na_opcao_do_item(self):
        response = self.client.get(reverse("distribuicao_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "saldo: 10.00")

    def test_contexto_da_view_contem_saldo_por_item(self):
        response = self.client.get(reverse("distribuicao_create"))
        self.assertEqual(response.status_code, 200)
        itens_saldo = response.context["itens_saldo"]
        self.assertEqual(itens_saldo[str(self.item.pk)]["saldo"], "10.00")
        self.assertEqual(itens_saldo[str(self.item.pk)]["unidade"], "kg")

    def test_formulario_abre_com_data_de_hoje_em_formato_iso(self):
        response = self.client.get(reverse("distribuicao_create"))
        self.assertContains(response, f'value="{timezone.localdate().isoformat()}"')

    def test_menu_lateral_tem_links_das_movimentacoes_e_dos_historicos(self):
        response = self.client.get(reverse("distribuicao_create"))
        for url_name in (
            "doacao_create",
            "doacao_list",
            "distribuicao_create",
            "distribuicao_list",
        ):
            self.assertContains(response, f'href="{reverse(url_name)}"')

    def test_submenu_de_movimentacoes_vem_fechado_fora_do_grupo(self):
        response = self.client.get(reverse("painel"))
        self.assertContains(response, "<details")
        self.assertNotContains(response, "<details open")

    def test_submenu_de_movimentacoes_abre_nas_paginas_do_grupo(self):
        response = self.client.get(reverse("distribuicao_list"))
        self.assertContains(response, "<details open")


class DoacaoListTestCase(TestCase):
    def test_totais_agrupam_por_identidade_do_doador_e_item(self):
        outro_item = Item.objects.create(
            nome=self.item.nome,
            categoria=self.item.categoria,
            unidade_medida=self.item.unidade_medida,
        )
        self.doador2.nome = self.doador1.nome
        self.doador2.save()
        for item, quantidade in [(self.item, "2.75"), (outro_item, "4.50")]:
            Doacao.objects.create(
                doador=self.doador1,
                item=item,
                registrado_por=self.voluntario,
                quantidade=Decimal(quantidade),
                data=date(2026, 1, 10),
            )
        response = self.client.get(reverse("doacao_list"))
        totais = {
            (linha["doador_id"], linha["item_id"]): linha["total"]
            for linha in response.context["totais_por_doador"]
        }
        self.assertEqual(
            totais,
            {
                (self.doador1.pk, self.item.pk): Decimal("7.75"),
                (self.doador1.pk, outro_item.pk): Decimal("4.50"),
                (self.doador2.pk, self.item.pk): Decimal("3"),
            },
        )
        self.assertContains(response, "Totais por doador e item")
        self.assertContains(response, "kgd")

    def test_totais_respeitam_doador_e_limites_inclusivos_do_periodo(self):
        response = self.client.get(
            reverse("doacao_list"),
            {
                "id_doador": self.doador1.pk,
                "data_inicio": "2026-01-10",
                "data_fim": "2026-01-10",
            },
        )
        totais = list(response.context["totais_por_doador"])
        self.assertEqual(len(totais), 1)
        self.assertEqual(totais[0]["total"], Decimal("5"))
        response = self.client.get(reverse("doacao_list"), {"data_inicio": "2027-01-01"})
        self.assertEqual(list(response.context["totais_por_doador"]), [])
        self.assertContains(response, "Nenhuma doação encontrada.")

    def test_totais_incluem_registros_de_todas_as_paginas(self):
        Doacao.objects.bulk_create(
            [
                Doacao(
                    doador=self.doador1,
                    item=self.item,
                    registrado_por=self.voluntario,
                    quantidade=Decimal("1.25"),
                    data=date(2026, 1, 10),
                )
                for _ in range(25)
            ]
        )
        filtros = {"id_doador": self.doador1.pk}
        for pagina in [1, 2]:
            response = self.client.get(reverse("doacao_list"), {**filtros, "page": pagina})
            totais = list(response.context["totais_por_doador"])
            self.assertEqual(len(totais), 1)
            self.assertEqual(totais[0]["total"], Decimal("36.25"))

    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Voluntario Historico",
            email="voluntario-historico@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.doador1 = Doador.objects.create(nome="Doador Um", cpf_cnpj="111.111.111-11")
        self.doador2 = Doador.objects.create(nome="Doador Dois", cpf_cnpj="222.222.222-22")
        categoria = CategoriaItem.objects.create(nome="Alimento Historico Doacao")
        unidade = UnidadeMedida.objects.create(nome="Quilograma Historico Doacao", sigla="kgd")
        self.item = Item.objects.create(
            nome="Feijão", categoria=categoria, unidade_medida=unidade, estoque_minimo=1
        )

        self.doacao_antiga = Doacao.objects.create(
            doador=self.doador1,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("5"),
            data=date(2026, 1, 10),
        )
        self.doacao_recente = Doacao.objects.create(
            doador=self.doador2,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("3"),
            data=date(2026, 3, 15),
        )
        self.doacao_cancelada = Doacao.objects.create(
            doador=self.doador1,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("100"),
            data=date(2026, 2, 1),
            cancelado=True,
        )
        self._login(self.voluntario)

    def _login(self, usuario, senha="senha-teste"):
        self.client.post(reverse("login"), {"email": usuario.email, "senha": senha})

    def test_lista_todas_as_doacoes_sem_filtro(self):
        response = self.client.get(reverse("doacao_list"))
        self.assertEqual(response.status_code, 200)
        doacoes = list(response.context["page_obj"])
        self.assertEqual(len(doacoes), 2)
        self.assertNotIn(self.doacao_cancelada, doacoes)

    def test_filtro_por_doador_isolado(self):
        response = self.client.get(reverse("doacao_list"), {"id_doador": self.doador1.pk})
        doacoes = list(response.context["page_obj"])
        self.assertEqual(doacoes, [self.doacao_antiga])

    def test_filtro_por_periodo_isolado(self):
        response = self.client.get(
            reverse("doacao_list"), {"data_inicio": "2026-03-01", "data_fim": "2026-03-31"}
        )
        doacoes = list(response.context["page_obj"])
        self.assertEqual(doacoes, [self.doacao_recente])

    def test_filtro_por_doador_e_periodo_combinados(self):
        response = self.client.get(
            reverse("doacao_list"),
            {
                "id_doador": self.doador1.pk,
                "data_inicio": "2026-01-01",
                "data_fim": "2026-01-31",
            },
        )
        doacoes = list(response.context["page_obj"])
        self.assertEqual(doacoes, [self.doacao_antiga])

    def test_filtro_com_data_invalida_e_ignorado_sem_erro_500(self):
        response = self.client.get(reverse("doacao_list"), {"data_inicio": "data-invalida"})
        self.assertEqual(response.status_code, 200)
        doacoes = list(response.context["page_obj"])
        self.assertEqual(len(doacoes), 2)

    def test_paginacao_lista_doacoes(self):
        for _ in range(25):
            Doacao.objects.create(
                doador=self.doador1,
                item=self.item,
                registrado_por=self.voluntario,
                quantidade=Decimal("1"),
                data=date(2026, 5, 1),
            )
        response = self.client.get(reverse("doacao_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].has_other_pages())
        self.assertEqual(len(response.context["page_obj"]), 20)

    def test_lista_doacoes_acesso_anonimo_redireciona_para_login(self):
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("doacao_list"))
        self.assertRedirects(response, reverse("login"))


class DistribuicaoListTestCase(TestCase):
    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Voluntario Historico Dist",
            email="voluntario-historico-dist@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.familia1 = Familia.objects.create(
            nome_responsavel="Família Um", endereco="Rua 1", num_membros=2
        )
        self.familia2 = Familia.objects.create(
            nome_responsavel="Família Dois", endereco="Rua 2", num_membros=3
        )
        categoria = CategoriaItem.objects.create(nome="Alimento Historico Distribuicao")
        unidade = UnidadeMedida.objects.create(
            nome="Quilograma Historico Distribuicao", sigla="kgt"
        )
        self.item = Item.objects.create(
            nome="Macarrão", categoria=categoria, unidade_medida=unidade, estoque_minimo=1
        )

        self.distribuicao_antiga = Distribuicao.objects.create(
            familia=self.familia1,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("2"),
            data=date(2026, 1, 5),
        )
        self.distribuicao_recente = Distribuicao.objects.create(
            familia=self.familia2,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("4"),
            data=date(2026, 3, 20),
        )
        self.distribuicao_cancelada = Distribuicao.objects.create(
            familia=self.familia1,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal("50"),
            data=date(2026, 2, 10),
            cancelado=True,
        )
        self._login(self.voluntario)

    def _login(self, usuario, senha="senha-teste"):
        self.client.post(reverse("login"), {"email": usuario.email, "senha": senha})

    def test_lista_todas_as_distribuicoes_sem_filtro(self):
        response = self.client.get(reverse("distribuicao_list"))
        self.assertEqual(response.status_code, 200)
        distribuicoes = list(response.context["page_obj"])
        self.assertEqual(len(distribuicoes), 2)
        self.assertNotIn(self.distribuicao_cancelada, distribuicoes)

    def test_filtro_por_familia_isolado(self):
        response = self.client.get(reverse("distribuicao_list"), {"id_familia": self.familia2.pk})
        distribuicoes = list(response.context["page_obj"])
        self.assertEqual(distribuicoes, [self.distribuicao_recente])

    def test_filtro_por_periodo_isolado(self):
        response = self.client.get(
            reverse("distribuicao_list"), {"data_inicio": "2026-01-01", "data_fim": "2026-01-31"}
        )
        distribuicoes = list(response.context["page_obj"])
        self.assertEqual(distribuicoes, [self.distribuicao_antiga])

    def test_filtro_por_familia_e_periodo_combinados(self):
        response = self.client.get(
            reverse("distribuicao_list"),
            {
                "id_familia": self.familia1.pk,
                "data_inicio": "2026-01-01",
                "data_fim": "2026-01-31",
            },
        )
        distribuicoes = list(response.context["page_obj"])
        self.assertEqual(distribuicoes, [self.distribuicao_antiga])

    def test_filtro_com_data_invalida_e_ignorado_sem_erro_500(self):
        response = self.client.get(reverse("distribuicao_list"), {"data_fim": "data-invalida"})
        self.assertEqual(response.status_code, 200)
        distribuicoes = list(response.context["page_obj"])
        self.assertEqual(len(distribuicoes), 2)

    def test_paginacao_lista_distribuicoes(self):
        for _ in range(25):
            Distribuicao.objects.create(
                familia=self.familia1,
                item=self.item,
                registrado_por=self.voluntario,
                quantidade=Decimal("1"),
                data=date(2026, 5, 1),
            )
        response = self.client.get(reverse("distribuicao_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].has_other_pages())
        self.assertEqual(len(response.context["page_obj"]), 20)

    def test_lista_distribuicoes_acesso_anonimo_redireciona_para_login(self):
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("distribuicao_list"))
        self.assertRedirects(response, reverse("login"))


class MovimentacoesComHtmxTests(TestCase):
    """Doação e distribuição em modal, históricos sem recarregar e escolha no painel."""

    HTMX = {"HTTP_HX_REQUEST": "true"}

    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Admin Teste",
            email="admin@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.doador = Doador.objects.create(nome="Mercado Central", cpf_cnpj="123.456.789-01")
        self.familia = Familia.objects.create(
            nome_responsavel="Ana Paula Ferreira", endereco="Rua A, 1", num_membros=4
        )
        self.item = Item.objects.create(
            nome="Arroz 5kg",
            categoria=CategoriaItem.objects.create(nome="Alimento"),
            unidade_medida=UnidadeMedida.objects.create(nome="Pacote", sigla="pct"),
            estoque_minimo=2,
        )
        self.client.force_login(self.admin)

    def _doar(self, quantidade, data=None):
        return Doacao.objects.create(
            doador=self.doador,
            item=self.item,
            registrado_por=self.admin,
            quantidade=Decimal(quantidade),
            data=data or timezone.localdate(),
        )

    def _dados(self, pessoa, **extras):
        return {
            pessoa[0]: pessoa[1],
            "item": self.item.pk,
            "quantidade": "3",
            "data": timezone.localdate().isoformat(),
            **extras,
        }

    def test_doacao_no_modal_com_item_ja_escolhido(self):
        response = self.client.get(reverse("doacao_create"), {"item": self.item.pk}, **self.HTMX)

        self.assertNotContains(response, "<html")
        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, "Registrar doação")
        self.assertContains(response, f'<option value="{self.item.pk}" selected>')
        self.assertNotContains(response, "Voltar")

    def test_registrar_doacao_no_modal_fecha_e_avisa_as_listas(self):
        response = self.client.post(
            reverse("doacao_create"), self._dados(("doador", self.doador.pk)), **self.HTMX
        )

        self.assertEqual(response["HX-Trigger"], "registro-salvo")
        self.assertContains(response, "Doação registrada com sucesso!")
        self.assertEqual(self.item.saldo_atual, Decimal("3"))

    def test_distribuicao_no_modal_mostra_saldo_e_aviso(self):
        self._doar("10")

        response = self.client.get(
            reverse("distribuicao_create"), {"familia": self.familia.pk}, **self.HTMX
        )

        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, 'id="distribuicao-itens-saldo"')
        self.assertContains(response, 'id="distribuicao-form-aviso-saldo"')
        self.assertContains(response, f'<option value="{self.familia.pk}" selected>')

    def test_distribuicao_acima_do_saldo_continua_no_modal(self):
        self._doar("2")

        response = self.client.post(
            reverse("distribuicao_create"),
            self._dados(("familia", self.familia.pk), quantidade="5"),
            **self.HTMX,
        )

        self.assertNotIn("HX-Trigger", response)
        self.assertContains(response, 'id="modal-titulo"')
        self.assertFalse(Distribuicao.objects.exists())

    def test_escolha_de_movimentacao(self):
        response = self.client.get(reverse("movimentacao_nova"))
        self.assertContains(response, 'id="sidebar"')
        self.assertContains(response, f'href="{reverse("doacao_create")}"')
        self.assertContains(response, f'href="{reverse("distribuicao_create")}"')

        response = self.client.get(reverse("movimentacao_nova"), **self.HTMX)
        self.assertNotContains(response, "<html")
        self.assertContains(response, 'id="modal-titulo"')
        self.assertContains(response, f'hx-get="{reverse("doacao_create")}?escolha=1"')

    def test_formulario_aberto_pela_escolha_tem_voltar(self):
        response = self.client.get(reverse("doacao_create"), {"escolha": "1"}, **self.HTMX)

        self.assertContains(response, f'hx-get="{reverse("movimentacao_nova")}"')
        self.assertContains(response, "Voltar")
        self.assertContains(response, f'hx-post="{reverse("doacao_create")}?escolha=1"')

    def test_painel_abre_a_escolha_no_modal_e_se_atualiza(self):
        response = self.client.get(reverse("painel"))

        self.assertContains(response, f'hx-get="{reverse("movimentacao_nova")}"')
        self.assertContains(response, 'hx-trigger="registro-salvo from:body"')

    def test_atalhos_das_listas_abrem_o_modal(self):
        response = self.client.get(reverse("item_list"))
        self.assertContains(response, f'hx-get="{reverse("doacao_create")}?item={self.item.pk}"')
        self.assertContains(
            response, f'hx-get="{reverse("distribuicao_create")}?item={self.item.pk}"'
        )

        response = self.client.get(reverse("familia_list"))
        self.assertContains(
            response, f'hx-get="{reverse("distribuicao_create")}?familia={self.familia.pk}"'
        )

    def test_historico_de_doacoes_com_htmx_devolve_so_o_card(self):
        self._doar("4")

        response = self.client.get(reverse("doacao_list"), **self.HTMX)

        self.assertContains(response, 'id="doacao-card"')
        self.assertContains(response, "1 doação")
        self.assertNotContains(response, 'id="sidebar"')
        self.assertIn("HX-Request", response["Vary"])

    def test_atalho_este_mes_preenche_o_periodo(self):
        hoje = timezone.localdate()
        self._doar("4", data=hoje.replace(day=1))
        self._doar("6", data=hoje.replace(day=1) - timedelta(days=1))

        response = self.client.get(reverse("doacao_list"), {"periodo": "mes"})

        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertEqual(response.context["data_inicio"], hoje.replace(day=1).isoformat())
        self.assertEqual(response.context["data_fim"], hoje.isoformat())
        self.assertContains(response, 'value="mes" aria-pressed="true"')
        self.assertContains(response, "Limpar filtros")

    def test_historico_de_distribuicoes_exporta_com_os_filtros_atuais(self):
        response = self.client.get(
            reverse("distribuicao_list"), {"id_familia": self.familia.pk}, **self.HTMX
        )

        self.assertContains(response, 'id="distribuicao-card"')
        self.assertContains(
            response, f'href="{reverse("distribuicao_exportar_csv")}?id_familia={self.familia.pk}'
        )
        self.assertContains(response, "Nenhuma distribuição encontrada.")


class PainelTests(TestCase):
    HOJE = date(2026, 10, 15)

    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        self.admin = Usuario.objects.create(
            nome="Ana Admin",
            email="ana@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.doador = Doador.objects.create(nome="João Doador", cpf_cnpj="123.456.789-00")
        self.familia = Familia.objects.create(
            nome_responsavel="Família Silva", endereco="Rua A, 123", num_membros=4
        )
        self.alimento = CategoriaItem.objects.create(nome="Alimento")
        self.kg = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.pct = UnidadeMedida.objects.create(nome="Pacote", sigla="pct")

    def _item(self, nome, minimo=0, unidade=None, categoria=None):
        return Item.objects.create(
            nome=nome,
            categoria=categoria or self.alimento,
            unidade_medida=unidade or self.kg,
            estoque_minimo=minimo,
        )

    def _doar(self, item, quantidade, data=None, cancelado=False):
        return Doacao.objects.create(
            doador=self.doador,
            item=item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data or self.HOJE,
            cancelado=cancelado,
        )

    def _distribuir(self, item, quantidade, data=None, cancelado=False):
        return Distribuicao.objects.create(
            familia=self.familia,
            item=item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data or self.HOJE,
            cancelado=cancelado,
        )

    def _categoria(self, resumo, nome):
        return next(c for c in resumo["categorias"] if c["nome"] == nome)

    def test_ct15_total_da_categoria_soma_os_saldos_e_reflete_movimentacao(self):
        arroz = self._item("Arroz")
        self._doar(arroz, 10)
        self._doar(self._item("Feijão"), 20)
        self._doar(self._item("Milho"), 30)

        alimento = self._categoria(montar_resumo(self.HOJE), "Alimento")
        self.assertEqual([(t["quantidade"], t["sigla"]) for t in alimento["totais"]], [(60, "kg")])

        self._distribuir(arroz, 5)
        alimento = self._categoria(montar_resumo(self.HOJE), "Alimento")
        self.assertEqual([(t["quantidade"], t["sigla"]) for t in alimento["totais"]], [(55, "kg")])

    def test_categoria_com_unidades_diferentes_mostra_totais_separados(self):
        self._doar(self._item("Arroz", unidade=self.kg), 50)
        self._doar(self._item("Biscoito", unidade=self.pct), 12)

        alimento = self._categoria(montar_resumo(self.HOJE), "Alimento")

        self.assertEqual(
            [(t["quantidade"], t["sigla"]) for t in alimento["totais"]], [(50, "kg"), (12, "pct")]
        )

    def test_movimentacoes_canceladas_nao_entram_no_saldo(self):
        arroz = self._item("Arroz", minimo=5)
        self._doar(arroz, 20)
        self._doar(arroz, 100, cancelado=True)
        self._distribuir(arroz, 8, cancelado=True)

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(self._categoria(resumo, "Alimento")["totais"][0]["quantidade"], 20)
        self.assertEqual(resumo["itens_em_alerta"], 0)

    def test_pontos_de_atencao_listam_ate_cinco_itens_do_menor_saldo(self):
        for indice in range(7):
            self._doar(self._item(f"Item {indice}", minimo=10), 9 - indice)
        self._doar(self._item("Folgado", minimo=10), 50)

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(resumo["itens_em_alerta"], 7)
        self.assertEqual(
            [item.nome for item in resumo["pontos_de_atencao"]],
            ["Item 6", "Item 5", "Item 4", "Item 3", "Item 2"],
        )

    def test_saldo_igual_ao_minimo_conta_como_alerta(self):
        self._doar(self._item("Sabonete", minimo=20), 20)

        self.assertEqual(montar_resumo(self.HOJE)["itens_em_alerta"], 1)

    def test_percentual_de_itens_acima_do_minimo_por_categoria(self):
        self._doar(self._item("Arroz", minimo=5), 10)
        self._doar(self._item("Feijão", minimo=5), 10)
        self._doar(self._item("Milho", minimo=5), 10)
        self._doar(self._item("Leite", minimo=5), 2)
        CategoriaItem.objects.create(nome="Higiene")

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(self._categoria(resumo, "Alimento")["percentual_acima_minimo"], 75)
        higiene = self._categoria(resumo, "Higiene")
        self.assertEqual((higiene["quantidade_itens"], higiene["percentual_acima_minimo"]), (0, 0))
        self.assertEqual(higiene["totais"], [])

    def test_variacao_de_itens_em_estoque_compara_com_o_fim_do_mes_anterior(self):
        arroz = self._item("Arroz")
        self._doar(arroz, 10, data=date(2026, 9, 30))
        self._doar(self._item("Feijão"), 5, data=date(2026, 10, 2))
        self._doar(self._item("Milho"), 5, data=date(2026, 10, 3))

        resumo = montar_resumo(self.HOJE)
        self.assertEqual((resumo["itens_em_estoque"], resumo["variacao_itens_em_estoque"]), (3, 2))
        self.assertEqual(resumo["texto_variacao"], "+2 este mês")

        self._distribuir(arroz, 10, data=date(2026, 10, 4))
        self._distribuir(Item.objects.get(nome="Feijão"), 5, data=date(2026, 10, 5))
        self._distribuir(Item.objects.get(nome="Milho"), 5, data=date(2026, 10, 6))
        resumo = montar_resumo(self.HOJE)
        self.assertEqual(resumo["texto_variacao"], "−1 este mês")

    def test_sem_variacao(self):
        self.assertEqual(montar_resumo(self.HOJE)["texto_variacao"], "Sem variação este mês")

    def test_saudacao_pela_hora(self):
        self.assertEqual(
            [saudacao(hora) for hora in (4, 5, 11, 12, 17, 18, 23)],
            ["Boa noite", "Bom dia", "Bom dia", "Boa tarde", "Boa tarde", "Boa noite", "Boa noite"],
        )

    def test_voluntario_e_administrador_acessam_o_painel(self):
        for usuario in (self.voluntario, self.admin):
            with self.subTest(perfil=usuario.perfil):
                self.client.force_login(usuario)
                response = self.client.get(reverse("painel"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, usuario.nome.split()[0])

    def test_ver_todos_abre_os_itens_em_alerta(self):
        self._item("Leite em pó", minimo=10)
        self.client.force_login(self.voluntario)

        response = self.client.get(reverse("painel"))

        self.assertContains(response, f'href="{reverse("item_list")}?estoque=baixo"')

    def test_painel_renderiza_categorias_alertas_e_atalhos(self):
        self._doar(self._item("Arroz"), 60)
        self._doar(self._item("Leite em pó", minimo=10, unidade=self.pct), 4)
        self.client.force_login(self.voluntario)

        response = self.client.get(reverse("painel"))

        self.assertContains(response, "Estoque por categoria")
        self.assertContains(response, "60 kg")
        self.assertContains(response, "Leite em pó — 4 pct")
        self.assertContains(response, f'href="{reverse("item_list")}"')
        self.assertContains(response, f'href="{reverse("distribuicao_create")}"')

    def test_painel_com_banco_vazio(self):
        CategoriaItem.objects.all().delete()
        self.client.force_login(self.admin)

        response = self.client.get(reverse("painel"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum item no estoque mínimo.")

    def test_numero_de_consultas_nao_cresce_com_os_itens(self):
        self.client.force_login(self.voluntario)

        def consultas():
            with CaptureQueriesContext(connection) as contexto:
                self.client.get(reverse("painel"))
            return len(contexto)

        self._doar(self._item("Item 0", minimo=1), 3)
        com_um_item = consultas()
        for indice in range(1, 10):
            self._doar(self._item(f"Item {indice}", minimo=5), indice)

        self.assertEqual(consultas(), com_um_item)
        with self.assertNumQueries(6):
            montar_resumo(self.HOJE)


class LayoutBaseTests(SimpleTestCase):
    """Garante o padrão de layout: toda tela herda CSS compilado e transições dos bases."""

    TEMPLATES_BASE = ("base.html", "auth_base.html", "dashboard_base.html")

    def test_toda_pagina_estende_um_template_base(self):
        extends_validos = tuple(f'{{% extends "{nome}" %}}' for nome in self.TEMPLATES_BASE)
        paginas = sorted((settings.BASE_DIR / "templates" / "core").glob("*.html"))

        self.assertTrue(paginas)
        for pagina in paginas:
            with self.subTest(pagina=pagina.name):
                conteudo = pagina.read_text(encoding="utf-8")
                self.assertTrue(any(e in conteudo for e in extends_validos))

    def test_templates_base_carregam_css_compilado_e_app_css(self):
        for nome in self.TEMPLATES_BASE:
            with self.subTest(template=nome):
                conteudo = (settings.BASE_DIR / "templates" / nome).read_text(encoding="utf-8")
                self.assertIn("css/tailwind.css", conteudo)
                self.assertIn("css/app.css", conteudo)
                self.assertLess(conteudo.index("css/tailwind.css"), conteudo.index("css/app.css"))
                self.assertNotIn("cdn.tailwindcss.com", conteudo)
                self.assertNotIn("daisyui", conteudo)

    def test_painel_carrega_htmx_local_e_o_modal_compartilhado(self):
        conteudo = (settings.BASE_DIR / "templates" / "dashboard_base.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("js/htmx.min.js", conteudo)
        self.assertIn('<dialog id="modal"', conteudo)
        self.assertNotIn("unpkg.com", conteudo)

    def test_bases_com_formulario_travam_o_botao_de_envio(self):
        for nome in ("auth_base.html", "dashboard_base.html"):
            with self.subTest(template=nome):
                conteudo = (settings.BASE_DIR / "templates" / nome).read_text(encoding="utf-8")
                self.assertIn("js/formularios.js", conteudo)

    def test_app_css_ativa_view_transition(self):
        conteudo = (settings.BASE_DIR / "static" / "css" / "app.css").read_text(encoding="utf-8")

        self.assertIn("@view-transition", conteudo)
        self.assertIn("navigation: auto", conteudo)
        self.assertIn("prefers-reduced-motion", conteudo)

    def test_storage_de_producao_e_whitenoise_manifest(self):
        caminho_settings = settings.BASE_DIR / "conecta" / "settings.py"
        with mock.patch.object(sys, "argv", ["manage.py", "runserver"]):
            config = runpy.run_path(str(caminho_settings))

        self.assertEqual(
            config["STORAGES"]["staticfiles"]["BACKEND"],
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )


class LayoutRenderizadoTests(TestCase):
    def test_pagina_renderizada_usa_css_compilado(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "/static/css/tailwind.css")
        self.assertNotContains(response, "cdn.tailwindcss.com")


class DistribuicaoRelatorioTestCase(TestCase):
    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Voluntário Teste",
            email="vol2@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "vol2@conectasocial.org", "senha": "senha-teste"},
        )
        self.familia1 = Familia.objects.create(
            nome_responsavel="Família Silva", endereco="Rua A, 123", num_membros=4
        )
        self.familia2 = Familia.objects.create(
            nome_responsavel="Família Souza", endereco="Rua B, 456", num_membros=3
        )

        self.cat = CategoriaItem.objects.create(nome="Alimento")
        self.un = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.item1 = Item.objects.create(nome="Arroz", categoria=self.cat, unidade_medida=self.un)
        self.item2 = Item.objects.create(nome="Feijão", categoria=self.cat, unidade_medida=self.un)

        self.doador = Doador.objects.create(nome="Doador X", cpf_cnpj="111.111.111-11")
        Doacao.objects.create(
            doador=self.doador,
            item=self.item1,
            quantidade=Decimal("100.00"),
            data=timezone.localdate() - timedelta(days=10),
            registrado_por=self.voluntario,
        )
        Doacao.objects.create(
            doador=self.doador,
            item=self.item2,
            quantidade=Decimal("100.00"),
            data=timezone.localdate() - timedelta(days=10),
            registrado_por=self.voluntario,
        )

        self.hoje = timezone.localdate()
        self.semana_passada = self.hoje - timedelta(days=7)

        Distribuicao.objects.create(
            familia=self.familia1,
            item=self.item1,
            quantidade=Decimal("5.00"),
            data=self.hoje,
            registrado_por=self.voluntario,
        )
        Distribuicao.objects.create(
            familia=self.familia1,
            item=self.item1,
            quantidade=Decimal("3.00"),
            data=self.hoje,
            registrado_por=self.voluntario,
        )
        Distribuicao.objects.create(
            familia=self.familia1,
            item=self.item2,
            quantidade=Decimal("4.00"),
            data=self.hoje,
            registrado_por=self.voluntario,
        )
        Distribuicao.objects.create(
            familia=self.familia2,
            item=self.item1,
            quantidade=Decimal("10.00"),
            data=self.semana_passada,
            registrado_por=self.voluntario,
        )

    def linhas(self, **filtros):
        response = self.client.get(reverse("distribuicao_relatorio"), filtros)
        self.assertEqual(response.status_code, 200)
        return [
            (
                linha["familia__nome_responsavel"],
                linha["item__nome"],
                linha["quantidade_total"],
                linha["numero_distribuicoes"],
            )
            for linha in response.context["linhas"]
        ]

    def test_relatorio_distribuicoes_agrupa_por_familia_e_item(self):
        self.assertEqual(
            self.linhas(),
            [
                ("Família Silva", "Arroz", Decimal("8.00"), 2),
                ("Família Silva", "Feijão", Decimal("4.00"), 1),
                ("Família Souza", "Arroz", Decimal("10.00"), 1),
            ],
        )
        response = self.client.get(reverse("distribuicao_relatorio"))
        self.assertContains(response, "Alimento")
        self.assertContains(response, "8 kg")

    def test_ct16_relatorio_distribuicoes_filtra_por_periodo(self):
        linhas = self.linhas(data_inicio=self.hoje.isoformat(), data_fim=self.hoje.isoformat())
        self.assertEqual([linha[0] for linha in linhas], ["Família Silva", "Família Silva"])

    def test_ct17_relatorio_distribuicoes_filtra_por_familia(self):
        linhas = self.linhas(id_familia=str(self.familia2.id_familia))
        self.assertEqual(linhas, [("Família Souza", "Arroz", Decimal("10.00"), 1)])

    def test_relatorio_distribuicoes_filtra_combinado(self):
        filtros = {
            "id_familia": str(self.familia2.id_familia),
            "data_inicio": self.semana_passada.isoformat(),
            "data_fim": self.semana_passada.isoformat(),
        }
        self.assertEqual(self.linhas(**filtros), [("Família Souza", "Arroz", Decimal("10.00"), 1)])
        filtros["data_inicio"] = filtros["data_fim"] = self.hoje.isoformat()
        self.assertEqual(self.linhas(**filtros), [])

    def test_relatorio_distribuicoes_acesso_anonimo_redireciona(self):
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("distribuicao_relatorio"))
        self.assertRedirects(response, reverse("login"))

    def test_ultimo_registro_e_a_data_mais_recente_do_grupo(self):
        Distribuicao.objects.create(
            familia=self.familia2,
            item=self.item1,
            quantidade=Decimal("1.00"),
            data=self.semana_passada - timedelta(days=3),
            registrado_por=self.voluntario,
        )
        response = self.client.get(
            reverse("distribuicao_relatorio"), {"id_familia": str(self.familia2.id_familia)}
        )
        [linha] = response.context["linhas"]
        self.assertEqual(linha["ultimo_registro"], self.semana_passada)
        self.assertEqual(linha["numero_distribuicoes"], 2)
        self.assertContains(response, self.semana_passada.strftime("%d/%m/%Y"))

    def test_distribuicao_cancelada_fica_fora_do_relatorio(self):
        Distribuicao.objects.create(
            familia=self.familia2,
            item=self.item2,
            quantidade=Decimal("7.00"),
            data=self.hoje,
            registrado_por=self.voluntario,
            cancelado=True,
        )
        self.assertNotIn(("Família Souza", "Feijão", Decimal("7.00"), 1), self.linhas())
        response = self.client.get(reverse("distribuicao_relatorio"))
        self.assertEqual(response.context["resumo"]["numero_distribuicoes"], 4)

    def test_resumo_soma_por_unidade_e_conta_familias_e_distribuicoes(self):
        pacote = UnidadeMedida.objects.create(nome="Pacote", sigla="pct")
        macarrao = Item.objects.create(nome="Macarrão", categoria=self.cat, unidade_medida=pacote)
        Doacao.objects.create(
            doador=self.doador,
            item=macarrao,
            quantidade=Decimal("10.00"),
            data=self.semana_passada,
            registrado_por=self.voluntario,
        )
        Distribuicao.objects.create(
            familia=self.familia2,
            item=macarrao,
            quantidade=Decimal("2.00"),
            data=self.hoje,
            registrado_por=self.voluntario,
        )
        response = self.client.get(reverse("distribuicao_relatorio"))
        self.assertEqual(response.context["resumo"]["familias_atendidas"], 2)
        self.assertEqual(response.context["resumo"]["numero_distribuicoes"], 5)
        self.assertContains(response, "22 kg · 2 pct")

    def test_filtros_invalidos_sao_ignorados(self):
        for filtros in (
            {"id_familia": "abc"},
            {"data_inicio": "2026-02-30"},
            {"data_fim": "ontem"},
        ):
            with self.subTest(filtros=filtros):
                self.assertEqual(len(self.linhas(**filtros)), 3)

    def test_relatorio_sem_distribuicoes(self):
        Distribuicao.objects.all().delete()
        response = self.client.get(reverse("distribuicao_relatorio"))
        self.assertContains(response, "Nenhuma distribuição encontrada")
        self.assertEqual(response.context["resumo"]["familias_atendidas"], 0)

    def test_administrador_acessa_o_relatorio(self):
        Usuario.objects.create(
            nome="Admin Teste",
            email="admin2@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.client.post(
            reverse("login"), {"email": "admin2@conectasocial.org", "senha": "senha-teste"}
        )
        self.assertEqual(self.client.get(reverse("distribuicao_relatorio")).status_code, 200)

    def test_exportar_csv_leva_os_filtros_do_relatorio(self):
        response = self.client.get(
            reverse("distribuicao_relatorio"),
            {"id_familia": str(self.familia2.id_familia), "data_inicio": "2026-01-01"},
        )
        self.assertContains(
            response,
            f"{reverse('distribuicao_exportar_csv')}?id_familia={self.familia2.id_familia}"
            "&data_inicio=2026-01-01&data_fim=",
        )

    def test_numero_de_consultas_nao_cresce_com_as_linhas(self):
        with CaptureQueriesContext(connection) as poucas:
            self.client.get(reverse("distribuicao_relatorio"))
        for indice in range(10):
            item = Item.objects.create(
                nome=f"Item {indice}", categoria=self.cat, unidade_medida=self.un
            )
            Distribuicao.objects.create(
                familia=self.familia1,
                item=item,
                quantidade=Decimal("1.00"),
                data=self.hoje,
                registrado_por=self.voluntario,
            )
        with CaptureQueriesContext(connection) as muitas:
            self.client.get(reverse("distribuicao_relatorio"))
        self.assertEqual(len(poucas), len(muitas))

    def test_menu_lateral_tem_o_relatorio_aberto_no_grupo_de_movimentacoes(self):
        response = self.client.get(reverse("distribuicao_relatorio"))
        self.assertContains(response, f'href="{reverse("distribuicao_relatorio")}"')
        self.assertContains(response, "<details open")


class FiltrosInvalidosTests(TestCase):
    def setUp(self):
        Usuario.objects.create(
            nome="Voluntário Filtro",
            email="filtro@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.post(
            reverse("login"), {"email": "filtro@conectasocial.org", "senha": "senha-teste"}
        )

    def test_pessoa_e_data_invalidas_nao_derrubam_as_listas(self):
        for url_name, parametro in (
            ("doacao_list", "id_doador"),
            ("distribuicao_list", "id_familia"),
            ("distribuicao_exportar_csv", "id_familia"),
        ):
            with self.subTest(url_name=url_name):
                response = self.client.get(
                    reverse(url_name), {parametro: "abc", "data_inicio": "2026-02-30"}
                )
                self.assertEqual(response.status_code, 200)


class SchemaBancoTests(TestCase):
    """O banco criado pelas migrations precisa bater com o db/schema.sql da E3."""

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Voluntário Schema",
            email="schema@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        categoria = CategoriaItem.objects.create(nome="Alimento")
        unidade = UnidadeMedida.objects.create(nome="Pacote", sigla="pct")
        self.item = Item.objects.create(
            nome="Arroz 5kg", categoria=categoria, unidade_medida=unidade
        )
        self.doador = Doador.objects.create(nome="Doador Schema", cpf_cnpj="123.456.789-00")
        self.familia = Familia.objects.create(
            nome_responsavel="Família Schema", endereco="Rua A, 1", num_membros=2
        )

    def assertBancoRecusa(self, model, **campos):
        with self.assertRaises(IntegrityError), transaction.atomic():
            model.objects.create(**campos)

    def test_colunas_das_migrations_iguais_ao_schema_sql(self):
        ddl = (settings.BASE_DIR / "db" / "schema.sql").read_text(encoding="utf-8")
        for model in (
            Usuario,
            Doador,
            Familia,
            CategoriaItem,
            UnidadeMedida,
            Item,
            Doacao,
            Distribuicao,
        ):
            tabela = model._meta.db_table
            with self.subTest(tabela=tabela):
                bloco = re.search(rf"CREATE TABLE {tabela} \((.*?)\n\);", ddl, re.S)
                self.assertIsNotNone(bloco, f"tabela {tabela} não está no schema.sql")
                colunas_ddl = {linha.split()[0] for linha in bloco.group(1).strip().splitlines()}
                colunas_model = {campo.column for campo in model._meta.concrete_fields}
                self.assertEqual(colunas_model, colunas_ddl)

    def test_banco_recusa_movimentacao_com_quantidade_menor_ou_igual_a_zero(self):
        for quantidade in (Decimal("0"), Decimal("-1")):
            with self.subTest(quantidade=quantidade):
                self.assertBancoRecusa(
                    Doacao,
                    doador=self.doador,
                    item=self.item,
                    registrado_por=self.usuario,
                    quantidade=quantidade,
                    data=date.today(),
                )
                self.assertBancoRecusa(
                    Distribuicao,
                    familia=self.familia,
                    item=self.item,
                    registrado_por=self.usuario,
                    quantidade=quantidade,
                    data=date.today(),
                )

    def test_banco_recusa_familia_sem_membros(self):
        self.assertBancoRecusa(
            Familia, nome_responsavel="Família Vazia", endereco="Rua B, 2", num_membros=0
        )

    def test_banco_recusa_perfil_fora_dos_dois_perfis(self):
        self.assertBancoRecusa(
            Usuario,
            nome="Perfil Inválido",
            email="gestor@conectasocial.org",
            password=make_password("senha-teste"),
            perfil="gestor",
        )
