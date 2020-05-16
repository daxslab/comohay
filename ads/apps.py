from django.apps import AppConfig


class AdsConfig(AppConfig):
    name = 'ads'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Ad'))
