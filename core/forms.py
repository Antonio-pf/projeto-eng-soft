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
