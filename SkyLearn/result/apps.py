from django.apps import AppConfig


class ResultConfig(AppConfig):
    name = "result"

    def ready(self):
        import result.signals

