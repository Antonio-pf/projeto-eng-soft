from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Usuario não tem campo last_login (fora do schema do DER), então
        # desliga o receiver padrão do Django que tentaria gravar nele a cada login.
        from django.contrib.auth.signals import user_logged_in

        user_logged_in.disconnect(dispatch_uid="update_last_login")
