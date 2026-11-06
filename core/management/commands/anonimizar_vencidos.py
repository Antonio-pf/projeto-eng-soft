from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import Doador, Familia
from core.privacidade import PRAZO_RETENCAO_ANOS, data_limite


class Command(BaseCommand):
    help = (
        f"Anonimiza doadores e famílias sem movimentação há {PRAZO_RETENCAO_ANOS} anos "
        "(prazo de retenção do aviso de privacidade). As doações e distribuições ficam."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--simular",
            action="store_true",
            help="Só mostra quantos cadastros seriam anonimizados, sem gravar nada.",
        )

    def handle(self, *args, **options):
        hoje = timezone.localdate()
        limite = data_limite(hoje)
        prazo = (
            f"Prazo de retenção: {PRAZO_RETENCAO_ANOS} anos "
            f"(última movimentação até {limite:%d/%m/%Y})."
        )
        self.stdout.write(prazo)

        with transaction.atomic():
            doadores = list(Doador.objects.vencidos(hoje))
            familias = list(Familia.objects.vencidas(hoje))

            if options["simular"]:
                self.stdout.write(
                    f"Simulação: {len(doadores)} doador(es) e {len(familias)} família(s) "
                    "seriam anonimizados. Nada foi gravado."
                )
                return

            for doador in doadores:
                doador.anonimizar()
            for familia in familias:
                familia.anonimizar()

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(doadores)} doador(es) e {len(familias)} família(s) anonimizados."
            )
        )
