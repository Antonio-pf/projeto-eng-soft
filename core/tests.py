import runpy
import sys
from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.contrib.auth import SESSION_KEY, authenticate
from django.contrib.auth.hashers import make_password
from django.db import connection
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
        return next(c for c in resumo.categorias if c.nome == nome)

    def test_ct15_total_da_categoria_soma_os_saldos_e_reflete_movimentacao(self):
        arroz = self._item("Arroz")
        self._doar(arroz, 10)
        self._doar(self._item("Feijão"), 20)
        self._doar(self._item("Milho"), 30)

        alimento = self._categoria(montar_resumo(self.HOJE), "Alimento")
        self.assertEqual([(t.quantidade, t.sigla) for t in alimento.totais], [(60, "kg")])

        self._distribuir(arroz, 5)
        alimento = self._categoria(montar_resumo(self.HOJE), "Alimento")
        self.assertEqual([(t.quantidade, t.sigla) for t in alimento.totais], [(55, "kg")])

    def test_categoria_com_unidades_diferentes_mostra_totais_separados(self):
        self._doar(self._item("Arroz", unidade=self.kg), 50)
        self._doar(self._item("Biscoito", unidade=self.pct), 12)

        alimento = self._categoria(montar_resumo(self.HOJE), "Alimento")

        self.assertEqual(
            [(t.quantidade, t.sigla) for t in alimento.totais], [(50, "kg"), (12, "pct")]
        )

    def test_movimentacoes_canceladas_nao_entram_no_saldo(self):
        arroz = self._item("Arroz", minimo=5)
        self._doar(arroz, 20)
        self._doar(arroz, 100, cancelado=True)
        self._distribuir(arroz, 8, cancelado=True)

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(self._categoria(resumo, "Alimento").totais[0].quantidade, 20)
        self.assertEqual(resumo.itens_em_alerta, 0)

    def test_pontos_de_atencao_listam_ate_cinco_itens_do_menor_saldo(self):
        for indice in range(7):
            self._doar(self._item(f"Item {indice}", minimo=10), 9 - indice)
        self._doar(self._item("Folgado", minimo=10), 50)

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(resumo.itens_em_alerta, 7)
        self.assertEqual(
            [item.nome for item in resumo.pontos_de_atencao],
            ["Item 6", "Item 5", "Item 4", "Item 3", "Item 2"],
        )

    def test_saldo_igual_ao_minimo_conta_como_alerta(self):
        self._doar(self._item("Sabonete", minimo=20), 20)

        self.assertEqual(montar_resumo(self.HOJE).itens_em_alerta, 1)

    def test_percentual_de_itens_acima_do_minimo_por_categoria(self):
        self._doar(self._item("Arroz", minimo=5), 10)
        self._doar(self._item("Feijão", minimo=5), 10)
        self._doar(self._item("Milho", minimo=5), 10)
        self._doar(self._item("Leite", minimo=5), 2)
        CategoriaItem.objects.create(nome="Higiene")

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(self._categoria(resumo, "Alimento").percentual_acima_minimo, 75)
        higiene = self._categoria(resumo, "Higiene")
        self.assertEqual((higiene.quantidade_itens, higiene.percentual_acima_minimo), (0, 0))
        self.assertEqual(higiene.totais, ())

    def test_variacao_de_itens_em_estoque_compara_com_o_fim_do_mes_anterior(self):
        arroz = self._item("Arroz")
        self._doar(arroz, 10, data=date(2026, 9, 30))
        self._doar(self._item("Feijão"), 5, data=date(2026, 10, 2))
        self._doar(self._item("Milho"), 5, data=date(2026, 10, 3))

        resumo = montar_resumo(self.HOJE)
        self.assertEqual((resumo.itens_em_estoque, resumo.variacao_itens_em_estoque), (3, 2))
        self.assertEqual(resumo.texto_variacao, "+2 este mês")

        self._distribuir(arroz, 10, data=date(2026, 10, 4))
        self._distribuir(Item.objects.get(nome="Feijão"), 5, data=date(2026, 10, 5))
        self._distribuir(Item.objects.get(nome="Milho"), 5, data=date(2026, 10, 6))
        resumo = montar_resumo(self.HOJE)
        self.assertEqual(resumo.texto_variacao, "−1 este mês")

    def test_sem_variacao(self):
        self.assertEqual(montar_resumo(self.HOJE).texto_variacao, "Sem variação este mês")

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
