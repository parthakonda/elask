from importlib import import_module
import inspect

from elask.core.management.base import BaseCommand
from elask.db.models import Model

from elasticsearch_dsl import connections



class Command(BaseCommand):

    help = ("""
    To create the project
    """)

    def get_models(self, app):
        """
        To return list of models avialable in app
        """
        models_mod = import_module(app)        
        all_models = {}
        for model, model_class in inspect.getmembers(models_mod, inspect.isclass):
            if issubclass(model_class, Model):
                all_models.update({
                    model: model_class
                })
        return None if not all_models else all_models

    def init_models(self, app_models):
        """
        Will initiate all models
        """
        for app, app_model in app_models.items():
            for model, model_class in app_model.items():
                try:
                    model_class.init()
                    print("%s Initiated"%model)
                except Exception as e:
                    print(e)
                    print("%s - %"%(app, model))
        
    def handle(self, *args, **options):
        settings = import_module('settings.dev') # TODO: Need to get from env
        app_models = {}
        connections.create_connection(
            hosts=[settings.ELASTICSEARCH_DOMAIN]
        )
        for app in settings.INSTALLED_APPS:
            app_model = self.get_models("%s.models"%app)
            if app_model is not None:
                app_models.update({
                    app: app_model
                })
        self.init_models(app_models)
