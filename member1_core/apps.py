from django.apps import AppConfig


class Member1CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "member1_core"

    def ready(self):
        from . import signals  # noqa: F401