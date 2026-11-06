import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils import formats, timezone

from core.models import CategoriaItem, Distribuicao, Doacao, Doador, Familia, Item, Usuario

_INPUT_CLASS = (
    "input input-bordered h-12 w-full rounded-[10px] bg-white placeholder:text-conecta-muted"
)

_CARD_INPUT_CLASS = (
    "w-full rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-700 "
    "placeholder:text-gray-400"
)

_CARD_SELECT_CLASS = f"{_CARD_INPUT_CLASS} appearance-none pr-9"

_PATTERN_TELEFONE = r"(?:\d{10,11}|\(\d{2}\)\d{4,5}-\d{4})"
_TITLE_TELEFONE = "Informe o telefone com DDD."
_PATTERN_QUANTIDADE = r"[0-9]{1,8}([,.][0-9]{1,2})?"
_TITLE_QUANTIDADE = "Informe a quantidade com até 2 casas decimais, por exemplo 2,5."


def _attrs_mascara(mascara, inputmode, **attrs):
    """Campo de texto com a máscara de static/js/mascaras.js; sem JS, o pattern segura o envio."""
    return {"class": _CARD_INPUT_CLASS, "data-mascara": mascara, "inputmode": inputmode, **attrs}


def _inteiro(placeholder):
    return forms.TextInput(
        attrs=_attrs_mascara(
            "inteiro",
            "numeric",
            pattern="[0-9]*",
            title="Informe só números.",
            placeholder=placeholder,
        )
    )


def _quantidade(placeholder):
    return forms.TextInput(
        attrs=_attrs_mascara(
            "decimal",
            "decimal",
            pattern=_PATTERN_QUANTIDADE,
            title=_TITLE_QUANTIDADE,
            placeholder=placeholder,
        )
    )


def _normalizar_telefone(telefone_informado):
    """Vazio é aceito; 10 ou 11 dígitos com DDD viram (00)0000-0000 ou (00)00000-0000."""
    telefone_informado = telefone_informado.strip()

    if not telefone_informado:
        return ""

    numeros = re.sub(r"\D", "", telefone_informado)

    if len(numeros) == 11:
        return f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"

    if len(numeros) == 10:
        return f"({numeros[:2]}){numeros[2:6]}-{numeros[6:]}"

    raise forms.ValidationError("Informe um telefone válido com DDD.")


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "class": _INPUT_CLASS,
                "placeholder": "seu@email.com",
            }
        ),
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": f"{_INPUT_CLASS} pr-16",
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
            }
        ),
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "class": _CARD_INPUT_CLASS,
                "placeholder": "maria@conectasocial.org",
            }
        ),
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": _CARD_INPUT_CLASS,
                "autocomplete": "new-password",
            }
        ),
    )
    perfil = forms.ChoiceField(
        label="Perfil",
        choices=Usuario.Perfil.choices,
        widget=forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
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
                }
            ),
            "cpf_cnpj": forms.TextInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "000.000.000-00 ou CNPJ",
                    "data-mascara": "cpf-cnpj",
                    "inputmode": "numeric",
                    "maxlength": "18",
                    "pattern": (
                        r"(?:\d{11}|\d{14}|"
                        r"\d{3}\.\d{3}\.\d{3}-\d{2}|"
                        r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"
                    ),
                    "title": "Informe um CPF com 11 números ou CNPJ com 14 números.",
                }
            ),
            "telefone": forms.TextInput(
                attrs=_attrs_mascara(
                    "telefone",
                    "numeric",
                    placeholder="(00)00000-0000",
                    maxlength="14",
                    pattern=_PATTERN_TELEFONE,
                    title=_TITLE_TELEFONE,
                )
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "placeholder": "doador@email.com",
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
        return _normalizar_telefone(self.cleaned_data["telefone"])


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
                attrs=_attrs_mascara(
                    "telefone",
                    "numeric",
                    placeholder="(00)00000-0000",
                    maxlength="14",
                    pattern=_PATTERN_TELEFONE,
                    title=_TITLE_TELEFONE,
                )
            ),
            "num_membros": _inteiro("Ex.: 4"),
        }
        labels = {
            "nome_responsavel": "Nome do Responsável",
            "endereco": "Endereço",
            "telefone": "Telefone",
            "num_membros": "Número de Membros",
        }

    def clean_telefone(self):
        return _normalizar_telefone(self.cleaned_data["telefone"])


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
            "estoque_minimo": _inteiro("0"),
        }
        labels = {
            "nome": "Nome do Item",
            "categoria": "Categoria",
            "unidade_medida": "Unidade de Medida",
            "estoque_minimo": "Estoque Mínimo",
        }


class MovimentacaoForm(forms.ModelForm):
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


class DoacaoForm(MovimentacaoForm):
    class Meta:
        model = Doacao
        fields = ["doador", "item", "quantidade", "data"]
        # Aceita a vírgula decimal ("2,5") além do ponto.
        localized_fields = ["quantidade"]
        widgets = {
            "doador": forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
            "item": forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
            "quantidade": _quantidade("Quantidade doada (ex.: 2,5)"),
            "data": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "type": "date",
                },
            ),
        }
        labels = {
            "doador": "Doador",
            "item": "Item",
            "quantidade": "Quantidade",
            "data": "Data",
        }


class ItemComSaldoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nome} saldo: {formats.number_format(obj.saldo_atual, 2)}"


class DistribuicaoForm(MovimentacaoForm):
    item = ItemComSaldoChoiceField(
        queryset=Item.objects.select_related("unidade_medida"),
        label="Item",
        widget=forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
    )

    class Meta:
        model = Distribuicao
        fields = ["familia", "item", "quantidade", "data"]
        # Aceita a vírgula decimal ("2,5") além do ponto.
        localized_fields = ["quantidade"]
        widgets = {
            "familia": forms.Select(attrs={"class": _CARD_SELECT_CLASS}),
            "quantidade": _quantidade("Quantidade distribuída (ex.: 2,5)"),
            "data": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": _CARD_INPUT_CLASS,
                    "type": "date",
                },
            ),
        }
        labels = {
            "familia": "Família",
            "quantidade": "Quantidade",
            "data": "Data",
        }

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get("item")
        quantidade = cleaned_data.get("quantidade")
        if item is not None and quantidade is not None:
            saldo_atual = item.saldo_atual
            if quantidade > saldo_atual:
                raise forms.ValidationError(
                    f"Saldo insuficiente: disponível {formats.number_format(saldo_atual, 2)}, "
                    f"solicitado {formats.number_format(quantidade, 2)}."
                )
        return cleaned_data
