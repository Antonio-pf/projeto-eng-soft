import csv
import io
import os
import re
import runpy
import subprocess
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.contrib.auth import SESSION_KEY, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.contrib.staticfiles import finders
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from core.forms import DistribuicaoForm, DoacaoForm, FamiliaForm, ItemForm, UsuarioForm
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
from core.painel import (
    montar_resumo,
    movimentacoes_recentes,
    periodo_equivalente_do_mes_anterior,
    saudacao,
    texto_variacao_mes_anterior,
)
from core.privacidade import (
    CONTATO_PADRAO,
    FINALIDADES,
    NOME_ANONIMIZADO,
    NOME_ONG_PADRAO,
    controlador,
    data_limite,
    mascarar_documento,
)
from core.views import _celula_csv


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

    # CT41 (#28): foto do GitHub de quem tem, iniciais de quem não tem e link para o perfil.
    COM_FOTO = (
        ("Antonio-pf", "Antonio Pires Felipe"),
        ("luiz-Henrique-neres", "Luiz Henrique Neres"),
    )
    SEM_FOTO = (
        ("viktoralex321", "Alexandre Victoriano Ribeiro Ulhoa", "AU"),
        ("DanielSouzaMC", "Daniel Souza Monteiro de Carvalho", "DC"),
    )

    def test_ct41_quem_tem_foto_aparece_com_a_foto_servida_pelo_sistema(self):
        response = self.client.get(reverse("home"))

        for login, nome in self.COM_FOTO:
            with self.subTest(login=login):
                self.assertContains(
                    response, f'src="/static/img/equipe/{login}.jpg" alt="Foto de {nome}"'
                )
                self.assertIsNotNone(finders.find(f"img/equipe/{login}.jpg"))
        self.assertNotContains(response, 'src="https://')

    def test_ct41_quem_nao_tem_foto_continua_com_as_iniciais(self):
        response = self.client.get(reverse("home"))

        for login, nome, iniciais in self.SEM_FOTO:
            with self.subTest(login=login):
                self.assertContains(response, f'aria-hidden="true">{iniciais}</span>')
                self.assertNotContains(response, f"Foto de {nome}")
                self.assertNotContains(response, f"img/equipe/{login}")
        self.assertNotContains(response, 'aria-hidden="true">AF</span>')
        self.assertNotContains(response, 'aria-hidden="true">LN</span>')

    def test_ct41_cartoes_levam_ao_perfil_do_github_em_nova_aba(self):
        response = self.client.get(reverse("home"))

        logins = [login for login, _ in self.COM_FOTO] + [login for login, *_ in self.SEM_FOTO]
        for login in logins:
            with self.subTest(login=login):
                self.assertContains(
                    response,
                    f'href="https://github.com/{login}" target="_blank" rel="noopener noreferrer"',
                )
                self.assertContains(response, f"@{login}")

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

    def test_painel_da_marca_mostra_o_fio_do_doador_a_familia(self):
        response = self.client.get(reverse("login"))

        self.assertContains(response, "Do doador à família, sem perder o fio.")
        # O fio é decorativo: o leitor de tela lê só a frase.
        self.assertRegex(
            response.content.decode(), r'data-testid="fio-conecta"[^>]*aria-hidden="true"'
        )
        self.assertNotContains(response, "Equipe Conecta")
        self.assertContains(response, f'href="{reverse("privacidade")}"')

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
        self.assertContains(response, "Ana Pereira")
        # CPF/CNPJ mascarado na lista (#25, CT37): só os 4 últimos dígitos aparecem.
        self.assertContains(response, "***.***.*11-11")
        self.assertContains(response, "***.***.*22-22")
        self.assertNotContains(response, "111.111.111-11")

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

    def test_ct08_lista_de_familias_exibe_responsavel_endereco_e_membros(self):
        Familia.objects.create(
            nome_responsavel="Ana Pereira", endereco="Rua das Flores, 45", num_membros=5
        )

        response = self.client.get(reverse("familia_list"))

        for coluna in ("Responsável", "Endereço", "Membros"):
            self.assertContains(response, f'<th class="px-4 py-3 font-semibold">{coluna}</th>')
        self.assertContains(response, "Ana Pereira")
        self.assertContains(response, "Rua das Flores, 45")
        self.assertContains(response, "5 membros")

    def test_ct08_lista_de_familias_tem_no_maximo_20_por_pagina(self):
        for indice in range(25):
            Familia.objects.create(
                nome_responsavel=f"Família {indice:02d}", endereco="Rua 1", num_membros=1
            )

        pagina_1 = self.client.get(reverse("familia_list"))
        pagina_2 = self.client.get(reverse("familia_list"), {"page": 2})

        self.assertEqual(len(pagina_1.context["page_obj"]), 20)
        self.assertTrue(pagina_1.context["page_obj"].has_next())
        self.assertEqual(len(pagina_2.context["page_obj"]), 5)
        self.assertFalse(pagina_2.context["page_obj"].has_next())

    def test_ct08_busca_de_familias_continua_paginada(self):
        for indice in range(23):
            Familia.objects.create(
                nome_responsavel=f"Pereira {indice:02d}", endereco="Rua 1", num_membros=2
            )
        for sobrenome in ("Silva", "Souza", "Santos"):
            Familia.objects.create(
                nome_responsavel=f"Família {sobrenome}", endereco="Rua 2", num_membros=3
            )

        pagina_1 = self.client.get(reverse("familia_list"), {"q": "Pereira"})
        pagina_2 = self.client.get(reverse("familia_list"), {"q": "Pereira", "page": 2})

        self.assertEqual(pagina_1.context["page_obj"].paginator.count, 23)
        self.assertEqual(len(pagina_1.context["page_obj"]), 20)
        self.assertEqual(len(pagina_2.context["page_obj"]), 3)
        nomes = [
            familia.nome_responsavel
            for pagina in (pagina_1, pagina_2)
            for familia in pagina.context["page_obj"]
        ]
        self.assertEqual(len(set(nomes)), 23)
        self.assertTrue(all(nome.startswith("Pereira") for nome in nomes))


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
        self.assertIn("10,00", str(form.errors))
        self.assertIn("11,00", str(form.errors))
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
        self.assertContains(response, "saldo: 10,00")

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
        # A cancelada continua no histórico, marcada (#19); os totais é que a excluem.
        self.assertEqual(len(doacoes), 3)
        self.assertIn(self.doacao_cancelada, doacoes)
        self.assertContains(response, 'data-testid="doacao-historico-cancelada-badge"', count=1)

    def test_filtro_por_doador_isolado(self):
        response = self.client.get(reverse("doacao_list"), {"id_doador": self.doador1.pk})
        doacoes = list(response.context["page_obj"])
        self.assertEqual(doacoes, [self.doacao_cancelada, self.doacao_antiga])

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
        self.assertEqual(len(doacoes), 3)

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
        # A cancelada continua no histórico, marcada (#19).
        self.assertEqual(len(distribuicoes), 3)
        self.assertIn(self.distribuicao_cancelada, distribuicoes)
        self.assertContains(
            response, 'data-testid="distribuicao-historico-cancelada-badge"', count=1
        )

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
        self.assertEqual(len(distribuicoes), 3)

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
        # 6 do estoque + 2 de doações e famílias do mês + 2 das movimentações recentes (#24).
        with self.assertNumQueries(10):
            montar_resumo(self.HOJE)

    # --- #24: doações do mês, famílias atendidas e movimentações recentes (CT33) ---

    def _familia(self, nome):
        return Familia.objects.create(nome_responsavel=nome, endereco="Rua B, 5", num_membros=2)

    def _distribuir_para(self, familia, item, quantidade, data=None, cancelado=False):
        return Distribuicao.objects.create(
            familia=familia,
            item=item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data or self.HOJE,
            cancelado=cancelado,
        )

    def test_ct33_painel_do_mes_conta_doacoes_familias_e_lista_recentes(self):
        arroz = self._item("Arroz")
        self._doar(arroz, 50, data=date(2026, 10, 1))
        self._doar(arroz, 10, data=date(2026, 10, 15))
        self._doar(arroz, 99, data=date(2026, 10, 14), cancelado=True)
        self._doar(arroz, 20, data=date(2026, 9, 10))
        self._doar(arroz, 30, data=date(2026, 9, 30))  # depois de 15/09: fora da comparação
        lima, costa = self._familia("Família Lima"), self._familia("Família Costa")
        self._distribuir(arroz, 2, data=date(2026, 10, 3))
        self._distribuir(arroz, 3, data=date(2026, 10, 10))
        self._distribuir_para(lima, arroz, 4, data=date(2026, 10, 12))
        self._distribuir_para(costa, arroz, 8, data=date(2026, 10, 13), cancelado=True)
        self._distribuir_para(costa, arroz, 1, data=date(2026, 9, 20))

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(resumo["doacoes_no_mes"], 2)
        self.assertEqual(resumo["variacao_doacoes"], 1)
        self.assertEqual(resumo["texto_variacao_doacoes"], "+1 em relação ao mês anterior")
        self.assertEqual(resumo["familias_atendidas"], 2)
        self.assertEqual(
            [
                (linha["tipo"], linha["pessoa"], linha["quantidade"])
                for linha in resumo["movimentacoes_recentes"]
            ],
            [
                ("Doação", "João Doador", Decimal("10")),
                ("Distribuição", "Família Lima", Decimal("4")),
                ("Distribuição", "Família Silva", Decimal("3")),
                ("Distribuição", "Família Silva", Decimal("2")),
                ("Doação", "João Doador", Decimal("50")),
            ],
        )

    def test_variacao_compara_com_o_mesmo_intervalo_do_mes_anterior(self):
        arroz = self._item("Arroz")
        self._doar(arroz, 1, data=date(2026, 9, 15))
        self._doar(arroz, 1, data=date(2026, 9, 16))

        resumo = montar_resumo(self.HOJE)

        self.assertEqual(resumo["doacoes_no_mes"], 0)
        self.assertEqual(resumo["variacao_doacoes"], -1)
        self.assertEqual(resumo["texto_variacao_doacoes"], "−1 em relação ao mês anterior")

    def test_periodo_equivalente_limita_ao_ultimo_dia_do_mes_anterior(self):
        casos = {
            date(2026, 3, 31): (date(2026, 2, 1), date(2026, 2, 28)),
            date(2028, 3, 31): (date(2028, 2, 1), date(2028, 2, 29)),
            date(2026, 1, 15): (date(2025, 12, 1), date(2025, 12, 15)),
            date(2026, 11, 1): (date(2026, 10, 1), date(2026, 10, 1)),
        }
        for hoje, esperado in casos.items():
            with self.subTest(hoje=hoje):
                self.assertEqual(periodo_equivalente_do_mes_anterior(hoje), esperado)

    def test_texto_da_variacao_de_doacoes(self):
        self.assertEqual(texto_variacao_mes_anterior(3), "+3 em relação ao mês anterior")
        self.assertEqual(texto_variacao_mes_anterior(-2), "−2 em relação ao mês anterior")
        self.assertEqual(texto_variacao_mes_anterior(0), "Igual ao mês anterior")

    def test_familias_atendidas_conta_familias_distintas_do_mes_sem_canceladas(self):
        arroz = self._item("Arroz")
        self._distribuir(arroz, 1)
        self._distribuir(arroz, 1, data=date(2026, 10, 2))
        self._distribuir_para(self._familia("Família Lima"), arroz, 1, data=date(2026, 9, 30))
        self._distribuir_para(self._familia("Família Costa"), arroz, 1, cancelado=True)

        self.assertEqual(montar_resumo(self.HOJE)["familias_atendidas"], 1)

    def test_movimentacoes_recentes_ordenam_pela_data_e_desempatam_pelo_registro(self):
        arroz = self._item("Arroz")
        doacao_de_hoje = self._doar(arroz, 1)
        distribuicao_de_hoje = self._distribuir(arroz, 2)
        retroativa = self._doar(arroz, 3, data=date(2026, 10, 14))
        agora = timezone.now()
        Doacao.objects.filter(pk=doacao_de_hoje.pk).update(criado_em=agora - timedelta(hours=2))
        Distribuicao.objects.filter(pk=distribuicao_de_hoje.pk).update(
            criado_em=agora - timedelta(hours=1)
        )
        # Lançada por último, mas com data de ontem: fica abaixo das de hoje.
        Doacao.objects.filter(pk=retroativa.pk).update(criado_em=agora)

        recentes = movimentacoes_recentes()

        self.assertEqual(
            [(linha["entrada"], linha["quantidade"]) for linha in recentes],
            [(False, Decimal("2")), (True, Decimal("1")), (True, Decimal("3"))],
        )

    def test_movimentacoes_recentes_limitam_a_cinco_e_ignoram_canceladas(self):
        arroz = self._item("Arroz")
        for dia in range(1, 5):
            self._doar(arroz, dia, data=date(2026, 10, dia))
            self._distribuir(arroz, 1, data=date(2026, 10, dia))
        self._doar(arroz, 7, cancelado=True)
        self._distribuir(arroz, 7, cancelado=True)

        recentes = movimentacoes_recentes()

        self.assertEqual(
            [linha["data"] for linha in recentes],
            [date(2026, 10, 4)] * 2 + [date(2026, 10, 3)] * 2 + [date(2026, 10, 2)],
        )
        self.assertNotIn(Decimal("7"), [linha["quantidade"] for linha in recentes])

    def test_painel_mostra_doacoes_familias_e_recentes_para_os_dois_perfis(self):
        # A view usa a data real; as movimentações precisam cair no mês corrente.
        hoje = timezone.localdate()
        arroz = self._item("Arroz")
        self._doar(arroz, 12, data=hoje)
        self._distribuir(arroz, 2, data=hoje)

        for usuario in (self.voluntario, self.admin):
            with self.subTest(perfil=usuario.perfil):
                self.client.force_login(usuario)
                response = self.client.get(reverse("painel"))

                self.assertEqual(response.context["resumo"]["doacoes_no_mes"], 1)
                self.assertEqual(response.context["resumo"]["familias_atendidas"], 1)
                self.assertContains(response, 'data-testid="painel-doacoes-recebidas-card"')
                self.assertContains(response, 'data-testid="painel-familias-atendidas-card"')
                self.assertContains(response, "+1 em relação ao mês anterior")
                self.assertContains(response, "João Doador")
                self.assertContains(response, "Família Silva")
                self.assertContains(response, 'data-testid="painel-movimentacoes-recentes-lista"')

    def test_painel_sem_movimentacoes_mostra_estado_vazio_e_zeros(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("painel"))

        self.assertEqual(response.context["resumo"]["doacoes_no_mes"], 0)
        self.assertEqual(response.context["resumo"]["familias_atendidas"], 0)
        self.assertContains(response, "Igual ao mês anterior")
        self.assertContains(response, "Nenhuma movimentação registrada.")
        self.assertNotContains(response, 'data-testid="painel-movimentacoes-recentes-lista"')

    def test_painel_recarrega_os_novos_blocos_no_registro_salvo(self):
        self.client.force_login(self.voluntario)

        html = self.client.get(reverse("painel")).content.decode()

        inicio, fim = html.index('id="painel-conteudo"'), html.index("</main>")
        for testid in (
            "painel-doacoes-recebidas-card",
            "painel-familias-atendidas-card",
            "painel-movimentacoes-recentes",
        ):
            with self.subTest(bloco=testid):
                self.assertTrue(inicio < html.index(f'data-testid="{testid}"') < fim)


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


