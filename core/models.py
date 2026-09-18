from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.db import models


class UsuarioManager(BaseUserManager):
    def _criar_usuario(self, email, nome, perfil, password, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        usuario = self.model(
            email=self.normalize_email(email), nome=nome, perfil=perfil, **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, nome, password=None, perfil=None, **extra_fields):
        return self._criar_usuario(
            email, nome, perfil or Usuario.Perfil.VOLUNTARIO, password, **extra_fields
        )

    def create_superuser(self, email, nome, password=None, **extra_fields):
        # Necessário pra `createsuperuser`; não dá acesso a /admin/ (ver Usuario.is_staff).
        return self._criar_usuario(
            email, nome, Usuario.Perfil.ADMINISTRADOR, password, **extra_fields
        )


class Usuario(AbstractBaseUser):
    # Fora do schema do DER; o signal que gravaria aqui é desligado em core/apps.py.
    last_login = None

    class Perfil(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        VOLUNTARIO = "voluntario", "Voluntário"

    id_usuario = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    # Nome Python exigido pelo Django; grava na coluna já documentada no DER via db_column.
    password = models.CharField(max_length=255, db_column="senha_hash")
    perfil = models.CharField(max_length=15, choices=Perfil.choices)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        db_table = "usuario"
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return self.nome

    @property
    def is_active(self):
        return self.ativo

    @property
    def is_staff(self):
        # Sempre False: sem PermissionsMixin, ligar a `perfil` trocaria um 500 por outro em /admin/.
        return False


class Doador(models.Model):
    id_doador = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "doador"
        verbose_name = "doador"
        verbose_name_plural = "doadores"

    def __str__(self):
        return self.nome


class Familia(models.Model):
    id_familia = models.BigAutoField(primary_key=True)
    nome_responsavel = models.CharField(max_length=150)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20, blank=True)
    num_membros = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "familia"
        verbose_name = "família"
        verbose_name_plural = "famílias"

    def __str__(self):
        return self.nome_responsavel


class CategoriaItem(models.Model):
    id_categoria_item = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        db_table = "categoria_item"
        verbose_name = "categoria de item"
        verbose_name_plural = "categorias de item"

    def __str__(self):
        return self.nome


class UnidadeMedida(models.Model):
    id_unidade_medida = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    sigla = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = "unidade_medida"
        verbose_name = "unidade de medida"
        verbose_name_plural = "unidades de medida"

    def __str__(self):
        return self.nome


class Item(models.Model):
    id_item = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=150)
    categoria = models.ForeignKey(CategoriaItem, on_delete=models.PROTECT)
    unidade_medida = models.ForeignKey(UnidadeMedida, on_delete=models.PROTECT)
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "item"
        indexes = [models.Index(fields=["unidade_medida"], name="idx_item_id_unidade")]
        verbose_name = "item"
        verbose_name_plural = "itens"

    def __str__(self):
        return self.nome


class Doacao(models.Model):
    id_doacao = models.BigAutoField(primary_key=True)
    doador = models.ForeignKey(Doador, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    registrado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="doacoes_registradas"
    )
    quantidade = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    data = models.DateField()
    cancelado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)
    cancelado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="doacoes_canceladas",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "doacao"
        indexes = [
            models.Index(fields=["item"], name="idx_doacao_id_item"),
            models.Index(fields=["doador"], name="idx_doacao_id_doador"),
            models.Index(fields=["data"], name="idx_doacao_data"),
        ]
        verbose_name = "doação"
        verbose_name_plural = "doações"


class Distribuicao(models.Model):
    id_distribuicao = models.BigAutoField(primary_key=True)
    familia = models.ForeignKey(Familia, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="distribuicoes_registradas",
    )
    quantidade = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    data = models.DateField()
    cancelado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)
    cancelado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="distribuicoes_canceladas",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "distribuicao"
        indexes = [
            models.Index(fields=["item"], name="idx_dist_id_item"),
            models.Index(fields=["familia"], name="idx_dist_id_familia"),
            models.Index(fields=["data"], name="idx_dist_data"),
        ]
        verbose_name = "distribuição"
        verbose_name_plural = "distribuições"
