import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from core.models import CategoriaItem, Doacao, Doador, Familia, Item, Usuario

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


class DoadorForm(forms.ModelForm):
    class Meta:
        model = Doador
        fields = ["nome", "cpf_cnpj", "telefone", "email"]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "Nome do doador",
                    "data-testid": "doador-form-nome-input",
                }
            ),
            "cpf_cnpj": forms.TextInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "Digite o CPF ou CNPJ",
                    "inputmode": "numeric",
                    "maxlength": "18",
                    "pattern": (
                        r"(?:\d{11}|\d{14}|"
                        r"\d{3}\.\d{3}\.\d{3}-\d{2}|"
                        r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"
                    ),
                    "title": ("Informe um CPF com 11 números ou CNPJ com 14 números."),
                    "data-testid": "doador-form-cpf-cnpj-input",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "(00)00000-0000",
                    "inputmode": "numeric",
                    "maxlength": "14",
                    "pattern": (r"(?:\d{10,11}|\(\d{2}\)\d{4,5}-\d{4})"),
                    "title": "Informe o telefone com DDD.",
                    "data-testid": "doador-form-telefone-input",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "doador@email.com",
                    "data-testid": "doador-form-email-input",
                }
            ),
        }

        labels = {
            "nome": "Nome",
            "cpf_cnpj": "CPF/CNPJ",
            "telefone": "Telefone",
            "email": "E-mail",
        }

    def clean_cpf_cnpj(self):
        documento_informado = self.cleaned_data["cpf_cnpj"].strip()
        numeros = re.sub(r"\D", "", documento_informado)

        if len(numeros) == 11:
            documento = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        elif len(numeros) == 14:
            documento = (
                f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
            )
        else:
            raise forms.ValidationError("Informe um CPF com 11 números ou CNPJ com 14 números.")

        qs = Doador.objects.filter(cpf_cnpj=documento)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este CPF/CNPJ já está cadastrado.")

        return documento

    def clean_telefone(self):
        telefone_informado = self.cleaned_data["telefone"].strip()

        if not telefone_informado:
            return ""

        numeros = re.sub(r"\D", "", telefone_informado)

        if len(numeros) == 11:
            return f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"

        if len(numeros) == 10:
            return f"({numeros[:2]}){numeros[2:6]}-{numeros[6:]}"

        raise forms.ValidationError("Informe um telefone válido com DDD.")


class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ["nome_responsavel", "endereco", "telefone", "num_membros"]
        widgets = {
            "nome_responsavel": forms.TextInput(
                attrs={"class": _CARD_INPUT_CLASS, "placeholder": "Nome do responsável"}
            ),
            "endereco": forms.Textarea(
                attrs={"class": _CARD_INPUT_CLASS, "rows": 3, "placeholder": "Endereço completo"}
            ),
            "telefone": forms.TextInput(
                attrs={"class": _CARD_INPUT_CLASS, "placeholder": "(00) 00000-0000"}
            ),
            "num_membros": forms.NumberInput(attrs={"class": _CARD_INPUT_CLASS, "min": "1"}),
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
            "nome": forms.TextInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "Nome da categoria (ex: Alimento)",
                }
            ),
            "descricao": forms.Textarea(
                attrs={"class": _CARD_INPUT_CLASS, "rows": 3, "placeholder": "Descrição opcional"}
            ),
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
            "nome": forms.TextInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "Nome do item (ex: Arroz 5kg)",
                }
            ),
            "categoria": forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
            "unidade_medida": forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
            "estoque_minimo": forms.NumberInput(attrs={"class": _CARD_INPUT_CLASS, "min": "0"}),
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
            raise forms.ValidationError(
                "O estoque mínimo deve ser um número inteiro maior ou igual a zero."
            )
        return valor


class DoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ["doador", "item", "quantidade", "data"]
        widgets = {
            "doador": forms.Select(
                attrs={
                    "class": _CARD_SELECT_CLASS,
                    "data-testid": "doacao-form-doador-select",
                }
            ),
            "item": forms.Select(
                attrs={
                    "class": _CARD_SELECT_CLASS,
                    "data-testid": "doacao-form-item-select",
                }
            ),
            "quantidade": forms.NumberInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Quantidade doada",
                    "data-testid": "doacao-form-quantidade-input",
                }
            ),
            "data": forms.DateInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "type": "date",
                    "data-testid": "doacao-form-data-input",
                }
            ),
        }
        labels = {
            "doador": "Doador",
            "item": "Item",
            "quantidade": "Quantidade",
            "data": "Data",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and not self.initial.get("data"):
            self.initial["data"] = timezone.localdate()

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get("quantidade")
        if quantidade is not None and quantidade <= 0:
            raise forms.ValidationError("A quantidade deve ser maior que zero.")
        return quantidade

    def clean_data(self):
        data = self.cleaned_data.get("data")
        if data is not None and data > timezone.localdate():
            raise forms.ValidationError("A data não pode ser no futuro.")
        return data