class SegurancaProducaoTests(TestCase):
    """Em produção o sistema só funciona por HTTPS; em desenvolvimento continua em HTTP."""

    def carregar_settings(self, debug):
        caminho_settings = settings.BASE_DIR / "conecta" / "settings.py"
        with (
            mock.patch.object(sys, "argv", ["manage.py", "runserver"]),
            mock.patch.dict(os.environ, {"DEBUG": debug}),
        ):
            return runpy.run_path(str(caminho_settings))

    def test_producao_exige_https_e_cookies_seguros(self):
        config = self.carregar_settings(debug="False")

        self.assertTrue(config["SECURE_SSL_REDIRECT"])
        self.assertTrue(config["SESSION_COOKIE_SECURE"])
        self.assertTrue(config["CSRF_COOKIE_SECURE"])
        self.assertGreater(config["SECURE_HSTS_SECONDS"], 0)

    def test_desenvolvimento_continua_em_http(self):
        config = self.carregar_settings(debug="True")

        self.assertFalse(config.get("SECURE_SSL_REDIRECT", False))
        self.assertFalse(config.get("SESSION_COOKIE_SECURE", False))
        self.assertFalse(config.get("CSRF_COOKIE_SECURE", False))

    def test_http_redireciona_para_https_exceto_o_health_check(self):
        config = self.carregar_settings(debug="False")

        with self.settings(
            SECURE_SSL_REDIRECT=True,
            SECURE_PROXY_SSL_HEADER=config["SECURE_PROXY_SSL_HEADER"],
            SECURE_REDIRECT_EXEMPT=config["SECURE_REDIRECT_EXEMPT"],
        ):
            login_http = self.client.get(reverse("login"))
            login_pelo_proxy = self.client.get(
                reverse("login"), headers={"X-Forwarded-Proto": "https"}
            )
            health_http = self.client.get(reverse("health"))

        self.assertRedirects(
            login_http, "https://testserver/login/", status_code=301, fetch_redirect_response=False
        )
        # Requisição que chegou por HTTPS no proxy do Render não entra em loop de redirecionamento.
        self.assertEqual(login_pelo_proxy.status_code, 200)
        self.assertEqual(health_http.status_code, 200)

    def test_producao_escreve_os_erros_no_console(self):
        # Processo separado para não trocar a configuração de logs da suíte de testes.
        codigo = (
            "import django, logging; django.setup(); "
            "logging.getLogger('django.request').error('erro de teste')"
        )
        resultado = subprocess.run(
            [sys.executable, "-c", codigo],
            cwd=settings.BASE_DIR,
            env={**os.environ, "DEBUG": "False", "DJANGO_SETTINGS_MODULE": "conecta.settings"},
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("erro de teste", resultado.stderr)


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


class CenarioCancelamentoMixin:
    """Administrador, voluntário e um item com doador e família para os testes da #19."""

    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Ana Admin",
            email="ana-cancela@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria-cancela@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        self.doador = Doador.objects.create(nome="Mercado Bom Preço", cpf_cnpj="321.654.987-00")
        self.familia = Familia.objects.create(
            nome_responsavel="Família Souza", endereco="Rua C, 10", num_membros=3
        )
        categoria = CategoriaItem.objects.create(nome="Alimento Cancelamento")
        unidade = UnidadeMedida.objects.create(nome="Quilograma Cancelamento", sigla="kgc")
        self.item = Item.objects.create(nome="Arroz", categoria=categoria, unidade_medida=unidade)

    def _doar(self, quantidade, data=None):
        return Doacao.objects.create(
            doador=self.doador,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data or date(2026, 10, 20),
        )

    def _distribuir(self, quantidade, data=None):
        return Distribuicao.objects.create(
            familia=self.familia,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data or date(2026, 10, 21),
        )

    def _login(self, usuario):
        self.client.post(reverse("login"), {"email": usuario.email, "senha": "senha-teste"})


class CancelarMovimentacaoModeloTests(CenarioCancelamentoMixin, TestCase):
    """CT20 (#19): a regra de cancelamento no modelo."""

    def test_ct20_cancelar_doacao_reverte_saldo_e_preserva_registro(self):
        self._doar(10)
        doacao = self._doar(5)
        self.assertEqual(self.item.saldo_atual, 15)

        doacao.cancelar(self.admin)

        self.assertEqual(self.item.saldo_atual, 10)
        doacao.refresh_from_db()
        self.assertTrue(doacao.cancelado)
        self.assertEqual(doacao.cancelado_por, self.admin)
        self.assertIsNotNone(doacao.cancelado_em)
        self.assertEqual(doacao.quantidade, Decimal("5"))
        self.assertEqual(Doacao.objects.count(), 2)

    def test_cancelar_distribuicao_devolve_quantidade_ao_saldo(self):
        self._doar(10)
        distribuicao = self._distribuir(4)
        self.assertEqual(self.item.saldo_atual, 6)

        distribuicao.cancelar(self.admin)

        self.assertEqual(self.item.saldo_atual, 10)
        distribuicao.refresh_from_db()
        self.assertTrue(distribuicao.cancelado)
        self.assertEqual(distribuicao.cancelado_por, self.admin)

    def test_cancelar_doacao_bloqueado_quando_saldo_ficaria_negativo(self):
        doacao = self._doar(10)
        self._distribuir(8)

        with self.assertRaisesMessage(
            ValidationError,
            "Não é possível cancelar: o saldo de Arroz ficaria negativo "
            "(disponível 2 kgc, doação 10 kgc).",
        ):
            doacao.cancelar(self.admin)

        doacao.refresh_from_db()
        self.assertFalse(doacao.cancelado)
        self.assertIsNone(doacao.cancelado_em)
        self.assertIsNone(doacao.cancelado_por)
        self.assertEqual(self.item.saldo_atual, 2)

    def test_cancelar_doacao_permitido_quando_saldo_fica_zero(self):
        doacao = self._doar(10)
        self._doar(5)
        self._distribuir(5)

        doacao.cancelar(self.admin)

        self.assertEqual(self.item.saldo_atual, 0)

    def test_cancelar_movimentacao_ja_cancelada_nao_altera_nada(self):
        doacao = self._doar(5)
        # Cópia lida antes do primeiro cancelamento, como numa segunda aba aberta.
        copia_desatualizada = Doacao.objects.get(pk=doacao.pk)
        doacao.cancelar(self.admin)
        cancelado_em = Doacao.objects.get(pk=doacao.pk).cancelado_em
        outro_admin = Usuario.objects.create(
            nome="Bruno Admin",
            email="bruno-cancela@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )

        with self.assertRaisesMessage(ValidationError, "Esta movimentação já foi cancelada."):
            copia_desatualizada.cancelar(outro_admin)

        doacao.refresh_from_db()
        self.assertEqual(doacao.cancelado_em, cancelado_em)
        self.assertEqual(doacao.cancelado_por, self.admin)

    def test_cancelar_distribuicao_libera_o_cancelamento_da_doacao(self):
        doacao = self._doar(10)
        distribuicao = self._distribuir(8)
        self.assertIsNotNone(doacao.motivo_para_nao_cancelar())

        distribuicao.cancelar(self.admin)

        self.assertIsNone(doacao.motivo_para_nao_cancelar())
        doacao.cancelar(self.admin)
        self.assertEqual(self.item.saldo_atual, 0)


class CancelarMovimentacaoViewTests(CenarioCancelamentoMixin, TestCase):
    """CT20 (#19): cancelamento pelas telas, permissões e respostas para o htmx."""

    HTMX = {"HTTP_HX_REQUEST": "true"}
    BOTAO_CONFIRMAR = 'data-testid="movimentacao-cancelar-confirmar-button"'

    def test_admin_ve_confirmacao_sem_alterar_nada(self):
        doacao = self._doar(5)
        self._login(self.admin)

        response = self.client.get(reverse("doacao_cancelar", args=[doacao.pk]), **self.HTMX)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/_movimentacao_cancelar.html")
        self.assertTemplateNotUsed(response, "core/movimentacao_cancelar.html")
        self.assertContains(response, "Mercado Bom Preço")
        self.assertContains(response, "Arroz")
        self.assertContains(response, self.BOTAO_CONFIRMAR)
        doacao.refresh_from_db()
        self.assertFalse(doacao.cancelado)

    def test_sem_htmx_abre_a_pagina_inteira_com_volta_ao_historico(self):
        distribuicao = self._distribuir(2)
        self._login(self.admin)

        response = self.client.get(reverse("distribuicao_cancelar", args=[distribuicao.pk]))

        self.assertTemplateUsed(response, "core/movimentacao_cancelar.html")
        self.assertContains(response, "Família Souza")
        voltar = f'href="{reverse("distribuicao_list")}" data-testid="movimentacao-cancelar-voltar'
        self.assertContains(response, voltar)

    def test_ct20_admin_cancela_doacao_sem_htmx_e_volta_ao_historico(self):
        doacao = self._doar(5)
        self._login(self.admin)

        response = self.client.post(reverse("doacao_cancelar", args=[doacao.pk]), follow=True)

        self.assertRedirects(response, reverse("doacao_list"))
        self.assertContains(response, "Doação cancelada.")
        doacao.refresh_from_db()
        self.assertTrue(doacao.cancelado)
        self.assertEqual(doacao.cancelado_por, self.admin)

    def test_admin_cancela_distribuicao_com_htmx_e_dispara_evento(self):
        self._doar(10)
        distribuicao = self._distribuir(4)
        self._login(self.admin)

        response = self.client.post(
            reverse("distribuicao_cancelar", args=[distribuicao.pk]), **self.HTMX
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Trigger"], "movimentacao-cancelada")
        self.assertEqual(response["HX-Reswap"], "none")
        self.assertContains(response, "Distribuição cancelada.")
        self.assertEqual(self.item.saldo_atual, 10)

    def test_cancelamento_bloqueado_mostra_o_motivo_no_dialogo(self):
        doacao = self._doar(10)
        self._distribuir(8)
        self._login(self.admin)

        response = self.client.post(reverse("doacao_cancelar", args=[doacao.pk]), **self.HTMX)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("HX-Trigger", response)
        self.assertContains(response, "o saldo de Arroz ficaria negativo")
        self.assertNotContains(response, self.BOTAO_CONFIRMAR)
        doacao.refresh_from_db()
        self.assertFalse(doacao.cancelado)

    def test_movimentacao_ja_cancelada_mostra_aviso_sem_confirmar(self):
        doacao = self._doar(5)
        doacao.cancelar(self.admin)
        self._login(self.admin)

        response = self.client.get(reverse("doacao_cancelar", args=[doacao.pk]), **self.HTMX)

        self.assertContains(response, "Esta movimentação já foi cancelada.")
        self.assertNotContains(response, self.BOTAO_CONFIRMAR)

    def test_ct20_voluntario_nao_pode_cancelar(self):
        doacao = self._doar(5)
        distribuicao = self._distribuir(2)
        self._login(self.voluntario)

        for url in (
            reverse("doacao_cancelar", args=[doacao.pk]),
            reverse("distribuicao_cancelar", args=[distribuicao.pk]),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url).status_code, 403)

        doacao.refresh_from_db()
        distribuicao.refresh_from_db()
        self.assertFalse(doacao.cancelado)
        self.assertFalse(distribuicao.cancelado)

    def test_anonimo_vai_para_o_login(self):
        doacao = self._doar(5)
        url = reverse("doacao_cancelar", args=[doacao.pk])

        self.assertRedirects(self.client.post(url), reverse("login"))
        response = self.client.post(url, **self.HTMX)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["HX-Redirect"], reverse("login"))
        doacao.refresh_from_db()
        self.assertFalse(doacao.cancelado)

    def test_movimentacao_inexistente_404_e_metodo_nao_permitido_405(self):
        doacao = self._doar(5)
        self._login(self.admin)

        response = self.client.post(reverse("distribuicao_cancelar", args=[999999]))
        self.assertEqual(response.status_code, 404)
        response = self.client.put(reverse("doacao_cancelar", args=[doacao.pk]))
        self.assertEqual(response.status_code, 405)


class HistoricoComCanceladasTests(CenarioCancelamentoMixin, TestCase):
    """#19: as canceladas seguem nos históricos, marcadas, e fora de totais, relatório e CSV."""

    def _cancelada_em(self, movimentacao):
        movimentacao.refresh_from_db()
        return timezone.localtime(movimentacao.cancelado_em).strftime("%d/%m/%Y %H:%M")

    def test_historico_de_doacoes_mostra_cancelada_com_selo_autor_e_data(self):
        doacao = self._doar(5)
        doacao.cancelar(self.admin)
        self._login(self.voluntario)

        response = self.client.get(reverse("doacao_list"))

        self.assertIn(doacao, list(response.context["page_obj"]))
        self.assertContains(response, 'data-testid="doacao-historico-cancelada-badge"')
        self.assertContains(response, f"por Ana Admin em {self._cancelada_em(doacao)}")

    def test_historico_de_distribuicoes_mostra_cancelada_com_selo_autor_e_data(self):
        distribuicao = self._distribuir(2)
        distribuicao.cancelar(self.admin)
        self._login(self.voluntario)

        response = self.client.get(reverse("distribuicao_list"))

        self.assertIn(distribuicao, list(response.context["page_obj"]))
        self.assertContains(response, 'data-testid="distribuicao-historico-cancelada-badge"')
        self.assertContains(response, f"por Ana Admin em {self._cancelada_em(distribuicao)}")

    def test_botao_cancelar_so_para_admin_e_so_nas_linhas_ativas(self):
        ativa = self._doar(5)
        cancelada = self._doar(3)
        cancelada.cancelar(self.admin)
        distribuicao = self._distribuir(1)

        self._login(self.admin)
        response = self.client.get(reverse("doacao_list"))
        self.assertContains(response, f'href="{reverse("doacao_cancelar", args=[ativa.pk])}"')
        self.assertNotContains(response, reverse("doacao_cancelar", args=[cancelada.pk]))
        response = self.client.get(reverse("distribuicao_list"))
        self.assertContains(
            response, f'href="{reverse("distribuicao_cancelar", args=[distribuicao.pk])}"'
        )

        self.client.get(reverse("logout"))
        self._login(self.voluntario)
        for url in (reverse("doacao_list"), reverse("distribuicao_list")):
            with self.subTest(url=url):
                self.assertNotContains(self.client.get(url), "historico-cancelar-button")

    def test_totais_por_doador_excluem_a_doacao_cancelada_pela_tela(self):
        self._doar(10)
        doacao = self._doar(5)
        self._login(self.admin)
        self.client.post(reverse("doacao_cancelar", args=[doacao.pk]))

        response = self.client.get(reverse("doacao_list"))

        self.assertEqual(len(response.context["page_obj"]), 2)
        totais = [linha["total"] for linha in response.context["totais_por_doador"]]
        self.assertEqual(totais, [Decimal("10")])

    def test_relatorio_e_csv_excluem_a_distribuicao_cancelada_pela_tela(self):
        self._doar(10)
        self._distribuir(2)
        distribuicao = self._distribuir(3, data=date(2026, 10, 22))
        self._login(self.admin)
        self.client.post(reverse("distribuicao_cancelar", args=[distribuicao.pk]))

        relatorio = self.client.get(reverse("distribuicao_relatorio"))
        quantidades = [linha["quantidade_total"] for linha in relatorio.context["linhas"]]
        self.assertEqual(quantidades, [Decimal("2")])

        csv = self.client.get(reverse("distribuicao_exportar_csv")).content.decode("utf-8-sig")
        linhas = csv.strip().splitlines()
        self.assertEqual(len(linhas), 2)
        self.assertIn("2.00", linhas[1])

    def test_card_recarrega_com_os_filtros_e_a_pagina_atuais_depois_de_cancelar(self):
        self._doar(5)
        self._distribuir(1)
        self._login(self.admin)

        casos = (
            ("doacao_list", {"id_doador": self.doador.pk, "page": 1}),
            ("distribuicao_list", {"id_familia": self.familia.pk, "page": 1}),
        )
        for nome, filtros in casos:
            with self.subTest(lista=nome):
                response = self.client.get(reverse(nome), filtros)
                parametro, valor = next(iter(filtros.items()))
                self.assertContains(
                    response,
                    f'hx-get="{reverse(nome)}?{parametro}={valor}&amp;page=1" '
                    'hx-trigger="movimentacao-cancelada from:body"',
                )


class ExportarCsvTests(TestCase):
    """CT21 (#23): o CSV traz os mesmos dados e filtros da tela do relatório (#21)."""

    CABECALHO = [
        "Família",
        "Item",
        "Categoria",
        "Qtd total",
        "Unidade",
        "Nº distribuições",
        "Último registro",
    ]

    def setUp(self):
        self.voluntario = Usuario.objects.create(
            nome="Voluntária CSV",
            email="csv@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.post(
            reverse("login"), {"email": "csv@conectasocial.org", "senha": "senha-teste"}
        )
        self.silva = Familia.objects.create(
            nome_responsavel="Família Silva", endereco="Rua A, 123", num_membros=4
        )
        self.souza = Familia.objects.create(
            nome_responsavel="Família Souza", endereco="Rua B, 456", num_membros=3
        )
        self.alimento = CategoriaItem.objects.create(nome="Alimento")
        self.kg = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.arroz = Item.objects.create(
            nome="Arroz", categoria=self.alimento, unidade_medida=self.kg
        )
        self.feijao = Item.objects.create(
            nome="Feijão", categoria=self.alimento, unidade_medida=self.kg
        )
        hoje = timezone.localdate()
        self.dias = {n: hoje - timedelta(days=n) for n in (5, 10, 20, 40)}
        self._distribuir(self.silva, self.arroz, "2", self.dias[20])
        self._distribuir(self.silva, self.arroz, "3", self.dias[5])
        self._distribuir(self.silva, self.feijao, "1", self.dias[10])
        self._distribuir(self.souza, self.arroz, "4", self.dias[40])

    def _distribuir(self, familia, item, quantidade, data):
        return Distribuicao.objects.create(
            familia=familia,
            item=item,
            quantidade=Decimal(quantidade),
            data=data,
            registrado_por=self.voluntario,
        )

    def _exportar(self, filtros=None):
        return self.client.get(reverse("distribuicao_exportar_csv"), filtros or {})

    def _ler_csv(self, filtros=None):
        texto = self._exportar(filtros).content.decode("utf-8")
        return list(csv.reader(io.StringIO(texto.removeprefix("\ufeff"))))

    def _linhas_da_tela(self, filtros=None):
        relatorio = self.client.get(reverse("distribuicao_relatorio"), filtros or {})
        return [
            [
                linha["familia__nome_responsavel"],
                linha["item__nome"],
                linha["item__categoria__nome"],
                f"{linha['quantidade_total']:.2f}",
                linha["item__unidade_medida__sigla"],
                str(linha["numero_distribuicoes"]),
                linha["ultimo_registro"].strftime("%d/%m/%Y"),
            ]
            for linha in relatorio.context["linhas"]
        ]

    def test_ct21_csv_tem_cabecalho_em_portugues(self):
        response = self._exportar()

        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertEqual(
            response["Content-Disposition"], 'attachment; filename="relatorio_distribuicoes.csv"'
        )
        self.assertEqual(self._ler_csv()[0], self.CABECALHO)

    def test_ct21_csv_tem_as_mesmas_linhas_da_tela(self):
        linhas = self._ler_csv()[1:]

        data = "%d/%m/%Y"
        self.assertEqual(
            linhas,
            [
                [
                    "Família Silva",
                    "Arroz",
                    "Alimento",
                    "5.00",
                    "kg",
                    "2",
                    self.dias[5].strftime(data),
                ],
                [
                    "Família Silva",
                    "Feijão",
                    "Alimento",
                    "1.00",
                    "kg",
                    "1",
                    self.dias[10].strftime(data),
                ],
                [
                    "Família Souza",
                    "Arroz",
                    "Alimento",
                    "4.00",
                    "kg",
                    "1",
                    self.dias[40].strftime(data),
                ],
            ],
        )
        self.assertEqual(linhas, self._linhas_da_tela())

    def test_ct21_csv_aplica_os_mesmos_filtros_da_tela(self):
        periodo = {
            "data_inicio": self.dias[20].isoformat(),
            "data_fim": self.dias[10].isoformat(),
        }
        casos = {
            "família": {"id_familia": self.silva.pk},
            "período": periodo,
            "família e período": {"id_familia": self.silva.pk, **periodo},
        }
        for nome, filtros in casos.items():
            with self.subTest(filtro=nome):
                linhas = self._ler_csv(filtros)[1:]
                self.assertTrue(linhas)
                self.assertEqual(linhas, self._linhas_da_tela(filtros))
                self.assertLess(len(linhas), len(self._ler_csv()[1:]))

    def test_csv_tem_um_unico_bom_no_inicio(self):
        conteudo = self._exportar().content

        self.assertTrue(conteudo.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(conteudo.count(b"\xef\xbb\xbf"), 1)

    def test_csv_neutraliza_textos_que_viram_formula(self):
        familia = Familia.objects.create(
            nome_responsavel='=HYPERLINK("http://exemplo.com")', endereco="Rua C", num_membros=1
        )
        menos = Familia.objects.create(nome_responsavel="-5", endereco="Rua D", num_membros=1)
        categoria = CategoriaItem.objects.create(nome="@admin")
        item = Item.objects.create(nome="+SOMA(1;1)", categoria=categoria, unidade_medida=self.kg)
        self._distribuir(familia, item, "1", self.dias[5])
        self._distribuir(menos, self.arroz, "1", self.dias[5])

        textos = [linha[:3] for linha in self._ler_csv()[1:]]

        self.assertIn(["'" + familia.nome_responsavel, "'+SOMA(1;1)", "'@admin"], textos)
        self.assertIn(["'-5", "Arroz", "Alimento"], textos)
        self.assertIn(["Família Silva", "Arroz", "Alimento"], textos)

    def test_celula_csv_so_altera_texto_que_comeca_com_caractere_de_formula(self):
        casos = [
            ("=1+1", "'=1+1"),
            ("+55 16 3333-0000", "'+55 16 3333-0000"),
            ("-3", "'-3"),
            ("@usuario", "'@usuario"),
            ("\tsoma", "'\tsoma"),
            ("\rsoma", "'\rsoma"),
            ("Arroz = bom", "Arroz = bom"),
            ("Família Silva", "Família Silva"),
            ("", ""),
            (Decimal("-1"), Decimal("-1")),
            (None, None),
        ]
        for valor, esperado in casos:
            with self.subTest(valor=valor):
                self.assertEqual(_celula_csv(valor), esperado)

    def test_csv_exige_login(self):
        self.client.logout()

        self.assertRedirects(self._exportar(), reverse("login"))


class ExpiracaoSessaoTests(TestCase):
    """CT01 (#1): a sessão expira depois de 30 minutos sem atividade."""

    HTMX = {"HTTP_HX_REQUEST": "true"}

    def setUp(self):
        Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria@conectasocial.org",
            password=make_password("senha-correta"),
            perfil=Usuario.Perfil.VOLUNTARIO,
            ativo=True,
        )
        self.client.post(
            reverse("login"), {"email": "maria@conectasocial.org", "senha": "senha-correta"}
        )
        self.chave = self.client.session.session_key

    def _prazo_restante(self):
        expira_em = Session.objects.get(session_key=self.chave).expire_date
        return (expira_em - timezone.now()).total_seconds()

    def _expirar_em(self, prazo):
        Session.objects.filter(session_key=self.chave).update(expire_date=timezone.now() + prazo)

    def test_ct01_sessao_expira_apos_30_minutos_sem_atividade(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 30 * 60)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertAlmostEqual(self._prazo_restante(), 30 * 60, delta=60)

    def test_ct01_sessao_expirada_leva_ao_login(self):
        self.assertEqual(self.client.get(reverse("painel")).status_code, 200)

        self._expirar_em(timedelta(seconds=-1))

        self.assertRedirects(self.client.get(reverse("painel")), reverse("login"))

    def test_ct01_sessao_expirada_no_htmx_pede_redirecionamento_ao_login(self):
        self._expirar_em(timedelta(seconds=-1))

        response = self.client.get(reverse("familia_list"), **self.HTMX)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["HX-Redirect"], reverse("login"))

    def test_ct01_requisicao_ativa_renova_o_prazo_da_sessao(self):
        self._expirar_em(timedelta(seconds=60))

        self.assertEqual(self.client.get(reverse("painel")).status_code, 200)

        self.assertGreater(self._prazo_restante(), 29 * 60)


