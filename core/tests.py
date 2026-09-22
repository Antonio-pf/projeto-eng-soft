from django.contrib.auth import SESSION_KEY, authenticate
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from core.models import CategoriaItem, Doador, Item, UnidadeMedida
from core.forms import DoadorForm

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


<<<<<<< HEAD
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
=======
class DoadorTestCase(TestCase):
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
        self.assertRedirects(response, reverse("home"))
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
        self.assertRedirects(response, reverse("home"))
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
                "cpf_cnpj": "12345678901",
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
            cpf = f"111.111.11{i:02d}-11" if i < 10 else f"111.111.1{i:02d}/0001-11"
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
        self.assertEqual(self.doador1.telefone, "(11) 9999-9999")

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
        item1 = Item.objects.create(
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
        self.assertEqual(item.estoque_minimo, 4)


>>>>>>> ef7ff43 (feat(core): implementa cadastros, listagens e testes para doadores, famílias, categorias e itens)
