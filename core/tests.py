from django.contrib.auth import SESSION_KEY, authenticate
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from core.forms import UsuarioForm
from core.models import Usuario


class CoreSmokeTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conecta Social")

    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})


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