class SeedCommandTests(TestCase):
    """O comando seed cria os dados de exemplo e pode ser rodado de novo sem duplicar."""

    MODELOS = (Usuario, Doador, Familia, CategoriaItem, UnidadeMedida, Item, Doacao, Distribuicao)

    def _rodar_seed(self):
        saida = io.StringIO()
        call_command("seed", stdout=saida)
        return saida.getvalue()

    def test_seed_cria_os_dados_de_exemplo(self):
        saida = self._rodar_seed()

        self.assertIn("Dados iniciais criados ou atualizados com sucesso.", saida)
        self.assertTrue(
            Usuario.objects.filter(
                email="admin@conectasocial.org", perfil=Usuario.Perfil.ADMINISTRADOR
            ).exists()
        )
        self.assertTrue(Usuario.objects.filter(perfil=Usuario.Perfil.VOLUNTARIO).exists())
        self.assertEqual(Item.objects.count(), 8)
        self.assertTrue(Doacao.objects.exists())
        self.assertTrue(Distribuicao.objects.exists())

    def test_seed_pode_rodar_de_novo_sem_duplicar(self):
        self._rodar_seed()
        contagens = [modelo.objects.count() for modelo in self.MODELOS]

        self._rodar_seed()

        self.assertEqual([modelo.objects.count() for modelo in self.MODELOS], contagens)


