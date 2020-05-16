from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'ads'

    def ready(self):
        print('--------akakakakaka----------------------')
        from actstream import registry
        registry.register(self.get_model('Ad'))

default_app_config = 'comohay.ads.MyAppConfig'