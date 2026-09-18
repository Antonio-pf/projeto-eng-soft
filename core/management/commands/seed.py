from datetime import date
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

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


class Command(BaseCommand):
    help = "Cria ou atualiza dados iniciais para desenvolvimento."

    def handle(self, *args, **options):
        usuarios = {}
        for nome, email, perfil in [
            ("Admin Sistema", "admin@conectasocial.org", Usuario.Perfil.ADMINISTRADOR),
            ("Maria Voluntária", "maria@conectasocial.org", Usuario.Perfil.VOLUNTARIO),
            ("João Voluntário", "joao@conectasocial.org", Usuario.Perfil.VOLUNTARIO),
        ]:
            usuario, _ = Usuario.objects.update_or_create(
                email=email,
                defaults={
                    "nome": nome,
                    "perfil": perfil,
                    "password": make_password("alterar-senha"),
                    "ativo": True,
                },
            )
            usuarios[email] = usuario

        categorias = {}
        for nome, descricao in [
            ("Alimento", "Alimentos não perecíveis e secos"),
            ("Higiene", "Produtos de higiene pessoal"),
            ("Roupa", "Vestuário e calçados"),
            ("Limpeza", "Materiais de limpeza doméstica"),
        ]:
            categorias[nome], _ = CategoriaItem.objects.update_or_create(
                nome=nome,
                defaults={"descricao": descricao},
            )

        unidades = {}
        for nome, sigla in [
            ("Pacote", "pct"),
            ("Garrafa", "grf"),
            ("Unidade", "uni"),
            ("Quilograma", "kg"),
            ("Litro", "l"),
            ("Metro", "m"),
        ]:
            unidades[nome], _ = UnidadeMedida.objects.update_or_create(
                nome=nome,
                defaults={"sigla": sigla},
            )

        itens = {}
        for nome, categoria, unidade, estoque_minimo in [
            ("Arroz 5kg", "Alimento", "Pacote", 10),
            ("Feijão 1kg", "Alimento", "Pacote", 10),
            ("Óleo de soja 900ml", "Alimento", "Garrafa", 5),
            ("Sabonete", "Higiene", "Unidade", 20),
            ("Pasta de dente", "Higiene", "Unidade", 15),
            ("Camiseta adulto", "Roupa", "Unidade", 5),
            ("Calça jeans", "Roupa", "Unidade", 5),
            ("Detergente 500ml", "Limpeza", "Unidade", 10),
        ]:
            itens[nome], _ = Item.objects.update_or_create(
                nome=nome,
                defaults={
                    "categoria": categorias[categoria],
                    "unidade_medida": unidades[unidade],
                    "estoque_minimo": estoque_minimo,
                },
            )

        doadores = {}
        for nome, cpf_cnpj, telefone, email in [
            ("Carlos Mendonça", "123.456.789-00", "(11) 99001-1234", "carlos@email.com"),
            (
                "Supermercado Bom Preço",
                "12.345.678/0001-99",
                "(11) 3200-5678",
                "doacoes@bompreco.com.br",
            ),
            ("Ana Paula Ramos", "987.654.321-00", "(11) 97654-3210", ""),
        ]:
            doadores[nome], _ = Doador.objects.update_or_create(
                cpf_cnpj=cpf_cnpj,
                defaults={"nome": nome, "telefone": telefone, "email": email},
            )

        familias = {}
        for nome, endereco, telefone, num_membros in [
            ("Josefa Santos", "Rua das Flores 45, Bairro Esperança", "(11) 98765-0001", 4),
            ("Roberto Lima", "Av. Principal 200, Apto 3, Bairro Centro", "(11) 98765-0002", 6),
            ("Maria das Dores", "Rua Boa Vista 12, Bairro São Pedro", "", 3),
        ]:
            familias[nome], _ = Familia.objects.update_or_create(
                nome_responsavel=nome,
                defaults={
                    "endereco": endereco,
                    "telefone": telefone,
                    "num_membros": num_membros,
                },
            )

        doacoes = [
            (
                doadores["Carlos Mendonça"],
                itens["Arroz 5kg"],
                usuarios["maria@conectasocial.org"],
                20,
                date(2026, 9, 1),
            ),
            (
                doadores["Carlos Mendonça"],
                itens["Feijão 1kg"],
                usuarios["maria@conectasocial.org"],
                20,
                date(2026, 9, 1),
            ),
            (
                doadores["Supermercado Bom Preço"],
                itens["Arroz 5kg"],
                usuarios["maria@conectasocial.org"],
                50,
                date(2026, 9, 2),
            ),
            (
                doadores["Supermercado Bom Preço"],
                itens["Sabonete"],
                usuarios["maria@conectasocial.org"],
                100,
                date(2026, 9, 2),
            ),
            (
                doadores["Ana Paula Ramos"],
                itens["Óleo de soja 900ml"],
                usuarios["joao@conectasocial.org"],
                15,
                date(2026, 9, 3),
            ),
        ]
        for doador, item, usuario, quantidade, data in doacoes:
            Doacao.objects.get_or_create(
                doador=doador,
                item=item,
                registrado_por=usuario,
                quantidade=quantidade,
                data=data,
            )

        distribuicoes = [
            ("Josefa Santos", "Arroz 5kg", "maria@conectasocial.org", 5, date(2026, 9, 2)),
            ("Josefa Santos", "Feijão 1kg", "maria@conectasocial.org", 3, date(2026, 9, 2)),
            ("Roberto Lima", "Arroz 5kg", "joao@conectasocial.org", 8, date(2026, 9, 3)),
            ("Maria das Dores", "Sabonete", "joao@conectasocial.org", 10, date(2026, 9, 3)),
        ]
        for familia, item, email, quantidade, data in distribuicoes:
            Distribuicao.objects.get_or_create(
                familia=familias[familia],
                item=itens[item],
                registrado_por=usuarios[email],
                quantidade=Decimal(quantidade),
                data=data,
            )

        self.stdout.write(self.style.SUCCESS("Dados iniciais criados ou atualizados com sucesso."))