class CenarioPrivacidadeMixin:
    """Doador, família e item com estoque para os testes da #25 (LGPD)."""

    HOJE = date(2026, 11, 6)
    LIMITE = date(2021, 11, 6)  # HOJE menos o prazo de retenção (5 anos)

    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Ana Admin",
            email="ana-lgpd@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.voluntario = Usuario.objects.create(
            nome="Maria Voluntária",
            email="maria-lgpd@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        self.doador = Doador.objects.create(
            nome="Carlos Pereira",
            cpf_cnpj="123.456.789-01",
            telefone="(16) 99999-0000",
            email="carlos@example.com",
        )
        self.familia = Familia.objects.create(
            nome_responsavel="Família Lima",
            endereco="Rua das Flores, 12",
            telefone="(16) 98888-0000",
            num_membros=4,
        )
        categoria = CategoriaItem.objects.create(nome="Alimento LGPD")
        unidade = UnidadeMedida.objects.create(nome="Quilograma LGPD", sigla="kgl")
        self.item = Item.objects.create(nome="Arroz", categoria=categoria, unidade_medida=unidade)

    def _doar(self, data, doador=None, quantidade="10"):
        return Doacao.objects.create(
            doador=doador or self.doador,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data,
        )

    def _distribuir(self, data, familia=None, quantidade="2"):
        return Distribuicao.objects.create(
            familia=familia or self.familia,
            item=self.item,
            registrado_por=self.voluntario,
            quantidade=Decimal(quantidade),
            data=data,
        )

    def _cadastrado_em(self, registro, data):
        type(registro).objects.filter(pk=registro.pk).update(
            criado_em=timezone.make_aware(datetime(data.year, data.month, data.day, 12))
        )

    def _anonimizar(self, *argumentos):
        saida = io.StringIO()
        with mock.patch(
            "core.management.commands.anonimizar_vencidos.timezone.localdate",
            return_value=self.HOJE,
        ):
            call_command("anonimizar_vencidos", *argumentos, stdout=saida)
        return saida.getvalue()

    def _login(self, usuario):
        self.client.post(reverse("login"), {"email": usuario.email, "senha": "senha-teste"})


