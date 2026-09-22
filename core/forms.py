<<<<<<< HEAD
from django import forms
from django.contrib.auth.password_validation import validate_password

from core.models import Usuario

_INPUT_CLASS = (
    "input input-bordered h-12 w-full rounded-[10px] bg-white placeholder:text-conecta-muted"
)

_CARD_INPUT_CLASS = (
    "w-full rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-700 "
    "placeholder:text-gray-400"
)
_CARD_SELECT_CLASS = f"{_CARD_INPUT_CLASS} appearance-none pr-9"


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "class": _INPUT_CLASS,
                "placeholder": "seu@email.com",
                "data-testid": "login-form-email-input",
            }
        ),
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": f"{_INPUT_CLASS} pr-16",
                "data-testid": "login-form-senha-input",
            }
        ),
    )


class UsuarioForm(forms.Form):
    nome = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": _CARD_INPUT_CLASS,
                "placeholder": "Maria Oliveira",
                "data-testid": "usuario-form-nome-input",
            }
        ),
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": _CARD_INPUT_CLASS,
                "placeholder": "maria@conectasocial.org",
                "data-testid": "usuario-form-email-input",
            }
        ),
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": _CARD_INPUT_CLASS,
                "autocomplete": "new-password",
                "data-testid": "usuario-form-senha-input",
            }
        ),
    )
    perfil = forms.ChoiceField(
        label="Perfil",
        choices=Usuario.Perfil.choices,
        widget=forms.Select(
            attrs={
                "class": _CARD_SELECT_CLASS,
                "data-testid": "usuario-form-perfil-select",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_senha(self):
        senha = self.cleaned_data["senha"]
        validate_password(senha)
        return senha
=======
import re
from django import forms
from .models import CategoriaItem, Doador, Familia, Item, UnidadeMedida


class DoadorForm(forms.ModelForm):
    class Meta:
        model = Doador
        fields = ["nome", "cpf_cnpj", "telefone", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome completo"}),
            "cpf_cnpj": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "000.000.000-00", "id": "id_cpf_cnpj"}
            ),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "(00) 00000-0000"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@exemplo.com"}),
        }
        labels = {
            "nome": "Nome",
            "cpf_cnpj": "CPF/CNPJ",
            "telefone": "Telefone",
            "email": "E-mail",
        }

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get("cpf_cnpj", "").strip()
        
        # Regex for CPF format: XXX.XXX.XXX-XX or CNPJ format: XX.XXX.XXX/XXXX-XX
        cpf_pattern = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
        cnpj_pattern = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")
        
        if not cpf_pattern.match(cpf_cnpj) and not cnpj_pattern.match(cpf_cnpj):
            raise forms.ValidationError("Formato inválido. Utilize o formato XXX.XXX.XXX-XX para CPF ou XX.XXX.XXX/XXXX-XX para CNPJ.")
            
        # Check for duplication
        qs = Doador.objects.filter(cpf_cnpj=cpf_cnpj)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este CPF/CNPJ já está cadastrado no sistema.")
                
        return cpf_cnpj


class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ["nome_responsavel", "endereco", "telefone", "num_membros"]
        widgets = {
            "nome_responsavel": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do responsável"}),
            "endereco": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Endereço completo"}),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "(00) 00000-0000"}),
            "num_membros": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }
        labels = {
            "nome_responsavel": "Nome do Responsável",
            "endereco": "Endereço",
            "telefone": "Telefone",
            "num_membros": "Número de Membros",
        }


class CategoriaItemForm(forms.ModelForm):
    class Meta:
        model = CategoriaItem
        fields = ["nome", "descricao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da categoria (ex: Alimento)"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descrição opcional"}),
        }
        labels = {
            "nome": "Nome da Categoria",
            "descricao": "Descrição",
        }

    def clean_nome(self):
        nome = self.cleaned_data.get("nome", "").strip()
        qs = CategoriaItem.objects.filter(nome__iexact=nome)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Já existe uma categoria cadastrada com este nome.")
        return nome


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["nome", "categoria", "unidade_medida", "estoque_minimo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do item (ex: Arroz 5kg)"}),
            "categoria": forms.Select(attrs={"class": "form-control"}),
            "unidade_medida": forms.Select(attrs={"class": "form-control"}),
            "estoque_minimo": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
        }
        labels = {
            "nome": "Nome do Item",
            "categoria": "Categoria",
            "unidade_medida": "Unidade de Medida",
            "estoque_minimo": "Estoque Mínimo",
        }

    def clean_estoque_minimo(self):
        valor = self.cleaned_data.get("estoque_minimo")
        if valor is not None and valor < 0:
            raise forms.ValidationError("O estoque mínimo deve ser um número inteiro maior ou igual a zero.")
        return valor
>>>>>>> ef7ff43 (feat(core): implementa cadastros, listagens e testes para doadores, famílias, categorias e itens)