class PrazoRetencaoTests(SimpleTestCase):
    """Fonte única do aviso (core/privacidade.py): prazo e controlador."""

    def test_data_limite_e_cinco_anos_antes(self):
        self.assertEqual(data_limite(date(2026, 11, 6)), date(2021, 11, 6))

    def test_data_limite_de_29_de_fevereiro_cai_em_28(self):
        self.assertEqual(data_limite(date(2028, 2, 29)), date(2023, 2, 28))

    @override_settings(ONG_NOME="", ONG_CONTATO_PRIVACIDADE="")
    def test_controlador_sem_configuracao_usa_os_textos_padrao(self):
        self.assertEqual(
            controlador(),
            {"nome": NOME_ONG_PADRAO, "contato": CONTATO_PADRAO, "contato_configurado": False},
        )

    @override_settings(ONG_NOME="ONG Mãos Dadas", ONG_CONTATO_PRIVACIDADE="lgpd@maos.org")
    def test_controlador_usa_as_variaveis_de_ambiente(self):
        self.assertEqual(
            controlador(),
            {"nome": "ONG Mãos Dadas", "contato": "lgpd@maos.org", "contato_configurado": True},
        )


class AnonimizacaoTests(CenarioPrivacidadeMixin, TestCase):
    """CT36 (#25): cadastros sem movimentação há 5 anos são anonimizados pelo comando."""

    def _vencidos(self):
        return list(Doador.objects.vencidos(self.HOJE)), list(Familia.objects.vencidas(self.HOJE))

    def test_ct36_ultima_doacao_no_limite_exato_esta_vencida(self):
        self._doar(self.LIMITE)

        self.assertEqual(self._vencidos()[0], [self.doador])

    def test_ct36_ultima_doacao_um_dia_depois_do_limite_nao_esta_vencida(self):
        self._doar(self.LIMITE + timedelta(days=1))

        self.assertEqual(self._vencidos()[0], [])

    def test_ct36_vale_a_doacao_mais_recente(self):
        self._doar(date(2019, 3, 1))
        self._doar(date(2024, 5, 10))

        self.assertEqual(self._vencidos()[0], [])

    def test_ct36_doacao_cancelada_conta_como_movimentacao(self):
        self._doar(date(2019, 3, 1))
        self._doar(date(2024, 5, 10)).cancelar(self.admin)

        self.assertEqual(self._vencidos()[0], [])

    def test_ct36_sem_movimentacao_vale_a_data_do_cadastro(self):
        antigo = Doador.objects.create(nome="Doador Antigo", cpf_cnpj="111.222.333-44")
        self._cadastrado_em(antigo, date(2021, 1, 15))
        self._cadastrado_em(self.doador, date(2025, 1, 15))
        familia_antiga = Familia.objects.create(
            nome_responsavel="Família Antiga", endereco="Rua B, 1", num_membros=2
        )
        self._cadastrado_em(familia_antiga, date(2020, 6, 1))

        doadores, familias = self._vencidos()

        self.assertEqual(doadores, [antigo])
        self.assertEqual(familias, [familia_antiga])

    def test_ct36_familia_vale_a_ultima_distribuicao(self):
        self._doar(self.HOJE - timedelta(days=1), quantidade="50")
        outra = Familia.objects.create(
            nome_responsavel="Família Rocha", endereco="Rua D, 4", num_membros=3
        )
        self._distribuir(self.LIMITE)
        self._distribuir(self.LIMITE + timedelta(days=1), familia=outra)

        self.assertEqual(self._vencidos()[1], [self.familia])

    def test_ct36_comando_anonimiza_doador_e_familia_vencidos(self):
        self._doar(self.LIMITE, quantidade="10")
        self._distribuir(self.LIMITE)

        saida = self._anonimizar()

        self.doador.refresh_from_db()
        self.familia.refresh_from_db()
        self.assertEqual(self.doador.nome, NOME_ANONIMIZADO)
        self.assertEqual(self.doador.cpf_cnpj, f"ANON-{self.doador.pk}")
        self.assertEqual((self.doador.telefone, self.doador.email), ("", ""))
        self.assertTrue(self.doador.anonimizado)
        self.assertEqual(self.familia.nome_responsavel, NOME_ANONIMIZADO)
        self.assertEqual((self.familia.endereco, self.familia.telefone), ("", ""))
        self.assertEqual(self.familia.num_membros, 4)
        self.assertTrue(self.familia.anonimizada)
        self.assertIn("Prazo de retenção: 5 anos (última movimentação até 06/11/2021).", saida)
        self.assertIn("1 doador(es) e 1 família(s) anonimizados.", saida)

    def test_ct36_comando_mantem_movimentacoes_e_saldo(self):
        doacao = self._doar(self.LIMITE, quantidade="10")
        distribuicao = self._distribuir(self.LIMITE, quantidade="3")
        saldo_antes = self.item.saldo_atual

        self._anonimizar()

        self.assertEqual(self.item.saldo_atual, saldo_antes)
        self.assertEqual(Doacao.objects.get().pk, doacao.pk)
        self.assertEqual(Doacao.objects.get().doador_id, self.doador.pk)
        self.assertEqual(Distribuicao.objects.get().pk, distribuicao.pk)
        self.assertEqual(Distribuicao.objects.get().familia_id, self.familia.pk)

    def test_ct36_comando_nao_toca_em_quem_esta_no_prazo(self):
        self._doar(self.HOJE - timedelta(days=30))
        self._distribuir(self.HOJE - timedelta(days=20))

        saida = self._anonimizar()

        self.doador.refresh_from_db()
        self.familia.refresh_from_db()
        self.assertEqual(self.doador.cpf_cnpj, "123.456.789-01")
        self.assertEqual(self.familia.endereco, "Rua das Flores, 12")
        self.assertIn("0 doador(es) e 0 família(s) anonimizados.", saida)

    def test_ct36_comando_pode_rodar_de_novo_sem_reanonimizar(self):
        self._doar(self.LIMITE)
        self._anonimizar()

        saida = self._anonimizar()

        self.doador.refresh_from_db()
        self.assertEqual(self.doador.cpf_cnpj, f"ANON-{self.doador.pk}")
        self.assertIn("0 doador(es)", saida)

    def test_ct36_documento_anonimizado_e_unico_por_doador(self):
        outro = Doador.objects.create(nome="Outra Doadora", cpf_cnpj="987.654.321-00")
        self._doar(self.LIMITE)
        self._doar(self.LIMITE, doador=outro)

        self._anonimizar()

        self.assertEqual(
            sorted(Doador.objects.values_list("cpf_cnpj", flat=True)),
            sorted([f"ANON-{self.doador.pk}", f"ANON-{outro.pk}"]),
        )

    def test_ct36_simular_nao_grava(self):
        self._doar(self.LIMITE)
        self._distribuir(self.LIMITE)

        saida = self._anonimizar("--simular")

        self.doador.refresh_from_db()
        self.familia.refresh_from_db()
        self.assertEqual(self.doador.nome, "Carlos Pereira")
        self.assertEqual(self.familia.nome_responsavel, "Família Lima")
        self.assertIn(
            "Simulação: 1 doador(es) e 1 família(s) seriam anonimizados. Nada foi gravado.",
            saida,
        )


class DocumentoMascaradoTests(CenarioPrivacidadeMixin, TestCase):
    """CT37 (#25): a lista de doadores mostra o CPF ou CNPJ mascarado."""

    def test_ct37_cpf_mostra_so_os_4_ultimos_digitos(self):
        self.assertEqual(mascarar_documento("123.456.789-01"), "***.***.*89-01")

    def test_ct37_cnpj_mostra_so_os_4_ultimos_digitos(self):
        self.assertEqual(mascarar_documento("12.345.678/0001-90"), "**.***.***/**01-90")

    def test_ct37_valor_com_ate_4_digitos_nao_muda(self):
        self.assertEqual(mascarar_documento("12-34"), "12-34")
        self.assertEqual(mascarar_documento(""), "")

    def test_ct37_doador_anonimizado_nao_mostra_documento(self):
        self.doador.anonimizar()

        self.assertEqual(self.doador.documento_mascarado, "—")

    def test_ct37_lista_mostra_o_documento_mascarado_para_os_dois_perfis(self):
        for usuario in (self.voluntario, self.admin):
            with self.subTest(perfil=usuario.perfil):
                self._login(usuario)
                response = self.client.get(reverse("doador_list"))

                self.assertContains(response, "***.***.*89-01")
                self.assertNotContains(response, "123.456.789-01")
                self.client.logout()

    def test_ct37_edicao_do_administrador_mostra_o_documento_completo(self):
        self._login(self.admin)

        response = self.client.get(reverse("doador_update", args=[self.doador.pk]))

        self.assertContains(response, "123.456.789-01")


class AvisoPrivacidadeTests(TestCase):
    """CT34 (#25): aviso de privacidade público, sem login."""

    SECOES = (
        "1. Quem cuida dos seus dados",
        "2. Quais dados guardamos",
        "3. Para que usamos os dados e com qual base legal",
        "4. O cadastro é condição para o atendimento",
        "5. Quem vê os dados",
        "6. Com quem compartilhamos",
        "7. Por quanto tempo guardamos",
        "8. Seus direitos",
        "9. Atualização deste aviso",
    )

    def test_ct34_visitante_sem_login_ve_o_aviso_sem_consultar_o_banco(self):
        with self.assertNumQueries(0):
            response = self.client.get(reverse("privacidade"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/privacidade.html")

    def test_ct34_aviso_so_aceita_get(self):
        response = self.client.post(reverse("privacidade"))

        self.assertEqual(response.status_code, 405)

    def test_ct34_aviso_tem_as_9_secoes_na_ordem(self):
        conteudo = self.client.get(reverse("privacidade")).content.decode()

        posicoes = [conteudo.index(secao) for secao in self.SECOES]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_ct34_aviso_traz_finalidades_bases_legais_compartilhamento_e_prazo(self):
        response = self.client.get(reverse("privacidade"))

        for item in FINALIDADES:
            with self.subTest(finalidade=item["finalidade"]):
                self.assertContains(response, item["finalidade"])
                self.assertContains(response, item["base_legal"])
        self.assertContains(response, "a família precisa estar cadastrada")
        self.assertContains(response, "financiadores e parceiros da ONG para prestação de contas")
        self.assertContains(response, "por mais 5 anos depois da última doação ou entrega")
        self.assertContains(response, "Autoridade Nacional de Proteção de Dados")
        self.assertContains(response, "Atualizado em 06/11/2026")

    @override_settings(ONG_NOME="ONG Mãos Dadas", ONG_CONTATO_PRIVACIDADE="lgpd@maos.org")
    def test_ct34_aviso_usa_o_nome_e_o_contato_configurados(self):
        response = self.client.get(reverse("privacidade"))

        self.assertContains(response, "ONG Mãos Dadas")
        self.assertContains(response, "Contato: lgpd@maos.org")

    @override_settings(ONG_NOME="", ONG_CONTATO_PRIVACIDADE="")
    def test_ct34_sem_configuracao_o_aviso_usa_os_textos_padrao(self):
        response = self.client.get(reverse("privacidade"))

        self.assertContains(response, NOME_ONG_PADRAO)
        self.assertContains(response, CONTATO_PADRAO)
        self.assertNotContains(response, "Contato:")

    def test_ct34_link_na_tela_de_login_na_pagina_inicial_e_no_rodape_interno(self):
        link = f'href="{reverse("privacidade")}"'
        for nome in ("login", "home"):
            with self.subTest(pagina=nome):
                self.assertContains(self.client.get(reverse(nome)), link)

        Usuario.objects.create(
            nome="Voluntária Rodapé",
            email="rodape@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.VOLUNTARIO,
        )
        self.client.post(
            reverse("login"), {"email": "rodape@conectasocial.org", "senha": "senha-teste"}
        )
        self.assertContains(self.client.get(reverse("painel")), link)


class AvisoFormulariosTests(CenarioPrivacidadeMixin, TestCase):
    """CT35 (#25): os formulários de cadastro avisam o voluntário e levam ao aviso completo."""

    LINK = 'href="/privacidade/" target="_blank" rel="noopener"'
    CONDICAO = "o cadastro é necessário para a família receber as doações"

    def setUp(self):
        super().setUp()
        self._login(self.voluntario)

    def _pagina_e_modal(self, nome_url):
        yield "página", self.client.get(reverse(nome_url))
        yield "modal", self.client.get(reverse(nome_url), HTTP_HX_REQUEST="true")

    def test_ct35_novo_doador_avisa_e_leva_ao_aviso_em_nova_aba(self):
        for onde, response in self._pagina_e_modal("doador_create"):
            with self.subTest(onde=onde):
                self.assertContains(response, 'data-testid="aviso-privacidade-doador"')
                self.assertContains(response, self.LINK)

    def test_ct35_nova_familia_avisa_com_destaque_da_condicao_de_atendimento(self):
        for onde, response in self._pagina_e_modal("familia_create"):
            with self.subTest(onde=onde):
                self.assertContains(response, 'data-testid="aviso-privacidade-familia"')
                self.assertContains(response, self.CONDICAO)
                self.assertContains(response, self.LINK)

    def test_ct35_edicao_de_doador_nao_repete_o_aviso(self):
        self.client.logout()
        self._login(self.admin)

        response = self.client.get(reverse("doador_update", args=[self.doador.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'data-testid="aviso-privacidade-doador"')


class AvisoCsvTests(CenarioPrivacidadeMixin, TestCase):
    """CT38 (#25): o relatório avisa que o CSV exportado contém dados pessoais."""

    def test_ct38_relatorio_avisa_que_o_csv_traz_o_nome_das_familias(self):
        self._login(self.voluntario)

        response = self.client.get(reverse("distribuicao_relatorio"))

        self.assertContains(response, 'data-testid="aviso-privacidade-csv"')
        self.assertContains(response, "O CSV traz o nome do responsável de cada família.")


class AnonimizacaoNaInterfaceTests(CenarioPrivacidadeMixin, TestCase):
    """CT36 (#25): depois do comando, as telas e o CSV mostram o titular anonimizado."""

    def setUp(self):
        super().setUp()
        self._doar(self.LIMITE, quantidade="10")
        self._distribuir(self.LIMITE, quantidade="3")
        self._anonimizar()

    def test_ct36_lista_de_doadores_sem_documento_e_sem_botao_editar(self):
        self._login(self.admin)

        response = self.client.get(reverse("doador_list"))

        self.assertContains(response, NOME_ANONIMIZADO)
        self.assertContains(
            response,
            '<td class="px-4 py-4 text-sm text-gray-500" data-testid="doador-documento">—</td>',
            html=True,
        )
        self.assertNotContains(response, reverse("doador_update", args=[self.doador.pk]))

    def test_ct36_edicao_de_doador_anonimizado_responde_404(self):
        self._login(self.admin)

        response = self.client.get(reverse("doador_update", args=[self.doador.pk]))

        self.assertEqual(response.status_code, 404)

    def test_ct36_lista_de_familias_sem_endereco(self):
        self._login(self.voluntario)

        response = self.client.get(reverse("familia_list"))

        self.assertContains(response, NOME_ANONIMIZADO)
        self.assertNotContains(response, "Rua das Flores")

    def test_ct36_historicos_relatorio_e_csv_mostram_o_titular_anonimizado(self):
        self._login(self.voluntario)

        for nome_url in ("doacao_list", "distribuicao_list", "distribuicao_relatorio"):
            with self.subTest(tela=nome_url):
                response = self.client.get(reverse(nome_url))
                self.assertContains(response, NOME_ANONIMIZADO)
                self.assertNotContains(response, "Carlos Pereira")
                self.assertNotContains(response, "Família Lima")

        csv_exportado = self.client.get(reverse("distribuicao_exportar_csv"))
        linhas = list(csv.reader(io.StringIO(csv_exportado.content.decode("utf-8-sig"))))
        self.assertEqual(linhas[1][0], NOME_ANONIMIZADO)


class MascarasTests(TestCase):
    """CT40 (#27): campos com máscara e o que o servidor aceita e grava."""

    def setUp(self):
        self.admin = Usuario.objects.create(
            nome="Ana Admin",
            email="ana.mascaras@conectasocial.org",
            password=make_password("senha-teste"),
            perfil=Usuario.Perfil.ADMINISTRADOR,
            ativo=True,
        )
        self.client.post(
            reverse("login"),
            {"email": "ana.mascaras@conectasocial.org", "senha": "senha-teste"},
        )
        self.doador = Doador.objects.create(nome="Doador Máscara", cpf_cnpj="333.333.333-33")
        self.familia = Familia.objects.create(
            nome_responsavel="Família Máscara", endereco="Rua D, 2", num_membros=2
        )
        self.categoria = CategoriaItem.objects.create(nome="Alimento")
        self.unidade = UnidadeMedida.objects.create(nome="Quilograma", sigla="kg")
        self.item = Item.objects.create(
            nome="Arroz 5kg", categoria=self.categoria, unidade_medida=self.unidade
        )
        self.hoje = timezone.localdate().isoformat()
        Doacao.objects.create(
            doador=self.doador,
            item=self.item,
            quantidade=Decimal("10.00"),
            data=timezone.localdate(),
            registrado_por=self.admin,
        )

    def _campo(self, nome_url, nome_campo):
        conteudo = self.client.get(reverse(nome_url)).content.decode()
        return re.search(rf'<input[^>]*name="{nome_campo}"[^>]*>', conteudo).group(0)

    def _familia(self, **dados):
        return FamiliaForm(
            data={
                "nome_responsavel": "Família Teste",
                "endereco": "Rua E, 3",
                "telefone": "",
                "num_membros": "3",
                **dados,
            }
        )

    def test_ct40_campos_renderizam_com_mascara(self):
        esperado = [
            ("doador_create", "cpf_cnpj", "cpf-cnpj", "numeric", "000.000.000-00 ou CNPJ"),
            ("doador_create", "telefone", "telefone", "numeric", "(00)00000-0000"),
            ("familia_create", "telefone", "telefone", "numeric", "(00)00000-0000"),
            ("familia_create", "num_membros", "inteiro", "numeric", "Ex.: 4"),
            ("item_create", "estoque_minimo", "inteiro", "numeric", "0"),
            ("doacao_create", "quantidade", "decimal", "decimal", "Quantidade doada (ex.: 2,5)"),
            (
                "distribuicao_create",
                "quantidade",
                "decimal",
                "decimal",
                "Quantidade distribuída (ex.: 2,5)",
            ),
        ]
        for nome_url, nome_campo, mascara, teclado, placeholder in esperado:
            with self.subTest(pagina=nome_url, campo=nome_campo):
                campo = self._campo(nome_url, nome_campo)
                self.assertIn('type="text"', campo)
                self.assertIn(f'data-mascara="{mascara}"', campo)
                self.assertIn(f'inputmode="{teclado}"', campo)
                self.assertIn(f'placeholder="{placeholder}"', campo)
                self.assertIn("pattern=", campo)

    def test_ct40_telefone_da_familia_e_gravado_formatado(self):
        for informado, gravado in (
            ("11987654321", "(11)98765-4321"),
            ("(21) 3456-7890", "(21)3456-7890"),
            ("", ""),
        ):
            with self.subTest(telefone=informado):
                form = self._familia(telefone=informado)
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data["telefone"], gravado)

        self.client.post(
            reverse("familia_create"),
            {
                "nome_responsavel": "Família Gravada",
                "endereco": "Rua F, 4",
                "telefone": "(31) 99876-5432",
                "num_membros": "5",
            },
        )
        familia = Familia.objects.get(nome_responsavel="Família Gravada")
        self.assertEqual(familia.telefone, "(31)99876-5432")

    def test_ct40_telefone_da_familia_invalido_da_erro(self):
        for informado in ("119876543", "telefone"):
            with self.subTest(telefone=informado):
                form = self._familia(telefone=informado)
                self.assertFalse(form.is_valid())
                self.assertIn("Informe um telefone válido com DDD.", form.errors["telefone"])

    def test_ct40_quantidade_aceita_virgula_e_ponto(self):
        dados = {"doador": self.doador.pk, "item": self.item.pk, "data": self.hoje}
        for informado in ("2,5", "2.5"):
            with self.subTest(quantidade=informado):
                form = DoacaoForm(data={**dados, "quantidade": informado})
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data["quantidade"], Decimal("2.5"))

        self.assertFalse(DoacaoForm(data={**dados, "quantidade": "abc"}).is_valid())

        self.client.post(reverse("doacao_create"), {**dados, "quantidade": "3,25"})
        self.assertTrue(Doacao.objects.filter(quantidade=Decimal("3.25")).exists())

    def test_ct40_saldo_com_virgula_no_seletor_e_na_mensagem(self):
        resposta = self.client.get(reverse("distribuicao_create"))
        self.assertContains(resposta, "Arroz 5kg saldo: 10,00")

        form = DistribuicaoForm(
            data={
                "familia": self.familia.pk,
                "item": self.item.pk,
                "quantidade": "12,5",
                "data": self.hoje,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Saldo insuficiente: disponível 10,00, solicitado 12,50.", form.non_field_errors()
        )

    def test_ct40_inteiros_aceitam_so_numeros(self):
        self.assertEqual(self._familia(num_membros="4").is_valid(), True)
        self.assertIn("num_membros", self._familia(num_membros="0").errors)
        self.assertIn("num_membros", self._familia(num_membros="abc").errors)

        item = ItemForm(
            data={
                "nome": "Feijão 1kg",
                "categoria": self.categoria.pk,
                "unidade_medida": self.unidade.pk,
                "estoque_minimo": "7",
            }
        )
        self.assertTrue(item.is_valid(), item.errors)
        self.assertEqual(item.cleaned_data["estoque_minimo"], 7)

    def test_ct40_layout_carrega_as_mascaras(self):
        conteudo = self.client.get(reverse("painel")).content.decode()
        self.assertIn('src="/static/js/mascaras.js" defer', conteudo)
